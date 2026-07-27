"""Business Memory module: learnings, patterns, snapshots, successes, wisdom.

Snapshots are workspace-scoped (no ``moment_id``); the rest key off ``moment_id``.
Read-only overview.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business import schemas as bs
from app.domains.business.api_schemas import BusinessMemoryOverviewResponse
from app.domains.business.repository import (
    BusinessMemoryLearningsRepository,
    BusinessMemoryPatternsRepository,
    BusinessMemorySnapshotsRepository,
    BusinessSuccessMemoryRepository,
    BusinessWisdomRepository,
)
from app.domains.business.services.base import BusinessModuleService


class BusinessMemoryModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.learnings_repo = BusinessMemoryLearningsRepository(session)
        self.patterns_repo = BusinessMemoryPatternsRepository(session)
        self.snapshots_repo = BusinessMemorySnapshotsRepository(session)
        self.success_repo = BusinessSuccessMemoryRepository(session)
        self.wisdom_repo = BusinessWisdomRepository(session)

    async def memory_overview(self, user_id: UUID, moment_id: UUID) -> BusinessMemoryOverviewResponse:
        moment, _member = await self._access(user_id, moment_id)
        f = {"moment_id": moment_id}
        return BusinessMemoryOverviewResponse(
            learnings=await self._list(self.learnings_repo, bs.BusinessMemoryLearningsSchema, filters={**f, "learning_status": "active"}, order_by="-created_at", limit=25),
            patterns=await self._list(self.patterns_repo, bs.BusinessMemoryPatternsSchema, filters={**f, "pattern_status": "active"}, order_by="-pattern_strength", limit=25),
            snapshots=await self._list(self.snapshots_repo, bs.BusinessMemorySnapshotsSchema, filters={"workspace_id": moment.workspace_id}, order_by="-generated_at", limit=10),
            successes=await self._list(self.success_repo, bs.BusinessSuccessMemorySchema, filters=f, order_by="-created_at", limit=25),
            wisdom=await self._list(self.wisdom_repo, bs.BusinessWisdomSchema, filters=f, order_by="-created_at", limit=25),
        )
