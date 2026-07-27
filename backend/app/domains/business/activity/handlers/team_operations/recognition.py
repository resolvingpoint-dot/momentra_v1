"""Handler: RECOGNITION → team_recognitions."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, TeamRecognitions


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = TeamRecognitions(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        title=payload.get("title") or event.title,
        recipient_member_id=UUID(payload["recipient_member_id"]) if payload.get("recipient_member_id") else None,
        recognition_type=payload.get("recognition_type", "kudos"),
        notes=payload.get("notes"),
        created_by=event.created_by,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.recognition_id
