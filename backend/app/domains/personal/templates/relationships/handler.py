"""Relationships template projection handler."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.projection.cache import invalidate_projection_cache
from app.domains.personal.projection.service import ProjectionService
from app.domains.personal.templates.relationships.constants import MOMENT_TYPE_CODE
from app.domains.personal.templates.relationships.memory_mapper import (
    build_relationships_memory,
)
from app.domains.personal.templates.relationships.moments_mapper import (
    build_relationships_moments,
)
from app.domains.personal.templates.relationships.projection_builder import (
    RelationshipsProjectionBuilder,
)
from app.domains.personal.templates.relationships.pulse_mapper import (
    build_relationships_pulse,
)
from app.domains.personal.templates.shared_projection.base_handler import BaseTemplateHandler

_RS = MOMENT_TYPE_CODE
_EMPTY_ACCOUNTS = {"total_accounts": 0, "active_accounts": 0, "accounts": []}


class RelationshipsTemplateHandler(BaseTemplateHandler):
    moment_type_code = _RS

    async def _build_context(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID | None = None
    ):
        visible = await self._visible_moments(session, user_id)
        moment = (
            await self._require_typed_moment(session, user_id, moment_id)
            if moment_id
            else self._moment_for_type(visible, _RS)
        )
        return await RelationshipsProjectionBuilder.build(session, user_id, moment)

    async def moments(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        ctx = await self._build_context(session, user_id)
        base = build_relationships_moments(ctx, accounts_summary=_EMPTY_ACCOUNTS)
        if ctx.moment is None:
            return base
        cached = await ProjectionService(session).get_cached_context(user_id)
        return {**ProjectionService(session).envelope(cached), **base}

    async def moment_detail(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        ctx = await self._build_context(session, user_id, moment_id)
        base = build_relationships_moments(ctx, accounts_summary=_EMPTY_ACCOUNTS)
        cached = await ProjectionService(session).get_cached_context(user_id)
        return {**ProjectionService(session).envelope(cached), **base}

    async def pulse(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        ctx = await self._build_context(session, user_id)
        if ctx.moment is None or ctx.moment.status != "ACTIVE":
            return {"moment_type_code": _RS, "status": "EMPTY", "pulse": None}
        block = build_relationships_pulse(ctx)
        cached = await ProjectionService(session).get_cached_context(user_id)
        return {
            **ProjectionService(session).envelope(cached),
            "moment_type_code": _RS,
            "status": "ACTIVE",
            "pulse": block,
        }

    async def memory(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        ctx = await self._build_context(session, user_id)
        cached = await ProjectionService(session).get_cached_context(user_id)
        if ctx.moment is None:
            return {
                **ProjectionService(session).envelope(cached),
                "moment_type_code": _RS,
                "status": "EMPTY",
                "memory_projection": None,
            }
        status = "ACTIVE" if ctx.moment.status == "ACTIVE" else "SETUP"
        projection = build_relationships_memory(ctx) if status == "ACTIVE" else None
        return {
            **ProjectionService(session).envelope(cached),
            "moment_type_code": _RS,
            "status": status,
            "memory_projection": projection,
        }

    async def archive_moment(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        result = await super().archive_moment(session, user_id, moment_id)
        invalidate_projection_cache(user_id)
        return result

    async def complete_moment(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        result = await super().complete_moment(session, user_id, moment_id)
        invalidate_projection_cache(user_id)
        return result
