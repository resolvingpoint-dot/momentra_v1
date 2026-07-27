"""Handler: ISSUE_RISK → operations_issues."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import parse_date
from app.domains.business.models import BusinessActivityEvents, OperationsIssues


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    severity = str(payload.get("severity") or "medium").lower()
    if severity not in {"low", "medium", "high", "critical"}:
        severity = "medium"
    category = str(payload.get("issue_category") or payload.get("category") or "operations").lower()
    impact = str(payload.get("impact_area") or "operations").lower()
    status = str(payload.get("status") or payload.get("issue_status") or "open").lower()
    if status not in {"open", "investigating", "resolved", "archived"}:
        status = "open"

    row = OperationsIssues(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        issue_category=category
        if category
        in {"operations", "inventory", "vendor", "compliance", "customer", "technology", "other"}
        else "other",
        issue_title=payload.get("title") or event.title,
        severity=severity,
        impact_area=impact
        if impact in {"budget", "operations", "vendor", "customer", "compliance", "technology"}
        else "operations",
        issue_status=status,
        created_by=event.created_by,
        owner_id=UUID(payload["owner_id"]) if payload.get("owner_id") else None,
        target_resolution_date=parse_date(
            payload.get("target_date") or payload.get("target_resolution_date")
        ),
        description=payload.get("description") or payload.get("notes"),
        amount_minor=payload.get("amount_minor"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.operations_issue_id
