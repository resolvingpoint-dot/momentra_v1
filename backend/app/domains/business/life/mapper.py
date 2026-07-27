"""Map active business moments into Life contribution slices (not a dashboard)."""
from __future__ import annotations

from typing import Any

from app.domains.business.life.signals import (
    aggregate_life_band,
    build_life_dimensions,
    build_life_journey,
    derive_life_signals,
)
from app.domains.business.models import BusinessMoments

# Team Ops contribution slices — always present keys
TEAM_OPS_SLICES = (
    "team_health",
    "governance",
    "collaboration",
    "execution",
    "participation",
    "recognition",
    "issues",
)

# Runway contribution slices — always present keys when runway moments exist
RUNWAY_SLICES = (
    "financial_health",
    "stability",
    "cash_flow",
    "growth",
    "discipline",
    "risk",
    "forecast_accuracy",
)

# Business Operations contribution slices
OPS_SLICES = (
    "operational_health",
    "budget_discipline",
    "approval_efficiency",
    "vendor_health",
    "issue_load",
    "improvement_momentum",
    "governance",
    "execution",
)

ALL_LIFE_SLICES = TEAM_OPS_SLICES + RUNWAY_SLICES + OPS_SLICES

_SLICE_ACTION_MAP: dict[str, set[str]] = {
    "governance": {"APPROVAL_REQUEST", "ESCALATION", "REVIEW"},
    "collaboration": {"MEETING", "TEAM_UPDATE", "NOTE"},
    "execution": {"TEAM_UPDATE", "REVIEW", "MEMBER_UPDATE"},
    "participation": {"PARTICIPATION", "MEMBER_UPDATE"},
    "recognition": {"RECOGNITION"},
    "issues": {"ISSUE", "ESCALATION"},
}


def _empty_slice(key: str) -> dict[str, Any]:
    return {
        "key": key,
        "label": key.replace("_", " ").title(),
        "state": "empty",
        "count": 0,
        "items": [],
    }


def build_team_ops_slices(
    *,
    moment_id: str,
    moment_name: str,
    activities: list[dict[str, Any]],
    open_issues: int = 0,
    pending_approvals: int = 0,
    escalation_count: int = 0,
    member_count: int = 0,
) -> dict[str, dict[str, Any]]:
    """Seven Life slices for TEAM_OPERATIONS — no invented narrative."""
    slices: dict[str, dict[str, Any]] = {k: _empty_slice(k) for k in TEAM_OPS_SLICES}

    # team_health — rule band from raw counts only
    if member_count <= 0 and open_issues == 0 and pending_approvals == 0:
        band, state = "empty", "empty"
    elif escalation_count > 0 or open_issues >= 5:
        band, state = "at_risk", "partial"
    elif open_issues > 0 or pending_approvals > 3:
        band, state = "needs_attention", "partial"
    else:
        band, state = "healthy", "complete"
    slices["team_health"] = {
        "key": "team_health",
        "label": "Team Health",
        "state": state,
        "count": member_count + open_issues + pending_approvals,
        "band": band,
        "inputs": {
            "members": member_count,
            "open_issues": open_issues,
            "pending_approvals": pending_approvals,
            "escalations": escalation_count,
        },
        "items": [],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }

    for slice_key, types in _SLICE_ACTION_MAP.items():
        items = [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in activities
            if (a.get("action_type") or "") in types
        ]
        slices[slice_key] = {
            "key": slice_key,
            "label": slice_key.replace("_", " ").title(),
            "state": "empty" if not items else "complete",
            "count": len(items),
            "items": items[:20],
            "source_moment_id": moment_id,
            "source_moment_name": moment_name,
        }

    return slices


def build_runway_slices(
    *,
    moment_id: str,
    moment_name: str,
    activities: list[dict[str, Any]],
    runway_months: float | None = None,
    risk_count: int = 0,
    cash_available_minor: int = 0,
    monthly_burn_minor: int = 0,
    collection_rate_percent: int | None = None,
    alert_threshold_months: float | None = None,
) -> dict[str, dict[str, Any]]:
    """Seven Life slices for BUSINESS_RUNWAY — contribution only."""
    slices: dict[str, dict[str, Any]] = {k: _empty_slice(k) for k in RUNWAY_SLICES}
    threshold = float(alert_threshold_months or 6)

    if cash_available_minor <= 0 and monthly_burn_minor <= 0:
        band, state = "empty", "empty"
    elif runway_months is not None and runway_months < 1:
        band, state = "critical", "partial"
    elif runway_months is not None and runway_months < threshold:
        band, state = "needs_attention", "partial"
    elif risk_count > 0:
        band, state = "at_risk", "partial"
    else:
        band, state = "healthy", "complete"

    # Omit null keys so strict clients (e.g. Map<String, Int>) never see null literals.
    fin_inputs: dict[str, Any] = {
        "risk_count": risk_count,
        "cash_available_minor": cash_available_minor,
        "monthly_burn_minor": monthly_burn_minor,
    }
    if runway_months is not None:
        # Prefer int when whole so numeric maps stay Int-safe on older clients.
        fin_inputs["runway_months"] = (
            int(runway_months) if float(runway_months).is_integer() else float(runway_months)
        )

    slices["financial_health"] = {
        "key": "financial_health",
        "label": "Financial Health",
        "state": state,
        "count": 1 if band != "empty" else 0,
        "band": band,
        "inputs": fin_inputs,
        "items": [],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }

    stability_state = "empty" if runway_months is None else "complete"
    stability_payload: dict[str, Any] = {
        "key": "stability",
        "label": "Stability",
        "state": stability_state,
        "count": 1 if runway_months is not None else 0,
        "alert_threshold_months": threshold,
        "items": [],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    if runway_months is not None:
        stability_payload["runway_months"] = (
            int(runway_months) if float(runway_months).is_integer() else float(runway_months)
        )
    slices["stability"] = stability_payload

    inflows = [a for a in activities if a.get("action_type") == "CASH_INFLOW"]
    burns = [a for a in activities if a.get("action_type") == "EXPENSE_BURN"]
    slices["cash_flow"] = {
        "key": "cash_flow",
        "label": "Cash Flow",
        "state": "empty" if not inflows and not burns else "complete",
        "count": len(inflows) + len(burns),
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in (inflows + burns)[:20]
        ],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }

    growth_items = [
        a for a in activities if a.get("action_type") == "FINANCIAL_UPDATE"
    ]
    slices["growth"] = {
        "key": "growth",
        "label": "Growth",
        "state": "empty" if not growth_items else "complete",
        "count": len(growth_items),
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in growth_items[:20]
        ],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }

    slices["discipline"] = {
        "key": "discipline",
        "label": "Discipline",
        "state": "empty" if not burns else "complete",
        "count": len(burns),
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in burns[:20]
        ],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }

    risk_items = [a for a in activities if a.get("action_type") == "RUNWAY_RISK"]
    slices["risk"] = {
        "key": "risk",
        "label": "Risk",
        "state": "empty" if not risk_items and risk_count == 0 else "partial" if risk_count else "complete",
        "count": max(risk_count, len(risk_items)),
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in risk_items[:20]
        ],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }

    forecast_items = [
        a
        for a in activities
        if a.get("action_type") == "FINANCIAL_UPDATE"
        and "forecast" in (a.get("title") or "").lower()
    ]
    slices["forecast_accuracy"] = {
        "key": "forecast_accuracy",
        "label": "Forecast Accuracy",
        "state": "empty" if not forecast_items else "complete",
        "count": len(forecast_items),
        "collection_rate_percent": collection_rate_percent,
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in forecast_items[:20]
        ],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }

    return slices


def build_ops_slices(
    *,
    moment_id: str,
    moment_name: str,
    activities: list[dict[str, Any]],
    budget_usage_percent: float = 0.0,
    open_issue_count: int = 0,
    critical_issue_count: int = 0,
    pending_approvals: int = 0,
    vendor_count: int = 0,
    critical_vendor_count: int = 0,
    completed_improvement_count: int = 0,
    improvement_count: int = 0,
    health_band: str = "EMPTY",
    monitoring_level: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Eight Life slices for BUSINESS_OPERATIONS — contribution only."""
    slices: dict[str, dict[str, Any]] = {k: _empty_slice(k) for k in OPS_SLICES}
    band = (health_band or "EMPTY").upper()
    state = "empty" if band == "EMPTY" else ("partial" if band != "HEALTHY" else "complete")
    slices["operational_health"] = {
        "key": "operational_health",
        "label": "Operational Health",
        "state": state,
        "count": 1 if band != "EMPTY" else 0,
        "band": band.lower() if band != "EMPTY" else "empty",
        "items": [],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    slices["budget_discipline"] = {
        "key": "budget_discipline",
        "label": "Budget Discipline",
        "state": "empty" if budget_usage_percent <= 0 else "complete",
        "count": 1 if budget_usage_percent > 0 else 0,
        "budget_usage_percent": budget_usage_percent,
        "items": [],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    slices["approval_efficiency"] = {
        "key": "approval_efficiency",
        "label": "Approval Efficiency",
        "state": "empty" if pending_approvals <= 0 else "partial",
        "count": pending_approvals,
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in activities
            if a.get("action_type") == "OPS_APPROVAL_REQUEST"
        ][:20],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    slices["vendor_health"] = {
        "key": "vendor_health",
        "label": "Vendor Health",
        "state": "empty" if vendor_count <= 0 else ("partial" if critical_vendor_count else "complete"),
        "count": vendor_count,
        "critical_count": critical_vendor_count,
        "items": [],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    slices["issue_load"] = {
        "key": "issue_load",
        "label": "Issue Load",
        "state": "empty" if open_issue_count <= 0 else "partial",
        "count": open_issue_count,
        "critical_count": critical_issue_count,
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in activities
            if a.get("action_type") == "ISSUE_RISK"
        ][:20],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    slices["improvement_momentum"] = {
        "key": "improvement_momentum",
        "label": "Improvement Momentum",
        "state": "empty" if (completed_improvement_count + improvement_count) <= 0 else "complete",
        "count": completed_improvement_count + improvement_count,
        "completed": completed_improvement_count,
        "items": [],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    # Note: governance/execution keys also exist on Team Ops — merge carefully in map_life
    slices["governance"] = {
        "key": "governance",
        "label": "Governance",
        "state": "empty" if not monitoring_level and pending_approvals <= 0 else "complete",
        "count": (1 if monitoring_level else 0) + pending_approvals,
        "monitoring_level": monitoring_level,
        "items": [],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    exec_items = [
        a
        for a in activities
        if a.get("action_type")
        in {"SPEND_ENTRY", "VENDOR_UPDATE", "OPERATIONAL_IMPROVEMENT", "ISSUE_RISK"}
    ]
    slices["execution"] = {
        "key": "execution",
        "label": "Execution",
        "state": "empty" if not exec_items else "complete",
        "count": len(exec_items),
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title") or "",
                "occurred_at": str(a.get("occurred_at") or ""),
                "source_moment_id": moment_id,
            }
            for a in exec_items[:20]
        ],
        "source_moment_id": moment_id,
        "source_moment_name": moment_name,
    }
    return slices


def map_life(
    moments: list[BusinessMoments],
    *,
    team_ops_contributions: list[dict[str, Any]] | None = None,
    runway_contributions: list[dict[str, Any]] | None = None,
    ops_contributions: list[dict[str, Any]] | None = None,
) -> dict:
    moment_summaries = []
    for m in moments:
        moment_summaries.append({
            "moment_id": str(m.moment_id),
            "moment_type": m.moment_type,
            "moment_name": m.moment_name or "",
            "status": m.status or "draft",
        })

    # Always emit all Life slice keys (Team Ops + Runway)
    slices: dict[str, dict[str, Any]] = {k: _empty_slice(k) for k in ALL_LIFE_SLICES}
    for contrib in team_ops_contributions or []:
        for key, payload in (contrib.get("slices") or {}).items():
            if key not in slices:
                continue
            existing = slices[key]
            items = list(existing.get("items") or []) + list(payload.get("items") or [])
            count = existing.get("count", 0) + payload.get("count", 0)
            state = "empty" if count == 0 else (
                payload.get("state") if payload.get("state") in ("partial", "complete") else "complete"
            )
            merged = {
                **existing,
                "count": count,
                "items": items[:40],
                "state": state if count else "empty",
            }
            if key == "team_health" and payload.get("band"):
                # Prefer worst band across moments
                order = {"empty": 0, "healthy": 1, "needs_attention": 2, "at_risk": 3}
                prev = existing.get("band", "empty")
                nxt = payload.get("band", "empty")
                merged["band"] = nxt if order.get(nxt, 0) >= order.get(prev, 0) else prev
                merged["inputs"] = payload.get("inputs") or existing.get("inputs")
            slices[key] = merged

    for contrib in runway_contributions or []:
        for key, payload in (contrib.get("slices") or {}).items():
            if key not in slices:
                continue
            existing = slices[key]
            items = list(existing.get("items") or []) + list(payload.get("items") or [])
            count = existing.get("count", 0) + payload.get("count", 0)
            state = "empty" if count == 0 else (
                payload.get("state") if payload.get("state") in ("partial", "complete") else "complete"
            )
            merged = {
                **existing,
                **{k: v for k, v in payload.items() if k not in ("items", "count", "state")},
                "count": count,
                "items": items[:40],
                "state": state if count else "empty",
            }
            if key == "financial_health" and payload.get("band"):
                order = {"empty": 0, "healthy": 1, "needs_attention": 2, "at_risk": 3, "critical": 4}
                prev = existing.get("band", "empty")
                nxt = payload.get("band", "empty")
                merged["band"] = nxt if order.get(nxt, 0) >= order.get(prev, 0) else prev
                merged["inputs"] = payload.get("inputs") or existing.get("inputs")
            slices[key] = merged

    for contrib in ops_contributions or []:
        for key, payload in (contrib.get("slices") or {}).items():
            if key not in slices:
                continue
            existing = slices[key]
            items = list(existing.get("items") or []) + list(payload.get("items") or [])
            count = existing.get("count", 0) + payload.get("count", 0)
            state = "empty" if count == 0 else (
                payload.get("state") if payload.get("state") in ("partial", "complete") else "complete"
            )
            merged = {
                **existing,
                **{k: v for k, v in payload.items() if k not in ("items", "count", "state")},
                "count": count,
                "items": items[:40],
                "state": state if count else "empty",
            }
            if key == "operational_health" and payload.get("band"):
                order = {"empty": 0, "healthy": 1, "needs_attention": 2, "at_risk": 3}
                prev = str(existing.get("band", "empty")).lower()
                nxt = str(payload.get("band", "empty")).lower()
                merged["band"] = nxt if order.get(nxt, 0) >= order.get(prev, 0) else prev
            slices[key] = merged

    dimensions = build_life_dimensions(slices)
    journey = build_life_journey(slices)
    health = aggregate_life_band(dimensions)

    return {
        "active_moment_count": len(moments),
        "moments": moment_summaries,
        "health": health,
        "signals": derive_life_signals(moments, slices=slices),
        "dimensions": dimensions,
        "journey": journey,
        "slices": slices,
    }
