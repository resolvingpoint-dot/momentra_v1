"""Handler: MEMBER_UPDATE → team_member_updates."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, TeamMemberUpdates


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = TeamMemberUpdates(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        title=payload.get("title") or event.title,
        member_id=UUID(payload["member_id"]) if payload.get("member_id") else None,
        update_kind=payload.get("update_kind", "status"),
        notes=payload.get("notes"),
        created_by=event.created_by,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.member_update_id
