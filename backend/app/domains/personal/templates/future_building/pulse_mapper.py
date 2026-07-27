"""Future Building pulse projection mapper."""
from __future__ import annotations

from typing import Any

from app.domains.personal.catalog import moment_type_name
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.templates.future_building.projection_builder import (
    FutureBuildingProjectionContext,
)
from app.domains.personal.templates.future_building.series_helpers import build_trends_30d

_FB = "FUTURE_BUILDING"


def _status_label(score: int) -> str:
    if score >= 80:
        return "Accelerating"
    if score >= 65:
        return "Building"
    return "Exploring"


def build_future_building_pulse(ctx: FutureBuildingProjectionContext) -> dict[str, Any] | None:
    if ctx.moment is None or ctx.signals is None:
        return None

    moment = ctx.moment
    signals = ctx.signals
    momentum = signals.momentum
    status = _status_label(momentum)
    runtime = ctx.runtime

    money_by_qa = money_events_by_quick_add(ctx.money_events)
    recent_items = [
        map_timeline_to_recent_item(
            item,
            money=money_by_qa.get(item.quick_add_event_id),
            catalog=ctx.catalog,
        )
        for item in ctx.timeline[:8]
    ]

    invested_minor = sum(
        _money_minor(e)
        for e in ctx.money_events
        if (e.direction or "").upper() == "DEBIT"
    )
    segments: dict[str, int] = {}
    for e in ctx.money_events:
        if (e.direction or "").upper() != "DEBIT":
            continue
        key = (e.category_code or "learning").lower()
        segments[key] = segments.get(key, 0) + _money_minor(e)
    total_seg = sum(segments.values()) or 1
    financial_segments = [
        {
            "category_id": cat,
            "category_name": cat.replace("_", " ").title(),
            "amount_minor": amt,
            "share_percent": int(round(amt / total_seg * 100)),
        }
        for cat, amt in sorted(segments.items(), key=lambda x: -x[1])[:4]
    ]

    identity = (
        ctx.profile.future_identity
        if ctx.profile and ctx.profile.future_identity
        else "Growth Architect"
    )

    return {
        "hero_title": "Future Momentum",
        "hero_subtitle": runtime.runtime_summary if runtime and runtime.runtime_summary else "Building your future through intentional progress.",
        "confidence_label": ctx.profile.future_confidence if ctx.profile else "Hopeful",
        "confidence_trend": "↑ Building",
        "momentum_rate_percent": momentum,
        "momentum_rate_suffix": status,
        "opportunity_signals_title": "Opportunity Signals",
        "pattern_insight_title": "Pattern Insight",
        "pattern_insight_body": runtime.runtime_summary if runtime else "Your future system is learning from every investment and milestone.",
        "identity_label": identity,
        "direction_label": ctx.profile.future_theme if ctx.profile else "Career Growth",
        "confidence_section_label": "Future Confidence",
        "momentum_rate_section_label": "Momentum Rate",
        "horizon_trajectory": ctx.profile.current_momentum_state if ctx.profile else "Building Momentum",
        "horizon_opportunity": ctx.profile.primary_opportunity_label if ctx.profile else "Deep Skill Development",
        "dashboard_card": {
            "moment_id": str(moment.id),
            "moment_name": moment.title or moment_type_name(_FB),
            "moment_type_code": _FB,
            "kpis": [
                {"kpi_id": "momentum", "label": "Momentum", "value": str(momentum)},
                {"kpi_id": "learning", "label": "Learning", "value": str(ctx.learning_count)},
            ],
            "recent_items": recent_items,
            "empty_recent_message": "No activity yet. Log your first future event.",
        },
        "metrics": {
            "momentum_index": momentum,
            "momentum_index_delta_month": None,
            "status_band": status.upper().replace(" ", "_"),
            "status_label": status,
            "axis_scores": {
                "learning": signals.consistency,
                "execution": signals.discipline,
                "milestones": signals.growth,
                "opportunities": signals.clarity,
                "confidence": signals.confidence,
            },
            "capacity_stats": {
                "investments_minor": invested_minor,
                "milestones": ctx.milestone_count,
                "learning_events": ctx.learning_count,
                "opportunities": ctx.opportunity_count,
            },
            "signals": [
                {"signal_id": "momentum", "label": "Momentum", "trend": "UP" if momentum >= 70 else "STABLE"},
                {"signal_id": "learning", "label": "Learning", "trend": "UP" if ctx.learning_count > 0 else "STABLE"},
                {"signal_id": "execution", "label": "Execution", "trend": "UP" if signals.discipline >= 70 else "STABLE"},
            ],
            "financial_segments": financial_segments,
            "trends_30d": build_trends_30d(ctx.timeline),
            "score_drivers": [
                {"driver_id": "learning", "label": "Learning", "impact": signals.consistency - 50, "fill_percent": signals.consistency},
                {"driver_id": "execution", "label": "Execution", "impact": signals.discipline - 50, "fill_percent": signals.discipline},
                {"driver_id": "milestones", "label": "Milestones", "impact": signals.growth - 50, "fill_percent": signals.growth},
            ],
            "gauges": [
                {"gauge_id": "growth", "label": "Growth", "percent": signals.growth},
                {"gauge_id": "execution", "label": "Execution", "percent": signals.discipline},
                {"gauge_id": "momentum", "label": "Momentum", "percent": momentum},
                {"gauge_id": "confidence", "label": "Confidence", "percent": signals.confidence},
            ],
            "opportunity": {
                "priority_id": "learning_velocity",
                "title": "Increase Learning Velocity",
                "body": "Consistent learning sessions compound into future readiness.",
                "cta_label": "Log Learning",
                "cta_event_type": "LEARNING",
                "growth_impact": 7,
                "confidence_impact": 5,
            },
            "intelligence": {
                "insight_text": runtime.runtime_summary if runtime else "Your future momentum is building through learning and execution.",
                "confidence_percent": min(95, 40 + ctx.timeline_count * 4),
            },
            "recent_activity": recent_items,
        },
    }
