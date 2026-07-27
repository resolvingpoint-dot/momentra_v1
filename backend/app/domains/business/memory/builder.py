"""Build business memory view — allowlisted events only, no AI narrative."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domains.business.life.builder import _accessible_active_moments
from app.domains.business.memory.mapper import MEMORY_ACTION_ALLOWLIST, map_memory
from app.domains.business.models import BusinessActivityEvents, TeamIssueRisks


async def build_memory(session: AsyncSession, user_id: UUID) -> dict:
    moments = await _accessible_active_moments(session, user_id)
    if not moments:
        return map_memory([], events=[])

    moment_ids = [m.moment_id for m in moments]
    issue = aliased(TeamIssueRisks)
    events_result = await session.execute(
        select(BusinessActivityEvents, issue.resolution_status)
        .outerjoin(
            issue,
            (issue.event_id == BusinessActivityEvents.event_id)
            & (issue.is_voided.is_(False)),
        )
        .where(
            BusinessActivityEvents.business_moment_id.in_(moment_ids),
            BusinessActivityEvents.is_voided.is_(False),
            BusinessActivityEvents.action_type.in_(list(MEMORY_ACTION_ALLOWLIST)),
        )
        .order_by(BusinessActivityEvents.occurred_at.desc())
        .limit(200)
    )
    events = []
    for e, resolution_status in events_result.all():
        payload_status = None
        if isinstance(e.payload, dict):
            payload_status = e.payload.get("resolution_status") or e.payload.get("status")
        # Prefer specialty-table status for ISSUE honesty
        resolved = resolution_status or payload_status
        events.append({
            "event_id": str(e.event_id),
            "action_type": e.action_type,
            "title": e.title,
            "occurred_at": str(e.occurred_at),
            "source_moment_id": str(e.business_moment_id),
            "resolution_status": resolved,
        })
    return map_memory(moments, events=events)
