"""Handler: ISSUE → team_issue_risks."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, TeamIssueRisks


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = TeamIssueRisks(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        issue_title=payload.get("title") or event.title,
        issue_type=payload.get("issue_type", "general"),
        severity=payload.get("severity", "medium"),
        current_impact=payload.get("current_impact", "none_yet"),
        resolution_status="open",
        created_by=event.created_by,
        owner_id=UUID(payload["owner_id"]) if payload.get("owner_id") else None,
        description=payload.get("description"),
        amount_minor=payload.get("amount_minor"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.issue_id
