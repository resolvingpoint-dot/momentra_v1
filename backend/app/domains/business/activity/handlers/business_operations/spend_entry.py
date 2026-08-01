"""Handler: SPEND_ENTRY → operations_spend_entries."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import minor_to_decimal, parse_date
from app.domains.business.models import (
    BusinessActivityEvents,
    BusinessOperationsBudgetCategories,
    OperationsSpendEntries,
)

_SPEND_CATEGORIES = {
    "purchase",
    "vendor_payment",
    "staff_cost",
    "utility_bill",
    "maintenance",
    "marketing_spend",
    "inventory_refill",
    "service_charge",
    "travel_expense",
    "rent",
    "other",
}


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

    budget_category_id = payload.get("budget_category_id")
    if not budget_category_id:
        result = await session.execute(
            select(BusinessOperationsBudgetCategories.budget_category_id)
            .where(
                BusinessOperationsBudgetCategories.moment_id == event.business_moment_id,
                BusinessOperationsBudgetCategories.category_status == "active",
            )
            .limit(1)
        )
        first = result.scalar_one_or_none()
        budget_category_id = first if first else None

    if budget_category_id is None:
        cat = BusinessOperationsBudgetCategories(
            moment_id=event.business_moment_id,
            category_name="General",
            allocated_budget=Decimal("0"),
            currency=currency,
        )
        session.add(cat)
        await session.flush()
        budget_category_id = cat.budget_category_id

    spend_category = str(payload.get("spend_category") or "other").lower()
    if spend_category not in _SPEND_CATEGORIES:
        spend_category = "other"

    notes = payload.get("description") or payload.get("notes")
    vendor = (payload.get("vendor_name") or "").strip() or None

    row = OperationsSpendEntries(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        spend_name=payload.get("title") or event.title,
        budget_category_id=budget_category_id,
        spend_category=spend_category,
        currency=currency,
        amount=safe_amount,
        amount_minor=int(amount_minor or 0),
        exchange_rate_to_operating_currency=fx,
        amount_in_operating_currency=safe_amount * fx,
        spend_date=parse_date(payload.get("spend_date")),
        priority=payload.get("priority", "medium"),
        created_by=event.created_by,
        vendor_name=vendor,
        description=notes,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.spend_entry_id
