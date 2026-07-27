"""Handler: EXPENSE_BURN → runway_expense_burns."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import minor_to_decimal, parse_date
from app.domains.business.models import BusinessActivityEvents, RunwayExpenseBurns


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    currency = str(payload.get("currency_code") or payload.get("currency") or "INR")
    amount_minor = payload.get("amount_minor")
    if amount_minor is not None:
        amount = minor_to_decimal(amount_minor, currency=currency)
    else:
        amount = Decimal(str(payload.get("amount", 0)))
        amount_minor = (
            int(amount * 100)
            if currency.upper() not in {"JPY", "KRW", "VND", "KWD", "BHD", "OMR"}
            else int(amount)
        )
    fx = Decimal(str(payload.get("exchange_rate_to_operating_currency", 1)))
    safe_amount = amount if amount > 0 else Decimal("0.01")

    row = RunwayExpenseBurns(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        expense_category=payload.get("expense_category", "other"),
        amount=safe_amount,
        currency=currency,
        currency_code=currency,
        amount_minor=int(amount_minor or 0),
        exchange_rate_to_operating_currency=fx,
        amount_in_operating_currency=safe_amount * fx,
        expense_date=parse_date(payload.get("expense_date")),
        priority=payload.get("priority", "medium"),
        created_by=event.created_by,
        vendor_name=payload.get("vendor_name"),
        description=payload.get("description"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.expense_id
