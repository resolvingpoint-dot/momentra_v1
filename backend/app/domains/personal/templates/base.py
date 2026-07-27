"""Protocol for personal template tab projection handlers."""
from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal import app_schemas as s


class TemplateProjectionHandler(Protocol):
    """Maps a moment type to moments / life / memory tab projections."""

    moment_type_code: str

    async def moments(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        ...

    async def moment_detail(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        ...

    async def patch_moment(
        self,
        session: AsyncSession,
        user_id: UUID,
        moment_id: UUID,
        body: s.PersonalMomentUpdateRequest,
    ) -> dict[str, Any]:
        ...

    async def archive_moment(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        ...

    async def complete_moment(
        self, session: AsyncSession, user_id: UUID, moment_id: UUID
    ) -> dict[str, Any]:
        ...

    async def life(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        ...

    async def memory(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        ...

    async def pulse(self, session: AsyncSession, user_id: UUID) -> dict[str, Any]:
        ...
