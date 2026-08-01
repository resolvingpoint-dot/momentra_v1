"""Handler: OPS_APPROVAL_REQUEST → operations_approval_requests."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import minor_to_decimal, parse_date
from app.domains.business.models import BusinessActivityEvents, OperationsApprovalRequests

_REQUEST_TYPES = {
    "expense_approval",
    "vendor_approval",
    "budget_change",
    "policy_exception",
    "operational_request",
    "hiring",
    "contract",
    "purchase",
    "other",
}

# UX / legacy aliases → stored CHECK values
_REQUEST_TYPE_ALIASES = {
    "expense": "expense_approval",
    "vendor_payment": "vendor_approval",
    "vendor": "vendor_approval",
    "budget": "budget_change",
    "operational_change": "operational_request",
    "ops": "operational_request",
    "policy": "policy_exception",
}


def _normalize_request_type(raw: Any) -> str:
    value = str(raw or "operational_request").strip().lower()
    value = _REQUEST_TYPE_ALIASES.get(value, value)
    if value not in _REQUEST_TYPES:
        return "other"
    return value


def _parse_approver_ids(payload: dict[str, Any]) -> list[UUID]:
    raw = payload.get("approver_ids")
    ids: list[UUID] = []
    if isinstance(raw, list):
        for item in raw:
            if item is None or item == "":
                continue
            try:
                ids.append(UUID(str(item)))
            except (TypeError, ValueError):
                continue
    primary: UUID | None = None
    if payload.get("approver_id"):
        try:
            primary = UUID(str(payload["approver_id"]))
        except (TypeError, ValueError):
            primary = None
    # de-dupe preserving order; primary first when present
    seen: set[UUID] = set()
    ordered: list[UUID] = []
    if primary is not None:
        ordered.append(primary)
        seen.add(primary)
    for mid in ids:
        if mid not in seen:
            seen.add(mid)
            ordered.append(mid)
    return ordered


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    currency = str(payload.get("currency_code") or payload.get("currency") or "INR")
    amount_minor = payload.get("amount_minor")
    amount = None
    if amount_minor is not None:
        amount = minor_to_decimal(amount_minor, currency=currency)
    elif payload.get("amount") is not None:
        amount = Decimal(str(payload["amount"]))

    approver_ids = _parse_approver_ids(payload)
    if not approver_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "approvers_required", "message": "Select at least one approver"},
        )

    primary = approver_ids[0]
    priority = str(payload.get("priority") or "medium").lower()
    if priority not in {"low", "medium", "high", "critical"}:
        priority = "medium"
    if priority == "urgent":
        priority = "high"

    row = OperationsApprovalRequests(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        request_type=_normalize_request_type(payload.get("request_type")),
        request_title=payload.get("title") or event.title,
        priority=priority,
        description=payload.get("description") or "",
        approval_status="pending",
        requested_by=event.created_by,
        approver_id=primary,
        approver_ids=[str(x) for x in approver_ids],
        due_date=parse_date(payload.get("due_date")) if payload.get("due_date") else None,
        amount=amount,
        amount_minor=int(amount_minor) if amount_minor is not None else None,
        currency=currency,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.operations_approval_id
