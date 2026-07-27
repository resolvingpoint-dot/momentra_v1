"""Pulse projection mapper for Business Operations — deterministic section tree."""
from __future__ import annotations

from app.domains.business.templates.business_operations.context import OpsContext
from app.domains.business.templates.business_operations.section_helpers import (
    event_item,
    rule_based_operations_health,
    section_state,
)
from app.domains.business.templates.business_operations.signals import derive_signals


def build_pulse(ctx: OpsContext) -> dict:
    activities = list(ctx.activities or [])
    recent = [event_item(a) for a in activities[:20]]
    health = rule_based_operations_health(
        monthly_budget_minor=ctx.monthly_budget_minor or ctx.total_budget_minor,
        spent_minor=ctx.total_spend_minor,
        budget_usage_percent=ctx.budget_usage_pct,
        open_issue_count=ctx.open_issue_count,
        critical_issue_count=ctx.critical_issue_count,
        pending_approval_count=ctx.pending_approvals,
        overdue_approval_count=ctx.overdue_approval_count,
    )

    projection = ctx.projection
    if projection is not None:
        attention = list(projection.attention_items)
        signals = [
            {
                "signal_type": item.get("signal_type", ""),
                "label": item.get("title", ""),
                "title": item.get("title", ""),
                "summary": item.get("summary"),
                "change_percent": item.get("change_percent"),
                "severity": item.get("impact_level"),
            }
            for item in projection.signal_items
        ]
        next_action = projection.recommended_action
    else:
        attention = []
        signals = derive_signals(ctx)
        next_action = None

    budget = ctx.monthly_budget_minor or ctx.total_budget_minor
    has_ops = budget > 0 or ctx.total_spend_minor > 0 or ctx.open_issue_count > 0

    return {
        "moment_id": str(ctx.moment_id),
        "moment_type": ctx.moment_type,
        "moment_name": ctx.moment_name,
        "operations_name": ctx.operations_name,
        "status": ctx.status,
        "is_active": ctx.is_active,
        "operating_currency": ctx.operating_currency,
        "stats": {
            "monthly_budget_minor": budget,
            "spent_minor": ctx.total_spend_minor,
            "remaining_minor": ctx.remaining_minor,
            "budget_usage_percent": ctx.budget_usage_pct,
            "pending_approval_count": ctx.pending_approvals,
            "open_issue_count": ctx.open_issue_count,
            "active_vendor_count": ctx.vendor_count,
            "completed_improvement_count": ctx.completed_improvement_count,
            # legacy keys
            "total_spend_minor": ctx.total_spend_minor,
            "total_budget_minor": budget,
            "budget_usage_pct": ctx.budget_usage_pct,
            "vendor_count": ctx.vendor_count,
            "pending_approvals": ctx.pending_approvals,
            "improvement_count": ctx.improvement_count,
        },
        "hero": {
            "state": section_state(count=1 if ctx.operations_name or ctx.moment_name else 0),
            "moment_name": ctx.moment_name,
            "operations_name": ctx.operations_name,
            "operations_scope": ctx.operations_scope,
            "operating_model": ctx.operating_model,
            "owner": ctx.owner_name,
            "last_updated": ctx.last_updated,
        },
        "operations_health": {
            "state": section_state(count=1 if health.get("band") != "EMPTY" else 0),
            "label": health.get("label"),
            "band": health.get("band"),
            "rule": health.get("rule"),
            "drivers": health.get("drivers") or {},
        },
        "kpis": {
            "state": section_state(count=1 if has_ops else 0),
            "monthly_budget_minor": budget,
            "spent_minor": ctx.total_spend_minor,
            "remaining_minor": ctx.remaining_minor,
            "budget_usage_percent": ctx.budget_usage_pct,
            "pending_approval_count": ctx.pending_approvals,
            "open_issue_count": ctx.open_issue_count,
            "active_vendor_count": ctx.vendor_count,
            "completed_improvement_count": ctx.completed_improvement_count,
        },
        "budget_usage": {
            "state": section_state(count=1 if budget > 0 or ctx.total_spend_minor > 0 else 0),
            "total_budget_minor": budget,
            "total_spend_minor": ctx.total_spend_minor,
            "remaining_minor": ctx.remaining_minor,
            "allocations": ctx.allocations,
            "over_budget_allocations": ctx.over_budget_allocations,
            "unallocated_minor": ctx.unallocated_minor,
            "operating_currency": ctx.operating_currency,
        },
        "approvals": {
            "state": section_state(
                count=ctx.pending_approvals
                + ctx.approved_recently
                + ctx.rejected_recently
                + ctx.overdue_approval_count
            ),
            "pending": ctx.pending_approvals,
            "overdue": ctx.overdue_approval_count,
            "approved_recently": ctx.approved_recently,
            "rejected_recently": ctx.rejected_recently,
            "amount_awaiting_minor": ctx.amount_awaiting_minor,
        },
        "issues": {
            "state": section_state(
                count=ctx.open_issue_count + ctx.resolved_recently
            ),
            "open": ctx.open_issue_count,
            "critical": ctx.critical_issue_count,
            "overdue": ctx.overdue_issue_count,
            "unassigned": ctx.unassigned_issue_count,
            "resolved_recently": ctx.resolved_recently,
        },
        "vendors": {
            "state": section_state(count=ctx.vendor_count),
            "active": ctx.vendor_count,
            "status_changes": ctx.vendor_count,
            "critical_dependencies": ctx.critical_vendor_count,
            "unresolved_events": ctx.critical_vendor_count,
        },
        "improvements": {
            "state": section_state(
                count=ctx.planned_improvement_count
                + ctx.in_progress_improvement_count
                + ctx.completed_improvement_count
            ),
            "planned": ctx.planned_improvement_count,
            "in_progress": ctx.in_progress_improvement_count,
            "completed": ctx.completed_improvement_count,
            "overdue": ctx.overdue_improvement_count,
        },
        "monitoring": {
            "state": section_state(count=1 if ctx.monitoring_level else 0),
            "level": ctx.monitoring_level,
            "active_alerts": [],
            "recipients": [],
        },
        "attention_items": {
            "state": section_state(count=len(attention), has_attention=bool(attention)),
            "items": attention,
        },
        "signals": {
            "state": section_state(count=len(signals)),
            "items": signals,
        },
        "recent_activity": {
            "state": section_state(count=len(recent)),
            "items": recent,
        },
        "next_best_action": {
            "state": section_state(count=1 if next_action else 0),
            "item": next_action,
        },
    }
