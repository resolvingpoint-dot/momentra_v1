"""Load all projection source data in a single pass."""
from __future__ import annotations

import asyncio
from uuid import UUID

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository
from app.domains.personal.catalog import PERSONAL_CONTEXT, normalize_moment_type_code
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalLifeAggregateSnapshots,
    PersonalLifeConnections,
    PersonalLifeDriftAlerts,
    PersonalLifeHealthSnapshots,
    PersonalLifeJourneyEvents,
    PersonalLifeMonthlyChanges,
    PersonalFutureBuildingProfile,
    PersonalLifestyleProfile,
    PersonalRelationshipsProfile,
    PersonalLifeOperationsProfile,
    PersonalMemoryDriverRankings,
    PersonalMemoryEmotionalDna,
    PersonalMemoryEvolutionSnapshots,
    PersonalMemoryIdentitySnapshots,
    PersonalMemoryPatterns,
    PersonalMetricSnapshots,
    PersonalMomentHighlights,
    PersonalMomentTurningPoints,
    PersonalMoneyEvents,
    PersonalRecommendations,
    PersonalRuntimeSnapshots,
)
from app.domains.personal.projection.context import MomentContext, ProjectionContext
from app.domains.reference_data.catalog import get_reference_catalog

_ACTIVE = {"ACTIVE"}
_VISIBLE = {"DRAFT", "ACTIVE", "PAUSED", "SETUP"}
_MY_MONEY = {"LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS"}


class ProjectionBuilder:
    @staticmethod
    async def build(session: AsyncSession, user_id: UUID) -> ProjectionContext:
        repo = MomentRepository(session)
        all_moments = await repo.list_by_context(user_id, PERSONAL_CONTEXT)
        visible = [m for m in all_moments if m.status in _VISIBLE]
        active = [m for m in visible if m.status in _ACTIVE]

        moments_by_type: dict[str, MomentContext] = {}
        runtime_scores: dict[str, int] = {}

        moment_loads: list[tuple[str, Any]] = []
        for moment in active:
            code = normalize_moment_type_code(moment.moment_type or "")
            if code not in _MY_MONEY:
                continue
            moment_loads.append(
                (
                    code,
                    ProjectionBuilder._load_moment_context(
                        session, user_id, moment, code
                    ),
                )
            )

        if moment_loads:
            loaded = await asyncio.gather(*(coro for _, coro in moment_loads))
            for (code, _), mctx in zip(moment_loads, loaded):
                moments_by_type[code] = mctx
                if mctx.runtime and mctx.runtime.primary_score is not None:
                    runtime_scores[code] = int(round(float(mctx.runtime.primary_score)))

        (
            identity,
            patterns,
            drivers,
            dna,
            evolution,
            mem_recs,
            life_health,
            life_agg,
            connections,
            drift,
            journey,
            monthly,
            life_recs,
        ) = await asyncio.gather(
            ProjectionBuilder._load_identity_snapshots(session, user_id),
            ProjectionBuilder._load_memory_patterns(session, user_id),
            ProjectionBuilder._load_driver_rankings(session, user_id),
            ProjectionBuilder._load_emotional_dna(session, user_id),
            ProjectionBuilder._load_evolution(session, user_id),
            ProjectionBuilder._load_recommendations(session, user_id, "MEMORY"),
            ProjectionBuilder._load_life_health(session, user_id),
            ProjectionBuilder._load_life_aggregate(session, user_id),
            ProjectionBuilder._load_life_connections(session, user_id),
            ProjectionBuilder._load_drift_alerts(session, user_id),
            ProjectionBuilder._load_journey_events(session, user_id),
            ProjectionBuilder._load_monthly_changes(session, user_id),
            ProjectionBuilder._load_recommendations(session, user_id, "LIFE"),
        )

        return ProjectionContext(
            user_id=user_id,
            visible_moments=visible,
            active_moments=active,
            moments_by_type=moments_by_type,
            catalog=get_reference_catalog(),
            identity_snapshots=identity,
            memory_patterns=patterns,
            driver_rankings=drivers,
            emotional_dna=dna,
            evolution_snapshots=evolution,
            memory_recommendations=mem_recs,
            life_health=life_health,
            life_aggregate=life_agg,
            life_connections=connections,
            drift_alerts=drift,
            journey_events=journey,
            monthly_changes=monthly,
            life_recommendations=life_recs,
            runtime_scores_by_type=runtime_scores,
        )

    @staticmethod
    async def _load_moment_context(
        session: AsyncSession,
        user_id: UUID,
        moment: MomentModel,
        code: str,
    ) -> MomentContext:
        moment_id = moment.id

        timeline_result = await session.execute(
            select(PersonalActivityTimeline)
            .where(
                PersonalActivityTimeline.moment_id == moment_id,
                PersonalActivityTimeline.is_voided.is_(False),
            )
            .order_by(PersonalActivityTimeline.event_occurred_at.desc())
            .limit(50)
        )
        timeline = list(timeline_result.scalars().all())

        count_result = await session.execute(
            select(func.count())
            .select_from(PersonalActivityTimeline)
            .where(
                PersonalActivityTimeline.moment_id == moment_id,
                PersonalActivityTimeline.is_voided.is_(False),
            )
        )
        timeline_count = int(count_result.scalar_one() or 0)

        money_result = await session.execute(
            select(PersonalMoneyEvents).where(
                PersonalMoneyEvents.moment_id == moment_id,
                PersonalMoneyEvents.is_voided.is_(False),
            )
        )
        money_events = list(money_result.scalars().all())

        runtime_result = await session.execute(
            select(PersonalRuntimeSnapshots)
            .where(
                PersonalRuntimeSnapshots.moment_id == moment_id,
                PersonalRuntimeSnapshots.moment_type_code == code,
            )
            .order_by(PersonalRuntimeSnapshots.snapshot_date.desc())
            .limit(1)
        )
        runtime = runtime_result.scalar_one_or_none()

        metrics_result = await session.execute(
            select(PersonalMetricSnapshots)
            .where(
                PersonalMetricSnapshots.moment_id == moment_id,
                PersonalMetricSnapshots.moment_type_code == code,
            )
            .order_by(PersonalMetricSnapshots.snapshot_date.desc())
            .limit(10)
        )
        metrics = list(metrics_result.scalars().all())

        profile = None
        if code == "LIFE_OPERATIONS":
            prof_result = await session.execute(
                select(PersonalLifeOperationsProfile).where(
                    PersonalLifeOperationsProfile.moment_id == moment_id
                )
            )
            profile = prof_result.scalar_one_or_none()
        elif code == "FUTURE_BUILDING":
            prof_result = await session.execute(
                select(PersonalFutureBuildingProfile).where(
                    PersonalFutureBuildingProfile.moment_id == moment_id
                )
            )
            profile = prof_result.scalar_one_or_none()
        elif code == "LIFESTYLE":
            prof_result = await session.execute(
                select(PersonalLifestyleProfile).where(
                    PersonalLifestyleProfile.moment_id == moment_id
                )
            )
            profile = prof_result.scalar_one_or_none()
        elif code == "RELATIONSHIPS":
            prof_result = await session.execute(
                select(PersonalRelationshipsProfile).where(
                    PersonalRelationshipsProfile.moment_id == moment_id
                )
            )
            profile = prof_result.scalar_one_or_none()

        highlights_result = await session.execute(
            select(PersonalMomentHighlights)
            .where(
                PersonalMomentHighlights.moment_id == moment_id,
                PersonalMomentHighlights.is_current.is_(True),
            )
            .order_by(PersonalMomentHighlights.occurred_at.desc())
            .limit(6)
        )
        highlights = list(highlights_result.scalars().all())

        turning_result = await session.execute(
            select(PersonalMomentTurningPoints)
            .where(
                PersonalMomentTurningPoints.moment_id == moment_id,
                PersonalMomentTurningPoints.is_current.is_(True),
            )
            .order_by(PersonalMomentTurningPoints.occurred_at.desc().nullslast())
            .limit(6)
        )
        turning_points = list(turning_result.scalars().all())

        return MomentContext(
            moment=moment,
            timeline=timeline,
            timeline_count=timeline_count,
            money_events=money_events,
            runtime=runtime,
            metrics=metrics,
            profile=profile,
            highlights=highlights,
            turning_points=turning_points,
        )

    @staticmethod
    async def _load_identity_snapshots(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalMemoryIdentitySnapshots]:
        result = await session.execute(
            select(PersonalMemoryIdentitySnapshots).where(
                PersonalMemoryIdentitySnapshots.user_id == user_id,
                PersonalMemoryIdentitySnapshots.is_current.is_(True),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_memory_patterns(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalMemoryPatterns]:
        result = await session.execute(
            select(PersonalMemoryPatterns).where(
                PersonalMemoryPatterns.user_id == user_id,
                PersonalMemoryPatterns.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_driver_rankings(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalMemoryDriverRankings]:
        result = await session.execute(
            select(PersonalMemoryDriverRankings).where(
                PersonalMemoryDriverRankings.user_id == user_id,
                PersonalMemoryDriverRankings.is_current.is_(True),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_emotional_dna(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalMemoryEmotionalDna]:
        result = await session.execute(
            select(PersonalMemoryEmotionalDna).where(
                PersonalMemoryEmotionalDna.user_id == user_id,
                PersonalMemoryEmotionalDna.is_current.is_(True),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_evolution(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalMemoryEvolutionSnapshots]:
        result = await session.execute(
            select(PersonalMemoryEvolutionSnapshots).where(
                PersonalMemoryEvolutionSnapshots.user_id == user_id,
                PersonalMemoryEvolutionSnapshots.is_current.is_(True),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_recommendations(
        session: AsyncSession, user_id: UUID, scope: str
    ) -> list[PersonalRecommendations]:
        result = await session.execute(
            select(PersonalRecommendations).where(
                PersonalRecommendations.user_id == user_id,
                PersonalRecommendations.recommendation_scope == scope,
                PersonalRecommendations.status == "ACTIVE",
            )
            .order_by(PersonalRecommendations.priority_score.desc())
            .limit(5)
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_life_health(
        session: AsyncSession, user_id: UUID
    ) -> PersonalLifeHealthSnapshots | None:
        result = await session.execute(
            select(PersonalLifeHealthSnapshots)
            .where(
                PersonalLifeHealthSnapshots.user_id == user_id,
                PersonalLifeHealthSnapshots.is_current.is_(True),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _load_life_aggregate(
        session: AsyncSession, user_id: UUID
    ) -> PersonalLifeAggregateSnapshots | None:
        result = await session.execute(
            select(PersonalLifeAggregateSnapshots)
            .where(
                PersonalLifeAggregateSnapshots.user_id == user_id,
                PersonalLifeAggregateSnapshots.is_current.is_(True),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _load_life_connections(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalLifeConnections]:
        result = await session.execute(
            select(PersonalLifeConnections).where(
                PersonalLifeConnections.user_id == user_id,
                PersonalLifeConnections.is_current.is_(True),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_drift_alerts(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalLifeDriftAlerts]:
        result = await session.execute(
            select(PersonalLifeDriftAlerts).where(
                PersonalLifeDriftAlerts.user_id == user_id,
                PersonalLifeDriftAlerts.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_journey_events(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalLifeJourneyEvents]:
        result = await session.execute(
            select(PersonalLifeJourneyEvents)
            .where(PersonalLifeJourneyEvents.user_id == user_id)
            .order_by(PersonalLifeJourneyEvents.journey_month.desc())
            .limit(6)
        )
        return list(result.scalars().all())

    @staticmethod
    async def _load_monthly_changes(
        session: AsyncSession, user_id: UUID
    ) -> list[PersonalLifeMonthlyChanges]:
        result = await session.execute(
            select(PersonalLifeMonthlyChanges)
            .where(PersonalLifeMonthlyChanges.user_id == user_id)
            .order_by(PersonalLifeMonthlyChanges.snapshot_month.desc())
            .limit(6)
        )
        return list(result.scalars().all())
