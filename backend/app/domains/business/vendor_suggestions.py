"""Moment-scoped vendor suggestions with optional outstanding due amounts."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import OperationsSpendEntries, OperationsVendorUpdates

_VENDOR_CAP = 50


def spend_due_minor(
    *,
    amount_minor: int | None,
    payment_status: str | None,
    amount_paid_minor: int | None,
) -> int:
    total = max(0, int(amount_minor or 0))
    status = (payment_status or "paid_full").strip().lower()
    if status == "paid_full":
        return 0
    if status == "unpaid":
        return total
    paid = max(0, int(amount_paid_minor or 0))
    return max(0, total - min(paid, total))


async def list_moment_vendors(session: AsyncSession, moment_id: UUID) -> list[dict]:
    """Distinct vendor names for a moment, with aggregated due_minor from spends."""
    due_by_name: dict[str, int] = {}
    order: list[str] = []

    spend_rows = (
        await session.execute(
            select(
                OperationsSpendEntries.vendor_name,
                OperationsSpendEntries.amount_minor,
                OperationsSpendEntries.payment_status,
                OperationsSpendEntries.amount_paid_minor,
                OperationsSpendEntries.created_at,
            )
            .where(
                OperationsSpendEntries.moment_id == moment_id,
                OperationsSpendEntries.archived_at.is_(None),
                OperationsSpendEntries.is_voided.is_(False),
                OperationsSpendEntries.vendor_name.is_not(None),
            )
            .order_by(OperationsSpendEntries.created_at.desc())
        )
    ).all()

    for row in spend_rows:
        name = (row.vendor_name or "").strip()
        if not name:
            continue
        key = name.casefold()
        display = next((n for n in order if n.casefold() == key), None)
        if display is None:
            order.append(name)
            display = name
            due_by_name[display] = 0
        due_by_name[display] = due_by_name.get(display, 0) + spend_due_minor(
            amount_minor=row.amount_minor,
            payment_status=row.payment_status,
            amount_paid_minor=row.amount_paid_minor,
        )

    vendor_rows = (
        await session.execute(
            select(OperationsVendorUpdates.vendor_name, OperationsVendorUpdates.created_at)
            .where(
                OperationsVendorUpdates.moment_id == moment_id,
                OperationsVendorUpdates.archived_at.is_(None),
                OperationsVendorUpdates.is_voided.is_(False),
            )
            .order_by(OperationsVendorUpdates.created_at.desc())
        )
    ).all()

    for row in vendor_rows:
        name = (row.vendor_name or "").strip()
        if not name:
            continue
        key = name.casefold()
        if any(n.casefold() == key for n in order):
            continue
        order.append(name)
        due_by_name[name] = 0

    vendors: list[dict] = []
    for name in order[:_VENDOR_CAP]:
        due = int(due_by_name.get(name, 0) or 0)
        if due <= 0:
            label = name
        elif due % 100 == 0:
            label = f"{name} · Due ₹{due // 100:,}"
        else:
            label = f"{name} · Due ₹{due / 100:,.2f}"
        item: dict = {"value": name, "label": label}
        if due > 0:
            item["due_minor"] = due
        vendors.append(item)
    return vendors


def vendor_due_lookup(vendors: list[dict]) -> dict[str, int]:
    """casefold(vendor name) → aggregated due_minor from list_moment_vendors rows."""
    out: dict[str, int] = {}
    for v in vendors:
        name = str(v.get("value") or "").strip()
        if not name:
            continue
        out[name.casefold()] = int(v.get("due_minor") or 0)
    return out


def attach_vendor_due_minor(
    items: list[dict],
    due_by_name: dict[str, int] | None,
    *,
    name_keys: list[str] | None = None,
) -> list[dict]:
    """Copy event items and set due_minor when a name key matches outstanding due.

    ``name_keys`` lists field names to try on each item (default: title only).
    """
    if not due_by_name:
        return list(items)
    keys = name_keys or ["title"]
    enriched: list[dict] = []
    for item in items:
        row = dict(item)
        due = 0
        for key in keys:
            name = str(row.get(key) or "").strip()
            if not name:
                continue
            due = int(due_by_name.get(name.casefold(), 0) or 0)
            if due > 0:
                break
        if due > 0:
            row["due_minor"] = due
        enriched.append(row)
    return enriched


def vendor_timeline_items(
    activities: list[dict],
    due_by_name: dict[str, int] | None,
    *,
    vendor_action_types: set[str] | None = None,
) -> list[dict]:
    """Build vendor timeline event items with due_minor from spend aggregation."""
    types = vendor_action_types or {"VENDOR_UPDATE"}
    items: list[dict] = []
    for a in activities:
        if (a.get("action_type") or "") not in types:
            continue
        item = {
            "event_id": str(a.get("event_id") or ""),
            "action_type": a.get("action_type", ""),
            "title": a.get("title") or "",
            "subtitle": a.get("subtitle"),
            "occurred_at": str(a.get("occurred_at") or ""),
            "source_moment_id": a.get("source_moment_id"),
        }
        payload = a.get("payload") if isinstance(a.get("payload"), dict) else {}
        names = [
            str(item.get("title") or "").strip(),
            str(payload.get("vendor_name") or "").strip(),
        ]
        due = 0
        if due_by_name:
            for name in names:
                if not name:
                    continue
                due = int(due_by_name.get(name.casefold(), 0) or 0)
                if due > 0:
                    break
        if due > 0:
            item["due_minor"] = due
        items.append(item)
    return items
