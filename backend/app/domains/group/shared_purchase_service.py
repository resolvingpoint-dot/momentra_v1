"""Canonical Shared Purchase service — projection + activity driven."""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group.activity.engine import GroupActivityEngine
from app.domains.group.projection_cache import invalidate_group_projections
from app.domains.group.projection_read import cached_or_build
from app.domains.group.templates.shared_purchase.constants import MOMENT_TYPE
from app.domains.group.templates.shared_purchase.life_mapper import build_life
from app.domains.group.templates.shared_purchase.live_hub_mapper import build_live_hub
from app.domains.group.templates.shared_purchase.memory_mapper import build_memory_projection
from app.domains.group.templates.shared_purchase.moments_mapper import build_moments
from app.domains.group.templates.shared_purchase.projection_builder import SharedPurchaseProjectionBuilder
from app.domains.group.templates.shared_purchase.pulse_mapper import build_pulse
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository


class SharedPurchaseService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.builder = SharedPurchaseProjectionBuilder(session)
        self.activity = GroupActivityEngine(session)

    async def _require(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        from app.domains.group.access import require_group_moment_access

        return await require_group_moment_access(self.session, user_id, moment_id)

    async def _cached_or_build(
        self,
        user_id: UUID,
        moment_id: UUID,
        slice_type: str,
        builder_fn,
        *,
        force_refresh: bool = False,
    ) -> dict:
        async def build() -> dict:
            ctx = await self.builder.build(user_id, moment_id)
            return builder_fn(ctx)

        return await cached_or_build(
            user_id,
            moment_id,
            slice_type,
            build,
            moment_type=MOMENT_TYPE,
            force_refresh=force_refresh,
        )

    async def live_hub(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        await self._require(user_id, moment_id)
        return await self._cached_or_build(
            user_id, moment_id, "live_hub", build_live_hub, force_refresh=force_refresh
        )

    async def pulse(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        await self._require(user_id, moment_id)
        return await self._cached_or_build(
            user_id, moment_id, "pulse", build_pulse, force_refresh=force_refresh
        )

    async def moments_view(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        await self._require(user_id, moment_id)
        return await self._cached_or_build(
            user_id, moment_id, "moments", build_moments, force_refresh=force_refresh
        )

    async def life(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        await self._require(user_id, moment_id)
        return await self._cached_or_build(
            user_id, moment_id, "life", build_life, force_refresh=force_refresh
        )

    async def memory_projection(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        await self._require(user_id, moment_id)
        return await self._cached_or_build(
            user_id,
            moment_id,
            "memory",
            build_memory_projection,
            force_refresh=force_refresh,
        )

    async def list_activity(self, user_id: UUID, moment_id: UUID) -> list[dict]:
        return await self.activity.list_timeline(user_id, moment_id)

    async def invalidate(self, user_id: UUID, moment_id: UUID, *, reason: str = "manual") -> None:
        moment = await self._require(user_id, moment_id)
        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=MOMENT_TYPE,
            reason=reason,
            session=self.session,
            moment=moment,
        )
