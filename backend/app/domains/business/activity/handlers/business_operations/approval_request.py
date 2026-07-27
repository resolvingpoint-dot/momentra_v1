"""Handler: OPS_APPROVAL_REQUEST → operations_approval_requests."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import minor_to_decimal
from app.domains.business.models import BusinessActivityEvents, OperationsApprovalRequests


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    currency = str(payload.get("currency_code") or payload.get("currency") or "INR")
    amount_minor = payload.get("amount_minor")
    amount = None
    if amount_minor is not None:
        amount = minor_to_decimal(amount_minor, currency=currency)
    elif payload.get("amount") is not None:
        amount = Decimal(str(payload["amount"]))

    row = OperationsApprovalRequests(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        request_type=payload.get("request_type", "operational_request"),
        request_title=payload.get("title") or event.title,
        priority=payload.get("priority", "medium"),
        description=payload.get("description", ""),
        approval_status="pending",
        requested_by=event.created_by,
        approver_id=UUID(payload["approver_id"]) if payload.get("approver_id") else None,
        amount=amount,
        amount_minor=int(amount_minor) if amount_minor is not None else None,
        currency=currency,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.operations_approval_id
