"""Handler: MEETING → team_meetings."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, TeamMeetings


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = TeamMeetings(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        title=payload.get("title") or event.title,
        meeting_at=payload.get("meeting_at"),
        attendees=payload.get("attendees"),
        notes=payload.get("notes"),
        created_by=event.created_by,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.meeting_id
