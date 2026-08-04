"""Moments projection mapper for Business Operations — distinct from Pulse."""
from __future__ import annotations

from app.domains.business.templates.business_operations.context import OpsContext
from app.domains.business.templates.business_operations.section_helpers import (
    event_item,
    filter_actions,
    section_state,
)
from app.domains.business.vendor_suggestions import vendor_timeline_items

_SPEND = {"SPEND_ENTRY"}
_APPROVAL = {"OPS_APPROVAL_REQUEST"}
_ISSUE = {"ISSUE_RISK"}
_VENDOR = {"VENDOR_UPDATE"}
_IMPROVEMENT = {"OPERATIONAL_IMPROVEMENT"}


def _milestones(ctx: OpsContext, activities: list[dict]) -> list[dict]:
    items: list[dict] = []
    if ctx.activated_at or ctx.is_active:
        items.append(
            {
                "kind": "activation",
                "title": "Operations activated",
                "occurred_at": ctx.activated_at,
            }
        )
    first_by_type = {}
    for a in reversed(activities):  # chronological first
        at = a.get("action_type") or ""
        if at in first_by_type:
            continue
        if at in _SPEND | _APPROVAL | _ISSUE | _VENDOR | _IMPROVEMENT:
            first_by_type[at] = a
    labels = {
        "SPEND_ENTRY": "First spend",
        "OPS_APPROVAL_REQUEST": "First approval",
        "ISSUE_RISK": "First issue",
        "VENDOR_UPDATE": "First vendor update",
        "OPERATIONAL_IMPROVEMENT": "First improvement",
    }
    for at, a in first_by_type.items():
        items.append(
            {
                "kind": at.lower(),
                "title": labels.get(at, at),
                "occurred_at": a.get("occurred_at"),
                "event_id": str(a.get("event_id") or ""),
            }
        )
    if ctx.budget_usage_pct >= 50 and (ctx.monthly_budget_minor or ctx.total_budget_minor) > 0:
        items.append(
            {
                "kind": "budget_milestone",
                "title": f"Budget {ctx.budget_usage_pct:.0f}% used",
                "occurred_at": ctx.last_updated,
            }
        )
    return items


def build_moments(ctx: OpsContext) -> dict:
    activities = list(ctx.activities or [])
    spend = filter_actions(activities, _SPEND)
    approvals = filter_actions(activities, _APPROVAL)
    issues = filter_actions(activities, _ISSUE)
    vendors = vendor_timeline_items(activities, ctx.vendor_due_by_name, vendor_action_types=_VENDOR)
    improvements = filter_actions(activities, _IMPROVEMENT)
    timeline = [event_item(a) for a in activities]
    recent = [event_item(a) for a in activities[:10]]
    milestones = _milestones(ctx, activities)
    decisions = [
        a
        for a in approvals
        if "approv" in (a.get("title") or "").lower() or "reject" in (a.get("title") or "").lower()
    ] or approvals[:5]

    budget = ctx.monthly_budget_minor or ctx.total_budget_minor
    progress = None
    if milestones:
        progress = min(100, int(len(milestones) * 15))

    return {
        "moment_id": str(ctx.moment_id),
        "moment_type": ctx.moment_type,
        "moment_name": ctx.moment_name,
        "operations_name": ctx.operations_name,
        "status": ctx.status,
        "journey_hero": {
            "state": section_state(count=1 if (ctx.operations_name or ctx.moment_name) else 0),
            "title": ctx.operations_name or ctx.moment_name or "Business Operations",
            "start_date": ctx.activated_at,
            "current_phase": "active" if ctx.is_active else ctx.status,
            "progress_percent": progress,
        },
        "summary_stats": {
            "state": section_state(
                count=1
                if (
                    budget > 0
                    or ctx.pending_approvals
                    or ctx.open_issue_count
                    or ctx.vendor_count
                    or ctx.completed_improvement_count
                )
                else 0
            ),
            "budget_used_percent": ctx.budget_usage_pct,
            "approvals": ctx.pending_approvals,
            "open_issues": ctx.open_issue_count,
            "vendors": ctx.vendor_count,
            "improvements": ctx.completed_improvement_count,
        },
        "spend_timeline": {"state": section_state(count=len(spend)), "items": spend[:40]},
        "approval_timeline": {"state": section_state(count=len(approvals)), "items": approvals[:40]},
        "issue_timeline": {"state": section_state(count=len(issues)), "items": issues[:40]},
        "vendor_timeline": {"state": section_state(count=len(vendors)), "items": vendors[:40]},
        "improvement_timeline": {
            "state": section_state(count=len(improvements)),
            "items": improvements[:40],
        },
        "milestones": {"state": section_state(count=len(milestones)), "items": milestones[:20]},
        "key_decisions": {"state": section_state(count=len(decisions)), "items": decisions[:20]},
        "timeline": {"state": section_state(count=len(timeline)), "items": timeline},
        "recent_activity": {"state": section_state(count=len(recent)), "items": recent},
    }
