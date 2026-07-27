"""Dispatch personal template tab projections through the registry."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal import app_schemas as s
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.templates.registry import get_template_projection_registry
from app.domains.projections.projection_service import ProjectionReadService


class TemplateProjectionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._reads = ProjectionReadService(session)

    def _handler(self, moment_type: str):
        code = normalize_moment_type_code(moment_type)
        return get_template_projection_registry().resolve(code)

    async def moments(self, user_id: UUID, moment_type: str) -> dict:
        code = normalize_moment_type_code(moment_type)
        return await self._reads.get_slice(user_id, code, "moments")

    async def moment_detail(
        self, user_id: UUID, moment_type: str, moment_id: UUID
    ) -> dict:
        handler = self._handler(moment_type)
        return await handler.moment_detail(self.session, user_id, moment_id)

    async def patch_moment(
        self,
        user_id: UUID,
        moment_type: str,
        moment_id: UUID,
        body: s.PersonalMomentUpdateRequest,
    ) -> dict:
        handler = self._handler(moment_type)
        return await handler.patch_moment(self.session, user_id, moment_id, body)

    async def archive_moment(
        self, user_id: UUID, moment_type: str, moment_id: UUID
    ) -> dict:
        handler = self._handler(moment_type)
        return await handler.archive_moment(self.session, user_id, moment_id)

    async def complete_moment(
        self, user_id: UUID, moment_type: str, moment_id: UUID
    ) -> dict:
        handler = self._handler(moment_type)
        return await handler.complete_moment(self.session, user_id, moment_id)

    async def life(self, user_id: UUID, moment_type: str) -> dict:
        code = normalize_moment_type_code(moment_type)
        return await self._reads.get_slice(user_id, code, "life")

    async def memory(self, user_id: UUID, moment_type: str) -> dict:
        code = normalize_moment_type_code(moment_type)
        return await self._reads.get_slice(user_id, code, "memory")

    async def pulse(self, user_id: UUID, moment_type: str) -> dict:
        code = normalize_moment_type_code(moment_type)
        return await self._reads.get_slice(user_id, code, "pulse")
