"""Business Transactions module: operations spend + runway cash inflows + burns.

Multi-currency rows store an operating-currency amount; when the caller omits it
we derive ``amount * exchange_rate``.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.repository import (
    OperationsSpendEntriesRepository,
    RunwayCashInflowsRepository,
    RunwayExpenseBurnsRepository,
)
from app.domains.business.services.base import BusinessModuleService


def _with_operating_amount(data: dict[str, Any]) -> dict[str, Any]:
    rate = data.get("exchange_rate_to_operating_currency") or Decimal(1)
    data["exchange_rate_to_operating_currency"] = rate
    if data.get("amount_in_operating_currency") is None:
        data["amount_in_operating_currency"] = Decimal(str(data["amount"])) * Decimal(str(rate))
    return data


class BusinessTransactionsModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.spend_repo = OperationsSpendEntriesRepository(session)
        self.inflow_repo = RunwayCashInflowsRepository(session)
        self.burn_repo = RunwayExpenseBurnsRepository(session)

    # -------------------------- spend entries ------------------------ #
    async def list_spend(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.spend_repo, bs.OperationsSpendEntriesSchema,
            filters={"moment_id": moment_id}, order_by="-spend_date", page=page, per_page=per_page,
        )

    async def create_spend(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.OperationsSpendEntriesSchema:
        await self._require_member(user_id, moment_id)
        payload = _with_operating_amount(dict(data))
        payload.update({"moment_id": moment_id, "created_by": user_id})
        schema = await self._created(self.spend_repo, bs.OperationsSpendEntriesSchema, payload)
        await self.session.commit()
        return schema

    # -------------------------- cash inflows ------------------------- #
    async def list_inflows(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.inflow_repo, bs.RunwayCashInflowsSchema,
            filters={"moment_id": moment_id}, order_by="-inflow_date", page=page, per_page=per_page,
        )

    async def create_inflow(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.RunwayCashInflowsSchema:
        await self._require_member(user_id, moment_id)
        payload = _with_operating_amount(dict(data))
        payload.update({"moment_id": moment_id, "created_by": user_id})
        schema = await self._created(self.inflow_repo, bs.RunwayCashInflowsSchema, payload)
        await self.session.commit()
        return schema

    # ------------------------- expense burns ------------------------- #
    async def list_burns(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.burn_repo, bs.RunwayExpenseBurnsSchema,
            filters={"moment_id": moment_id}, order_by="-expense_date", page=page, per_page=per_page,
        )

    async def create_burn(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.RunwayExpenseBurnsSchema:
        await self._require_member(user_id, moment_id)
        payload = _with_operating_amount(dict(data))
        payload.update({"moment_id": moment_id, "created_by": user_id})
        schema = await self._created(self.burn_repo, bs.RunwayExpenseBurnsSchema, payload)
        await self.session.commit()
        return schema
