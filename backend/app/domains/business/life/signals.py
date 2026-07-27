"""Derive business life signals from moments + slices — sparse-safe, evidence only."""
from __future__ import annotations

from typing import Any

from app.domains.business.models import BusinessMoments


def derive_life_signals(
    moments: list[BusinessMoments],
    *,
    slices: dict[str, dict[str, Any]] | None = None,
) -> list[dict]:
    signals: list[dict] = []

    type_counts: dict[str, int] = {}
    for m in moments:
        mt = (m.moment_type or "unknown").upper()
        type_counts[mt] = type_counts.get(mt, 0) + 1
    for mt, count in type_counts.items():
        signals.append({
            "signal_type": "active_moments",
            "dimension": mt,
            "severity": "info",
            "count": count,
            "label": f"{count} active {mt.replace('_', ' ').lower()} moment{'s' if count != 1 else ''}",
        })

    s = slices or {}
    if not moments and not s:
        return signals

    # Evidence-based attention signals from slice bands / counts
    team = s.get("team_health") or {}
    band = str(team.get("band") or "empty").lower()
    if band in {"at_risk", "needs_attention"}:
        inputs = team.get("inputs") or {}
        signals.append({
            "signal_type": "team_attention",
            "dimension": "team_health",
            "severity": "high" if band == "at_risk" else "medium",
            "count": int(team.get("count") or 0),
            "label": (
                f"Team health is {band.replace('_', ' ')}"
                + (
                    f" ({inputs.get('open_issues', 0)} open issues, "
                    f"{inputs.get('pending_approvals', 0)} pending approvals)"
                    if inputs
                    else ""
                )
            ),
        })

    fin = s.get("financial_health") or {}
    fband = str(fin.get("band") or "empty").lower()
    if fband in {"at_risk", "needs_attention", "critical"}:
        inputs = fin.get("inputs") or {}
        months = inputs.get("runway_months")
        signals.append({
            "signal_type": "runway_attention",
            "dimension": "financial_health",
            "severity": "high" if fband in {"at_risk", "critical"} else "medium",
            "count": int(fin.get("count") or 0),
            "label": (
                f"Financial health is {fband.replace('_', ' ')}"
                + (f" ({months:.1f} months runway)" if isinstance(months, (int, float)) else "")
            ),
        })

    ops = s.get("operational_health") or {}
    oband = str(ops.get("band") or "empty").lower()
    if oband in {"at_risk", "needs_attention"}:
        signals.append({
            "signal_type": "ops_attention",
            "dimension": "operational_health",
            "severity": "high" if oband == "at_risk" else "medium",
            "count": int(ops.get("count") or 0),
            "label": f"Operational health is {oband.replace('_', ' ')}",
        })

    issues = s.get("issues") or s.get("issue_load") or {}
    issue_count = int(issues.get("count") or 0)
    if issue_count >= 3:
        signals.append({
            "signal_type": "issue_load",
            "dimension": "issues",
            "severity": "medium",
            "count": issue_count,
            "label": f"{issue_count} open or tracked issues across business moments",
        })

    vendors = s.get("vendor_health") or {}
    critical = int(vendors.get("critical_count") or 0)
    if critical > 0:
        signals.append({
            "signal_type": "vendor_dependency",
            "dimension": "vendor_health",
            "severity": "medium",
            "count": critical,
            "label": f"{critical} critical vendor dependenc{'ies' if critical != 1 else 'y'}",
        })

    return signals


def build_life_dimensions(slices: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Roll Part I dimensions from contribution slice bands — no composite score."""
    mapping = [
        ("team_health", "team_health", "Team Health"),
        ("financial_health", "financial_health", "Financial Health"),
        ("operational_health", "operational_health", "Operational Health"),
        ("customer_revenue_health", "growth", "Customer / Revenue Health"),
        ("vendor_health", "vendor_health", "Vendor Health"),
        ("governance", "governance", "Governance"),
        ("risk", "risk", "Risk"),
        ("growth", "growth", "Growth"),
        ("execution", "execution", "Execution"),
    ]
    # Prefer issue_load for risk when runway risk slice empty
    dims: list[dict[str, Any]] = []
    for dim_key, slice_key, label in mapping:
        src_key = slice_key
        if dim_key == "risk":
            risk = slices.get("risk") or {}
            issue_load = slices.get("issue_load") or slices.get("issues") or {}
            if int(risk.get("count") or 0) == 0 and int(issue_load.get("count") or 0) > 0:
                src_key = "issue_load" if "issue_load" in slices else "issues"
        src = slices.get(src_key) or {}
        band = str(src.get("band") or ("empty" if int(src.get("count") or 0) == 0 else "healthy")).lower()
        count = int(src.get("count") or 0)
        state = str(src.get("state") or ("empty" if count == 0 else "complete"))
        dims.append({
            "key": dim_key,
            "label": label,
            "band": band,
            "state": state,
            "count": count,
            "source_slice": src_key,
            "source_moment_id": src.get("source_moment_id"),
            "source_moment_name": src.get("source_moment_name"),
        })
    return dims


def build_life_journey(slices: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Chronological milestones from real slice event items — no fabricated dates."""
    candidates: list[dict[str, Any]] = []
    milestone_types = {
        "MEETING": "First meeting recorded",
        "MEMBER_UPDATE": "Team membership updated",
        "VENDOR_UPDATE": "First vendor update",
        "RECOGNITION": "First recognition",
        "CASH_INFLOW": "First cash inflow",
        "SPEND_ENTRY": "First spend recorded",
        "REVIEW": "First review",
        "STRATEGIC_DECISION": "Strategic decision recorded",
    }
    seen_actions: set[str] = set()
    for slice_payload in slices.values():
        for item in slice_payload.get("items") or []:
            action = str(item.get("action_type") or "").upper()
            occurred = str(item.get("occurred_at") or "")
            if not action or not occurred or action in seen_actions:
                continue
            if action not in milestone_types:
                continue
            seen_actions.add(action)
            candidates.append({
                "kind": action,
                "title": milestone_types[action],
                "occurred_at": occurred,
                "event_id": item.get("event_id"),
                "source_moment_id": item.get("source_moment_id"),
            })

    # Also: first activity threshold from any items
    all_items: list[dict[str, Any]] = []
    for slice_payload in slices.values():
        all_items.extend(slice_payload.get("items") or [])
    all_items = [i for i in all_items if i.get("occurred_at")]
    all_items.sort(key=lambda x: str(x.get("occurred_at") or ""))
    if len(all_items) >= 1:
        first = all_items[0]
        candidates.append({
            "kind": "FIRST_ACTIVITY",
            "title": "First business activity recorded",
            "occurred_at": first.get("occurred_at"),
            "event_id": first.get("event_id"),
            "source_moment_id": first.get("source_moment_id"),
        })
    if len(all_items) >= 100:
        hundredth = all_items[99]
        candidates.append({
            "kind": "ACTIVITY_100",
            "title": "100 activities recorded",
            "occurred_at": hundredth.get("occurred_at"),
            "event_id": hundredth.get("event_id"),
            "source_moment_id": hundredth.get("source_moment_id"),
        })

    # Dedupe by kind, keep earliest
    by_kind: dict[str, dict[str, Any]] = {}
    for c in candidates:
        kind = str(c.get("kind") or "")
        prev = by_kind.get(kind)
        if prev is None or str(c.get("occurred_at") or "") < str(prev.get("occurred_at") or ""):
            by_kind[kind] = c
    journey = list(by_kind.values())
    journey.sort(key=lambda x: str(x.get("occurred_at") or ""))
    return journey[:12]


def aggregate_life_band(dimensions: list[dict[str, Any]]) -> dict[str, Any]:
    """Overall band from dimensions — label only, no numeric score."""
    order = {"empty": 0, "healthy": 1, "needs_attention": 2, "at_risk": 3, "critical": 4}
    worst = "empty"
    active = 0
    for d in dimensions:
        band = str(d.get("band") or "empty").lower()
        if band != "empty":
            active += 1
        if order.get(band, 0) >= order.get(worst, 0):
            worst = band
    labels = {
        "empty": "Not started",
        "healthy": "Healthy",
        "needs_attention": "Needs attention",
        "at_risk": "At risk",
        "critical": "Critical",
    }
    return {
        "band": worst,
        "label": labels.get(worst, worst.replace("_", " ").title()),
        "active_dimension_count": active,
        "description": (
            "Overall business health from operational discipline, execution quality, "
            "financial resilience, vendor reliability, and team participation."
            if active
            else "Activate business moments to start Life contributions."
        ),
    }
