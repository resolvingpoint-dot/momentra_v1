"""Handler: OPERATIONAL_IMPROVEMENT → operations_improvements."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.handlers._helpers import parse_date
from app.domains.business.models import BusinessActivityEvents, OperationsImprovements

_IMPROVEMENT_TYPES = {
    "process_improvement",
    "budget_control_improvement",
    "customer_experience_improvement",
    "inventory_improvement",
    "compliance_improvement",
    "staffing_scheduling_improvement",
    "approval_flow_improvement",
    "service_quality_improvement",
    "operational_control_improvement",
    "vendor_experience_improvement",
    "other",
}

_EXPECTED_IMPACT = {
    "reduce_cost",
    "improve_speed",
    "reduce_issues",
    "improve_service",
    "improve_control",
    "improve_visibility",
    "increase_revenue",
    "other",
}

_IMPACT_AREA_BY_TYPE = {
    "process_improvement": "operations",
    "budget_control_improvement": "budget",
    "inventory_improvement": "inventory",
    "vendor_experience_improvement": "operations",
    "staffing_scheduling_improvement": "staff",
    "compliance_improvement": "compliance",
    "service_quality_improvement": "customer",
    "operational_control_improvement": "operations",
    "approval_flow_improvement": "approval_flow",
    "customer_experience_improvement": "customer",
}


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    improvement_type = str(payload.get("improvement_type") or "process_improvement").lower()
    if improvement_type not in _IMPROVEMENT_TYPES:
        improvement_type = "other"

    expected = str(payload.get("expected_impact") or "improve_speed").lower()
    if expected not in _EXPECTED_IMPACT:
        expected = "other"

    impact_area = str(
        payload.get("impact_area") or _IMPACT_AREA_BY_TYPE.get(improvement_type) or "operations"
    ).lower()
    allowed_areas = {
        "budget",
        "operations",
        "customer",
        "compliance",
        "inventory",
        "staff",
        "approval_flow",
    }
    if impact_area not in allowed_areas:
        impact_area = "operations"

    # effective_date is NOT NULL — prefer target_date from Quick Add
    effective = parse_date(payload.get("target_date") or payload.get("effective_date"))
    priority = str(payload.get("priority") or "medium").lower()
    follow_up = bool(payload.get("follow_up_required")) or priority in {"high", "critical"}

    description = payload.get("description")
    if priority and priority != "medium":
        tag = f"Priority: {priority}"
        description = f"{tag}\n{description}".strip() if description else tag

    owner_raw = payload.get("owner_id")
    owner_id = UUID(str(owner_raw)) if owner_raw else None

    row = OperationsImprovements(
        moment_id=event.business_moment_id,
        event_id=event.event_id,
        improvement_type=improvement_type,
        improvement_title=payload.get("title") or event.title,
        impact_area=impact_area,
        expected_impact=expected,
        effective_date=effective,
        follow_up_required=follow_up,
        improvement_status="recorded",
        created_by=event.created_by,
        owner_id=owner_id,
        description=description,
        amount_minor=payload.get("amount_minor"),
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row.improvement_id
