"""Life Operations template projection handler (reference vertical)."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.accounts_service import PersonalAccountsService
from app.domains.personal.projection.service import ProjectionService
from app.domains.personal.templates.shared_projection.base_handler import BaseTemplateHandler

_LIFE_OPS = "LIFE_OPERATIONS"


class LifeOperationsTemplateHandler(BaseTemplateHandler):
    moment_type_code = _LIFE_OPS

    async def _accounts_summary(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        accounts_svc = PersonalAccountsService(session)
        accounts = await accounts_svc.list_accounts(user_id)
        active = [a for a in accounts if a.get("is_active", True)]
        return {
            "total_accounts": len(accounts),
            "active_accounts": len(active),
            "accounts": active[:6],
        }

    async def moments(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        visible = await self._visible_moments(session, user_id)
        moment = self._moment_for_type(visible, _LIFE_OPS)
        accounts_summary = await self._accounts_summary(session, user_id)
        return await ProjectionService(session).moment_slice(
            user_id, moment, _LIFE_OPS, accounts_summary=accounts_summary
        )

    async def moment_detail(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        moment = await self._require_typed_moment(session, user_id, moment_id)
        accounts_summary = await self._accounts_summary(session, user_id)
        return await ProjectionService(session).moment_slice(
            user_id, moment, _LIFE_OPS, accounts_summary=accounts_summary
        )

    async def pulse(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        from app.domains.personal.catalog import moment_type_name
        from app.domains.personal.life_operations.pulse_mapper import (
            build_life_operations_pulse,
        )

        visible = await self._visible_moments(session, user_id)
        moment = self._moment_for_type(visible, _LIFE_OPS)
        if moment is None or moment.status != "ACTIVE":
            return {"moment_type_code": _LIFE_OPS, "status": "EMPTY", "pulse": None}
        block = await build_life_operations_pulse(
            session,
            user_id,
            moment.id,
            moment.title or moment_type_name(_LIFE_OPS),
        )
        return {"moment_type_code": _LIFE_OPS, "status": "ACTIVE", "pulse": block}
