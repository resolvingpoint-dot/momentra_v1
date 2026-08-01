"""Handler: VENDOR_UPDATE → operations_vendor_updates."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import parse_date
from app.domains.business.models import BusinessActivityEvents, OperationsVendorUpdates

_EVENT_TYPES = {
    "new_vendor",
    "vendor_evaluation",
    "vendor_issue",
    "contract_renewal",
    "payment_status",
    "contract_change",
    "vendor_suspension",
    "vendor_reactivation",
    "contact_update",
    "other",
}

_STATUSES = {
    "active",
    "preferred_vendor",
    "under_review",
    "on_hold",
    "blocked",
    "terminated",
}


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    event_type = str(payload.get("vendor_event_type") or "other").lower()
    if event_type not in _EVENT_TYPES:
        event_type = "other"

    status = str(payload.get("vendor_status") or "active").lower()
    # UX chips map Open/In progress/Resolved
    status_aliases = {
        "open": "active",
        "in_progress": "under_review",
        "resolved": "terminated",
    }
    status = status_aliases.get(status, status)
    if status not in _STATUSES:
        status = "active"

    notes = (payload.get("description") or "").strip()
    effective = payload.get("effective_date")
    if effective:
        eff = parse_date(effective)
        prefix = f"Effective: {eff.isoformat()}"
        notes = f"{prefix}\n{notes}".strip() if notes else prefix

    row = OperationsVendorUpdates(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        vendor_event_type=event_type,
        vendor_name=payload.get("vendor_name") or event.title,
        vendor_category=payload.get("vendor_category", "other"),
        vendor_status=status,
        impact_level=payload.get("impact_level", "medium"),
        created_by=event.created_by,
        description=notes or None,
        amount_minor=payload.get("amount_minor"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.vendor_update_id
