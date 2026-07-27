"""Handler: STRATEGIC_DECISION → runway_strategic_decisions."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, RunwayStrategicDecisions


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    currency = str(payload.get("currency_code") or payload.get("currency") or "INR")
    row = RunwayStrategicDecisions(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        decision_type=payload.get("decision_type", "other"),
        decision_title=payload.get("title") or event.title,
        expected_impact=payload.get("expected_impact", "neutral"),
        decision_status="active",
        created_by=event.created_by,
        decision_owner_id=UUID(payload["decision_owner_id"]) if payload.get("decision_owner_id") else None,
        description=payload.get("description"),
        amount_minor=payload.get("amount_minor"),
        currency_code=currency,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.decision_id
