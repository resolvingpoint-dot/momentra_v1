"""Moments projection mapper for Business Runway — distinct from Pulse timeline."""
from __future__ import annotations

from app.domains.business.templates.business_runway.context import RunwayContext
from app.domains.business.templates.business_runway.section_helpers import (
    event_item,
    filter_actions,
    section_state,
)

_INFLOW = {"CASH_INFLOW"}
_BURN = {"EXPENSE_BURN"}
_FINANCIAL = {"FINANCIAL_UPDATE"}
_RISK = {"RUNWAY_RISK"}
_DECISION = {"STRATEGIC_DECISION"}


def _funding_events(activities: list[dict]) -> list[dict]:
    items = filter_actions(activities, _INFLOW)
    funding = []
    for item in items:
        text = f"{item.get('title', '')} {item.get('subtitle', '')}".lower()
        if "fund" in text or "invest" in text or "loan" in text:
            funding.append(item)
    return funding


def build_moments(ctx: RunwayContext) -> dict:
    activities = list(ctx.activities or [])
    inflows = filter_actions(activities, _INFLOW)
    burns = filter_actions(activities, _BURN)
    financial = filter_actions(activities, _FINANCIAL)
    risks = filter_actions(activities, _RISK)
    decisions = filter_actions(activities, _DECISION)
    funding = _funding_events(activities)
    milestones = risks + decisions
    revenue_updates = [
        a for a in financial if "revenue" in (a.get("title") or "").lower()
    ] or financial
    forecast_changes = [
        a
        for a in financial
        if "forecast" in (a.get("title") or "").lower()
        or "forecast" in (a.get("subtitle") or "").lower()
    ]
    timeline = [event_item(a) for a in activities]
    recent = [event_item(a) for a in activities[:10]]

    return {
        "moment_id": str(ctx.moment_id),
        "moment_type": ctx.moment_type,
        "moment_name": ctx.moment_name,
        "runway_name": ctx.runway_name,
        "status": ctx.status,
        "runway_hub": {
            "cash_available_minor": ctx.cash_available_minor,
            "monthly_burn_minor": ctx.monthly_burn_setup_minor or ctx.net_burn_minor,
            "runway_months": ctx.runway_months,
            "risk_count": ctx.risk_count,
            "decision_count": ctx.decision_count,
            "operating_currency": ctx.operating_currency,
        },
        "journey_hero": {
            "state": section_state(count=1 if (ctx.runway_name or ctx.moment_name) else 0),
            "title": ctx.runway_name or ctx.moment_name or "Business Runway",
            "subtitle": "Financial journey",
            "activity_count": ctx.activity_count,
            "is_active": ctx.is_active,
            "runway_months": ctx.runway_months,
        },
        "cash_available": {
            "state": section_state(count=1 if ctx.cash_available_minor > 0 else 0),
            "cash_available_minor": ctx.cash_available_minor,
            "operating_currency": ctx.operating_currency,
        },
        "runway_months": {
            "state": section_state(count=1 if ctx.runway_months is not None else 0),
            "runway_months": ctx.runway_months,
            "runway_goal_months": ctx.runway_goal_months,
        },
        "timeline": {
            "state": section_state(count=len(timeline)),
            "items": timeline,
        },
        "revenue_updates": {
            "state": section_state(count=len(revenue_updates)),
            "items": revenue_updates[:20],
        },
        "forecast_changes": {
            "state": section_state(count=len(forecast_changes)),
            "items": forecast_changes[:20],
        },
        "expense_events": {
            "state": section_state(count=len(burns)),
            "items": burns[:20],
        },
        "inflow_events": {
            "state": section_state(count=len(inflows)),
            "items": inflows[:20],
        },
        "funding_events": {
            "state": section_state(count=len(funding)),
            "items": funding[:20],
        },
        "invoices": {
            "state": "empty",
            "items": [],
            "empty_reason": "no_invoice_handler_v1",
        },
        "payroll": {
            "state": "empty",
            "items": [],
            "empty_reason": "no_payroll_handler_v1",
        },
        "milestones": {
            "state": section_state(count=len(milestones)),
            "items": milestones[:20],
        },
        "recent_activity": {
            "state": section_state(count=len(recent)),
            "items": recent,
        },
    }
