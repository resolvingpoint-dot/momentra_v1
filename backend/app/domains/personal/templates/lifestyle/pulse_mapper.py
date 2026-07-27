"""Lifestyle pulse projection mapper."""
from __future__ import annotations

from typing import Any

from app.domains.personal.catalog import moment_type_name
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.templates.lifestyle.constants import MOMENT_TYPE_CODE
from app.domains.personal.templates.lifestyle.projection_builder import (
    LifestyleProjectionContext,
)
from app.domains.personal.templates.lifestyle.series_helpers import build_trends_30d

_LS = MOMENT_TYPE_CODE


def _status_label(score: int) -> str:
    if score >= 80:
        return "Thriving"
    if score >= 65:
        return "Balanced"
    return "Building"


def build_lifestyle_pulse(ctx: LifestyleProjectionContext) -> dict[str, Any] | None:
    if ctx.moment is None or ctx.signals is None:
        return None

    moment = ctx.moment
    signals = ctx.signals
    vitality = signals.momentum
    status = _status_label(vitality)
    runtime = ctx.runtime
    profile = ctx.profile

    money_by_qa = money_events_by_quick_add(ctx.money_events)
    recent_items = [
        map_timeline_to_recent_item(
            item,
            money=money_by_qa.get(item.quick_add_event_id),
            catalog=ctx.catalog,
        )
        for item in ctx.timeline[:8]
    ]

    spend_minor = sum(
        _money_minor(e)
        for e in ctx.money_events
        if (e.direction or "").upper() == "DEBIT"
    )
    segments: dict[str, int] = {}
    for e in ctx.money_events:
        if (e.direction or "").upper() != "DEBIT":
            continue
        key = (e.category_code or "lifestyle").lower()
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

    identity = profile.lifestyle_identity if profile else "Lifestyle Curator"
    style = profile.lifestyle_style if profile else "Balanced"
    energy = profile.lifestyle_energy if profile else "Steady"

    return {
        "hero_title": "Lifestyle Vitality",
        "hero_subtitle": runtime.runtime_summary if runtime and runtime.runtime_summary else "Designing a life that feels aligned day to day.",
        "vitality_label": energy,
        "vitality_trend": "↑ Rising" if vitality >= 70 else "→ Steady",
        "fulfillment_rate_percent": signals.wellbeing,
        "fulfillment_rate_suffix": status,
        "experience_signals_title": "Experience Signals",
        "pattern_insight_title": "Pattern Insight",
        "pattern_insight_body": runtime.runtime_summary if runtime else "Your lifestyle patterns are emerging from experiences and wellbeing logs.",
        "identity_label": identity,
        "style_label": style,
        "vitality_section_label": "Vitality Index",
        "fulfillment_rate_section_label": "Fulfillment Rate",
        "horizon_trajectory": profile.current_lifestyle_state if profile else "Steady",
        "horizon_opportunity": profile.primary_lifestyle_opportunity if profile else "More Experiences",
        "dashboard_card": {
            "moment_id": str(moment.id),
            "moment_name": moment.title or moment_type_name(_LS),
            "moment_type_code": _LS,
            "kpis": [
                {"kpi_id": "vitality", "label": "Vitality", "value": str(vitality)},
                {"kpi_id": "experiences", "label": "Experiences", "value": str(ctx.experience_count)},
            ],
            "recent_items": recent_items,
            "empty_recent_message": "No activity yet. Log your first lifestyle moment.",
        },
        "metrics": {
            "vitality_index": vitality,
            "vitality_delta_month": None,
            "status_band": status.upper().replace(" ", "_"),
            "axis_scores": {
                "joy": signals.social,
                "fulfillment": signals.wellbeing,
                "vitality": signals.energy,
                "exploration": signals.environment,
            },
            "capacity": {
                "lifestyle_spend_minor": spend_minor,
                "experience_count": ctx.experience_count,
                "discovery_count": ctx.discovery_count,
                "creative_session_count": ctx.expression_count,
            },
            "signals": [
                {"signal_id": "health", "trend": "UP" if signals.health >= 70 else "STABLE"},
                {"signal_id": "energy", "trend": "UP" if signals.energy >= 70 else "STABLE"},
                {"signal_id": "routine", "trend": "UP" if signals.routine >= 70 else "STABLE"},
                {"signal_id": "balance", "trend": "UP" if signals.balance >= 70 else "STABLE"},
            ],
            "financial_segments": financial_segments,
            "trends_30d": build_trends_30d(ctx.timeline),
            "score_drivers": [
                {"driver_id": "health", "label": "Health", "impact": signals.health - 50, "icon": "favorite"},
                {"driver_id": "energy", "label": "Energy", "impact": signals.energy - 50, "icon": "bolt"},
                {"driver_id": "routine", "label": "Routine", "impact": signals.routine - 50, "icon": "repeat"},
                {"driver_id": "balance", "label": "Balance", "impact": signals.balance - 50, "icon": "balance"},
            ],
            "gauges": [
                {"gauge_id": "health", "label": "Health", "percent": signals.health},
                {"gauge_id": "routine", "label": "Routine", "percent": signals.routine},
                {"gauge_id": "balance", "label": "Balance", "percent": signals.balance},
                {"gauge_id": "wellbeing", "label": "Wellbeing", "percent": signals.wellbeing},
            ],
            "opportunity": {
                "priority_id": "experience_depth",
                "title": "Deepen Experiences",
                "body": "More intentional experiences will lift fulfillment faster than passive spending.",
                "cta_label": "Log Experience",
            },
            "intelligence": {
                "pattern_id": "lifestyle_rhythm",
                "confidence_percent": min(95, 40 + ctx.timeline_count * 4),
                "quote": runtime.runtime_summary if runtime else "Your lifestyle system learns from experiences, wellbeing, and creative expression.",
            },
        },
    }
