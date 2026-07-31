"""Contract-first Business service consumed by the mobile clients.

Business moments are persisted in the shared ``moments`` table
(``context_type = "BUSINESS"``) so create / patch / cover flows are real and
work against the test ``MockSession``. The rich analytical surfaces (pulse /
live / memory) return schema-valid empty-state payloads that render on both
apps; wiring them to the ``business_*`` snapshot tables/views is the iterative
data-backing step.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import StateTransitionError
from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.business import app_schemas as s
from app.domains.business.catalog import (
    BUSINESS_CONTEXT,
    BUSINESS_CREATE_CATALOG,
    BUSINESS_DIMENSIONS,
    V1_CREATABLE_CODES,
    business_type_id,
    business_type_name,
    normalize_moment_type_code,
)
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
from app.domains.business.setup.service import BusinessSetupService
from app.domains.business.workspace_service import BusinessWorkspaceService

_ACTIVE_STATUSES = {"ACTIVE"}
# COMPLETED included so switcher/landing can link completed moments (client ACTIVE-family).
_VISIBLE_STATUSES = {"DRAFT", "SETUP", "ACTIVE", "PAUSED", "COMPLETED"}
# Personal parity: switcher-active family + link priority (lower = better).
_SWITCHER_ACTIVE_STATUSES = {"ACTIVE", "PAUSED", "COMPLETED"}
_LINK_STATUS_PRIORITY = {
    "ACTIVE": 0,
    "PAUSED": 1,
    "COMPLETED": 2,
    "SETUP": 3,
    "DRAFT": 4,
}


def _benefits() -> list[s.BusinessBenefitItem]:
    return [
        s.BusinessBenefitItem(
            item_code="clarity",
            title="One calm dashboard",
            description="Stop stitching together spreadsheets and chat threads.",
            icon_name="layout",
        ),
        s.BusinessBenefitItem(
            item_code="runway",
            title="Runway you can trust",
            description="Always know how much time and cash you have.",
            icon_name="wallet",
        ),
        s.BusinessBenefitItem(
            item_code="memory",
            title="Decisions remembered",
            description="Every choice becomes context you can revisit later.",
            icon_name="sparkles",
        ),
    ]


def _how_it_works() -> list[s.BusinessStepItem]:
    return [
        s.BusinessStepItem(
            item_code="step_create",
            title="Create a moment",
            description="Pick Team Operations, Business Runway, or Business Operations.",
            icon_name="plus",
            display_order=1,
            is_active=True,
            step_label="1",
        ),
        s.BusinessStepItem(
            item_code="step_configure",
            title="Configure it",
            description="Set up the workspace and who's involved.",
            icon_name="settings",
            display_order=2,
            step_label="2",
        ),
        s.BusinessStepItem(
            item_code="step_run",
            title="Run it live",
            description="Capture spend, approvals and progress as it happens.",
            icon_name="bolt",
            display_order=3,
            step_label="3",
            is_goal=True,
        ),
    ]


def _modules() -> list[s.BusinessEmptyStateItem]:
    return [
        s.BusinessEmptyStateItem(
            item_code=d.code.lower(),
            item_kind="module",
            title=d.name,
            description=d.tagline,
            icon_name=d.icon_name,
            accent_main=d.accent_main,
            accent_soft_tint=d.accent_soft_tint,
            badge_label=d.badge_label,
            display_order=d.display_order,
        )
        for d in BUSINESS_DIMENSIONS
    ]


class BusinessAppService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.modules = ModuleStateService(session)
        self.bootstrap = AppBootstrapService(session)
        self.setup = BusinessSetupService(session)
        self.workspaces = BusinessWorkspaceService(session)
        self.engine = MomentEngine()
        self._adapter = get_domain_registry().adapter(session, BUSINESS_CONTEXT)

    # ----- helpers -------------------------------------------------------- #
    async def _visible_moments(
        self,
        user_id: UUID,
        *,
        workspace_id: UUID | None = None,
        moments: list[MomentModel] | None = None,
        allowed_ids: set[UUID] | None = None,
    ) -> list[MomentModel]:
        """Workspace-scoped visible inventory.

        Callers that already loaded ``moments`` / ``allowed_ids`` in parallel
        can pass them to avoid a second round-trip.
        """
        owned = (
            moments
            if moments is not None
            else await self.moments.list_business_accessible(user_id)
        )
        visible = [m for m in owned if m.status in _VISIBLE_STATUSES]
        if workspace_id is None:
            return visible
        allowed = (
            allowed_ids
            if allowed_ids is not None
            else await self.workspaces.moment_ids_for_workspace(workspace_id)
        )
        if not allowed:
            # Legacy moments may lack business_moments rows until setup sync.
            return visible
        return [m for m in visible if m.id in allowed]

    async def _resolve_workspace(
        self, user_id: UUID, *, workspace_id: UUID | None = None
    ):
        return await self.workspaces.resolve_selected(user_id, workspace_id=workspace_id)

    async def _inventory_for_replacement(self, user_id: UUID) -> list[MomentModel]:
        moments = await self.moments.list_business_accessible(user_id)
        return [m for m in moments if (m.status or "").upper() != "ARCHIVED"]

    def _latest_by_code(self, moments: list[MomentModel]) -> dict[str, MomentModel]:
        """Pick the best linked moment per type (Personal parity).

        ACTIVE beats newer DRAFT duplicates; same status → newer updated_at/created_at.
        """
        best: dict[str, MomentModel] = {}
        for m in moments:
            raw = m.moment_type or ""
            code = normalize_moment_type_code(raw) or raw
            if not code:
                continue
            existing = best.get(code)
            if existing is None:
                best[code] = m
                continue
            m_rank = _LINK_STATUS_PRIORITY.get((m.status or "").upper(), 99)
            e_rank = _LINK_STATUS_PRIORITY.get((existing.status or "").upper(), 99)
            if m_rank < e_rank:
                best[code] = m
            elif m_rank == e_rank:
                m_at = getattr(m, "updated_at", None) or getattr(m, "created_at", None)
                e_at = getattr(existing, "updated_at", None) or getattr(existing, "created_at", None)
                if m_at and e_at and m_at > e_at:
                    best[code] = m
        return best

    async def _require_moment(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        from app.domains.business.access import require_business_moment_access

        moment = await require_business_moment_access(self.session, user_id, moment_id)
        if (moment.context_type or "").upper() != BUSINESS_CONTEXT:
            raise deny_access(
                context_type=BUSINESS_CONTEXT,
                moment_id=moment_id,
                moment_type=moment.moment_type,
                user_id=user_id,
                action="require_moment",
                denial_reason="context_mismatch",
                message="This moment does not belong to Business.",
                owner_match=moment.user_id == user_id,
            )
        return moment

    async def _flip_setup(self, user_id: UUID) -> None:
        await self.modules.set_state(user_id, "BUSINESS", "SETUP", "business_moment_draft")
        await self.modules.set_state(user_id, "PULSE", "SETUP", "business_moment_draft")
        await self.bootstrap.invalidate_cache(user_id)

    async def _flip_active(self, user_id: UUID) -> None:
        await self.modules.set_state(user_id, "BUSINESS", "ACTIVE", "business_moment")
        await self.modules.set_state(user_id, "PULSE", "ACTIVE", "business_moment")
        await self.modules.set_state(user_id, "MOMENTS", "ACTIVE", "business_moment")
        await self.bootstrap.invalidate_cache(user_id)

    def _dimension_cards(self, latest: dict[str, MomentModel]) -> list[s.BusinessMomentTypeCard]:
        cards: list[s.BusinessMomentTypeCard] = []
        for d in BUSINESS_DIMENSIONS:
            linked = latest.get(d.code)
            linked_status = linked.status if linked else None
            cards.append(
                s.BusinessMomentTypeCard(
                    moment_type_id=d.type_id,
                    moment_type_code=d.code,
                    moment_type_name=d.name,
                    description=d.description,
                    create_tagline=d.tagline,
                    badge_label=d.badge_label,
                    icon_name=d.icon_name,
                    accent_main=d.accent_main,
                    accent_soft_tint=d.accent_soft_tint,
                    display_order=d.display_order,
                    linked_moment_id=str(linked.id) if linked else None,
                    linked_moment_status=linked_status,
                    is_active=bool(
                        linked and (linked_status or "").upper() in _SWITCHER_ACTIVE_STATUSES
                    ),
                    action_label="Open" if linked else "Explore",
                )
            )
        return cards

    def _map_moment(self, moment: MomentModel) -> s.BusinessMomentResponse:
        raw = moment.moment_type or ""
        code = normalize_moment_type_code(raw) or raw
        return s.BusinessMomentResponse(
            moment_id=str(moment.id),
            moment_type_id=business_type_id(code),
            moment_type_code=code or None,
            moment_name=moment.title or business_type_name(code),
            moment_description=moment.description,
            status=moment.status,
        )

    def _pulse_payload_from_moments(self, moments: list[MomentModel]) -> dict:
        active = [m for m in moments if m.status in _ACTIVE_STATUSES]
        latest = self._latest_by_code(moments)
        return s.BusinessPulseResponse(
            is_empty=len(active) == 0,
            active_moment_count=len(active),
            benefits=_benefits(),
            dimension_cards=self._dimension_cards(latest),
        ).model_dump(mode="json")

    def _moments_home_payload_from_moments(self, moments: list[MomentModel]) -> dict:
        active = [m for m in moments if m.status in _ACTIVE_STATUSES]
        latest = self._latest_by_code(moments)
        return s.BusinessMomentsHomeResponse(
            is_empty=len(active) == 0,
            active_moment_count=len(active),
            cards=self._dimension_cards(latest),
        ).model_dump(mode="json")

    # ----- landing surfaces ---------------------------------------------- #
    async def pulse(self, user_id: UUID, *, workspace_id: UUID | None = None) -> dict:
        resolved = await self._resolve_workspace(user_id, workspace_id=workspace_id)
        ws_id = resolved[0].workspace_id if resolved else None
        moments = await self._visible_moments(user_id, workspace_id=ws_id)
        return self._pulse_payload_from_moments(moments)

    async def moments_home(self, user_id: UUID, *, workspace_id: UUID | None = None) -> dict:
        resolved = await self._resolve_workspace(user_id, workspace_id=workspace_id)
        ws_id = resolved[0].workspace_id if resolved else None
        moments = await self._visible_moments(user_id, workspace_id=ws_id)
        return self._moments_home_payload_from_moments(moments)

    async def live(self, user_id: UUID, *, workspace_id: UUID | None = None) -> dict:
        resolved = await self._resolve_workspace(user_id, workspace_id=workspace_id)
        ws_id = resolved[0].workspace_id if resolved else None
        moments = await self._visible_moments(user_id, workspace_id=ws_id)
        active = [m for m in moments if m.status in _ACTIVE_STATUSES]
        return s.BusinessLiveResponse(
            is_empty=len(active) == 0,
            active_moment_count=len(active),
            how_it_works=_how_it_works(),
            modules=_modules(),
        ).model_dump(mode="json")

    async def memory(self, user_id: UUID, *, workspace_id: UUID | None = None) -> dict:
        resolved = await self._resolve_workspace(user_id, workspace_id=workspace_id)
        ws_id = resolved[0].workspace_id if resolved else None
        moments = await self._visible_moments(user_id, workspace_id=ws_id)
        active = [m for m in moments if m.status in _ACTIVE_STATUSES]
        return s.BusinessMemoryResponse(
            is_empty=len(active) == 0,
            active_moment_count=len(active),
            patterns=[],
        ).model_dump(mode="json")

    async def create_options(self, user_id: UUID, *, workspace_id: UUID | None = None) -> dict:
        """Catalog-only — clients attach linked moment ids from session inventory."""
        _ = (user_id, workspace_id)
        cards = [
            s.BusinessCreateOptionCard(
                moment_type_id=d.type_id,
                moment_type_code=d.code,
                moment_type_name=d.name,
                create_tagline=d.tagline,
                description=d.description,
                icon_name=d.icon_name,
                accent_main=d.accent_main,
                accent_soft_tint=d.accent_soft_tint,
                badge_label=d.badge_label,
                display_order=d.display_order,
                linked_moment_id=None,
                linked_moment_status=None,
                is_active=False,
                is_available=d.is_available,
                implementation_status=d.implementation_status,
            )
            for d in BUSINESS_CREATE_CATALOG
        ]
        return s.BusinessCreateOptionsResponse(
            is_empty=True,
            active_moment_count=0,
            journey_steps=_how_it_works(),
            cards=cards,
        ).model_dump(mode="json")

    async def get_session(
        self, user_id: UUID, *, workspace_id: UUID | None = None
    ) -> dict:
        memberships = await self.workspaces.list_memberships(user_id)
        workspaces_payload = [
            s.BusinessWorkspaceSummary(**self.workspaces.map_workspace(ws, member))
            for ws, member in memberships
        ]
        resolved = await self.workspaces.resolve_selected(
            user_id, workspace_id=workspace_id, memberships=memberships
        )
        selected_summary = None
        if resolved is not None:
            selected_summary = s.BusinessWorkspaceSummary(
                **self.workspaces.map_workspace(resolved[0], resolved[1])
            )
        return s.BusinessSessionResponse(
            selected_workspace=selected_summary,
            workspaces=workspaces_payload,
            module_tiles=[
                s.BusinessModuleTile(**t) for t in self.workspaces.module_tiles()
            ],
        ).model_dump(mode="json")

    async def get_workspace_overview(self, user_id: UUID, workspace_id: UUID) -> dict:
        await self.workspaces.require_member(workspace_id, user_id)
        moments, allowed, member_count = await asyncio.gather(
            self.moments.list_business_accessible(user_id),
            self.workspaces.moment_ids_for_workspace(workspace_id),
            self.workspaces.count_active_members(workspace_id),
        )
        visible = await self._visible_moments(
            user_id,
            workspace_id=workspace_id,
            moments=moments,
            allowed_ids=allowed,
        )
        open_for_dash = sum(
            1
            for m in visible
            if (m.status or "").lower() in ("active", "configured", "draft")
            or (m.status or "").upper() in _ACTIVE_STATUSES
        )
        dash = {
            "open_moments": open_for_dash,
            "pending_approvals": 0,
            "member_count": member_count,
            "revenue_today": None,
            "cash_balance": None,
        }
        recent = [self._map_moment(m) for m in visible[:5]]
        return s.BusinessWorkspaceOverviewResponse(
            workspace_id=str(workspace_id),
            dashboard=s.BusinessDashboardSummary(**dash),
            recent_moments=recent,
        ).model_dump(mode="json")

    async def get_workspace_moments(self, user_id: UUID, workspace_id: UUID) -> dict:
        await self.workspaces.require_member(workspace_id, user_id)
        moments, allowed = await asyncio.gather(
            self.moments.list_business_accessible(user_id),
            self.workspaces.moment_ids_for_workspace(workspace_id),
        )
        visible = await self._visible_moments(
            user_id,
            workspace_id=workspace_id,
            moments=moments,
            allowed_ids=allowed,
        )
        home = self._moments_home_payload_from_moments(visible)
        pulse = self._pulse_payload_from_moments(visible)
        return s.BusinessWorkspaceMomentsResponse(
            workspace_id=str(workspace_id),
            moments_home=s.BusinessMomentsHomeResponse(**home),
            moments=[self._map_moment(m) for m in visible],
            pulse=s.BusinessPulseResponse(**pulse),
        ).model_dump(mode="json")

    async def session_bootstrap(
        self, user_id: UUID, *, workspace_id: UUID | None = None
    ) -> dict:
        """Thin composer: session chrome + inventory-derived home/pulse/dashboard (single pass)."""
        memberships = await self.workspaces.list_memberships(user_id)
        workspaces_payload = [
            s.BusinessWorkspaceSummary(**self.workspaces.map_workspace(ws, member))
            for ws, member in memberships
        ]
        resolved = await self.workspaces.resolve_selected(
            user_id, workspace_id=workspace_id, memberships=memberships
        )

        selected_summary: s.BusinessWorkspaceSummary | None = None
        ws_id: UUID | None = None
        if resolved is not None:
            ws, member = resolved
            ws_id = ws.workspace_id
            selected_summary = s.BusinessWorkspaceSummary(
                **self.workspaces.map_workspace(ws, member)
            )

        # Parallel independent reads; no write-on-GET module flip.
        if ws_id is not None:
            moments, allowed, member_count = await asyncio.gather(
                self.moments.list_business_accessible(user_id),
                self.workspaces.moment_ids_for_workspace(ws_id),
                self.workspaces.count_active_members(ws_id),
            )
            visible = await self._visible_moments(
                user_id,
                workspace_id=ws_id,
                moments=moments,
                allowed_ids=allowed,
            )
        else:
            visible = await self._visible_moments(user_id, workspace_id=None)
            member_count = 0

        pulse = self._pulse_payload_from_moments(visible)
        home = self._moments_home_payload_from_moments(visible)
        open_for_dash = sum(
            1
            for m in visible
            if (m.status or "").lower() in ("active", "configured", "draft")
            or (m.status or "").upper() in _ACTIVE_STATUSES
        )
        dashboard = s.BusinessDashboardSummary(
            open_moments=open_for_dash,
            pending_approvals=0,
            member_count=member_count,
            revenue_today=None,
            cash_balance=None,
        )
        return s.BusinessSessionBootstrapResponse(
            pulse=s.BusinessPulseResponse(**pulse),
            moments_home=s.BusinessMomentsHomeResponse(**home),
            moments=[self._map_moment(m) for m in visible],
            selected_workspace=selected_summary,
            workspaces=workspaces_payload,
            module_tiles=[
                s.BusinessModuleTile(**t) for t in self.workspaces.module_tiles()
            ],
            dashboard=dashboard,
        ).model_dump(mode="json")

    # ----- moment create / manage ---------------------------------------- #
    async def create_moment(
        self,
        user_id: UUID,
        moment_type_code: str,
        moment_name: str | None,
        *,
        title: str | None = None,
        template_id: str | None = None,
        template_version: str | int | None = "1",
        workspace_id: UUID | None = None,
    ) -> dict:
        resolved = await self._resolve_workspace(user_id, workspace_id=workspace_id)
        if resolved is None:
            # First Business use: auto-create a company workspace for the owner.
            created = await self.workspaces.create_workspace(
                user_id, name=(moment_name or title or "My Business")[:255]
            )
            ws_id = UUID(created["id"])
        else:
            ws_id = resolved[0].workspace_id
        return await self.setup.create_draft(
            user_id,
            moment_type_code=moment_type_code,
            title=title or moment_name,
            template_id=template_id,
            template_version=template_version,
            workspace_id=ws_id,
        )

    async def get_setup_state(self, user_id: UUID, moment_id: UUID) -> dict:
        return await self.setup.get_setup_state(user_id, moment_id)

    async def save_setup_draft(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        progress = body.get("progress")
        return await self.setup.save_draft(
            user_id,
            moment_id,
            answers=body.get("answers") or {},
            progress=progress if isinstance(progress, dict) else None,
            template_id=body.get("template_id"),
            template_version=body.get("template_version"),
            setup_version=body.get("setup_version"),
        )

    async def preview_setup(self, user_id: UUID, moment_id: UUID, body: dict | None = None) -> dict:
        body = body or {}
        return await self.setup.preview(
            user_id,
            moment_id,
            answers=body.get("answers"),
        )

    async def activate_setup(self, user_id: UUID, moment_id: UUID) -> dict:
        return await self.setup.activate(user_id, moment_id)

    async def setup_invite_draft(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        local_id: str,
        channel: str = "EMAIL",
    ) -> dict:
        return await self.setup.invite_draft(
            user_id, moment_id, local_id=local_id, channel=channel
        )

    async def archive_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        return await self.setup.archive(user_id, moment_id)

    async def complete_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        return await self.setup.complete(user_id, moment_id)

    async def patch_moment(
        self, user_id: UUID, moment_id: UUID, body: s.BusinessMomentUpdateRequest
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
            code = normalize_moment_type_code(moment.moment_type or "") or (
                moment.moment_type or ""
            )
            if body.status == "ACTIVE":
                await self._flip_active(user_id)
                module_state = "ACTIVE"
            else:
                await self.bootstrap.invalidate_cache(user_id)
                try:
                    from app.domains.business.projection_cache import (
                        invalidate_business_projections,
                    )

                    await invalidate_business_projections(
                        user_id,
                        moment_id,
                        moment_type=code,
                        reason=f"business_moment_{body.status.lower()}",
                    )
                except Exception:  # noqa: BLE001
                    pass
                module_state = "ACTIVE" if body.status != "ARCHIVED" else "SETUP"
            inventory = await self._inventory_for_replacement(user_id)
            exclude = moment.id if body.status == "ARCHIVED" else None
            preferred = None if body.status == "ARCHIVED" else moment.id
            repl_id, repl_type = pick_replacement_moment(
                inventory, exclude_id=exclude, preferred_id=preferred
            )
            log_lifecycle_transition(
                context_type=BUSINESS_CONTEXT,
                moment_id=moment.id,
                moment_type=code,
                action=body.status.lower(),
                previous_status=previous,
                final_status=moment.status,
                module_state=module_state,
                replacement_moment_id=repl_id,
            )
            return build_lifecycle_response(
                moment=moment,
                context_type=BUSINESS_CONTEXT,
                previous_status=previous,
                module_state=module_state,
                replacement_moment_id=repl_id,
                replacement_moment_type_code=repl_type,
            )
        moment = await self._adapter.get_model(user_id, moment_id)
        return self._map_moment(moment).model_dump(mode="json")

    # ----- cover upload --------------------------------------------------- #
    async def cover_upload_url(
        self, user_id: UUID, moment_id: UUID, content_type: str
    ) -> dict:
        from fastapi import HTTPException, status

        from app.core.storage import build_storage_path, build_upload_url

        moment = await self._require_moment(user_id, moment_id)
        storage_path = build_storage_path(f"business/covers/{moment.id}", content_type)
        try:
            upload_url = build_upload_url(storage_path)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
            ) from exc
        return s.BusinessImageUploadUrlResponse(
            upload_url=upload_url,
            storage_path=storage_path,
            token=None,
        ).model_dump(mode="json")

    async def cover_confirm(self, user_id: UUID, moment_id: UUID, storage_path: str) -> dict:
        from fastapi import HTTPException, status

        from app.core.storage import assert_storage_path_under

        moment = await self._require_moment(user_id, moment_id)
        try:
            assert_storage_path_under(storage_path, f"business/covers/{moment.id}")
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        moment.updated_at = datetime.now(timezone.utc)
        return self._map_moment(moment).model_dump(mode="json")
