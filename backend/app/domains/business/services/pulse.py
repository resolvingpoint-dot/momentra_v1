"""Business Pulse module: recent pulse snapshots (read-only)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business import schemas as bs
from app.domains.business.repository import BusinessPulseSnapshotsRepository
from app.domains.business.services.base import BusinessModuleService


class BusinessPulseModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.pulse_repo = BusinessPulseSnapshotsRepository(session)

    async def get_pulse(self, user_id: UUID, moment_id: UUID, *, limit: int = 20) -> list[bs.BusinessPulseSnapshotsSchema]:
        await self._access(user_id, moment_id)
        return await self._list(
            self.pulse_repo, bs.BusinessPulseSnapshotsSchema,
            filters={"moment_id": moment_id}, order_by="-snapshot_date", limit=limit,
        )
