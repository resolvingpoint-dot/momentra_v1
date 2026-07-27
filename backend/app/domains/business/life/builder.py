"""Build business life view — aggregate across user's accessible ACTIVE business moments."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.life.mapper import (
    build_ops_slices,
    build_runway_slices,
    build_team_ops_slices,
    map_life,
)
from app.domains.business.models import BusinessMomentMembers, BusinessMoments
from app.domains.business.templates.business_operations.handler import OpsTemplateBuilder
from app.domains.business.templates.business_operations.section_helpers import (
    rule_based_operations_health,
)
from app.domains.business.templates.business_runway.handler import RunwayTemplateBuilder
from app.domains.business.templates.team_operations.handler import TeamOpsTemplateBuilder


async def _accessible_active_moments(session: AsyncSession, user_id: UUID) -> list[BusinessMoments]:
    """Moments the user owns or is an active/configured member of."""
    member_moment_ids = (
        select(BusinessMomentMembers.moment_id)
        .where(
            BusinessMomentMembers.user_id == user_id,
            BusinessMomentMembers.member_status.in_(("active", "configured")),
        )
        .scalar_subquery()
    )
    result = await session.execute(
        select(BusinessMoments).where(
            func.lower(BusinessMoments.status) == "active",
            or_(
                BusinessMoments.created_by == user_id,
                BusinessMoments.moment_id.in_(member_moment_ids),
            ),
        )
    )
    return list(result.scalars().unique().all())


async def build_life(session: AsyncSession, user_id: UUID) -> dict:
    """Sparse-safe life aggregate with Team Ops + Runway + Ops contribution slices."""
    moments = await _accessible_active_moments(session, user_id)
    team_contributions: list[dict] = []
    runway_contributions: list[dict] = []
    ops_contributions: list[dict] = []

    for m in moments:
        mt = (m.moment_type or "").upper().replace(" ", "_")
        if mt == "TEAM_OPERATIONS":
            try:
                # Life only needs counts / activity rows — skip analytics projector.
                ctx = await TeamOpsTemplateBuilder(session).build(
                    user_id, m.moment_id, with_projection=False
                )
            except ValueError:
                continue
            team_contributions.append({
                "moment_id": str(m.moment_id),
                "slices": build_team_ops_slices(
                    moment_id=str(m.moment_id),
                    moment_name=m.moment_name or "",
                    activities=ctx.activities,
                    open_issues=ctx.open_issues,
                    pending_approvals=ctx.pending_approvals,
                    escalation_count=ctx.escalation_count,
                    member_count=ctx.member_count,
                ),
            })
        elif mt == "BUSINESS_RUNWAY":
            try:
                ctx = await RunwayTemplateBuilder(session).build(user_id, m.moment_id)
            except ValueError:
                continue
            runway_contributions.append({
                "moment_id": str(m.moment_id),
                "slices": build_runway_slices(
                    moment_id=str(m.moment_id),
                    moment_name=m.moment_name or "",
                    activities=ctx.activities,
                    runway_months=ctx.runway_months,
                    risk_count=ctx.risk_count,
                    cash_available_minor=ctx.cash_available_minor,
                    monthly_burn_minor=ctx.monthly_burn_setup_minor or ctx.net_burn_minor,
                    collection_rate_percent=ctx.collection_rate_percent,
                    alert_threshold_months=ctx.alert_threshold_months,
                ),
            })
        elif mt in {"BUSINESS_OPERATIONS", "DEPARTMENT_OPERATIONS"}:
            try:
                ctx = await OpsTemplateBuilder(session).build(user_id, m.moment_id)
            except ValueError:
                continue
            health = rule_based_operations_health(
                monthly_budget_minor=ctx.monthly_budget_minor or ctx.total_budget_minor,
                spent_minor=ctx.total_spend_minor,
                budget_usage_percent=ctx.budget_usage_pct,
                open_issue_count=ctx.open_issue_count,
                critical_issue_count=ctx.critical_issue_count,
                pending_approval_count=ctx.pending_approvals,
                overdue_approval_count=ctx.overdue_approval_count,
            )
            ops_contributions.append({
                "moment_id": str(m.moment_id),
                "slices": build_ops_slices(
                    moment_id=str(m.moment_id),
                    moment_name=m.moment_name or "",
                    activities=ctx.activities,
                    budget_usage_percent=ctx.budget_usage_pct,
                    open_issue_count=ctx.open_issue_count,
                    critical_issue_count=ctx.critical_issue_count,
                    pending_approvals=ctx.pending_approvals,
                    vendor_count=ctx.vendor_count,
                    critical_vendor_count=ctx.critical_vendor_count,
                    completed_improvement_count=ctx.completed_improvement_count,
                    improvement_count=ctx.improvement_count,
                    health_band=str(health.get("band") or "EMPTY"),
                    monitoring_level=ctx.monitoring_level,
                ),
            })

    return map_life(
        moments,
        team_ops_contributions=team_contributions,
        runway_contributions=runway_contributions,
        ops_contributions=ops_contributions,
    )
