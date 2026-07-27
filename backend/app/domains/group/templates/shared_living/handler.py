"""Shared Living template handler — dispatches projections and quick-add."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group.templates.shared_living.active_mapper import (
    map_active_life,
    map_active_memory,
    map_active_moments,
    map_active_pulse,
)
from app.domains.group.templates.shared_living.constants import MOMENT_TYPE
from app.domains.group.templates.shared_living.projection_builder import SharedLivingProjectionBuilder
from app.domains.group.shared_living_service import SharedLivingService


class SharedLivingTemplateHandler:
    moment_type = MOMENT_TYPE

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.service = SharedLivingService(session)
        self.builder = SharedLivingProjectionBuilder(session)

    async def active_pulse(self, user_id: UUID, moment_id: UUID) -> dict:
        await self.service.pulse(user_id, moment_id)
        moment = await self.service._require(user_id, moment_id)
        ctx = self.builder.build_from_moment(moment)
        return map_active_pulse(ctx)

    async def active_moments(self, user_id: UUID, moment_id: UUID) -> dict:
        await self.service.moments_view(user_id, moment_id)
        moment = await self.service._require(user_id, moment_id)
        ctx = self.builder.build_from_moment(moment)
        return map_active_moments(ctx)

    async def active_memory(self, user_id: UUID, moment_id: UUID) -> dict:
        await self.service.memory_projection(user_id, moment_id)
        moment = await self.service._require(user_id, moment_id)
        ctx = self.builder.build_from_moment(moment)
        return map_active_memory(ctx)

    async def active_life_for_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        await self.service.life(user_id, moment_id)
        moment = await self.service._require(user_id, moment_id)
        ctx = self.builder.build_from_moment(moment)
        return map_active_life(ctx)

    async def quick_add_config(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self.service._require(user_id, moment_id)
        ctx = self.builder.build_from_moment(moment)
        modules = ctx.profile.quick_add_modules
        from app.domains.group.templates.shared_living.quick_add import (
            build_living_quick_add_categories,
        )

        return {
            "moment_id": str(moment.id),
            "moment_type": MOMENT_TYPE,
            "moment_profile": ctx.profile.code,
            "categories": build_living_quick_add_categories(modules),
        }
