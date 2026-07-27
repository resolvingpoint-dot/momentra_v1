"""Shared Purchase template handler — dispatches projections and quick-add."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group.templates.shared_purchase.active_mapper import (
    map_active_life,
    map_active_memory,
    map_active_moments,
    map_active_pulse,
)
from app.domains.group.templates.shared_purchase.constants import MOMENT_TYPE
from app.domains.group.templates.shared_purchase.projection_builder import SharedPurchaseProjectionBuilder
from app.domains.group.shared_purchase_service import SharedPurchaseService


class SharedPurchaseTemplateHandler:
    moment_type = MOMENT_TYPE

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.service = SharedPurchaseService(session)
        self.builder = SharedPurchaseProjectionBuilder(session)

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
        from app.domains.group.templates.shared_purchase.quick_add import (
            build_purchase_quick_add_categories,
        )

        return {
            "moment_id": str(moment.id),
            "moment_type": MOMENT_TYPE,
            "moment_profile": ctx.profile.code,
            "categories": build_purchase_quick_add_categories(modules),
        }
