"""Persistence helpers for personal_master_expenses."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.master_expense.models import PersonalMasterExpenses


class MasterExpenseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_client_request_id(
        self, user_id: UUID, client_request_id: UUID
    ) -> PersonalMasterExpenses | None:
        result = await self.session.execute(
            select(PersonalMasterExpenses).where(
                PersonalMasterExpenses.user_id == user_id,
                PersonalMasterExpenses.client_request_id == client_request_id,
                PersonalMasterExpenses.is_voided.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(
        self, user_id: UUID, master_expense_id: UUID
    ) -> PersonalMasterExpenses | None:
        result = await self.session.execute(
            select(PersonalMasterExpenses).where(
                PersonalMasterExpenses.user_id == user_id,
                PersonalMasterExpenses.master_expense_id == master_expense_id,
                PersonalMasterExpenses.is_voided.is_(False),
            )
        )
        return result.scalar_one_or_none()

    def add(self, row: PersonalMasterExpenses) -> PersonalMasterExpenses:
        self.session.add(row)
        return row
