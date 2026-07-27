"""Handler: VENDOR_UPDATE → operations_vendor_updates."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, OperationsVendorUpdates


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = OperationsVendorUpdates(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        vendor_event_type=payload.get("vendor_event_type", "other"),
        vendor_name=payload.get("vendor_name") or event.title,
        vendor_category=payload.get("vendor_category", "other"),
        vendor_status=payload.get("vendor_status", "active"),
        impact_level=payload.get("impact_level", "medium"),
        created_by=event.created_by,
        description=payload.get("description"),
        amount_minor=payload.get("amount_minor"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.vendor_update_id
