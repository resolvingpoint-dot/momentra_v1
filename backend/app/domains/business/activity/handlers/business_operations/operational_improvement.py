"""Handler: OPERATIONAL_IMPROVEMENT → operations_improvements."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import parse_date
from app.domains.business.models import BusinessActivityEvents, OperationsImprovements


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    row = OperationsImprovements(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        improvement_type=payload.get("improvement_type", "process_improvement"),
        improvement_title=payload.get("title") or event.title,
        impact_area=payload.get("impact_area", "operations"),
        expected_impact=payload.get("expected_impact", "improve_speed"),
        effective_date=parse_date(payload.get("effective_date")),
        follow_up_required=bool(payload.get("follow_up_required")),
        improvement_status="recorded",
        created_by=event.created_by,
        owner_id=UUID(payload["owner_id"]) if payload.get("owner_id") else None,
        description=payload.get("description"),
        amount_minor=payload.get("amount_minor"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.improvement_id
