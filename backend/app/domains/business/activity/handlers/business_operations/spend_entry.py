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
from app.domains.business.vendor_suggestions import spend_due_minor

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

_PAYMENT_METHODS = {"cash", "upi", "credit"}
_PAYMENT_STATUSES = {"paid_full", "paid_partial", "unpaid"}


def _normalize_payment(
    *,
    amount_minor: int,
    payment_method: str | None,
    payment_status: str | None,
    amount_paid_raw: Any,
) -> tuple[str, str, int, int]:
    method = (payment_method or "cash").strip().lower()
    if method == "online":
        method = "upi"
    if method not in _PAYMENT_METHODS:
        method = "cash"
    status = (payment_status or "paid_full").strip().lower()
    if status not in _PAYMENT_STATUSES:
        status = "paid_full"

    if status == "paid_full":
        paid = amount_minor
    elif status == "unpaid":
        paid = 0
    else:
        try:
            paid = int(amount_paid_raw) if amount_paid_raw is not None else 0
        except (TypeError, ValueError):
            paid = 0
        paid = max(0, min(paid, amount_minor))

    due = spend_due_minor(
        amount_minor=amount_minor,
        payment_status=status,
        amount_paid_minor=paid,
    )
    return method, status, paid, due


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
    amount_minor_int = int(amount_minor or 0)

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

    method, status, paid_minor, due_minor = _normalize_payment(
        amount_minor=amount_minor_int,
        payment_method=payload.get("payment_method"),
        payment_status=payload.get("payment_status"),
        amount_paid_raw=payload.get("amount_paid_minor"),
    )
    payload["payment_method"] = method
    payload["payment_status"] = status
    payload["amount_paid_minor"] = paid_minor
    payload["amount_due_minor"] = due_minor

    row = OperationsSpendEntries(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        spend_name=payload.get("title") or event.title,
        budget_category_id=budget_category_id,
        spend_category=spend_category,
        currency=currency,
        amount=safe_amount,
        amount_minor=amount_minor_int,
        exchange_rate_to_operating_currency=fx,
        amount_in_operating_currency=safe_amount * fx,
        spend_date=parse_date(payload.get("spend_date")),
        priority=payload.get("priority", "medium"),
        created_by=event.created_by,
        vendor_name=vendor,
        description=notes,
        is_voided=False,
        payment_method=method,
        payment_status=status,
        amount_paid_minor=paid_minor,
    )
    session.add(row)
    await session.flush()
    return row.spend_entry_id
