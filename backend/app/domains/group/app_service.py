"""Contract-first Group service consumed by the mobile clients.

Group moments are persisted in the shared ``moments`` table
(``context_type = "GROUP"``) so create / setup / activate flows are real and
work against the test ``MockSession``. The rich analytical surfaces (pulse /
memory / life / live) return schema-valid empty-state payloads that render on
both apps; wiring them to the ``group_*`` snapshot tables/views is the iterative
data-backing step.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, PermissionDeniedError, StateTransitionError
from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.group import app_schemas as s
from app.domains.group.catalog import (
    GROUP_CONTEXT,
    GROUP_MOMENT_TYPES,
    group_default_name,
    group_profiles_for,
    group_type_name,
)
from app.domains.group.shared_experience_service import SharedExperienceService
from app.domains.group.shared_living_service import SharedLivingService
from app.domains.group.shared_purchase_service import SharedPurchaseService
from app.domains.group.templates.shared_living.handler import SharedLivingTemplateHandler
from app.domains.group.templates.shared_purchase.handler import SharedPurchaseTemplateHandler
from app.domains.group.group_life_command_mapper import build_group_life_command_center
from app.domains.group.templates.shared_experience.active_mapper import (
    map_active_life,
    map_active_memory,
    map_active_moments,
    map_active_pulse,
)
from app.domains.group.templates.shared_experience.projection_builder import SharedExperienceProjectionBuilder
from app.domains.group.access import require_group_moment_access
from app.domains.group.domain_row import ensure_group_moments_row
from app.domains.group.templates.shared_experience.quick_add import build_trip_quick_add_categories
from app.domains.module_states.service import ModuleStateService
from app.domains.moment_engine.engine import MomentEngine
from app.domains.moment_engine.lifecycle_contract import (
    build_lifecycle_response,
    deny_access,
    log_lifecycle_transition,
    pick_replacement_moment,
)
from app.domains.moment_engine.registry import get_domain_registry
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository

import time
import logging

logger = logging.getLogger(__name__)

_ACTIVE_STATUSES = {"ACTIVE"}
_VISIBLE_STATUSES = {"DRAFT", "SETUP", "ACTIVE", "PAUSED"}

_CATEGORY_BY_CODE = {mt.code: mt.category for mt in GROUP_MOMENT_TYPES}


def _norm_status(value: str | None) -> str:
    return (value or "").strip().upper()


def _moment_is_active(moment: MomentModel) -> bool:
    if _norm_status(moment.status) in _ACTIVE_STATUSES:
        return True
    return _norm_status(moment.setup_state) == "ACTIVE"


def _moment_is_visible(moment: MomentModel) -> bool:
    status = _norm_status(moment.status)
    if status in _VISIBLE_STATUSES:
        return True
    return _moment_is_active(moment)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _why_groups() -> list[s.GroupEmptyStateItem]:
    return [
        s.GroupEmptyStateItem(
            item_code="one_place",
            item_kind="why",
            title="Everything in one place",
            description="Plans, money and updates stop living across five chat threads.",
            icon_name="layers",
            display_order=1,
        ),
        s.GroupEmptyStateItem(
            item_code="fair_money",
            item_kind="why",
            title="Money stays fair",
            description="Shared costs are tracked and split automatically.",
            icon_name="scale",
            display_order=2,
        ),
        s.GroupEmptyStateItem(
            item_code="kept_forever",
            item_kind="why",
            title="Moments kept forever",
            description="Every group moment becomes a memory you can revisit.",
            icon_name="sparkles",
            display_order=3,
        ),
    ]


def _magic_steps() -> list[s.GroupEmptyStateItem]:
    return [
        s.GroupEmptyStateItem(
            item_code="step_create",
            item_kind="step",
            title="Create a moment",
            description="Pick a type and give it a name.",
            icon_name="plus",
            display_order=1,
        ),
        s.GroupEmptyStateItem(
            item_code="step_invite",
            item_kind="step",
            title="Invite your people",
            description="Add the crew and set who does what.",
            icon_name="users",
            display_order=2,
        ),
        s.GroupEmptyStateItem(
            item_code="step_live",
            item_kind="step",
            title="Live it together",
            description="Coordinate, spend and capture as it happens.",
            icon_name="bolt",
            display_order=3,
        ),
    ]


class GroupAppService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.modules = ModuleStateService(session)
        self.bootstrap = AppBootstrapService(session)
        self.engine = MomentEngine()
        self._adapter = get_domain_registry().adapter(session, GROUP_CONTEXT)

    # ----- helpers -------------------------------------------------------- #
    async def _load_moment_inventories(
        self, user_id: UUID
    ) -> tuple[list[MomentModel], list[MomentModel], list[MomentModel], list[MomentModel]]:
        """One inventory pass per request — owned ∪ member-accessible moments.

        Owned moments are sorted ahead of invitee-accessible ones so switchers
        prefer the caller's own ACTIVE moment when both share a type.
        """
        all_moments = await self.moments.list_group_accessible(user_id)

        # Owned first (newest within bucket) so focus_moment_id prefers the caller.
        owned = [m for m in all_moments if m.user_id == user_id]
        invited = [m for m in all_moments if m.user_id != user_id]
        owned.sort(
            key=lambda m: m.created_at or datetime(1970, 1, 1, tzinfo=timezone.utc),
            reverse=True,
        )
        invited.sort(
            key=lambda m: m.created_at or datetime(1970, 1, 1, tzinfo=timezone.utc),
            reverse=True,
        )
        all_moments = owned + invited
        visible = [m for m in all_moments if _moment_is_visible(m)]
        active = [m for m in visible if _moment_is_active(m)]
        replacement = [
            m
            for m in all_moments
            if _norm_status(m.status) not in {"ARCHIVED", "DELETED"}
        ]
        return all_moments, visible, active, replacement

    async def _visible_moments(self, user_id: UUID) -> list[MomentModel]:
        _, visible, _, _ = await self._load_moment_inventories(user_id)
        return visible

    async def _inventory_for_replacement(self, user_id: UUID) -> list[MomentModel]:
        _, _, _, replacement = await self._load_moment_inventories(user_id)
        return replacement

    async def _active_moments(self, user_id: UUID) -> list[MomentModel]:
        _, _, active, _ = await self._load_moment_inventories(user_id)
        return active

    def _pulse_payload_from_moments(
        self, moments: list[MomentModel], active: list[MomentModel]
    ) -> s.GroupPulseResponse:
        latest = self._latest_by_code(moments)
        return s.GroupPulseResponse(
            is_empty=len(active) == 0,
            active_moment_count=len(active),
            type_cards=self._type_cards(latest),
            why_groups=_why_groups(),
            magic_steps=_magic_steps(),
        )

    def _live_overview_from_moments(
        self,
        moments: list[MomentModel],
        active: list[MomentModel],
        *,
        viewer_id: UUID | None = None,
    ) -> s.GroupLiveOverview:
        return s.GroupLiveOverview(
            active_moment_count=len(active),
            total_group_moment_count=len(moments),
            live_cards=[self._map_list_item(m, viewer_id=viewer_id) for m in active],
        )

    def _session_fields_from_moments(
        self,
        moments: list[MomentModel],
        active: list[MomentModel],
        *,
        drafts: list[MomentModel] | None = None,
    ) -> dict:
        draft_list = drafts if drafts is not None else [
            m for m in moments if _norm_status(m.status) == "DRAFT"
        ]
        first_active = active[0] if active else None
        first_draft = draft_list[0] if draft_list else None
        active_moment_id = str(first_active.id) if first_active else None
        return {
            "is_empty": len(active) == 0 and first_draft is None,
            "active_moment_count": len(active),
            "focus_moment_id": active_moment_id,
            "active_moment_id": active_moment_id,
            "moment_type": (
                first_active.moment_type
                if first_active
                else (first_draft.moment_type if first_draft else None)
            ),
            "draft_moment_id": str(first_draft.id) if first_draft else None,
            "draft_moment_type": first_draft.moment_type if first_draft else None,
            "has_draft": first_draft is not None,
            "linked_moment_status": (
                first_active.status
                if first_active
                else (first_draft.status if first_draft else None)
            ),
        }

    def _latest_by_code(self, moments: list[MomentModel]) -> dict[str, MomentModel]:
        latest: dict[str, MomentModel] = {}
        for m in moments:  # newest-first
            code = m.moment_type or ""
            if code and code not in latest:
                latest[code] = m
        return latest

    async def _require_moment(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        """Owner-only gate for mutations (patch/activate/archive).

        Members who can see the moment get 403 ``moment_not_owned`` instead of
        a misleading 404 so clients can show a permission message.
        """
        from app.domains.group.access import is_active_group_member

        moment = await self.moments.get_by_id(moment_id)
        if moment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found")
        if (moment.context_type or "").upper() != GROUP_CONTEXT:
            raise deny_access(
                context_type=GROUP_CONTEXT,
                moment_id=moment_id,
                moment_type=moment.moment_type,
                user_id=user_id,
                action="require_moment",
                denial_reason="context_mismatch",
                message="This moment does not belong to Group.",
                owner_match=moment.user_id == user_id,
            )
        if moment.user_id != user_id:
            membership_found = await is_active_group_member(
                self.session, user_id, moment_id, moment
            )
            if membership_found:
                raise deny_access(
                    context_type=GROUP_CONTEXT,
                    moment_id=moment_id,
                    moment_type=moment.moment_type,
                    user_id=user_id,
                    action="require_moment",
                    denial_reason="moment_not_owned",
                    message="Only the owner can change this moment.",
                    owner_match=False,
                    membership_found=True,
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found")
        return moment

    async def _require_accessible_moment(
        self, user_id: UUID, moment_id: UUID
    ) -> MomentModel:
        """Owner or active invitee — for pulse / moments / memory reads."""
        moment = await require_group_moment_access(self.session, user_id, moment_id)
        if (moment.context_type or "").upper() != GROUP_CONTEXT:
            raise deny_access(
                context_type=GROUP_CONTEXT,
                moment_id=moment_id,
                moment_type=moment.moment_type,
                user_id=user_id,
                action="require_accessible_moment",
                denial_reason="context_mismatch",
                message="This moment does not belong to Group.",
                owner_match=moment.user_id == user_id,
            )
        return moment

    async def _invalidate_template_projections(
        self, user_id: UUID, moment_id: UUID, code: str, reason: str
    ) -> None:
        try:
            if code == "SHARED_EXPERIENCE":
                await SharedExperienceService(self.session).invalidate(
                    user_id, moment_id, reason=reason
                )
            elif code == "SHARED_PURCHASE":
                await SharedPurchaseService(self.session).invalidate(
                    user_id, moment_id, reason=reason
                )
            elif code == "SHARED_LIVING":
                await SharedLivingService(self.session).invalidate(
                    user_id, moment_id, reason=reason
                )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Group projection invalidate failed: %s", exc)

    async def _after_lifecycle(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        code: str,
        reason: str,
        flip_active: bool,
        active_moments: list[MomentModel] | None = None,
    ) -> str:
        t0 = time.perf_counter()
        if flip_active:
            await self._flip_active(user_id)
            module_state = "ACTIVE"
        else:
            remaining = (
                active_moments
                if active_moments is not None
                else await self._active_moments(user_id)
            )
            if remaining:
                await self.bootstrap.invalidate_cache(user_id)
                module_state = "ACTIVE"
            else:
                await self.modules.set_state(user_id, "GROUP", "SETUP", reason)
                # Shared PULSE/MOMENTS — only demote when no other context is live.
                personal = await self.modules.get_state(user_id, "MY_MONEY")
                business = await self.modules.get_state(user_id, "BUSINESS")
                other_active = any(
                    row and (row.state or "").upper() == "ACTIVE"
                    for row in (personal, business)
                )
                if not other_active:
                    await self.modules.set_state(user_id, "PULSE", "SETUP", reason)
                    await self.modules.set_state(user_id, "MOMENTS", "SETUP", reason)
                await self.bootstrap.invalidate_cache(user_id)
                module_state = "SETUP"
        await self._invalidate_template_projections(user_id, moment_id, code, reason)
        _ = int((time.perf_counter() - t0) * 1000)
        return module_state

    async def _run_lifecycle(
        self,
        user_id: UUID,
        moment: MomentModel,
        *,
        previous_status: str,
        action: str,
        reason: str,
        flip_active: bool,
        exclude_from_replacement: bool,
    ) -> dict:
        """Post-mutation lifecycle: one inventory read for module + replacement."""
        _, _, active, replacement = await self._load_moment_inventories(user_id)
        code = moment.moment_type or ""
        module_state = await self._after_lifecycle(
            user_id,
            moment.id,
            code=code,
            reason=reason,
            flip_active=flip_active,
            active_moments=active,
        )
        return await self._lifecycle_result(
            user_id,
            moment,
            previous_status=previous_status,
            action=action,
            module_state=module_state,
            exclude_from_replacement=exclude_from_replacement,
            replacement_inventory=replacement,
        )

    async def _lifecycle_result(
        self,
        user_id: UUID,
        moment: MomentModel,
        *,
        previous_status: str,
        action: str,
        module_state: str,
        exclude_from_replacement: bool,
        replacement_inventory: list[MomentModel] | None = None,
    ) -> dict:
        inventory = (
            replacement_inventory
            if replacement_inventory is not None
            else await self._inventory_for_replacement(user_id)
        )
        exclude_id = moment.id if exclude_from_replacement else None
        preferred = None if exclude_from_replacement else moment.id
        repl_id, repl_type = pick_replacement_moment(
            inventory,
            exclude_id=exclude_id,
            preferred_id=preferred,
        )
        log_lifecycle_transition(
            context_type=GROUP_CONTEXT,
            moment_id=moment.id,
            moment_type=moment.moment_type,
            action=action,
            previous_status=previous_status,
            final_status=moment.status,
            module_state=module_state,
            replacement_moment_id=repl_id,
        )
        return build_lifecycle_response(
            moment=moment,
            context_type=GROUP_CONTEXT,
            previous_status=previous_status,
            module_state=module_state,
            replacement_moment_id=repl_id,
            replacement_moment_type_code=repl_type,
        )

    async def _latest_draft_of_type(self, user_id: UUID, code: str) -> MomentModel:
        for m in await self._visible_moments(user_id):
            if (m.moment_type or "") == code:
                return m
        return await self.moments.create(
            user_id=user_id,
            context_type=GROUP_CONTEXT,
            moment_type=code,
            title=group_default_name(code),
            status="DRAFT",
            setup_state="SETUP",
        )

    async def _flip_setup(self, user_id: UUID) -> None:
        """Draft create → GROUP/PULSE SETUP. Do not demote an already-ACTIVE Group."""
        existing = await self.modules.get_state(user_id, "GROUP")
        if existing and (existing.state or "").upper() == "ACTIVE":
            await self.bootstrap.invalidate_cache(user_id)
            return
        await self.modules.set_state(user_id, "GROUP", "SETUP", "group_moment_draft")
        await self.modules.set_state(user_id, "PULSE", "SETUP", "group_moment_draft")
        await self.bootstrap.invalidate_cache(user_id)

    async def _flip_active(self, user_id: UUID) -> None:
        await self.modules.set_state(user_id, "GROUP", "ACTIVE", "group_moment")
        await self.modules.set_state(user_id, "PULSE", "ACTIVE", "group_moment")
        await self.modules.set_state(user_id, "MOMENTS", "ACTIVE", "group_moment")
        await self.bootstrap.invalidate_cache(user_id)

    def _type_cards(self, latest: dict[str, MomentModel]) -> list[s.GroupMomentTypeCard]:
        cards: list[s.GroupMomentTypeCard] = []
        for mt in GROUP_MOMENT_TYPES:
            linked = latest.get(mt.code)
            cards.append(
                s.GroupMomentTypeCard(
                    moment_type_id=mt.type_id,
                    moment_type_code=mt.code,
                    moment_type_name=mt.name,
                    description=mt.description,
                    create_tagline=mt.tagline,
                    icon_name=mt.icon_name,
                    image_url=mt.image_url,
                    accent_main=mt.accent_main,
                    accent_soft_tint=mt.accent_soft_tint,
                    card_layout=mt.card_layout,
                    display_order=mt.display_order,
                    linked_moment_id=str(linked.id) if linked else None,
                    linked_moment_status=linked.status if linked else None,
                    cover_image_url=None,
                    action_label="Open" if linked else "Begin",
                )
            )
        return cards

    def _map_list_item(
        self, moment: MomentModel, *, viewer_id: UUID | None = None
    ) -> s.GroupMomentListItem:
        code = moment.moment_type or ""
        is_owned = viewer_id is None or moment.user_id == viewer_id
        return s.GroupMomentListItem(
            id=str(moment.id),
            name=moment.title or group_default_name(code),
            moment_type=code or None,
            category=_CATEGORY_BY_CODE.get(code, "trips"),
            status_label=(moment.status or "DRAFT").title(),
            status_tone="positive" if _moment_is_active(moment) else "neutral",
            orchestration_state=moment.setup_state,
            lifecycle_status=moment.status,
            is_owned=is_owned,
            updated_at=(moment.updated_at or datetime.now(timezone.utc)).isoformat(),
        )

    # ----- landing surfaces ---------------------------------------------- #
    async def pulse(self, user_id: UUID) -> dict:
        _, visible, active, _ = await self._load_moment_inventories(user_id)
        return self._pulse_payload_from_moments(visible, active).model_dump(mode="json")

    async def moments_home(self, user_id: UUID) -> dict:
        _, visible, active, _ = await self._load_moment_inventories(user_id)
        latest = self._latest_by_code(visible)
        return s.GroupMomentsHomeResponse(
            is_empty=len(active) == 0,
            active_moment_count=len(active),
            type_cards=self._type_cards(latest),
            how_it_works=_magic_steps(),
        ).model_dump(mode="json")

    async def live_empty(self, user_id: UUID) -> dict:
        active = await self._active_moments(user_id)
        return s.GroupLiveEmptyResponse(
            is_empty=len(active) == 0,
            active_moment_count=len(active),
            pillars=_why_groups(),
        ).model_dump(mode="json")

    async def memory(self, user_id: UUID) -> dict:
        active = await self._active_moments(user_id)
        return s.GroupMemoryResponse(
            is_empty=len(active) == 0,
            active_moment_count=len(active),
            insights=[],
        ).model_dump(mode="json")

    async def create_options(self, user_id: UUID) -> dict:
        cards = [
            s.GroupCreateOptionCard(
                moment_type_id=mt.type_id,
                moment_type_code=mt.code,
                moment_type_name=mt.name,
                description=mt.description,
                create_tagline=mt.tagline,
                icon_name=mt.icon_name,
                image_url=mt.image_url,
                accent_main=mt.accent_main,
                accent_soft_tint=mt.accent_soft_tint,
                card_layout=mt.card_layout,
                display_order=mt.display_order,
            )
            for mt in GROUP_MOMENT_TYPES
        ]
        return s.GroupCreateOptionsResponse(cards=cards).model_dump(mode="json")

    async def life(self, user_id: UUID) -> dict:
        active = await self._active_moments(user_id)
        if not active:
            return s.GroupLifeResponse(is_empty=True, active_moment_count=0).model_dump(mode="json")
        raw_metrics = build_group_life_command_center(active)
        date_range_label = raw_metrics.pop("date_range_label", None)
        metrics = s.GroupLifeMetrics.model_validate(raw_metrics)
        return s.GroupLifeResponse(
            active_moment_count=len(active),
            is_empty=False,
            date_range_label=date_range_label,
            metrics=metrics,
        ).model_dump(mode="json")

    async def life_activity(self, user_id: UUID, moment_id: str | None) -> dict:
        return s.GroupLifeOpsActivityResponse(moment_id=moment_id or "").model_dump(mode="json")

    # ----- templates / profiles ------------------------------------------ #
    async def list_templates(self) -> list[dict]:
        return [
            s.GroupMomentTemplate(
                id=mt.type_id,
                moment_type=mt.code,
                title=mt.name,
                subtitle=mt.tagline,
                icon=mt.icon_name,
                image_url=mt.image_url or "",
                layout=mt.card_layout,
                sort_order=mt.display_order,
                default_name=mt.default_name,
            ).model_dump(mode="json")
            for mt in GROUP_MOMENT_TYPES
        ]

    async def setup_profiles(self, moment_type: str) -> list[dict]:
        return [
            s.GroupSetupProfile(
                profile_id=p.profile_id,
                moment_type=moment_type,
                profile_code=p.code,
                profile_name=p.name,
                profile_description=p.description,
                icon_name=p.icon_name,
                image_url=p.image_url,
                display_order=p.display_order,
            ).model_dump(mode="json")
            for p in group_profiles_for(moment_type)
        ]

    # ----- session bootstrap --------------------------------------------- #
    async def get_session(self, user_id: UUID) -> dict:
        _, visible, active, _ = await self._load_moment_inventories(user_id)
        fields = self._session_fields_from_moments(visible, active)
        return s.GroupSessionResponse(**fields).model_dump(mode="json")

    async def get_inventory(self, user_id: UUID) -> dict:
        _, visible, active, _ = await self._load_moment_inventories(user_id)
        pulse = self._pulse_payload_from_moments(visible, active)
        overview = self._live_overview_from_moments(visible, active, viewer_id=user_id)
        return s.GroupInventoryResponse(
            pulse=pulse,
            moments=[self._map_list_item(m, viewer_id=user_id) for m in visible],
            live_overview=overview,
        ).model_dump(mode="json")

    async def session_bootstrap(self, user_id: UUID) -> dict:
        """Thin composer for native clients — one inventory pass."""
        _, visible, active, _ = await self._load_moment_inventories(user_id)
        pulse = self._pulse_payload_from_moments(visible, active)
        overview = self._live_overview_from_moments(visible, active, viewer_id=user_id)
        fields = self._session_fields_from_moments(visible, active)
        return s.GroupSessionBootstrapResponse(
            pulse=pulse,
            moments=[self._map_list_item(m, viewer_id=user_id) for m in visible],
            live_overview=overview,
            **fields,
        ).model_dump(mode="json")

    # ----- moment create / manage ---------------------------------------- #
    async def create_moment(
        self, user_id: UUID, moment_type_code: str, moment_name: str | None
    ) -> dict:
        name = moment_name or group_default_name(moment_type_code)
        moment = await self.moments.create(
            user_id=user_id,
            context_type=GROUP_CONTEXT,
            moment_type=moment_type_code,
            title=name,
            status="DRAFT",
            setup_state="SETUP",
        )
        await ensure_group_moments_row(self.session, moment, ensure_owner_member=True)
        await self._flip_setup(user_id)
        return s.GroupDraftMomentResponse(
            moment_id=str(moment.id),
            moment_type_code=moment_type_code,
            moment_name=name,
            orchestration_state=moment.setup_state,
        ).model_dump(mode="json")

    async def patch_moment(
        self, user_id: UUID, moment_id: UUID, body: s.GroupMomentUpdateRequest
    ) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        previous = moment.status
        if body.moment_name is not None:
            await self.engine.update(
                self._adapter, user_id, moment_id, title=body.moment_name
            )
        if body.status is not None:
            try:
                await self.engine.transition_status(
                    self._adapter,
                    user_id,
                    moment_id,
                    body.status,
                    setup_state="ACTIVE" if body.status == "ACTIVE" else None,
                )
            except StateTransitionError as exc:
                raise StateTransitionError(
                    str(exc),
                    code="lifecycle_transition_invalid",
                    details={
                        "previous_status": previous,
                        "requested_status": body.status,
                    },
                ) from exc
            moment = await self._adapter.get_model(user_id, moment_id)
            flip = body.status == "ACTIVE"
            return await self._run_lifecycle(
                user_id,
                moment,
                previous_status=previous,
                action=body.status.lower(),
                reason=f"group_moment_{body.status.lower()}",
                flip_active=flip,
                exclude_from_replacement=body.status == "ARCHIVED",
            )
        moment = await self._adapter.get_model(user_id, moment_id)
        code = moment.moment_type or ""
        return s.GroupMomentManageResponse(
            moment_id=str(moment.id),
            moment_type_code=code,
            moment_name=moment.title or group_default_name(code),
            orchestration_state=moment.setup_state,
            lifecycle_status=moment.status,
            status=moment.status,
            is_archived=moment.status == "ARCHIVED",
        ).model_dump(mode="json")

    async def complete_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        previous = moment.status
        try:
            await self.engine.complete(self._adapter, user_id, moment_id)
        except NotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found")
        except StateTransitionError as exc:
            raise StateTransitionError(
                str(exc),
                code="lifecycle_transition_invalid",
                details={"previous_status": previous, "requested_status": "COMPLETED"},
            ) from exc
        moment = await self._adapter.get_model(user_id, moment_id)
        return await self._run_lifecycle(
            user_id,
            moment,
            previous_status=previous,
            action="complete",
            reason="group_moment_completed",
            flip_active=False,
            exclude_from_replacement=True,
        )

    async def archive_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        previous = moment.status
        try:
            await self.engine.archive(self._adapter, user_id, moment_id)
        except NotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found")
        except StateTransitionError as exc:
            raise StateTransitionError(
                str(exc),
                code="lifecycle_transition_invalid",
                details={"previous_status": previous, "requested_status": "ARCHIVED"},
            ) from exc
        moment = await self._adapter.get_model(user_id, moment_id)
        return await self._run_lifecycle(
            user_id,
            moment,
            previous_status=previous,
            action="archive",
            reason="group_moment_archived",
            flip_active=False,
            exclude_from_replacement=True,
        )

    async def delete_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        """Permanent purge: ops data cleared, analytics retained, members exited."""
        from app.domains.moments.purge_service import MomentPurgeService

        moment = await self._require_moment(user_id, moment_id)
        previous = moment.status
        try:
            moment = await MomentPurgeService(self.session).purge(
                user_id, moment_id, expected_context=GROUP_CONTEXT
            )
        except PermissionDeniedError:
            raise
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
            )
        return await self._run_lifecycle(
            user_id,
            moment,
            previous_status=previous,
            action="delete",
            reason="group_moment_deleted",
            flip_active=False,
            exclude_from_replacement=True,
        )

    async def leave_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        """Active member exits self; owner must archive/delete instead."""
        from sqlalchemy import select

        from app.domains.group import moment_store as group_store
        from app.domains.group.models import GroupMomentMembers

        moment = await self._require_accessible_moment(user_id, moment_id)
        if moment.user_id == user_id:
            raise deny_access(
                context_type=GROUP_CONTEXT,
                moment_id=moment_id,
                moment_type=moment.moment_type,
                user_id=user_id,
                action="leave",
                denial_reason="owner_cannot_leave",
                message="Owners must archive or delete the moment.",
                owner_match=True,
                membership_found=True,
            )

        previous = moment.status
        now = datetime.now(timezone.utc)
        naive = now.replace(tzinfo=None)

        result = await self.session.execute(
            select(GroupMomentMembers).where(
                GroupMomentMembers.moment_id == moment_id,
                GroupMomentMembers.user_id == user_id,
            )
        )
        for row in result.scalars().all():
            status_val = (row.status or "").upper()
            if status_val in {"LEFT", "REMOVED", "DECLINED"} and row.left_at is not None:
                continue
            row.status = "LEFT"
            row.left_at = naive

        uid = str(user_id)
        state = group_store.read_state(moment)
        members = state.get("runtime", {}).get("members") or []
        changed = False
        for member in members:
            if member.get("deleted"):
                continue
            member_uid = str(member.get("user_id") or member.get("id") or "")
            if member_uid != uid:
                continue
            member["status"] = "LEFT"
            member["deleted"] = True
            member["left_at"] = now.isoformat()
            member["updated_at"] = group_store.now_iso()
            changed = True
        if changed:
            group_store.write_state(moment, state)

        await self.session.flush()
        return await self._run_lifecycle(
            user_id,
            moment,
            previous_status=previous,
            action="leave",
            reason="group_moment_left",
            flip_active=False,
            exclude_from_replacement=True,
        )

    # ----- setup flow ----------------------------------------------------- #
    async def setup_basics(self, user_id: UUID, moment_type: str, body: dict) -> dict:
        name = str(body.get("moment_name") or "").strip() or group_default_name(moment_type)
        moment = await self.moments.create(
            user_id=user_id,
            context_type=GROUP_CONTEXT,
            moment_type=moment_type,
            title=name,
            status="DRAFT",
            setup_state="SETUP",
        )
        await self._flip_active(user_id)
        return s.GroupSetupBasicsResponse(
            moment_id=str(moment.id),
            moment_type_code=moment_type,
            moment_name=name,
            lifecycle_status="SETUP",
            orchestration_state="SETUP",
        ).model_dump(mode="json")

    async def setup_people(
        self, user_id: UUID, moment_type: str, moment_id: UUID | None, body: dict
    ) -> dict:
        if moment_id is not None:
            moment = await self._require_moment(user_id, moment_id)
        else:
            moment = await self._latest_draft_of_type(user_id, moment_type)
        moment.updated_at = datetime.now(timezone.utc)
        code = moment.moment_type or moment_type
        return s.GroupSetupPeopleResponse(
            moment_id=str(moment.id),
            moment_type_code=code,
            moment_name=moment.title or group_default_name(code),
            status="SETUP",
            orchestration_state=moment.setup_state,
        ).model_dump(mode="json")

    async def setup_review(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        code = moment.moment_type or ""
        name = moment.title or group_default_name(code)
        profiles = group_profiles_for(code)
        profile_name = profiles[0].name if profiles else group_type_name(code)
        return s.GroupSetupReviewResponse(
            moment_id=str(moment.id),
            moment_name=name,
            profile_name=profile_name,
            summary_items=[
                s.GroupSetupReviewItem(label="Type", value=group_type_name(code), icon_name="tag"),
                s.GroupSetupReviewItem(label="Name", value=name, icon_name="pencil"),
            ],
            insight_text="You're all set — activate to bring this moment to life.",
            moment_type=code,
            moment_profile=profile_name,
            basics={"moment_name": name},
            people=[],
        ).model_dump(mode="json")

    async def setup_activate(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        previous = moment.status
        try:
            await self.engine.activate(
                self._adapter, user_id, moment_id, setup_state="ACTIVE"
            )
        except StateTransitionError as exc:
            raise StateTransitionError(
                str(exc),
                code="lifecycle_transition_invalid",
                details={"previous_status": previous, "requested_status": "ACTIVE"},
            ) from exc
        moment = await self._adapter.get_model(user_id, moment_id)
        await ensure_group_moments_row(self.session, moment, ensure_owner_member=True)
        payload = await self._run_lifecycle(
            user_id,
            moment,
            previous_status=previous,
            action="activate",
            reason="group_moment_activated",
            flip_active=True,
            exclude_from_replacement=False,
        )
        # Preserve legacy activate fields
        payload["activated_at"] = moment.updated_at.isoformat() if moment.updated_at else None
        payload["lifecycle_status"] = "ACTIVE"
        return payload

    # ----- iOS active surface -------------------------------------------- #
    async def active_pulse(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        moment = await self._require_accessible_moment(user_id, moment_id)
        code = moment.moment_type or ""
        if code == "SHARED_EXPERIENCE":
            from app.core.request_context import set_cache_hit
            from app.domains.group.projection_cache import get_cached_slice
            from app.domains.group.templates.shared_experience.active_mapper import (
                wrap_trip_pulse_to_active,
            )

            if not force_refresh:
                cached = await get_cached_slice(
                    user_id, moment_id, "pulse", moment_type=code
                )
                if cached is not None and "pulse_data" in cached:
                    set_cache_hit(True)
                    return cached
                if cached is not None and "trip_name" in cached:
                    set_cache_hit(True)
                    return wrap_trip_pulse_to_active(cached, moment_type=code)

            svc = SharedExperienceService(self.session)
            trip_pulse = await svc.pulse(
                user_id, moment_id, force_refresh=force_refresh
            )
            return wrap_trip_pulse_to_active(trip_pulse, moment_type=code)
        if code == "SHARED_PURCHASE":
            handler = SharedPurchaseTemplateHandler(self.session)
            return await handler.active_pulse(user_id, moment_id)
        if code == "SHARED_LIVING":
            handler = SharedLivingTemplateHandler(self.session)
            return await handler.active_pulse(user_id, moment_id)
        profiles = group_profiles_for(code)
        return s.GroupPulseDataResponse(
            moment_id=str(moment.id),
            moment_type=code,
            moment_profile=profiles[0].code if profiles else "",
            moment_name=moment.title or group_default_name(code),
        ).model_dump(mode="json")

    async def active_moments(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        moment = await self._require_accessible_moment(user_id, moment_id)
        code = moment.moment_type or ""
        if code == "SHARED_EXPERIENCE":
            from app.core.request_context import set_cache_hit
            from app.domains.group.projection_cache import get_cached_slice, set_cached_slice
            from app.domains.group.templates.shared_experience.active_mapper import map_active_moments
            from app.domains.group.templates.shared_experience.projection_builder import (
                SharedExperienceProjectionBuilder,
            )

            if not force_refresh:
                cached = await get_cached_slice(
                    user_id, moment_id, "moments", moment_type=code
                )
                if cached is not None and (
                    "stat_tiles" in cached
                    or "recent_events" in cached
                    or "memories" in cached
                ):
                    set_cache_hit(True)
                    return cached

            svc = SharedExperienceService(self.session)
            trip_moments = await svc.moments_view(
                user_id, moment_id, force_refresh=force_refresh
            )
            if "stat_tiles" in trip_moments or "gallery" in trip_moments:
                return trip_moments
            ctx = SharedExperienceProjectionBuilder(self.session).build_from_moment(moment)
            payload = map_active_moments(ctx)
            await set_cached_slice(user_id, moment_id, "moments", payload, moment_type=code)
            return payload
        if code == "SHARED_PURCHASE":
            handler = SharedPurchaseTemplateHandler(self.session)
            return await handler.active_moments(user_id, moment_id)
        if code == "SHARED_LIVING":
            handler = SharedLivingTemplateHandler(self.session)
            return await handler.active_moments(user_id, moment_id)
        return {
            "moment_id": str(moment.id),
            "moment_type": code,
            "moment_name": moment.title or group_default_name(code),
            "memories": [],
            "recent_events": [],
            "updates": [],
        }

    async def active_memory(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        moment = await self._require_accessible_moment(user_id, moment_id)
        code = moment.moment_type or ""
        if code == "SHARED_EXPERIENCE":
            from app.core.request_context import set_cache_hit
            from app.domains.group.projection_cache import get_cached_slice, set_cached_slice
            from app.domains.group.templates.shared_experience.active_mapper import map_active_memory
            from app.domains.group.templates.shared_experience.projection_builder import (
                SharedExperienceProjectionBuilder,
            )

            if not force_refresh:
                cached = await get_cached_slice(
                    user_id, moment_id, "memory", moment_type=code
                )
                if cached is not None and (
                    "timeline" in cached
                    or "highlights" in cached
                    or "memory_data" in cached
                ):
                    set_cache_hit(True)
                    return cached

            svc = SharedExperienceService(self.session)
            proj = await svc.memory_projection(
                user_id, moment_id, force_refresh=force_refresh
            )
            if "timeline" in proj or "highlights" in proj:
                return proj
            ctx = SharedExperienceProjectionBuilder(self.session).build_from_moment(moment)
            payload = map_active_memory(ctx)
            await set_cached_slice(user_id, moment_id, "memory", payload, moment_type=code)
            return payload
        if code == "SHARED_PURCHASE":
            handler = SharedPurchaseTemplateHandler(self.session)
            return await handler.active_memory(user_id, moment_id)
        if code == "SHARED_LIVING":
            handler = SharedLivingTemplateHandler(self.session)
            return await handler.active_memory(user_id, moment_id)
        return s.GroupMemoryDataContainer().model_dump(mode="json")

    async def active_life(self, user_id: UUID) -> dict:
        active = await self._active_moments(user_id)
        if not active:
            return s.GroupActiveLifeResponse(is_empty=True, active_moment_count=0).model_dump(mode="json")
        raw_metrics = build_group_life_command_center(active)
        raw_metrics.pop("date_range_label", None)
        metrics = s.GroupLifeMetrics.model_validate(raw_metrics)
        return s.GroupActiveLifeResponse(
            is_empty=False,
            active_moment_count=len(active),
            metrics=metrics,
        ).model_dump(mode="json")

    async def quick_add_config(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require_accessible_moment(user_id, moment_id)
        code = moment.moment_type or ""
        if code == "SHARED_EXPERIENCE":
            ctx = SharedExperienceProjectionBuilder(self.session).build_from_moment(moment)
            modules = ctx.experience_type.quick_add_modules
            return s.GroupQuickAddConfigResponse(
                moment_id=str(moment.id),
                moment_type=code,
                moment_profile=ctx.experience_type.code,
                categories=build_trip_quick_add_categories(modules),
            ).model_dump(mode="json")
        if code == "SHARED_PURCHASE":
            handler = SharedPurchaseTemplateHandler(self.session)
            return await handler.quick_add_config(user_id, moment_id)
        if code == "SHARED_LIVING":
            handler = SharedLivingTemplateHandler(self.session)
            return await handler.quick_add_config(user_id, moment_id)
        profiles = group_profiles_for(code)
        return s.GroupQuickAddConfigResponse(
            moment_id=str(moment.id),
            moment_type=code,
            moment_profile=profiles[0].code if profiles else "",
            categories=[],
        ).model_dump(mode="json")
