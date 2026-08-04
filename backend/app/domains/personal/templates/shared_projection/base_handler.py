"""Base template projection handler with shared lifecycle and life/memory defaults."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, PermissionDeniedError, TemplateNotRegisteredError
from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.moment_engine.engine import MomentEngine
from app.domains.moment_engine.registry import get_domain_registry
from app.domains.module_states.service import ModuleStateService
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository
from app.domains.personal import app_schemas as s
from app.domains.personal.catalog import PERSONAL_CONTEXT, normalize_moment_type_code
from app.domains.personal.inventory import load_moment_inventories, sync_module_states
from app.domains.personal.personal_moment_sync import try_ensure_personal_moment
from app.domains.personal.projection.service import ProjectionService
from app.domains.personal.templates.shared_projection.life_mapper import build_life_operating_view

_ACTIVE = {"ACTIVE"}
_VISIBLE = {"DRAFT", "ACTIVE", "PAUSED", "SETUP"}


class BaseTemplateHandler:
    """Shared lifecycle + life/memory defaults; subclasses implement template-specific tabs."""

    moment_type_code: str

    def __init__(self) -> None:
        self._engine = MomentEngine()

    async def _session_deps(self, session: AsyncSession) -> dict[str, Any]:
        return {
            "session": session,
            "moments": MomentRepository(session),
            "adapter": get_domain_registry().adapter(session, PERSONAL_CONTEXT),
            "modules": ModuleStateService(session),
            "bootstrap": AppBootstrapService(session),
        }

    async def _visible_moments(
        self, session: AsyncSession, user_id: UUID
    ) -> list[MomentModel]:
        _, visible, _, _ = await load_moment_inventories(session, user_id)
        return visible

    def _moment_for_type(
        self, moments: list[MomentModel], moment_type_code: str | None = None
    ) -> MomentModel | None:
        code = normalize_moment_type_code(moment_type_code or self.moment_type_code)
        typed = [
            m
            for m in moments
            if normalize_moment_type_code(m.moment_type or "") == code
        ]
        if not typed:
            return None
        for status in ("ACTIVE", "DRAFT", "PAUSED", "SETUP"):
            for m in typed:
                if m.status == status:
                    return m
        return typed[0]

    def _resolve_moment(self, moments: list[MomentModel]) -> MomentModel | None:
        active = [m for m in moments if m.status in _ACTIVE]
        return self._moment_for_type(active) or self._moment_for_type(moments)

    def _not_registered(self, feature: str) -> TemplateNotRegisteredError:
        return TemplateNotRegisteredError(
            f"{feature} projection not registered for {self.moment_type_code}",
            code="template_not_registered",
        )

    async def _require_typed_moment(
        self,
        session: AsyncSession,
        user_id: UUID,
        moment_id: UUID,
    ) -> MomentModel:
        repo = MomentRepository(session)
        moment = await repo.get_by_user_and_id(user_id, moment_id)
        if moment is None:
            raise NotFoundError("Moment not found", code="moment_not_found")
        code = normalize_moment_type_code(moment.moment_type or "")
        expected = normalize_moment_type_code(self.moment_type_code)
        if code != expected:
            raise PermissionDeniedError(f"Moment is not a {expected} moment")
        return moment

    async def _sync_module_states(self, session: AsyncSession, user_id: UUID) -> None:
        _, visible, _, _ = await load_moment_inventories(session, user_id)
        await sync_module_states(
            session,
            user_id,
            visible_moments=visible,
            invalidate_projection=True,
        )

    async def _lifecycle_moment_response(
        self, session: AsyncSession, moment: MomentModel
    ) -> dict[str, Any]:
        from app.domains.personal.app_service import PersonalAppService

        svc = PersonalAppService(session)
        return svc._map_moment(moment).model_dump(mode="json")

    async def moments(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        raise self._not_registered("Moments")

    async def moment_detail(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        raise self._not_registered("Moments")

    async def pulse(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        raise self._not_registered("Pulse")

    async def patch_moment(
        self,
        session: AsyncSession,
        user_id: UUID,
        moment_id: UUID,
        body: s.PersonalMomentUpdateRequest,
    ) -> dict[str, Any]:
        deps = await self._session_deps(session)
        await self._require_typed_moment(session, user_id, moment_id)
        adapter = deps["adapter"]
        if body.moment_name is not None or body.moment_description is not None:
            fields: dict[str, str | None] = {}
            if body.moment_name is not None:
                fields["title"] = body.moment_name
            if body.moment_description is not None:
                fields["description"] = body.moment_description
            await self._engine.update(adapter, user_id, moment_id, **fields)
        moment = await adapter.get_model(user_id, moment_id)
        if await try_ensure_personal_moment(session, moment):
            await session.commit()
        return await self.moment_detail(session, user_id, moment_id)

    async def archive_moment(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        deps = await self._session_deps(session)
        await self._require_typed_moment(session, user_id, moment_id)
        await self._engine.archive(deps["adapter"], user_id, moment_id)
        await self._sync_module_states(session, user_id)
        moment = await deps["adapter"].get_model(user_id, moment_id)
        if await try_ensure_personal_moment(session, moment):
            await session.commit()
        return await self._lifecycle_moment_response(session, moment)

    async def delete_moment(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        from app.domains.moment_engine.lifecycle_contract import (
            build_lifecycle_response,
            pick_replacement_moment,
        )
        from app.domains.moments.purge_service import MomentPurgeService

        await self._require_typed_moment(session, user_id, moment_id)
        deps = await self._session_deps(session)
        moment_before = await deps["adapter"].get_model(user_id, moment_id)
        previous = moment_before.status
        moment = await MomentPurgeService(session).purge(
            user_id, moment_id, expected_context=PERSONAL_CONTEXT
        )
        await self._sync_module_states(session, user_id)
        await session.commit()
        all_moments, _, _, _ = await load_moment_inventories(session, user_id)
        inventory = [
            m
            for m in all_moments
            if (m.status or "").upper() not in {"ARCHIVED", "DELETED"}
        ]
        repl_id, repl_type = pick_replacement_moment(inventory, exclude_id=moment.id)
        return build_lifecycle_response(
            moment=moment,
            context_type=PERSONAL_CONTEXT,
            previous_status=previous,
            module_state="SETUP",
            replacement_moment_id=repl_id,
            replacement_moment_type_code=repl_type,
        )

    async def complete_moment(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        deps = await self._session_deps(session)
        await self._require_typed_moment(session, user_id, moment_id)
        await self._engine.complete(deps["adapter"], user_id, moment_id)
        await self._sync_module_states(session, user_id)
        moment = await deps["adapter"].get_model(user_id, moment_id)
        if await try_ensure_personal_moment(session, moment):
            await session.commit()
        return await self._lifecycle_moment_response(session, moment)

    async def life(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        visible = await self._visible_moments(session, user_id)
        moment = self._resolve_moment(visible)
        return await build_life_operating_view(
            session, user_id, moment, self.moment_type_code
        )

    async def memory(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        visible = await self._visible_moments(session, user_id)
        moment = self._resolve_moment(visible)
        return await ProjectionService(session).memory_slice(
            user_id, moment, self.moment_type_code
        )
