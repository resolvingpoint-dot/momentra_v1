"""Map Memory contribution — event allowlist only, no narrative/AI."""
from __future__ import annotations

from typing import Any

from app.domains.business.memory.patterns import (
    build_memory_journey,
    build_memory_source_filters,
    build_memory_summary,
    derive_memory_patterns,
    derive_success_and_risk_memory,
)
from app.domains.business.models import BusinessMoments

# Memory stores real event references only
MEMORY_ACTION_ALLOWLIST = frozenset({
    "APPROVAL_REQUEST",  # important approvals
    "RECOGNITION",
    "ISSUE",  # resolved issues filtered by caller when possible
    "TEAM_UPDATE",
    "MEETING",
    "REVIEW",  # milestones / reviews
    "MEMBER_UPDATE",
    "STRATEGIC_DECISION",
    # Runway v1 handlers
    "CASH_INFLOW",
    "EXPENSE_BURN",
    "FINANCIAL_UPDATE",
    "RUNWAY_RISK",
    # Business Operations v1
    "SPEND_ENTRY",
    "VENDOR_UPDATE",
    "OPS_APPROVAL_REQUEST",
    "ISSUE_RISK",
    "OPERATIONAL_IMPROVEMENT",
})


def map_memory_event(a: dict[str, Any], *, moment_id: str, moment_name: str) -> dict[str, Any] | None:
    action = (a.get("action_type") or "").upper()
    if action not in MEMORY_ACTION_ALLOWLIST:
        return None
    # For ISSUE: only resolved/closed belong in Memory (Pulse owns open issues)
    if action == "ISSUE":
        status = (a.get("resolution_status") or a.get("status") or "open").lower()
        if status not in ("resolved", "closed", "done"):
            return None
    if action == "ISSUE_RISK":
        status = (a.get("resolution_status") or a.get("status") or a.get("issue_status") or "open").lower()
        # Open issues stay on Pulse; Memory only when resolved/archived unless payload says so
        payload = a.get("payload") or {}
        status = str(payload.get("issue_status") or payload.get("status") or status).lower()
        if status not in ("resolved", "closed", "done", "archived"):
            return None
    return {
        "event_id": str(a.get("event_id") or ""),
        "action_type": action,
        "title": a.get("title") or "",
        "occurred_at": str(a.get("occurred_at") or ""),
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
        "source_moment_type": a.get("moment_type") or "TEAM_OPERATIONS",
    }


def map_memory(
    moments: list[BusinessMoments],
    *,
    events: list[dict[str, Any]] | None = None,
) -> dict:
    moment_summaries = []
    by_id = {}
    for m in moments:
        mid = str(m.moment_id)
        by_id[mid] = m
        moment_summaries.append({
            "moment_id": mid,
            "moment_type": m.moment_type,
            "moment_name": m.moment_name or "",
            "status": m.status or "draft",
        })

    memory_events: list[dict[str, Any]] = []
    for a in events or []:
        mid = str(a.get("source_moment_id") or a.get("moment_id") or "")
        m = by_id.get(mid)
        name = (m.moment_name if m else "") or a.get("source_moment_name") or ""
        item = map_memory_event(a, moment_id=mid, moment_name=name)
        if item:
            memory_events.append(item)

    # Bucket by allowlisted kinds (no summaries)
    buckets = {
        "milestones": [e for e in memory_events if e["action_type"] in {"REVIEW", "STRATEGIC_DECISION", "MEETING"}],
        "important_approvals": [e for e in memory_events if e["action_type"] == "APPROVAL_REQUEST"],
        "recognitions": [e for e in memory_events if e["action_type"] == "RECOGNITION"],
        "resolved_issues": [e for e in memory_events if e["action_type"] in {"ISSUE", "ISSUE_RISK"}],
        "team_updates": [e for e in memory_events if e["action_type"] in {"TEAM_UPDATE", "MEMBER_UPDATE"}],
        "meetings": [e for e in memory_events if e["action_type"] == "MEETING"],
        # Runway contribution buckets (Stitch-first allowlist)
        "funding": [
            e for e in memory_events
            if e["action_type"] == "CASH_INFLOW"
            and any(k in e["title"].lower() for k in ("fund", "invest", "loan"))
        ],
        "large_payments": [
            e for e in memory_events
            if e["action_type"] in {"EXPENSE_BURN", "CASH_INFLOW"}
            and any(k in e["title"].lower() for k in ("large", "major", "payment"))
        ],
        "revenue_milestones": [
            e for e in memory_events
            if e["action_type"] == "FINANCIAL_UPDATE"
            and "revenue" in e["title"].lower()
        ],
        "major_expenses": [e for e in memory_events if e["action_type"] == "EXPENSE_BURN"],
        "loans": [
            e for e in memory_events
            if "loan" in e["title"].lower()
        ],
        "investments": [
            e for e in memory_events
            if any(k in e["title"].lower() for k in ("invest", "funding"))
        ],
        "forecast_changes": [
            e for e in memory_events
            if e["action_type"] == "FINANCIAL_UPDATE"
            and "forecast" in e["title"].lower()
        ],
        "runway_risks": [e for e in memory_events if e["action_type"] == "RUNWAY_RISK"],
        # Business Operations buckets
        "major_spend": [e for e in memory_events if e["action_type"] == "SPEND_ENTRY"],
        "approval_decisions": [e for e in memory_events if e["action_type"] == "OPS_APPROVAL_REQUEST"],
        "vendor_changes": [e for e in memory_events if e["action_type"] == "VENDOR_UPDATE"],
        "completed_improvements": [
            e for e in memory_events if e["action_type"] == "OPERATIONAL_IMPROVEMENT"
        ],
        "operational_milestones": [
            e
            for e in memory_events
            if e["action_type"]
            in {"OPERATIONAL_IMPROVEMENT", "OPS_APPROVAL_REQUEST", "SPEND_ENTRY"}
        ],
        "key_decisions": [
            e for e in memory_events if e["action_type"] in {"OPS_APPROVAL_REQUEST", "STRATEGIC_DECISION"}
        ],
        "recurring_issue_patterns": [e for e in memory_events if e["action_type"] == "ISSUE_RISK"],
        "budget_patterns": [e for e in memory_events if e["action_type"] == "SPEND_ENTRY"],
    }

    # Attach moment type onto events for client filters
    for e in memory_events:
        mid = e.get("source_moment_id") or ""
        m = by_id.get(mid)
        if m and not e.get("source_moment_type"):
            e["source_moment_type"] = m.moment_type or "TEAM_OPERATIONS"

    success_memory, risk_memory = derive_success_and_risk_memory(memory_events)

    return {
        "active_moment_count": len(moments),
        "moments": moment_summaries,
        "summary": build_memory_summary(moments, memory_events),
        "source_filters": build_memory_source_filters(moments),
        "patterns": derive_memory_patterns(moments, events=memory_events),
        "success_memory": success_memory,
        "risk_memory": risk_memory,
        "playbooks": [],  # only when SQL-backed rows exist — never invent
        "journey": build_memory_journey(memory_events),
        "events": memory_events[:100],
        "buckets": {k: {"state": "empty" if not v else "complete", "items": v[:40]} for k, v in buckets.items()},
    }
