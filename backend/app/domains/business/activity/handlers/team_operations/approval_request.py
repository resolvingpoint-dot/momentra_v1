"""Handler: APPROVAL_REQUEST → team_approval_requests."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import minor_to_decimal, resolve_member_id
from app.domains.business.models import BusinessActivityEvents, TeamApprovalRequests


async def _member_id(
    session: AsyncSession,
    event: BusinessActivityEvents,
    payload: dict[str, Any],
    key: str,
) -> UUID:
    if payload.get(key):
        return UUID(payload[key])
    member_id = await resolve_member_id(session, event.business_moment_id, event.created_by)
    if member_id is None:
        raise ValueError("member required")
    return member_id


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    currency = str(payload.get("currency_code") or payload.get("currency") or "INR")
    amount_minor = payload.get("amount_minor")
    if amount_minor is not None:
        amount = minor_to_decimal(amount_minor, currency=currency)
    else:
        amount = Decimal(str(payload.get("amount", 0)))

    row = TeamApprovalRequests(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        request_title=payload.get("title") or event.title,
        amount=amount,
        amount_minor=int(amount_minor) if amount_minor is not None else None,
        approval_type=payload.get("approval_type", "general"),
        reason=payload.get("reason", ""),
        priority=payload.get("priority", "normal"),
        requested_by=await _member_id(session, event, payload, "requested_by"),
        approver_id=await _member_id(session, event, payload, "approver_id"),
        approval_status="pending",
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.approval_id
