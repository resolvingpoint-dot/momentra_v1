"""Personal money account CRUD."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.models import PersonalAccounts, PersonalMoneyEvents
from app.domains.reference_data.catalog import get_reference_catalog


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PersonalAccountsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._catalog = get_reference_catalog()

    async def list_accounts(
        self, user_id: UUID, *, include_archived: bool = False
    ) -> list[dict[str, Any]]:
        query = select(PersonalAccounts).where(PersonalAccounts.user_id == user_id)
        if not include_archived:
            query = query.where(PersonalAccounts.is_active.is_(True))
        query = query.order_by(
            PersonalAccounts.is_default.desc(), PersonalAccounts.account_name
        )
        result = await self.session.execute(query)
        accounts = list(result.scalars().all())
        counts = await self._transaction_counts(
            user_id, [a.account_id for a in accounts]
        )
        return [self._to_dict(a, counts.get(a.account_id, 0)) for a in accounts]

    async def get_account(self, user_id: UUID, account_id: UUID) -> dict[str, Any]:
        account = await self._require_account(user_id, account_id)
        count = await self._transaction_count(user_id, account_id)
        return self._to_dict(account, count)

    async def create_account(
        self,
        user_id: UUID,
        *,
        account_name: str,
        account_type: str,
        currency_code: str = "INR",
        opening_balance: str | None = None,
        opening_balance_minor: int | None = None,
        is_primary: bool = False,
    ) -> dict[str, Any]:
        account_type_code = self._catalog.validate_code("account_types", account_type)
        currency = self._catalog.validate_currency(currency_code)

        if opening_balance_minor is not None:
            balance = self._catalog.major_from_minor(int(opening_balance_minor), currency)
        else:
            balance = Decimal(opening_balance or "0")

        if is_primary:
            await self._clear_default(user_id)

        row = PersonalAccounts(
            user_id=user_id,
            account_name=account_name[:120],
            account_type=account_type_code,
            currency_code=currency,
            opening_balance=balance,
            current_balance=balance,
            is_default=is_primary,
            is_active=True,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return self._to_dict(row, 0)

    async def patch_account(
        self,
        user_id: UUID,
        account_id: UUID,
        *,
        account_name: str | None = None,
        account_type: str | None = None,
        currency_code: str | None = None,
        current_balance_minor: int | None = None,
        is_default: bool | None = None,
    ) -> dict[str, Any]:
        account = await self._require_account(user_id, account_id)
        tx_count = await self._transaction_count(user_id, account_id)

        if account_name is not None:
            account.account_name = account_name.strip()[:120]
        if account_type is not None:
            account.account_type = self._catalog.validate_code(
                "account_types", account_type
            )
        if currency_code is not None:
            if tx_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="currency_code cannot be changed after transactions exist",
                )
            account.currency_code = self._catalog.validate_currency(currency_code)
        if current_balance_minor is not None:
            account.current_balance = self._catalog.major_from_minor(
                int(current_balance_minor), account.currency_code
            )
        if is_default is True:
            await self._clear_default(user_id)
            account.is_default = True
        elif is_default is False and account.is_default:
            account.is_default = False

        account.updated_at = _now()
        await self.session.commit()
        await self.session.refresh(account)
        return self._to_dict(account, tx_count)

    async def archive_account(self, user_id: UUID, account_id: UUID) -> dict[str, Any]:
        account = await self._require_account(user_id, account_id)
        account.is_active = False
        if account.is_default:
            account.is_default = False
        account.updated_at = _now()
        await self.session.commit()
        await self.session.refresh(account)
        count = await self._transaction_count(user_id, account_id)
        return self._to_dict(account, count)

    async def delete_account(self, user_id: UUID, account_id: UUID) -> None:
        account = await self._require_account(user_id, account_id)
        tx_count = await self._transaction_count(user_id, account_id)
        if tx_count > 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Account with transactions cannot be deleted; archive instead",
            )
        await self.session.delete(account)
        await self.session.commit()

    async def _require_account(
        self, user_id: UUID, account_id: UUID
    ) -> PersonalAccounts:
        result = await self.session.execute(
            select(PersonalAccounts).where(
                PersonalAccounts.account_id == account_id,
                PersonalAccounts.user_id == user_id,
            )
        )
        account = result.scalar_one_or_none()
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        return account

    async def _clear_default(self, user_id: UUID) -> None:
        result = await self.session.execute(
            select(PersonalAccounts).where(
                PersonalAccounts.user_id == user_id,
                PersonalAccounts.is_default.is_(True),
            )
        )
        for existing in result.scalars().all():
            existing.is_default = False

    async def _transaction_count(self, user_id: UUID, account_id: UUID) -> int:
        counts = await self._transaction_counts(user_id, [account_id])
        return counts.get(account_id, 0)

    async def _transaction_counts(
        self, user_id: UUID, account_ids: list[UUID]
    ) -> dict[UUID, int]:
        if not account_ids:
            return {}
        result = await self.session.execute(
            select(PersonalMoneyEvents.account_id, func.count())
            .where(
                PersonalMoneyEvents.user_id == user_id,
                PersonalMoneyEvents.account_id.in_(account_ids),
                PersonalMoneyEvents.is_voided.is_(False),
            )
            .group_by(PersonalMoneyEvents.account_id)
        )
        return {row[0]: int(row[1]) for row in result.all()}

    def _balance_minor(self, account: PersonalAccounts, field: str) -> int:
        value = getattr(account, field, None) or Decimal("0")
        return self._catalog.minor_from_major_string(str(value), account.currency_code)

    def _type_label(self, account_type: str) -> str:
        for row in self._catalog.get("account_types", active_only=True):
            if row["code"] == account_type:
                return str(row["label"])
        return account_type.replace("_", " ").title()

    def _to_dict(self, account: PersonalAccounts, transaction_count: int) -> dict[str, Any]:
        opening_minor = self._balance_minor(account, "opening_balance")
        current_minor = self._balance_minor(account, "current_balance")
        return {
            "id": str(account.account_id),
            "account_id": str(account.account_id),
            "account_name": account.account_name,
            "account_type": account.account_type,
            "account_type_label": self._type_label(account.account_type),
            "currency_code": account.currency_code,
            "current_balance": str(account.current_balance),
            "current_balance_minor": current_minor,
            "opening_balance_minor": opening_minor,
            "is_default": account.is_default,
            "is_primary": account.is_default,
            "is_archived": not account.is_active,
            "transaction_count": transaction_count,
            "created_at": account.created_at.isoformat() if account.created_at else None,
            "updated_at": account.updated_at.isoformat() if account.updated_at else None,
        }
