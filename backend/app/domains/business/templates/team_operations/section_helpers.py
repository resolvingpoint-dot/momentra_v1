"""Presentation helpers for Team Ops projection sections."""
from __future__ import annotations

from typing import Any


def section_state(*, count: int = 0, has_attention: bool = False) -> str:
    """Backend never emits loading — clients own that state while fetching."""
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


def rule_based_team_health(
    *,
    member_count: int,
    open_issues: int,
    pending_approvals: int,
    escalation_count: int,
) -> dict[str, Any]:
    """v1 rule-based health only — no weighted scoring engine."""
    if member_count <= 0 and open_issues == 0 and pending_approvals == 0:
        label, band = "Not started", "empty"
    elif escalation_count > 0 or open_issues >= 5:
        label, band = "At risk", "at_risk"
    elif open_issues > 0 or pending_approvals > 3:
        label, band = "Needs attention", "needs_attention"
    else:
        label, band = "On track", "healthy"

    denom = max(member_count, 1)
    return {
        "label": label,
        "band": band,
        "rule": "escalations_or_issues_thresholds",
        "inputs": {
            "members": member_count,
            "open_issues": open_issues,
            "pending_approvals": pending_approvals,
            "escalations": escalation_count,
        },
        # Percentages derived only from raw counts (not inventing composites)
        "open_issues_per_member_pct": round((open_issues / denom) * 100, 1),
        "pending_approvals_per_member_pct": round((pending_approvals / denom) * 100, 1),
    }
