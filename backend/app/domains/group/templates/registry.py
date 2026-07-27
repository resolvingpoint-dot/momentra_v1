"""Group template handler registry."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import shared_catalog as cat
from app.domains.group.shared_experience_service import SharedExperienceService
from app.domains.group.templates.shared_experience.active_mapper import (
    map_active_life,
    map_active_memory,
    map_active_moments,
    map_active_pulse,
)
from app.domains.group.templates.shared_experience.projection_builder import SharedExperienceProjectionBuilder
from app.domains.group.templates.shared_living.handler import SharedLivingTemplateHandler
from app.domains.group.templates.shared_purchase.handler import SharedPurchaseTemplateHandler
from app.domains.moments.repository import MomentRepository


class GroupTemplateRegistry:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.experience = SharedExperienceService(session)
        self.experience_builder = SharedExperienceProjectionBuilder(session)
        self.purchase = SharedPurchaseTemplateHandler(session)
        self.living = SharedLivingTemplateHandler(session)

    async def _moment_type(self, user_id: UUID, moment_id: UUID) -> str:
        from fastapi import HTTPException

        from app.domains.group.access import require_group_moment_access

        try:
            moment = await require_group_moment_access(self.session, user_id, moment_id)
        except HTTPException:
            return ""
        return moment.moment_type or ""

    async def active_pulse(self, user_id: UUID, moment_id: UUID) -> dict:
        code = await self._moment_type(user_id, moment_id)
        if code == cat.PURCHASE:
            return await self.purchase.active_pulse(user_id, moment_id)
        if code == cat.LIVING:
            return await self.living.active_pulse(user_id, moment_id)
        if code == cat.EXPERIENCE:
            await self.experience.pulse(user_id, moment_id)
            moment = await self.experience._require(user_id, moment_id)
            ctx = self.experience_builder.build_from_moment(moment)
            return map_active_pulse(ctx)
        return {}

    async def active_moments(self, user_id: UUID, moment_id: UUID) -> dict:
        code = await self._moment_type(user_id, moment_id)
        if code == cat.PURCHASE:
            return await self.purchase.active_moments(user_id, moment_id)
        if code == cat.LIVING:
            return await self.living.active_moments(user_id, moment_id)
        if code == cat.EXPERIENCE:
            await self.experience.moments_view(user_id, moment_id)
            moment = await self.experience._require(user_id, moment_id)
            ctx = self.experience_builder.build_from_moment(moment)
            return map_active_moments(ctx)
        return {}

    async def active_memory(self, user_id: UUID, moment_id: UUID) -> dict:
        code = await self._moment_type(user_id, moment_id)
        if code == cat.PURCHASE:
            return await self.purchase.active_memory(user_id, moment_id)
        if code == cat.LIVING:
            return await self.living.active_memory(user_id, moment_id)
        if code == cat.EXPERIENCE:
            await self.experience.memory_projection(user_id, moment_id)
            moment = await self.experience._require(user_id, moment_id)
            ctx = self.experience_builder.build_from_moment(moment)
            return map_active_memory(ctx)
        return {}

    async def active_life_for_moment(self, user_id: UUID, moment_id: UUID) -> dict:
        code = await self._moment_type(user_id, moment_id)
        if code == cat.PURCHASE:
            return await self.purchase.active_life_for_moment(user_id, moment_id)
        if code == cat.LIVING:
            return await self.living.active_life_for_moment(user_id, moment_id)
        if code == cat.EXPERIENCE:
            moment = await self.experience._require(user_id, moment_id)
            ctx = self.experience_builder.build_from_moment(moment)
            return map_active_life(ctx)
        return {}

    async def quick_add_config(self, user_id: UUID, moment_id: UUID) -> dict:
        code = await self._moment_type(user_id, moment_id)
        if code == cat.PURCHASE:
            return await self.purchase.quick_add_config(user_id, moment_id)
        if code == cat.LIVING:
            return await self.living.quick_add_config(user_id, moment_id)
        if code == cat.EXPERIENCE:
            moment = await self.experience._require(user_id, moment_id)
            ctx = self.experience_builder.build_from_moment(moment)
            modules = ctx.experience_type.quick_add_modules
            return {
                "moment_id": str(moment.id),
                "moment_type": code,
                "moment_profile": ctx.experience_type.code,
                "categories": [
                    {"id": m.lower(), "label": m.replace("_", " ").title(), "modules": [m]}
                    for m in modules
                ],
            }
        return {"moment_id": str(moment_id), "moment_type": code, "categories": []}
