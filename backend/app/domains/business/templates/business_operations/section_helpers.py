"""Presentation helpers for Business Operations projection sections."""
from __future__ import annotations

from typing import Any


def section_state(*, count: int = 0, has_attention: bool = False) -> str:
    if count <= 0:
        return "empty"
    if has_attention:
        return "partial"
    return "complete"


def event_item(a: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": str(a.get("event_id") or ""),
        "action_type": a.get("action_type", ""),
        "title": a.get("title") or "",
        "subtitle": a.get("subtitle"),
        "occurred_at": str(a.get("occurred_at") or ""),
        "source_moment_id": a.get("source_moment_id"),
    }


def filter_actions(activities: list[dict], types: set[str]) -> list[dict]:
    return [event_item(a) for a in activities if (a.get("action_type") or "") in types]


def rule_based_operations_health(
    *,
    monthly_budget_minor: int,
    spent_minor: int,
    budget_usage_percent: float,
    open_issue_count: int,
    critical_issue_count: int,
    pending_approval_count: int,
    overdue_approval_count: int,
) -> dict[str, Any]:
    """v1 rule-based operations health — no fabricated composite scores."""
    has_any = (
        monthly_budget_minor > 0
        or spent_minor > 0
        or open_issue_count > 0
        or pending_approval_count > 0
    )
    if not has_any:
        label, band = "Not started", "EMPTY"
    elif critical_issue_count > 0 or budget_usage_percent >= 100:
        label, band = "At risk", "AT_RISK"
    elif overdue_approval_count > 0 or budget_usage_percent >= 90 or open_issue_count > 0:
        label, band = "Needs attention", "NEEDS_ATTENTION"
    else:
        label, band = "Healthy", "HEALTHY"

    return {
        "label": label,
        "band": band,
        "rule": "budget_issues_approvals_thresholds",
        "drivers": {
            "budget_usage_percent": budget_usage_percent,
            "open_issue_count": open_issue_count,
            "critical_issue_count": critical_issue_count,
            "pending_approval_count": pending_approval_count,
            "overdue_approval_count": overdue_approval_count,
            "spent_minor": spent_minor,
            "monthly_budget_minor": monthly_budget_minor,
        },
    }
