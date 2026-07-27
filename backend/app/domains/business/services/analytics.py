"""Business Analytics module: signals, recommended actions, health drivers,
attention items and the moment metrics rollup (read-only)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business import schemas as bs
from app.domains.business.api_schemas import BusinessAnalyticsResponse
from app.domains.business.repository import (
    BusinessAttentionItemsRepository,
    BusinessHealthDriverScoresRepository,
    BusinessMomentMetricsRepository,
    BusinessRecommendedActionsRepository,
    BusinessSignalInsightsRepository,
)
from app.domains.business.services.base import BusinessModuleService


class BusinessAnalyticsModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.signals_repo = BusinessSignalInsightsRepository(session)
        self.actions_repo = BusinessRecommendedActionsRepository(session)
        self.drivers_repo = BusinessHealthDriverScoresRepository(session)
        self.attention_repo = BusinessAttentionItemsRepository(session)
        self.metrics_repo = BusinessMomentMetricsRepository(session)

    async def analytics(self, user_id: UUID, moment_id: UUID) -> BusinessAnalyticsResponse:
        await self._access(user_id, moment_id)
        f = {"moment_id": moment_id}
        metrics = await self.metrics_repo.get_by(moment_id=moment_id)
        return BusinessAnalyticsResponse(
            metrics=bs.BusinessMomentMetricsSchema.model_validate(metrics) if metrics else None,
            signals=await self._list(self.signals_repo, bs.BusinessSignalInsightsSchema, filters={**f, "signal_status": "active"}, order_by="-generated_at", limit=15),
            recommended_actions=await self._list(self.actions_repo, bs.BusinessRecommendedActionsSchema, filters={**f, "status": "active"}, order_by="-created_at", limit=15),
            health_drivers=await self._list(self.drivers_repo, bs.BusinessHealthDriverScoresSchema, filters=f, order_by="-calculated_at", limit=25),
            attention_items=await self._list(self.attention_repo, bs.BusinessAttentionItemsSchema, filters={**f, "status": "open"}, order_by="-created_at", limit=25),
        )
