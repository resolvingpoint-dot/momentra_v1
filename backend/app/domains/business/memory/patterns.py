"""Derive business memory patterns from moments + events — sparse-safe."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from app.domains.business.models import BusinessMoments


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def derive_memory_patterns(
    moments: list[BusinessMoments],
    *,
    events: list[dict[str, Any]] | None = None,
) -> list[dict]:
    if not moments:
        return []
    patterns: list[dict] = []
    type_set = {(m.moment_type or "unknown").upper() for m in moments}
    for mt in sorted(type_set):
        short = mt.replace("_", " ").title()
        # Short labels for radar satellites — not long "tracked" slogans for flow UI.
        patterns.append({
            "pattern_type": "dimension_active",
            "dimension": mt,
            "label": short,
        })

    events = events or []
    counts = Counter((e.get("action_type") or "").upper() for e in events if e.get("action_type"))
    if counts.get("MEETING", 0) >= 3:
        patterns.append({
            "pattern_type": "meeting_cadence",
            "dimension": "TEAM_OPERATIONS",
            "label": f"{counts['MEETING']} meetings recorded — recurring coordination pattern",
            "count": counts["MEETING"],
        })
    if counts.get("VENDOR_UPDATE", 0) >= 2:
        patterns.append({
            "pattern_type": "vendor_activity",
            "dimension": "BUSINESS_OPERATIONS",
            "label": f"{counts['VENDOR_UPDATE']} vendor updates observed",
            "count": counts["VENDOR_UPDATE"],
        })
    if counts.get("RECOGNITION", 0) >= 2:
        patterns.append({
            "pattern_type": "recognition_culture",
            "dimension": "TEAM_OPERATIONS",
            "label": f"{counts['RECOGNITION']} recognitions recorded",
            "count": counts["RECOGNITION"],
        })
    if counts.get("RUNWAY_RISK", 0) >= 1:
        patterns.append({
            "pattern_type": "runway_risk_memory",
            "dimension": "BUSINESS_RUNWAY",
            "label": f"{counts['RUNWAY_RISK']} runway risk event(s) remembered",
            "count": counts["RUNWAY_RISK"],
        })
    return patterns


def build_memory_summary(
    moments: list[BusinessMoments],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Factual summary — no composite strength score."""
    dates = [_parse_dt(e.get("occurred_at")) for e in events]
    dates = [d for d in dates if d is not None]
    months_active = 0
    if dates:
        earliest = min(dates)
        now = datetime.now(timezone.utc)
        if earliest.tzinfo is None:
            earliest = earliest.replace(tzinfo=timezone.utc)
        delta_days = max(0, (now - earliest).days)
        months_active = max(1, delta_days // 30) if delta_days >= 30 else (1 if delta_days > 0 else 0)
    # Fall back to moment created_at if no events
    if months_active == 0 and moments:
        created = []
        for m in moments:
            ca = getattr(m, "created_at", None)
            if ca is not None:
                created.append(ca if getattr(ca, "tzinfo", None) else ca.replace(tzinfo=timezone.utc))
        if created:
            earliest = min(created)
            now = datetime.now(timezone.utc)
            delta_days = max(0, (now - earliest).days)
            months_active = max(1, delta_days // 30) if delta_days >= 30 else (1 if delta_days > 0 else 0)

    # When moments exist, never report 0 months (same-day creates still count as month 1).
    if moments and months_active < 1:
        months_active = 1

    return {
        "active_moment_count": len(moments),
        "event_count": len(events),
        "months_active": months_active,
        "description": (
            "Your business has accumulated operational knowledge through recorded moments and events."
            if events or moments
            else "Activate business moments to start Memory."
        ),
    }


def build_memory_source_filters(moments: list[BusinessMoments]) -> list[dict[str, Any]]:
    """Tabs for All / Team / Runway / Ops filtering by source_moment_type."""
    present = {(m.moment_type or "").upper().replace(" ", "_") for m in moments}
    filters = [{"key": "all", "label": "All", "moment_types": []}]
    if present & {"TEAM_OPERATIONS"}:
        filters.append({"key": "team", "label": "Team", "moment_types": ["TEAM_OPERATIONS"]})
    if present & {"BUSINESS_RUNWAY"}:
        filters.append({"key": "runway", "label": "Runway", "moment_types": ["BUSINESS_RUNWAY"]})
    if present & {"BUSINESS_OPERATIONS", "DEPARTMENT_OPERATIONS"}:
        filters.append({
            "key": "ops",
            "label": "Ops",
            "moment_types": ["BUSINESS_OPERATIONS", "DEPARTMENT_OPERATIONS"],
        })
    return filters


def build_memory_journey(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not events:
        return []
    ordered = sorted(
        [e for e in events if e.get("occurred_at")],
        key=lambda e: str(e.get("occurred_at") or ""),
    )
    journey: list[dict[str, Any]] = []
    if ordered:
        first = ordered[0]
        journey.append({
            "kind": "FIRST_MEMORY_EVENT",
            "title": "First memory event",
            "occurred_at": first.get("occurred_at"),
            "event_id": first.get("event_id"),
            "source_moment_id": first.get("source_moment_id"),
        })
    # First of notable types
    for action, title in (
        ("RECOGNITION", "First recognition remembered"),
        ("VENDOR_UPDATE", "First vendor change remembered"),
        ("CASH_INFLOW", "First funding / inflow remembered"),
        ("REVIEW", "First review remembered"),
    ):
        hit = next((e for e in ordered if (e.get("action_type") or "").upper() == action), None)
        if hit:
            journey.append({
                "kind": action,
                "title": title,
                "occurred_at": hit.get("occurred_at"),
                "event_id": hit.get("event_id"),
                "source_moment_id": hit.get("source_moment_id"),
            })
    journey.sort(key=lambda x: str(x.get("occurred_at") or ""))
    return journey[:10]


def derive_success_and_risk_memory(events: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    """Frequency-based success/risk memory — only when evidence exists."""
    counts = Counter((e.get("action_type") or "").upper() for e in events)
    success: list[dict] = []
    risk: list[dict] = []

    if counts.get("RECOGNITION", 0) >= 2:
        success.append({
            "kind": "recognition_momentum",
            "title": "Recognition culture",
            "detail": f"{counts['RECOGNITION']} recognition events recorded",
            "observed_count": counts["RECOGNITION"],
        })
    if counts.get("OPERATIONAL_IMPROVEMENT", 0) >= 2:
        success.append({
            "kind": "improvement_momentum",
            "title": "Operational improvements",
            "detail": f"{counts['OPERATIONAL_IMPROVEMENT']} improvements recorded",
            "observed_count": counts["OPERATIONAL_IMPROVEMENT"],
        })
    if counts.get("CASH_INFLOW", 0) >= 1:
        success.append({
            "kind": "funding_memory",
            "title": "Cash inflows remembered",
            "detail": f"{counts['CASH_INFLOW']} inflow event(s)",
            "observed_count": counts["CASH_INFLOW"],
        })

    if counts.get("RUNWAY_RISK", 0) >= 1:
        risk.append({
            "kind": "runway_risk",
            "title": "Runway risks",
            "detail": f"Observed {counts['RUNWAY_RISK']} time(s)",
            "observed_count": counts["RUNWAY_RISK"],
            "impact": "Financial stability",
        })
    issue_n = counts.get("ISSUE", 0) + counts.get("ISSUE_RISK", 0)
    if issue_n >= 2:
        risk.append({
            "kind": "recurring_issues",
            "title": "Recurring issues",
            "detail": f"Observed {issue_n} resolved issue memories",
            "observed_count": issue_n,
            "impact": "Execution delays",
        })
    if counts.get("OPS_APPROVAL_REQUEST", 0) + counts.get("APPROVAL_REQUEST", 0) >= 3:
        n = counts.get("OPS_APPROVAL_REQUEST", 0) + counts.get("APPROVAL_REQUEST", 0)
        risk.append({
            "kind": "approval_volume",
            "title": "High approval volume",
            "detail": f"Observed {n} approval memories",
            "observed_count": n,
            "impact": "Approval backlog",
        })

    return success, risk
