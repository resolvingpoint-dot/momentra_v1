"""Pulse projection mapper for Business Runway — deterministic section tree."""
from __future__ import annotations

from app.domains.business.templates.business_runway.context import RunwayContext
from app.domains.business.templates.business_runway.section_helpers import (
    event_item,
    filter_actions,
    rule_based_runway_health,
    section_state,
)
from app.domains.business.templates.business_runway.signals import derive_signals

_INFLOW = {"CASH_INFLOW"}
_BURN = {"EXPENSE_BURN"}
_FINANCIAL = {"FINANCIAL_UPDATE"}
_RISK = {"RUNWAY_RISK"}
_DECISION = {"STRATEGIC_DECISION"}


def _merge_health(ctx: RunwayContext, fallback: dict) -> dict:
    return fallback


def build_pulse(ctx: RunwayContext) -> dict:
    activities = list(ctx.activities or [])
    recent = [event_item(a) for a in activities[:20]]
    health = _merge_health(
        ctx,
        rule_based_runway_health(
            runway_months=ctx.runway_months,
            risk_count=ctx.risk_count,
            alert_threshold_months=ctx.alert_threshold_months,
            cash_available_minor=ctx.cash_available_minor,
            monthly_burn_minor=ctx.monthly_burn_setup_minor or ctx.net_burn_minor,
        ),
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
        trends = projection.trend_items
    else:
        attention = []
        if ctx.risk_count > 0:
            attention.append({
                "kind": "runway_risks",
                "label": f"{ctx.risk_count} open risk{'s' if ctx.risk_count != 1 else ''}",
                "count": ctx.risk_count,
            })
        signals = derive_signals(ctx)
        next_action = None
        trends = []

    effective_burn = ctx.monthly_burn_setup_minor or ctx.net_burn_minor
    has_financials = ctx.cash_available_minor > 0 or effective_burn > 0

    return {
        "moment_id": str(ctx.moment_id),
        "moment_type": ctx.moment_type,
        "moment_name": ctx.moment_name,
        "runway_name": ctx.runway_name,
        "status": ctx.status,
        "is_active": ctx.is_active,
        "operating_currency": ctx.operating_currency,
        "stats": {
            "cash_available_minor": ctx.cash_available_minor,
            "monthly_burn_minor": effective_burn,
            "monthly_revenue_minor": ctx.monthly_revenue_minor,
            "total_inflow_minor": ctx.total_inflow_minor,
            "total_burn_minor": ctx.total_burn_minor,
            "net_burn_minor": ctx.net_burn_minor,
            "runway_months": ctx.runway_months,
            "risk_count": ctx.risk_count,
            "decision_count": ctx.decision_count,
            "collection_rate_percent": ctx.collection_rate_percent,
        },
        "hero": {
            "state": section_state(count=1 if ctx.runway_name else 0),
            "title": ctx.runway_name or ctx.moment_name or "Business Runway",
            "subtitle": "Financial runway",
            "status": ctx.status,
            "is_active": ctx.is_active,
            "runway_health": health,
        },
        "runway_health": {
            "state": section_state(count=1 if health.get("band") != "empty" else 0),
            "health": health,
        },
        "cash_position": {
            "state": section_state(count=1 if ctx.cash_available_minor > 0 else 0),
            "cash_available_minor": ctx.cash_available_minor,
            "operating_currency": ctx.operating_currency,
        },
        "monthly_burn": {
            "state": section_state(count=1 if effective_burn > 0 else 0),
            "monthly_burn_minor": effective_burn,
            "activity_burn_minor": ctx.total_burn_minor,
            "operating_currency": ctx.operating_currency,
        },
        "revenue_trend": {
            "state": section_state(count=1 if ctx.monthly_revenue_minor > 0 else 0),
            "monthly_revenue_minor": ctx.monthly_revenue_minor,
            "revenue_status": ctx.revenue_status,
            "operating_currency": ctx.operating_currency,
        },
        "collection_rate": {
            "state": section_state(
                count=1 if ctx.collection_rate_percent is not None else 0
            ),
            "collection_rate_percent": ctx.collection_rate_percent,
        },
        "runway_months": {
            "state": section_state(count=1 if ctx.runway_months is not None else 0),
            "runway_months": ctx.runway_months,
            "runway_goal_months": ctx.runway_goal_months,
            "alert_threshold_months": ctx.alert_threshold_months,
        },
        "cash_movement": {
            "state": section_state(
                count=1 if (ctx.total_inflow_minor > 0 or ctx.total_burn_minor > 0) else 0
            ),
            "total_inflow_minor": ctx.total_inflow_minor,
            "total_burn_minor": ctx.total_burn_minor,
            "net_burn_minor": ctx.net_burn_minor,
            "operating_currency": ctx.operating_currency,
        },
        "kpis": {
            "state": section_state(count=1 if has_financials else 0),
            "cash_available_minor": ctx.cash_available_minor,
            "monthly_burn_minor": effective_burn,
            "monthly_revenue_minor": ctx.monthly_revenue_minor,
            "runway_months": ctx.runway_months,
            "risk_count": ctx.risk_count,
            "collection_rate_percent": ctx.collection_rate_percent,
        },
        "forecast": {
            "state": section_state(
                count=1 if ctx.runway_goal_months is not None else 0
            ),
            "runway_goal_months": ctx.runway_goal_months,
            "projected_runway_months": ctx.runway_months,
            "alert_threshold_months": ctx.alert_threshold_months,
        },
        "attention_items": {
            "state": section_state(count=len(attention), has_attention=bool(attention)),
            "items": attention,
        },
        "trends": {
            "state": section_state(count=len(trends)),
            "items": trends,
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
