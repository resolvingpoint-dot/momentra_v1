"""Presentation helpers for Business Runway projection sections."""
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


def rule_based_runway_health(
    *,
    runway_months: float | None,
    risk_count: int,
    alert_threshold_months: float | None,
    cash_available_minor: int,
    monthly_burn_minor: int,
) -> dict[str, Any]:
    """v1 rule-based runway health — no fabricated composite scores."""
    threshold = float(alert_threshold_months or 6)
    if cash_available_minor <= 0 and monthly_burn_minor <= 0:
        label, band = "Not started", "empty"
    elif runway_months is not None and runway_months < 1:
        label, band = "Critical", "critical"
    elif runway_months is not None and runway_months < threshold:
        label, band = "Needs attention", "needs_attention"
    elif risk_count > 0:
        label, band = "At risk", "at_risk"
    elif runway_months is None and monthly_burn_minor <= 0:
        label, band = "Cashflow positive", "healthy"
    else:
        label, band = "Healthy", "healthy"

    return {
        "label": label,
        "band": band,
        "rule": "runway_months_and_risk_thresholds",
        "inputs": {
            "runway_months": runway_months,
            "risk_count": risk_count,
            "alert_threshold_months": threshold,
            "cash_available_minor": cash_available_minor,
            "monthly_burn_minor": monthly_burn_minor,
        },
    }


def format_minor_amount(minor: int, currency: str = "INR") -> str:
    major = minor / 100
    return f"{currency} {major:,.2f}"
