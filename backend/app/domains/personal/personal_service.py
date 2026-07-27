"""Personal module service (business logic + orchestration).

Sits between the router and the repositories/per-table services. It owns the
module's business rules -- validation, ownership permission checks, moment
state transitions (activate / pause / archive), quick-add ingestion, and the
pulse / memory / analytics aggregations -- and returns Pydantic schemas only,
never SQLAlchemy models. No HTTP concerns here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, StateTransitionError, ValidationError
from app.core.service import Page
from app.domains.personal.api_schemas import (
    PersonalAnalyticsResponse,
    PersonalMemoryOverviewResponse,
    PersonalMomentCounts,
)
from app.domains.personal.repository import (
    PersonalMomentsRepository,
    PersonalMomentTypesRepository,
    PersonalQuickAddEventsRepository,
)
from app.domains.personal.schemas import (
    PersonalMomentProfilesSchema,
    PersonalMomentsSchema,
    PersonalMomentTypesSchema,
    PersonalPulseSnapshotsSchema,
    PersonalQuickAddEventsSchema,
)
from app.domains.personal.service import (
    PersonalInsightsService,
    PersonalMemoryDriverRankingsService,
    PersonalMemoryEmotionalDnaService,
    PersonalMemoryEvolutionSnapshotsService,
    PersonalMemoryIdentitySnapshotsService,
    PersonalMemoryPatternsService,
    PersonalMetricSnapshotsService,
    PersonalMomentProfilesService,
    PersonalMomentsService,
    PersonalMomentTypesService,
    PersonalPulseSnapshotsService,
    PersonalRecommendationsService,
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PersonalService:
    """Facade orchestrating the Personal domain repositories/services."""

    ACTIVATE_FROM = {"DRAFT", "PAUSED"}
    PAUSE_FROM = {"ACTIVE"}

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        # per-table services (reads + generic writes, all schema-returning)
        self.types = PersonalMomentTypesService(session)
        self.moments = PersonalMomentsService(session)
        self.profiles = PersonalMomentProfilesService(session)
        self.pulse = PersonalPulseSnapshotsService(session)
        self.insights = PersonalInsightsService(session)
        self.recommendations = PersonalRecommendationsService(session)
        self.metrics = PersonalMetricSnapshotsService(session)
        self.mem_identity = PersonalMemoryIdentitySnapshotsService(session)
        self.mem_patterns = PersonalMemoryPatternsService(session)
        self.mem_emotional = PersonalMemoryEmotionalDnaService(session)
        self.mem_drivers = PersonalMemoryDriverRankingsService(session)
        self.mem_evolution = PersonalMemoryEvolutionSnapshotsService(session)
        # repositories for atomic multi-step workflows
        self.moments_repo = PersonalMomentsRepository(session)
        self.types_repo = PersonalMomentTypesRepository(session)
        self.quick_add_repo = PersonalQuickAddEventsRepository(session)

    # ------------------------------------------------------------------ #
    # moment types (global reference data)
    # ------------------------------------------------------------------ #
    async def list_moment_types(self, *, active_only: bool = True) -> list[PersonalMomentTypesSchema]:
        filters = {"is_active": True} if active_only else None
        return await self.types.list(filters=filters, order_by="display_order", limit=None)

    # ------------------------------------------------------------------ #
    # moments
    # ------------------------------------------------------------------ #
    async def list_moments(
        self,
        user_id: UUID,
        *,
        status: str | None = None,
        moment_type_id: UUID | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Page[PersonalMomentsSchema]:
        filters: dict[str, Any] = {}
        if status:
            filters["status"] = status
        if moment_type_id:
            filters["moment_type_id"] = moment_type_id
        # archived moments are soft-deleted (archived_at); include them only when asked
        include_deleted = status == "ARCHIVED"
        return await self.moments.paginate(
            actor=user_id,
            filters=filters or None,
            order_by="-created_at",
            limit=per_page,
            offset=(page - 1) * per_page,
            include_deleted=include_deleted,
        )

    async def get_moment(self, user_id: UUID, moment_id: UUID) -> PersonalMomentsSchema:
        return await self.moments.get_or_raise(moment_id, actor=user_id)

    async def create_moment(
        self, user_id: UUID, *, moment_type_id: UUID, moment_name: str
    ) -> PersonalMomentsSchema:
        moment_type = await self.types_repo.get_by_id(moment_type_id)
        if moment_type is None or not moment_type.is_active:
            raise ValidationError("moment_type_id does not reference an active moment type")
        return await self.moments.create(
            {"moment_type_id": moment_type_id, "moment_name": moment_name, "status": "DRAFT"},
            actor=user_id,
        )

    async def _owned_moment(self, user_id: UUID, moment_id: UUID):
        obj = await self.moments_repo.get_by_id(moment_id)
        if obj is None or obj.user_id != user_id:
            raise NotFoundError("Personal moment not found")
        return obj

    async def _finalize(self, obj) -> PersonalMomentsSchema:
        await self.session.flush()
        schema = PersonalMomentsSchema.model_validate(obj)
        await self.session.commit()
        return schema

    async def activate_moment(self, user_id: UUID, moment_id: UUID) -> PersonalMomentsSchema:
        obj = await self._owned_moment(user_id, moment_id)
        if obj.status not in self.ACTIVATE_FROM:
            raise StateTransitionError(f"Cannot activate a moment in status {obj.status}")
        now = _now()
        obj.status = "ACTIVE"
        # DB constraint: an ACTIVE moment must have activated_at set
        obj.activated_at = obj.activated_at or now
        obj.last_activity_at = now
        obj.updated_at = now
        return await self._finalize(obj)

    async def pause_moment(self, user_id: UUID, moment_id: UUID) -> PersonalMomentsSchema:
        obj = await self._owned_moment(user_id, moment_id)
        if obj.status not in self.PAUSE_FROM:
            raise StateTransitionError(f"Cannot pause a moment in status {obj.status}")
        obj.status = "PAUSED"
        obj.updated_at = _now()
        return await self._finalize(obj)

    async def archive_moment(self, user_id: UUID, moment_id: UUID) -> PersonalMomentsSchema:
        obj = await self._owned_moment(user_id, moment_id)
        if obj.status == "ARCHIVED":
            raise StateTransitionError("Moment is already archived")
        now = _now()
        obj.status = "ARCHIVED"
        obj.archived_at = now  # soft-delete marker for personal_moments
        obj.updated_at = now
        return await self._finalize(obj)

    # ------------------------------------------------------------------ #
    # profiles (setup / identity snapshots attached to a moment)
    # ------------------------------------------------------------------ #
    async def list_profiles(
        self, user_id: UUID, *, moment_id: UUID | None = None, page: int = 1, per_page: int = 20
    ) -> Page[PersonalMomentProfilesSchema]:
        filters = {"moment_id": moment_id} if moment_id else None
        return await self.profiles.paginate(
            actor=user_id,
            filters=filters,
            order_by="-created_at",
            limit=per_page,
            offset=(page - 1) * per_page,
        )

    async def create_profile(
        self, user_id: UUID, moment_id: UUID, data: dict[str, Any]
    ) -> PersonalMomentProfilesSchema:
        await self._owned_moment(user_id, moment_id)  # ownership + existence check
        return await self.profiles.create({**data, "moment_id": moment_id}, actor=user_id)

    # ------------------------------------------------------------------ #
    # quick add (ingest a raw event against an active moment)
    # ------------------------------------------------------------------ #
    async def quick_add(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        moment_type_code: str,
        quick_add_tab_code: str,
        event_type: str,
        raw_payload: dict[str, Any],
        event_occurred_at: datetime | None = None,
    ) -> PersonalQuickAddEventsSchema:
        moment = await self._owned_moment(user_id, moment_id)
        if moment.status != "ACTIVE":
            raise StateTransitionError("Quick add is only allowed on ACTIVE moments")
        now = _now()
        event = await self.quick_add_repo.create(
            {
                "moment_id": moment_id,
                "user_id": user_id,
                "moment_type_code": moment_type_code,
                "quick_add_tab_code": quick_add_tab_code,
                "event_type": event_type,
                "event_occurred_at": event_occurred_at or now,
                "raw_payload": raw_payload,
            }
        )
        await self.session.refresh(event)
        # keep the parent moment's activity fresh
        moment.last_activity_at = now
        moment.updated_at = now
        schema = PersonalQuickAddEventsSchema.model_validate(event)
        await self.session.commit()
        return schema

    # ------------------------------------------------------------------ #
    # pulse
    # ------------------------------------------------------------------ #
    async def get_pulse(
        self, user_id: UUID, *, moment_id: UUID | None = None, limit: int = 20
    ) -> list[PersonalPulseSnapshotsSchema]:
        filters = {"moment_id": moment_id} if moment_id else None
        return await self.pulse.list(
            actor=user_id, filters=filters, order_by="-snapshot_date", limit=limit
        )

    # ------------------------------------------------------------------ #
    # memory
    # ------------------------------------------------------------------ #
    async def memory_overview(
        self, user_id: UUID, *, moment_id: UUID | None = None
    ) -> PersonalMemoryOverviewResponse:
        base: dict[str, Any] = {"moment_id": moment_id} if moment_id else {}
        current = {**base, "is_current": True}
        return PersonalMemoryOverviewResponse(
            identity_snapshots=await self.mem_identity.list(
                actor=user_id, filters=current, order_by="-snapshot_month", limit=10
            ),
            patterns=await self.mem_patterns.list(
                actor=user_id, filters=base or None, order_by="-confidence_score", limit=20
            ),
            emotional_dna=await self.mem_emotional.list(
                actor=user_id, filters=current, order_by="emotion_rank", limit=20
            ),
            driver_rankings=await self.mem_drivers.list(
                actor=user_id, filters=current, order_by="driver_rank", limit=20
            ),
            evolution_snapshots=await self.mem_evolution.list(
                actor=user_id, filters=current, order_by="-snapshot_month", limit=10
            ),
        )

    # ------------------------------------------------------------------ #
    # analytics
    # ------------------------------------------------------------------ #
    async def analytics(self, user_id: UUID) -> PersonalAnalyticsResponse:
        active = await self.moments.count(actor=user_id, filters={"status": "ACTIVE"})
        paused = await self.moments.count(actor=user_id, filters={"status": "PAUSED"})
        draft = await self.moments.count(actor=user_id, filters={"status": "DRAFT"})
        archived = await self.moments.count(
            actor=user_id, filters={"status": "ARCHIVED"}, include_deleted=True
        )
        counts = PersonalMomentCounts(
            total=active + paused + draft + archived,
            draft=draft,
            active=active,
            paused=paused,
            archived=archived,
        )
        insights = await self.insights.list(
            actor=user_id, filters={"is_active": True}, order_by="-created_at", limit=10
        )
        recommendations = await self.recommendations.list(
            actor=user_id, filters={"status": "ACTIVE"}, order_by="-priority_score", limit=10
        )
        metrics = await self.metrics.list(actor=user_id, order_by="-created_at", limit=10)
        return PersonalAnalyticsResponse(
            counts=counts,
            insights=insights,
            recommendations=recommendations,
            metrics=metrics,
        )
