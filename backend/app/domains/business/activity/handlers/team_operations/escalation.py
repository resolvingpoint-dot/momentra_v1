"""Handler: ESCALATION → team_escalations."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, TeamEscalations


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = TeamEscalations(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        title=payload.get("title") or event.title,
        severity=payload.get("severity", "medium"),
        status="open",
        notes=payload.get("notes"),
        created_by=event.created_by,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.escalation_id
