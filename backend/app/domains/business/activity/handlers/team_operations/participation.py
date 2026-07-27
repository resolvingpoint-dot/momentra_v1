"""Handler: PARTICIPATION → team_participation."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, TeamParticipation


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = TeamParticipation(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        title=payload.get("title") or event.title,
        member_id=UUID(payload["member_id"]) if payload.get("member_id") else None,
        participation_type=payload.get("participation_type", "check_in"),
        notes=payload.get("notes"),
        created_by=event.created_by,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.participation_id
