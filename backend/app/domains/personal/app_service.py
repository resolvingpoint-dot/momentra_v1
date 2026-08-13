"""Contract-first Personal service consumed by the mobile clients.

Personal moments are persisted in the shared ``moments`` table
(``context_type = "MY_MONEY"``) so create/list/patch flows are real and
work against the existing test ``MockSession``. The rich analytical surfaces
(pulse / memory / life / live) return schema-valid empty-state payloads that
render correctly on both apps; wiring them to the ``personal_*`` snapshot
tables/views is the iterative data-backing step.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, SnapshotRebuildingError, ValidationError
from app.core.template_analytics import log_setup_step

from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.moment_engine.engine import MomentEngine
from app.domains.moment_engine.registry import get_domain_registry
from app.domains.module_states.service import ModuleStateService
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository
from app.domains.personal import app_schemas as s
from app.domains.personal.catalog import (
    MOMENT_TYPES,
    PERSONAL_CONTEXT,
    moment_type_id,
    moment_type_name,
    normalize_moment_type_code,
)
from app.domains.personal.templates.future_building.setup_schema import (
    FUTURE_BUILDING_TEMPLATE_CONTRACT,
    upsert_future_building_profile,
)
from app.domains.personal.templates.life_operations.setup_schema import (
    LIFE_OPERATIONS_TEMPLATE_CONTRACT,
    upsert_life_operations_profile,
)
from app.domains.personal.templates.lifestyle.setup_schema import (
    LIFESTYLE_TEMPLATE_CONTRACT,
    upsert_lifestyle_profile,
)
from app.domains.personal.templates.relationships.setup_schema import (
    RELATIONSHIPS_TEMPLATE_CONTRACT,
    upsert_relationships_profile,
)
from app.domains.personal.accounts_service import PersonalAccountsService
from app.domains.personal.inventory import (
    latest_by_code as _shared_latest_by_code,
    load_moment_inventories,
    sync_module_states,
)
from app.domains.personal.quick_add.router import PersonalQuickAddRouter
from app.domains.personal.personal_moment_sync import ensure_personal_moment, try_ensure_personal_moment

_ACTIVE_STATUSES = {"ACTIVE"}
_SWITCHER_ACTIVE_STATUSES = {"ACTIVE", "PAUSED", "COMPLETED"}
_VISIBLE_STATUSES = {"DRAFT", "ACTIVE", "PAUSED", "COMPLETED", "SETUP"}

_DETAIL_TEMPLATES = ("FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS")
_MEMORY_SECTION_LABELS = {
    "FUTURE_BUILDING": "Future Building Memory",
    "LIFESTYLE": "Lifestyle Memory",
    "RELATIONSHIPS": "Relationships Memory",
}

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_minor(amount: str | None) -> int:
    if not amount:
        return 0
    try:
        return int((Decimal(str(amount)) * 100).quantize(Decimal("1")))
    except (InvalidOperation, ValueError):
        return 0


def _moments_detail_from_slice(payload: dict | None) -> dict | None:
    if not payload:
        return None
    proj = payload.get("moment_projection")
    if proj is None:
        return None
    return {"metrics": proj}


def _memory_block_from_slice(payload: dict | None, *, section_label: str) -> dict | None:
    """Map Redis template memory slice → aggregate /memory block shape."""
    if not payload:
        return None
    if payload.get("metrics") is not None and payload.get("section_label"):
        return payload
    mp = payload.get("memory_projection")
    if mp is None:
        return None
    identity = mp.get("identity_snapshot") if isinstance(mp, dict) else None
    identity = identity if isinstance(identity, dict) else {}
    ai = mp.get("ai_interpretation") if isinstance(mp, dict) else None
    ai = ai if isinstance(ai, dict) else {}
    return {
        "section_label": section_label,
        "status_label": str(payload.get("status") or "ACTIVE"),
        "synthesis_title": identity.get("title") or section_label,
        "synthesis_body": identity.get("body") or "",
        "system_state": "Active",
        "days_analyzed": 1,
        "confidence_percent": 70,
        "confidence_title": "Pattern Confidence",
        "confidence_body": ai.get("quote") or "",
        "identity_label": identity.get("title") or "",
        "direction_label": "",
        "style_label": "",
        "focus_label": "",
        "neural_growth_title": "",
        "neural_growth_subtitle": "",
        "breakthrough_title": "",
        "breakthrough_body": "",
        "breakthrough_active": False,
        "focus_title": "Focus",
        "focus_percent": 70,
        "focus_body": "",
        "metrics": mp,
        "identified_patterns": (
            mp.get("behavioral_patterns")
            or mp.get("identified_patterns")
            or []
            if isinstance(mp, dict)
            else []
        ),
        "confidence_evolution": (
            mp.get("confidence_evolution") or [] if isinstance(mp, dict) else []
        ),
    }

class PersonalAppService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.engine = MomentEngine()
        self.modules = ModuleStateService(session)
        self.bootstrap = AppBootstrapService(session)
        self._adapter = get_domain_registry().adapter(session, PERSONAL_CONTEXT)

    # ----- moment mapping ------------------------------------------------- #
    def _map_moment(self, moment: MomentModel) -> s.PersonalMomentResponse:
        code = normalize_moment_type_code(moment.moment_type or "")
        is_active = moment.status in _ACTIVE_STATUSES
        return s.PersonalMomentResponse(
            moment_id=str(moment.id),
            moment_type_id=moment_type_id(code),
            moment_type_code=code or None,
            moment_name=moment.title or moment_type_name(code) or "Untitled",
            moment_description=moment.description,
            status=moment.status,
            current_runtime_state=moment.setup_state,
            activated_at=moment.updated_at.isoformat() if is_active and moment.updated_at else None,
        )

    async def _load_moment_inventories(
        self, user_id: UUID
    ) -> tuple[list[MomentModel], list[MomentModel], list[MomentModel], dict[str, MomentModel]]:
        return await load_moment_inventories(self.session, user_id)

    async def _visible_moments(self, user_id: UUID) -> list[MomentModel]:
        _, visible, _, _ = await self._load_moment_inventories(user_id)
        return visible

    def _latest_by_code(self, moments: list[MomentModel]) -> dict[str, MomentModel]:
        return _shared_latest_by_code(moments)

    async def _require_moment(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        moment = await self.moments.get_by_user_and_id(user_id, moment_id)
        if moment is None:
            raise NotFoundError("Moment not found")
        return moment

    async def _sync_module_states(
        self,
        user_id: UUID,
        *,
        visible_moments: list[MomentModel] | None = None,
    ) -> str:
        return await sync_module_states(
            self.session,
            user_id,
            visible_moments=visible_moments,
        )

    async def _run_lifecycle(
        self,
        user_id: UUID,
        moment: MomentModel,
        *,
        previous_status: str,
        action: str,
    ) -> dict:
        """Post-mutation: one inventory read for module sync + mapped response."""
        del previous_status, action
        _, visible, _, _ = await self._load_moment_inventories(user_id)
        await self._sync_module_states(user_id, visible_moments=visible)
        if await try_ensure_personal_moment(self.session, moment):
            await self.session.commit()
        return self._map_moment(moment).model_dump(mode="json")

    # ----- moments -------------------------------------------------------- #
    async def list_moments(
        self, user_id: UUID, status_filter: str | None = None
    ) -> list[dict]:
        moments = await self.moments.list_by_context(
            user_id, PERSONAL_CONTEXT, status=status_filter
        )
        return [self._map_moment(m).model_dump(mode="json") for m in moments]

    async def create_moment(
        self, user_id: UUID, moment_type_code: str, moment_name: str | None
    ) -> dict:
        ref = await self.engine.create(
            self._adapter,
            user_id,
            moment_type=moment_type_code,
            title=moment_name,
        )
        moment = await self._adapter.get_model(user_id, ref.moment_id)
        if await try_ensure_personal_moment(self.session, moment):
            await self.session.commit()
        return self._map_moment(moment).model_dump(mode="json")

    async def get_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        return self._map_moment(moment).model_dump(mode="json")

    async def patch_moment(
        self, user_id: UUID, moment_id: UUID, body: s.PersonalMomentUpdateRequest
    ) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        previous = moment.status
        if body.status is not None:
            await self.engine.transition_status(
                self._adapter,
                user_id,
                moment_id,
                body.status,
                setup_state="ACTIVE" if body.status == "ACTIVE" else None,
            )
            moment = await self._adapter.get_model(user_id, moment_id)
            return await self._run_lifecycle(
                user_id,
                moment,
                previous_status=previous,
                action=body.status.lower(),
            )
        fields: dict[str, str | None] = {}
        if body.moment_name is not None:
            fields["title"] = body.moment_name
        if body.moment_description is not None:
            fields["description"] = body.moment_description
        if fields:
            await self.engine.update(self._adapter, user_id, moment_id, **fields)
        else:
            await self._adapter.get_owned(user_id, moment_id)
        moment = await self._adapter.get_model(user_id, moment_id)
        if await try_ensure_personal_moment(self.session, moment):
            await self.session.commit()
        return self._map_moment(moment).model_dump(mode="json")

    async def list_moment_types(self) -> list[dict]:
        return [
            s.PersonalMomentTypeResponse(
                moment_type_id=mt.type_id,
                moment_type_code=mt.code,
                moment_type_name=mt.name,
                description=mt.tagline,
                theme_color=mt.theme_color,
                icon_name=mt.icon_name,
                display_order=mt.display_order,
            ).model_dump(mode="json")
            for mt in MOMENT_TYPES
        ]

    # ----- create options ------------------------------------------------- #
    async def create_options(self, user_id: UUID) -> dict:
        _, moments, _, latest = await self._load_moment_inventories(user_id)
        cards: list[s.PersonalCreateOptionCard] = []
        for mt in MOMENT_TYPES:
            linked = latest.get(mt.code)
            cards.append(
                s.PersonalCreateOptionCard(
                    moment_type_id=mt.type_id,
                    moment_type_code=mt.code,
                    moment_type_name=mt.name,
                    create_tagline=mt.tagline,
                    is_create_featured=(mt.display_order == 1),
                    theme_color=mt.theme_color,
                    icon_name=mt.icon_name,
                    display_order=mt.display_order,
                    linked_moment_id=str(linked.id) if linked else None,
                    linked_moment_status=linked.status if linked else None,
                    has_draft=bool(linked and linked.status != "ACTIVE"),
                    action_label="Continue Setup" if linked else "Begin Journey",
                )
            )
        return s.PersonalCreateOptionsResponse(cards=cards).model_dump(mode="json")

    # ----- pulse / home / bootstrap -------------------------------------- #
    async def _maybe_refresh_orchestration(
        self, moment_id: UUID, *, force_refresh: bool
    ) -> None:
        """No-op on GET paths.

        Mutations mark projections stale and Celery refreshes orchestration.
        Pull-to-refresh may still purge Redis and sync-rebuild slices via
        ProjectionReadService; it must not await sp_refresh_personal_orchestration.
        """
        del moment_id, force_refresh
        return

    def _session_fields_from_moments(
        self,
        visible: list[MomentModel],
        active: list[MomentModel],
        latest: dict[str, MomentModel],
    ) -> dict:
        drafts = [m for m in visible if m.status == "DRAFT"]
        type_hints: list[dict] = []
        for mt in MOMENT_TYPES:
            linked = latest.get(mt.code)
            type_hints.append(
                {
                    "moment_type_code": mt.code,
                    "linked_moment_id": str(linked.id) if linked else None,
                    "linked_moment_status": linked.status if linked else None,
                    "has_draft": bool(linked and linked.status == "DRAFT"),
                    "is_active": bool(linked and linked.status in _ACTIVE_STATUSES),
                }
            )
        return {
            "is_empty": len(active) == 0 and len(drafts) == 0,
            "active_moment_count": len(active),
            "has_draft": len(drafts) > 0,
            "type_hints": type_hints,
        }

    async def _pulse_payload_from_moments(
        self,
        user_id: UUID,
        active: list[MomentModel],
        *,
        force_refresh: bool = False,
        latest_active: dict[str, MomentModel] | None = None,
        moment_type_code: str | None = None,
    ) -> s.PersonalPulseResponse:
        from app.domains.projections.projection_service import ProjectionReadService

        count = len(active)
        latest = latest_active if latest_active is not None else self._latest_by_code(active)

        selected = normalize_moment_type_code(moment_type_code or "") or None

        if force_refresh:
            refresh_codes = (
                (selected,)
                if selected
                else ("LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS")
            )
            for code in refresh_codes:
                m = latest.get(code)
                if m is not None and (code == "LIFE_OPERATIONS" or m.status in _ACTIVE_STATUSES):
                    await self._maybe_refresh_orchestration(m.id, force_refresh=True)

        if selected:
            active_templates = [selected] if any(
                normalize_moment_type_code(m.moment_type or "") == selected for m in active
            ) else []
        else:
            active_templates = sorted(
                {
                    normalize_moment_type_code(m.moment_type or "")
                    for m in active
                    if m.moment_type
                }
            )
        read = ProjectionReadService(self.session)
        composed = await read.get_aggregate_pulse(
            user_id,
            active_templates,
            active_count=count,
            force_refresh=force_refresh,
        )
        life_ops_block = composed.get("life_operations")
        if force_refresh and life_ops_block is None and latest.get("LIFE_OPERATIONS"):
            raise SnapshotRebuildingError(
                "Personal snapshot is rebuilding; retry shortly"
            )
        return s.PersonalPulseResponse(
            overall_rhythm_state=composed.get("overall_rhythm_state", "EMPTY"),
            active_moment_count=count,
            is_empty=count == 0,
            life_operations=life_ops_block,
            future_building=composed.get("future_building"),
            lifestyle=composed.get("lifestyle"),
            emotional_security=composed.get("emotional_security"),
        )

    async def _slice_payload(
        self,
        user_id: UUID,
        template: str,
        slice_type: str,
        *,
        force_refresh: bool = False,
    ) -> dict | None:
        from app.domains.projections.projection_service import ProjectionReadService

        try:
            return await ProjectionReadService(self.session).get_slice(
                user_id, template, slice_type, force_refresh=force_refresh
            )
        except Exception:
            logger.exception(
                "Failed to read %s slice for template=%s", slice_type, template
            )
            return None

    async def _moments_home_payload_from_moments(
        self,
        user_id: UUID,
        visible: list[MomentModel],
        active: list[MomentModel],
        latest: dict[str, MomentModel],
        *,
        include_details: bool = True,
        force_refresh: bool = False,
    ) -> s.PersonalMomentsHomeResponse:
        del visible
        cards: list[s.PersonalMomentHomeCard] = []
        for mt in MOMENT_TYPES:
            linked = latest.get(mt.code)
            cards.append(
                s.PersonalMomentHomeCard(
                    moment_type_id=mt.type_id,
                    moment_type_code=mt.code,
                    moment_type_name=mt.name,
                    description=mt.tagline,
                    theme_color=mt.theme_color,
                    icon_name=mt.icon_name,
                    display_order=mt.display_order,
                    linked_moment_id=str(linked.id) if linked else None,
                    linked_moment_status=linked.status if linked else None,
                    moment_name=linked.title if linked and linked.title else None,
                    current_runtime_state=linked.setup_state if linked else None,
                    is_active=bool(linked and linked.status in _SWITCHER_ACTIVE_STATUSES),
                    action_label="Open" if linked else "Create",
                )
            )

        fb_detail = ls_detail = rs_detail = None
        if include_details:
            for code in _DETAIL_TEMPLATES:
                moment = latest.get(code)
                if not moment or moment.status not in _ACTIVE_STATUSES:
                    continue
                payload = await self._slice_payload(
                    user_id, code, "moments", force_refresh=force_refresh
                )
                detail = _moments_detail_from_slice(payload)
                if code == "FUTURE_BUILDING":
                    fb_detail = detail
                elif code == "LIFESTYLE":
                    ls_detail = detail
                elif code == "RELATIONSHIPS":
                    rs_detail = detail

        return s.PersonalMomentsHomeResponse(
            active_moment_count=len(active),
            is_empty=len(active) == 0,
            cards=cards,
            future_building_detail=fb_detail,
            lifestyle_detail=ls_detail,
            emotional_security_detail=rs_detail,
        )

    async def pulse(
        self,
        user_id: UUID,
        *,
        force_refresh: bool = False,
        moment_type_code: str | None = None,
    ) -> s.PersonalPulseResponse:
        _, _, active, _ = await self._load_moment_inventories(user_id)
        latest_active = self._latest_by_code(active)
        return await self._pulse_payload_from_moments(
            user_id,
            active,
            force_refresh=force_refresh,
            latest_active=latest_active,
            moment_type_code=moment_type_code,
        )

    async def moments_home(
        self,
        user_id: UUID,
        *,
        force_refresh: bool = False,
        moment_type_code: str | None = None,
    ) -> s.PersonalMomentsHomeResponse:
        del moment_type_code
        _, visible, active, latest = await self._load_moment_inventories(user_id)
        if force_refresh:
            for m in active:
                await self._maybe_refresh_orchestration(m.id, force_refresh=True)
        return await self._moments_home_payload_from_moments(
            user_id,
            visible,
            active,
            latest,
            include_details=True,
            force_refresh=force_refresh,
        )

    async def get_session(self, user_id: UUID) -> dict:
        _, visible, active, latest = await self._load_moment_inventories(user_id)
        fields = self._session_fields_from_moments(visible, active, latest)
        return s.PersonalSessionResponse(**fields).model_dump(mode="json")

    async def get_inventory(
        self,
        user_id: UUID,
        *,
        moment_type_code: str | None = None,
    ) -> dict:
        """Lightweight inventory — cards + selected-type pulse without heavy moments detail."""
        _, visible, active, latest = await self._load_moment_inventories(user_id)
        pulse = await self._pulse_payload_from_moments(
            user_id,
            active,
            force_refresh=False,
            latest_active=self._latest_by_code(active),
            moment_type_code=moment_type_code,
        )
        home = await self._moments_home_payload_from_moments(
            user_id, visible, active, latest, include_details=False
        )
        return s.PersonalInventoryResponse(pulse=pulse, moments_home=home).model_dump(
            mode="json"
        )

    async def session_bootstrap(
        self,
        user_id: UUID,
        *,
        force_refresh: bool = False,
        moment_type_code: str | None = None,
    ) -> dict:
        """Thin composer — one inventory pass, derive selected-type pulse + moments_home."""
        _, visible, active, latest = await self._load_moment_inventories(user_id)
        # Heal MY_MONEY/PULSE if ACTIVE inventory exists but module flags lagged at SETUP.
        await self._sync_module_states(user_id, visible_moments=visible)
        pulse = await self._pulse_payload_from_moments(
            user_id,
            active,
            force_refresh=force_refresh,
            latest_active=self._latest_by_code(active),
            moment_type_code=moment_type_code,
        )
        home = await self._moments_home_payload_from_moments(
            user_id, visible, active, latest, include_details=False
        )
        return s.PersonalSessionBootstrapResponse(
            pulse=pulse, moments_home=home
        ).model_dump(mode="json")

    # ----- memory / life / live ------------------------------------------ #
    async def memory(
        self,
        user_id: UUID,
        *,
        force_refresh: bool = False,
        moment_type_code: str | None = None,
    ) -> dict:
        # Compose from Redis template memory slices (same path as /templates/.../memory).
        del moment_type_code
        moments = await self._visible_moments(user_id)
        active = [m for m in moments if m.status in _ACTIVE_STATUSES]
        if force_refresh:
            for m in active:
                await self._maybe_refresh_orchestration(m.id, force_refresh=True)
        latest = self._latest_by_code(active)
        blocks: dict[str, dict | None] = {
            "FUTURE_BUILDING": None,
            "LIFESTYLE": None,
            "RELATIONSHIPS": None,
        }
        for code in _DETAIL_TEMPLATES:
            moment = latest.get(code)
            if not moment or moment.status not in _ACTIVE_STATUSES:
                continue
            payload = await self._slice_payload(
                user_id, code, "memory", force_refresh=force_refresh
            )
            blocks[code] = _memory_block_from_slice(
                payload, section_label=_MEMORY_SECTION_LABELS[code]
            )
        return s.PersonalMemoryResponse(
            is_empty=len(active) == 0,
            future_building=blocks["FUTURE_BUILDING"],
            lifestyle=blocks["LIFESTYLE"],
            emotional_security=blocks["RELATIONSHIPS"],
        ).model_dump(mode="json")

    async def memory_summary(self, user_id: UUID) -> dict:
        return s.PersonalMemorySummaryResponse().model_dump(mode="json")

    async def life(self, user_id: UUID, *, force_refresh: bool = False) -> dict:
        from app.domains.projections.projection_service import ProjectionReadService

        return await ProjectionReadService(self.session).get_personal_life(
            user_id, force_refresh=force_refresh
        )

    async def live(self, user_id: UUID) -> dict:
        moments = await self._visible_moments(user_id)
        active = [m for m in moments if m.status in _ACTIVE_STATUSES]
        return s.PersonalLiveResponse(
            active_moment_count=len(active), is_empty=len(active) == 0
        ).model_dump(mode="json")

    async def life_activity(self, user_id: UUID, moment_id: str | None) -> dict:
        from sqlalchemy import func, select

        from app.domains.personal.life_operations.activity_mapper import (
            map_timeline_to_recent_item,
            money_events_by_quick_add,
        )
        from app.domains.personal.models import (
            PersonalActivityTimeline,
            PersonalMoneyEvents,
        )
        from app.domains.reference_data.catalog import get_reference_catalog

        if not moment_id:
            return s.PersonalLifeOpsActivityResponse(moment_id="").model_dump(mode="json")
        try:
            mid = UUID(str(moment_id))
        except ValueError as exc:
            raise ValidationError("Invalid moment_id") from exc
        await self._require_moment(user_id, mid)

        timeline_result = await self.session.execute(
            select(PersonalActivityTimeline)
            .where(
                PersonalActivityTimeline.moment_id == mid,
                PersonalActivityTimeline.is_voided.is_(False),
            )
            .order_by(PersonalActivityTimeline.event_occurred_at.desc())
            .limit(50)
        )
        timeline = list(timeline_result.scalars().all())

        money_result = await self.session.execute(
            select(PersonalMoneyEvents).where(
                PersonalMoneyEvents.moment_id == mid,
                PersonalMoneyEvents.is_voided.is_(False),
            )
        )
        money_by_qa = money_events_by_quick_add(list(money_result.scalars().all()))
        catalog = get_reference_catalog()

        items = [
            map_timeline_to_recent_item(
                row, money=money_by_qa.get(row.quick_add_event_id), catalog=catalog
            )
            for row in timeline
        ]

        month_start = datetime.now(timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        ).replace(tzinfo=None)
        this_month = sum(
            1 for row in timeline if row.event_occurred_at >= month_start
        )
        total_minor = sum(
            int(m.amount_minor or 0)
            for m in money_by_qa.values()
            if m.direction == "DEBIT"
        )

        return s.PersonalLifeOpsActivityResponse(
            moment_id=str(mid),
            summary=s.PersonalLifeOpsActivitySummary(
                total_logs=len(timeline),
                this_month=this_month,
                total_amount_minor=total_minor,
            ),
            items=items,
        ).model_dump(mode="json")

    # ----- quick add ------------------------------------------------------ #
    async def quick_add_options(
        self, user_id: UUID, *, moment_id: str | None = None
    ) -> dict:
        moments = await self._visible_moments(user_id)
        parsed_moment_id: UUID | None = None
        if moment_id:
            try:
                parsed_moment_id = UUID(str(moment_id))
            except ValueError as exc:
                raise ValidationError("Invalid moment_id") from exc
        return await PersonalQuickAddRouter(self.session).options(
            user_id, moments, moment_id=parsed_moment_id
        )

    async def quick_add_submit(self, user_id: UUID, body: dict) -> dict:
        raw_moment_id = body.get("moment_id")
        if not raw_moment_id:
            raise ValidationError("moment_id is required")
        try:
            moment_id = UUID(str(raw_moment_id))
        except ValueError as exc:
            raise ValidationError("Invalid moment_id") from exc
        moment = await self._require_moment(user_id, moment_id)
        return await PersonalQuickAddRouter(self.session).submit(user_id, moment, body)

    async def quick_add_detail(self, user_id: UUID, event_id: str) -> dict:
        return await PersonalQuickAddRouter(self.session).detail(user_id, event_id)

    async def quick_add_patch(self, user_id: UUID, event_id: str, body: dict) -> dict:
        return await PersonalQuickAddRouter(self.session).patch(
            user_id, event_id, body
        )

    async def quick_add_delete(self, user_id: UUID, event_id: str) -> None:
        from app.domains.personal.quick_add.edit_service import (
            PersonalQuickAddEditService,
        )

        await PersonalQuickAddEditService(self.session).delete(user_id, event_id)

    async def template_activity_list(
        self,
        user_id: UUID,
        moment_type: str,
        *,
        moment_id: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict:
        from app.domains.personal.templates.activity.service import (
            TemplateActivityService,
        )

        return await TemplateActivityService(self.session).list_activity(
            user_id,
            moment_type,
            moment_id=moment_id,
            cursor=cursor,
            limit=limit,
        )

    async def unified_activity(
        self,
        user_id: UUID,
        *,
        range: str = "all",
        domain: str = "all",
        kind: str = "all",
        q: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict:
        from app.domains.personal.activity.unified_service import (
            UnifiedPersonalActivityService,
        )

        return await UnifiedPersonalActivityService(self.session).list_activity(
            user_id,
            range=range,
            domain=domain,
            kind=kind,
            q=q,
            cursor=cursor,
            limit=limit,
        )

    async def template_activity_get(
        self, user_id: UUID, moment_type: str, event_id: str
    ) -> dict:
        from app.domains.personal.templates.activity.service import (
            TemplateActivityService,
        )

        return await TemplateActivityService(self.session).get_activity(
            user_id, moment_type, event_id
        )

    async def template_activity_patch(
        self,
        user_id: UUID,
        moment_type: str,
        event_id: str,
        body: dict,
    ) -> dict:
        from app.domains.personal.templates.activity.service import (
            TemplateActivityService,
        )

        return await TemplateActivityService(self.session).patch_activity(
            user_id, moment_type, event_id, body
        )

    async def template_activity_delete(
        self, user_id: UUID, moment_type: str, event_id: str
    ) -> None:
        from app.domains.personal.templates.activity.service import (
            TemplateActivityService,
        )

        result = await TemplateActivityService(self.session).delete_activity(
            user_id, moment_type, event_id
        )
        if not result.get("deleted") and not result.get("already_deleted"):
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )

    async def list_accounts(
        self, user_id: UUID, *, include_archived: bool = False
    ) -> list[dict]:
        return await PersonalAccountsService(self.session).list_accounts(
            user_id, include_archived=include_archived
        )

    async def get_account(self, user_id: UUID, account_id: UUID) -> dict:
        return await PersonalAccountsService(self.session).get_account(
            user_id, account_id
        )

    async def create_account(
        self, user_id: UUID, body: s.PersonalAccountCreateRequest
    ) -> dict:
        return await PersonalAccountsService(self.session).create_account(
            user_id,
            account_name=body.account_name,
            account_type=body.account_type,
            currency_code=body.currency_code,
            opening_balance=body.opening_balance,
            opening_balance_minor=body.opening_balance_minor,
            is_primary=body.is_primary,
        )

    async def patch_account(
        self, user_id: UUID, account_id: UUID, body: s.PersonalAccountPatchRequest
    ) -> dict:
        return await PersonalAccountsService(self.session).patch_account(
            user_id,
            account_id,
            account_name=body.account_name,
            account_type=body.account_type,
            currency_code=body.currency_code,
            current_balance_minor=body.current_balance_minor,
            is_default=body.is_default,
        )

    async def archive_account(self, user_id: UUID, account_id: UUID) -> dict:
        return await PersonalAccountsService(self.session).archive_account(
            user_id, account_id
        )

    async def delete_account(self, user_id: UUID, account_id: UUID) -> None:
        await PersonalAccountsService(self.session).delete_account(user_id, account_id)

    # ----- master expense ------------------------------------------------- #
    async def master_expense_options(self, user_id: UUID) -> dict:
        from app.domains.personal.master_expense.service import MasterExpenseService

        moments = await self._visible_moments(user_id)
        return await MasterExpenseService(self.session).options(user_id, moments)

    async def master_expense_submit(self, user_id: UUID, body: dict) -> dict:
        from app.domains.personal.master_expense.service import MasterExpenseService

        return await MasterExpenseService(self.session).create(user_id, body)

    # ----- setup ---------------------------------------------------------- #
    def _setup_response(
        self, moment: MomentModel, answers: dict | None = None
    ) -> s.PersonalSetupResponse:
        from app.domains.personal.templates.future_building.setup_schema import (
            to_setup_fields as fb_setup_fields,
        )
        from app.domains.personal.templates.life_operations.setup_schema import (
            to_setup_fields as lo_setup_fields,
        )
        from app.domains.personal.templates.lifestyle.setup_schema import (
            to_setup_fields as ls_setup_fields,
        )

        code = normalize_moment_type_code(moment.moment_type or "")
        if code == "LIFE_OPERATIONS":
            fields = [
                s.PersonalSetupField(**field) for field in lo_setup_fields()
            ]
            return s.PersonalSetupResponse(
                moment_id=str(moment.id),
                moment_type_code=code,
                moment_name=moment.title or moment_type_name(code),
                status=moment.status,
                title="Life Operations Setup",
                subtitle="Align your rhythm and what restores you.",
                fields=fields,
                mission=s.PersonalSetupMission(
                    badge_label="Your Mission",
                    title="Build an operating rhythm that works with you",
                    body=(
                        "Momentra uses your patterns to shape a personal system "
                        "for steadier energy, clearer priorities and meaningful recovery."
                    ),
                ),
                saved_answers=answers,
                cta_label="Begin My New Rhythm",
                footer_note="Your rhythm adapts as you live",
            )
        if code == "FUTURE_BUILDING":
            fields = [
                s.PersonalSetupField(**field) for field in fb_setup_fields()
            ]
            return s.PersonalSetupResponse(
                moment_id=str(moment.id),
                moment_type_code=code,
                moment_name=moment.title or moment_type_name(code),
                status=moment.status,
                title="Set up Future Building",
                subtitle="Define the future you are building toward.",
                fields=fields,
                mission=s.PersonalSetupMission(
                    badge_label="Your Mission",
                    title="Build a future that compounds",
                    body="Momentra will learn from every investment, milestone, and lesson.",
                ),
                saved_answers=answers,
                cta_label="Begin Building My Future",
            )
        if code == "LIFESTYLE":
            fields = [
                s.PersonalSetupField(**field) for field in ls_setup_fields()
            ]
            return s.PersonalSetupResponse(
                moment_id=str(moment.id),
                moment_type_code=code,
                moment_name=moment.title or moment_type_name(code),
                status=moment.status,
                title="Set up Lifestyle",
                subtitle="Design the life you want to live day to day.",
                fields=fields,
                mission=s.PersonalSetupMission(
                    badge_label="Your Mission",
                    title="Curate a life that feels alive",
                    body="Momentra will learn from experiences, wellbeing, and creative expression.",
                ),
                saved_answers=answers,
                cta_label="Activate Lifestyle",
            )
        return s.PersonalSetupResponse(
            moment_id=str(moment.id),
            moment_type_code=code,
            moment_name=moment.title or moment_type_name(code),
            status=moment.status,
            title=f"Set up {moment_type_name(code)}",
            subtitle="Answer a few questions to calibrate your system.",
            fields=[
                s.PersonalSetupField(
                    field_key="moment_name",
                    label="Name this moment",
                    helper_text="Give this part of your life a name.",
                    field_type="TEXT",
                    required=True,
                ),
                s.PersonalSetupField(
                    field_key="focus",
                    label="Primary focus",
                    field_type="SINGLE_SELECT",
                    required=True,
                    options=[
                        s.PersonalSetupOption(value="STABILITY", label="Stability"),
                        s.PersonalSetupOption(value="GROWTH", label="Growth"),
                        s.PersonalSetupOption(value="BALANCE", label="Balance"),
                    ],
                ),
            ],
            mission=s.PersonalSetupMission(
                badge_label="Your Mission",
                title="Build a system that works with you",
                body="Momentra will learn from what you capture and adapt.",
            ),
            saved_answers=answers,
        )

    async def setup_get(self, user_id: UUID, moment_id: UUID) -> dict:
        from app.domains.personal.models import (
            PersonalFutureBuildingProfile,
            PersonalLifeOperationsProfile,
            PersonalLifestyleProfile,
            PersonalRelationshipsProfile,
        )
        from app.domains.personal.templates.future_building.setup_draft import (
            load_setup_draft as load_fb_draft,
        )
        from app.domains.personal.templates.future_building.setup_schema import (
            merge_saved_answers as merge_fb_answers,
        )
        from app.domains.personal.templates.life_operations.setup_draft import (
            load_setup_draft as load_lo_draft,
        )
        from app.domains.personal.templates.life_operations.setup_schema import (
            merge_saved_answers as merge_lo_answers,
        )
        from app.domains.personal.templates.lifestyle.setup_draft import (
            load_setup_draft as load_ls_draft,
        )
        from app.domains.personal.templates.lifestyle.setup_schema import (
            merge_saved_answers as merge_ls_answers,
        )
        from app.domains.personal.templates.relationships.setup_draft import (
            load_setup_draft as load_rs_draft,
        )
        from app.domains.personal.templates.relationships.setup_schema import (
            merge_saved_answers as merge_rs_answers,
        )

        moment = await self._require_moment(user_id, moment_id)
        code = normalize_moment_type_code(moment.moment_type or "")
        log_setup_step(
            user_id=user_id,
            moment_id=moment_id,
            moment_type_code=code,
            step="get",
        )
        answers: dict | None = None
        if code == "LIFE_OPERATIONS":
            from sqlalchemy import select

            draft = await load_lo_draft(self.session, moment_id)
            result = await self.session.execute(
                select(PersonalLifeOperationsProfile).where(
                    PersonalLifeOperationsProfile.moment_id == moment_id
                )
            )
            profile = result.scalar_one_or_none()
            merged = merge_lo_answers(draft, profile)
            if merged:
                answers = merged
        elif code == "FUTURE_BUILDING":
            from sqlalchemy import select

            draft = await load_fb_draft(self.session, moment_id)
            result = await self.session.execute(
                select(PersonalFutureBuildingProfile).where(
                    PersonalFutureBuildingProfile.moment_id == moment_id
                )
            )
            profile = result.scalar_one_or_none()
            merged = merge_fb_answers(draft, profile)
            if merged:
                answers = merged
        elif code == "LIFESTYLE":
            from sqlalchemy import select

            draft = await load_ls_draft(self.session, moment_id)
            result = await self.session.execute(
                select(PersonalLifestyleProfile).where(
                    PersonalLifestyleProfile.moment_id == moment_id
                )
            )
            profile = result.scalar_one_or_none()
            merged = merge_ls_answers(draft, profile)
            if merged:
                answers = merged
        elif code == "RELATIONSHIPS":
            from sqlalchemy import select

            draft = await load_rs_draft(self.session, moment_id)
            result = await self.session.execute(
                select(PersonalRelationshipsProfile).where(
                    PersonalRelationshipsProfile.moment_id == moment_id
                )
            )
            profile = result.scalar_one_or_none()
            merged = merge_rs_answers(draft, profile)
            if merged:
                answers = merged
        return self._setup_response(moment, answers=answers).model_dump(mode="json")

    async def setup_draft(self, user_id: UUID, moment_id: UUID, answers: dict) -> dict:
        from app.domains.personal.templates.future_building.setup_draft import (
            save_setup_draft as save_fb_draft,
        )
        from app.domains.personal.templates.life_operations.setup_draft import (
            save_setup_draft as save_lo_draft,
        )
        from app.domains.personal.templates.lifestyle.setup_draft import (
            save_setup_draft as save_ls_draft,
        )
        from app.domains.personal.templates.relationships.setup_draft import (
            save_setup_draft as save_rs_draft,
        )

        moment = await self._require_moment(user_id, moment_id)
        code = normalize_moment_type_code(moment.moment_type or "")
        log_setup_step(
            user_id=user_id,
            moment_id=moment_id,
            moment_type_code=code,
            step="draft",
        )
        normalized = dict(answers)
        if code == "LIFE_OPERATIONS":
            normalized = LIFE_OPERATIONS_TEMPLATE_CONTRACT.normalize_answers(answers)
            await save_lo_draft(self.session, user_id, moment_id, normalized)
        elif code == "FUTURE_BUILDING":
            normalized = FUTURE_BUILDING_TEMPLATE_CONTRACT.normalize_answers(answers)
            await save_fb_draft(self.session, user_id, moment_id, normalized)
        elif code == "LIFESTYLE":
            normalized = LIFESTYLE_TEMPLATE_CONTRACT.normalize_answers(answers)
            await save_ls_draft(self.session, user_id, moment_id, normalized)
        elif code == "RELATIONSHIPS":
            normalized = RELATIONSHIPS_TEMPLATE_CONTRACT.normalize_answers(answers)
            await save_rs_draft(self.session, user_id, moment_id, normalized)
        name = normalized.get("moment_name")
        if isinstance(name, str) and name.strip():
            moment.title = name.strip()
        moment.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return self._setup_response(moment, answers=normalized).model_dump(mode="json")

    async def setup_preview(self, user_id: UUID, moment_id: UUID, answers: dict) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        code = normalize_moment_type_code(moment.moment_type or "")
        log_setup_step(
            user_id=user_id,
            moment_id=moment_id,
            moment_type_code=code,
            step="preview",
        )
        preview_kwargs: dict = {
            "runtime_priorities": ["Consistency", "Recovery", "Focus"],
            "identity_chips": ["Builder", "Balanced"],
        }
        if code == "LIFE_OPERATIONS":
            block = LIFE_OPERATIONS_TEMPLATE_CONTRACT.preview_block(answers)
            preview_kwargs["narrative"] = block["narrative"]
            preview_kwargs["rhythm"] = block["rhythm"]
            preview_kwargs["pressure"] = block["pressure"]
            preview_kwargs["recovery"] = block["recovery"]
            preview_kwargs["runtime_priorities"] = block["runtime_priorities"]
            preview_kwargs["identity_chips"] = block["identity_chips"]
        elif code == "FUTURE_BUILDING":
            preview_kwargs["future_building"] = FUTURE_BUILDING_TEMPLATE_CONTRACT.preview_block(
                answers
            )
            fields = FUTURE_BUILDING_TEMPLATE_CONTRACT.to_profile_fields(answers)
            preview_kwargs["identity_chips"] = [fields["future_identity"]]
            preview_kwargs["runtime_priorities"] = list(fields["future_values"][:3])
        elif code == "LIFESTYLE":
            preview_kwargs["lifestyle"] = LIFESTYLE_TEMPLATE_CONTRACT.preview_block(answers)
            fields = LIFESTYLE_TEMPLATE_CONTRACT.to_profile_fields(answers)
            preview_kwargs["identity_chips"] = [fields["lifestyle_identity"]]
            preview_kwargs["runtime_priorities"] = list(fields["desired_lifestyle_vectors"][:3])
        elif code == "RELATIONSHIPS":
            preview_kwargs["emotional_security"] = RELATIONSHIPS_TEMPLATE_CONTRACT.preview_block(
                answers
            )
            fields = RELATIONSHIPS_TEMPLATE_CONTRACT.to_profile_fields(answers)
            preview_kwargs["identity_chips"] = [fields["relationship_identity"]]
            preview_kwargs["runtime_priorities"] = list(fields["desired_connection_types"][:3])
        return s.PersonalSetupPreviewResponse(**preview_kwargs).model_dump(mode="json")

    async def setup_commit(self, user_id: UUID, moment_id: UUID, answers: dict) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        code = normalize_moment_type_code(moment.moment_type or "")
        log_setup_step(
            user_id=user_id,
            moment_id=moment_id,
            moment_type_code=code,
            step="commit",
        )
        name = answers.get("moment_name")
        if isinstance(name, str) and name.strip():
            await self.engine.update(
                self._adapter,
                user_id,
                moment_id,
                title=name.strip(),
            )
            moment = await self._adapter.get_model(user_id, moment_id)
        if code == "LIFE_OPERATIONS":
            await ensure_personal_moment(self.session, moment)
            await upsert_life_operations_profile(
                self.session, user_id, moment_id, answers
            )
        elif code == "FUTURE_BUILDING":
            await ensure_personal_moment(self.session, moment)
            await upsert_future_building_profile(
                self.session, user_id, moment_id, answers
            )
        elif code == "LIFESTYLE":
            await ensure_personal_moment(self.session, moment)
            await upsert_lifestyle_profile(self.session, user_id, moment_id, answers)
        elif code == "RELATIONSHIPS":
            await ensure_personal_moment(self.session, moment)
            await upsert_relationships_profile(self.session, user_id, moment_id, answers)
        if moment.status != "ACTIVE":
            await self.engine.activate(
                self._adapter,
                user_id,
                moment_id,
                setup_state="ACTIVE",
            )
        _, visible, _, _ = await self._load_moment_inventories(user_id)
        await self._sync_module_states(user_id, visible_moments=visible)
        if code in ("LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS"):
            from app.workers import procedures as procs

            await procs.try_refresh_personal_orchestration(self.session, moment_id)
        moment = await self._adapter.get_model(user_id, moment_id)
        await try_ensure_personal_moment(self.session, moment)
        from app.domains.personal.projection.cache import invalidate_projection_cache
        from app.domains.projections.handlers import SETUP_COMPLETED
        from app.shared.events.base import DomainEvent
        from app.shared.events.publisher import get_event_publisher

        invalidate_projection_cache(user_id)
        await get_event_publisher().publish(
            DomainEvent(
                name=SETUP_COMPLETED,
                user_id=user_id,
                moment_id=moment_id,
                context="MY_MONEY",
                moment_type=code,
                payload={"moment_type_code": code},
            )
        )
        payload = self._map_moment(moment).model_dump(mode="json")
        payload["projection_status"] = "REFRESHING"
        return payload

    # ----- cover upload --------------------------------------------------- #
    async def cover_upload_url(
        self, user_id: UUID, moment_id: UUID, content_type: str
    ) -> dict:
        from fastapi import HTTPException, status

        from app.core.storage import build_storage_path, build_upload_url

        moment = await self._require_moment(user_id, moment_id)
        storage_path = build_storage_path(
            f"personal/covers/{moment.id}", content_type
        )
        try:
            upload_url = build_upload_url(storage_path)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
            ) from exc
        return s.PersonalImageUploadUrlResponse(
            upload_url=upload_url,
            storage_path=storage_path,
            token=None,
        ).model_dump(mode="json")

    async def cover_confirm(
        self, user_id: UUID, moment_id: UUID, storage_path: str
    ) -> dict[str, str]:
        from fastapi import HTTPException, status

        from app.core.storage import assert_storage_path_under, public_url_for

        moment = await self._require_moment(user_id, moment_id)
        try:
            path = assert_storage_path_under(
                storage_path, f"personal/covers/{moment.id}"
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        return {"cover_image_url": public_url_for(path)}
