"""Handler: FINANCIAL_UPDATE → runway_financial_updates."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents, RunwayFinancialUpdates


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    from app.domains.business.activity.handlers._helpers import minor_to_decimal

    currency = str(payload.get("currency_code") or payload.get("currency") or "INR")
    amount_minor = payload.get("amount_minor")
    if payload.get("new_value") is not None:
        new_value = Decimal(str(payload.get("new_value", 0)))
    elif amount_minor is not None:
        new_value = minor_to_decimal(amount_minor, currency=currency)
    else:
        new_value = Decimal("0")
    row = RunwayFinancialUpdates(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        update_type=payload.get("update_type", "cash_available"),
        current_value=Decimal(str(payload.get("current_value", 0))),
        new_value=new_value,
        reason=payload.get("reason", ""),
        approval_required=bool(payload.get("approval_required")),
        approval_status="not_required" if not payload.get("approval_required") else "pending",
        applied_status="pending",
        created_by=event.created_by,
        currency=currency,
        currency_code=currency,
        amount_minor=amount_minor,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.financial_update_id
