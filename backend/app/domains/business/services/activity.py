"""Business Activity Feed module: live feed + activity center items (read-only).

``business_live_feed.is_deleted`` is a soft-delete flag, so the repository hides
deleted rows automatically.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.repository import (
    BusinessActivityCenterItemsRepository,
    BusinessLiveFeedRepository,
)
from app.domains.business.services.base import BusinessModuleService


class BusinessActivityFeedModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.feed_repo = BusinessLiveFeedRepository(session)
        self.center_repo = BusinessActivityCenterItemsRepository(session)

    async def list_feed(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.feed_repo, bs.BusinessLiveFeedSchema,
            filters={"moment_id": moment_id}, order_by="-event_timestamp", page=page, per_page=per_page,
        )

    async def list_activity_center(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.center_repo, bs.BusinessActivityCenterItemsSchema,
            filters={"moment_id": moment_id}, order_by="-occurred_at", page=page, per_page=per_page,
        )
