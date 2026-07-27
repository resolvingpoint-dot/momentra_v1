"""Handler: RUNWAY_RISK → runway_risks."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, RunwayRisks


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    currency = str(payload.get("currency_code") or payload.get("currency") or "INR")
    row = RunwayRisks(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        risk_title=payload.get("title") or event.title,
        risk_type=payload.get("risk_type", "other"),
        severity=payload.get("severity", "medium"),
        expected_impact=payload.get("expected_impact", "1_3_months"),
        risk_status="open",
        adjustment_required=bool(payload.get("adjustment_required")),
        created_by=event.created_by,
        owner_id=UUID(payload["owner_id"]) if payload.get("owner_id") else None,
        description=payload.get("description"),
        amount_minor=payload.get("amount_minor"),
        currency_code=currency,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.risk_id
