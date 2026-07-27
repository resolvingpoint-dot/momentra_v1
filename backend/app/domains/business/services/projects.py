"""Business Projects module.

A "project" is a business moment of type ``project_operations``. Composes
:class:`BusinessMomentsModule` and fixes the moment type (no duplicated logic).
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.services.moments import BusinessMomentsModule

_MOMENT_TYPE = "project_operations"


class BusinessProjectsModule:
    def __init__(self, session: AsyncSession) -> None:
        self.moments = BusinessMomentsModule(session)

    async def list_projects(
        self, user_id: UUID, *, status: str | None = None, workspace_id: UUID | None = None, page: int = 1, per_page: int = 20
    ) -> Page:
        return await self.moments.list_moments(
            user_id, status=status, moment_type=_MOMENT_TYPE, workspace_id=workspace_id, page=page, per_page=per_page
        )

    async def create_project(
        self, user_id: UUID, *, moment_name: str, workspace_id: UUID | None = None, owner_name: str = "Owner"
    ) -> bs.BusinessMomentsSchema:
        return await self.moments.create_moment(
            user_id, moment_type=_MOMENT_TYPE, moment_name=moment_name, workspace_id=workspace_id, owner_name=owner_name
        )
