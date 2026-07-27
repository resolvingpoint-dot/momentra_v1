"""Handler: TEAM_UPDATE → team_activities."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, TeamActivities


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = TeamActivities(
        moment_id=event.business_moment_id,
        activity_title=payload.get("title") or event.title,
        category=payload.get("category", "general"),
        activity_status=payload.get("activity_status", "planned"),
        has_spend=bool(payload.get("amount_minor") or payload.get("amount")),
        priority=payload.get("priority", "medium"),
        created_by=event.created_by,
        description=payload.get("description"),
        activity_owner_id=UUID(payload["activity_owner_id"]) if payload.get("activity_owner_id") else None,
        amount=payload.get("amount"),
        vendor_name=payload.get("vendor_name"),
        event_id=event.event_id,
        amount_minor=payload.get("amount_minor"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.activity_id
