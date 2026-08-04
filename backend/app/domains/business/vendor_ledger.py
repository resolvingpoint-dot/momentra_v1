"""Vendor spend ledger for Business Operations Moments detail sheet."""
from __future__ import annotations

from calendar import month_name
from collections import defaultdict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessOperationsSetup, OperationsSpendEntries
from app.domains.business.vendor_suggestions import spend_due_minor

_LEDGER_CAP = 100


def _month_key(d) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def _month_label(d) -> str:
    return f"{month_name[d.month]} {d.year}"


def _paid_minor(row: OperationsSpendEntries, amount_minor: int) -> int:
    status = (row.payment_status or "paid_full").strip().lower()
    if status == "paid_full":
        return amount_minor
    if status == "unpaid":
        return 0
    try:
        paid = int(row.amount_paid_minor or 0)
    except (TypeError, ValueError):
        paid = 0
    return max(0, min(paid, amount_minor))


async def build_vendor_ledger(
    session: AsyncSession,
    moment_id: UUID,
    vendor_name: str,
) -> dict:
    """Monthly spend ledger for one vendor on a Business Operations moment."""
    name = (vendor_name or "").strip()
    if not name:
        return {
            "vendor_name": "",
            "currency_code": "INR",
            "balance_due_minor": 0,
            "total_spent_minor": 0,
            "total_paid_minor": 0,
            "months": [],
        }

    currency_row = (
        await session.execute(
            select(BusinessOperationsSetup.operating_currency).where(
                BusinessOperationsSetup.moment_id == moment_id
            )
        )
    ).scalar_one_or_none()
    currency = (currency_row or "INR").strip().upper() or "INR"

    rows = (
        await session.execute(
            select(OperationsSpendEntries)
            .where(
                OperationsSpendEntries.moment_id == moment_id,
                OperationsSpendEntries.archived_at.is_(None),
                OperationsSpendEntries.is_voided.is_(False),
                OperationsSpendEntries.vendor_name.is_not(None),
                func.lower(func.trim(OperationsSpendEntries.vendor_name)) == name.casefold(),
            )
            .order_by(
                OperationsSpendEntries.spend_date.desc(),
                OperationsSpendEntries.created_at.desc(),
            )
            .limit(_LEDGER_CAP)
        )
    ).scalars().all()

    display_name = name
    if rows:
        for row in rows:
            vn = (row.vendor_name or "").strip()
            if vn:
                display_name = vn
                break
        if rows[0].currency:
            currency = (rows[0].currency or currency).strip().upper() or currency

    months_map: dict[str, dict] = {}
    total_spent = 0
    total_paid = 0
    total_due = 0

    for row in rows:
        amount = max(0, int(row.amount_minor or 0))
        paid = _paid_minor(row, amount)
        due = spend_due_minor(
            amount_minor=amount,
            payment_status=row.payment_status,
            amount_paid_minor=paid,
        )
        total_spent += amount
        total_paid += paid
        total_due += due

        spend_date = row.spend_date
        key = _month_key(spend_date)
        if key not in months_map:
            months_map[key] = {
                "month": key,
                "label": _month_label(spend_date),
                "month_spent_minor": 0,
                "month_paid_minor": 0,
                "month_due_minor": 0,
                "items": [],
                "_sort": (spend_date.year, spend_date.month),
            }
        bucket = months_map[key]
        bucket["month_spent_minor"] += amount
        bucket["month_paid_minor"] += paid
        bucket["month_due_minor"] += due
        occurred = row.created_at.isoformat() if row.created_at else f"{spend_date.isoformat()}T00:00:00"
        bucket["items"].append(
            {
                "spend_entry_id": str(row.spend_entry_id),
                "title": row.spend_name or "Spend",
                "amount_minor": amount,
                "amount_paid_minor": paid,
                "amount_due_minor": due,
                "payment_status": (row.payment_status or "paid_full").strip().lower(),
                "payment_method": (row.payment_method or "cash").strip().lower(),
                "spend_date": spend_date.isoformat(),
                "occurred_at": occurred,
            }
        )

    months = sorted(months_map.values(), key=lambda m: m["_sort"], reverse=True)
    for m in months:
        m.pop("_sort", None)

    return {
        "vendor_name": display_name,
        "currency_code": currency,
        "balance_due_minor": total_due,
        "total_spent_minor": total_spent,
        "total_paid_minor": total_paid,
        "months": months,
    }
