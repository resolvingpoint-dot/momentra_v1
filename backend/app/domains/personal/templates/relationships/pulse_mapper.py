"""Relationships pulse projection mapper."""
from __future__ import annotations

from typing import Any

from app.domains.personal.catalog import moment_type_name
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.templates.relationships.constants import MOMENT_TYPE_CODE
from app.domains.personal.templates.relationships.projection_builder import (
    RelationshipsProjectionContext,
)
from app.domains.personal.templates.relationships.series_helpers import build_trends_30d

_RS = MOMENT_TYPE_CODE


def _status_label(score: int) -> str:
    if score >= 80:
        return "Thriving"
    if score >= 65:
        return "Connected"
    return "Building"


def build_relationships_pulse(ctx: RelationshipsProjectionContext) -> dict[str, Any] | None:
    if ctx.moment is None or ctx.signals is None:
        return None

    moment = ctx.moment
    signals = ctx.signals
    bond = signals.relationship_health
    status = _status_label(bond)
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
        key = (e.category_code or "relationships").lower()
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

    identity = profile.relationship_identity if profile else "Connection Builder"
    focus = profile.relationship_focus if profile else "Family"
    energy = profile.relationship_energy if profile else "Steady"
    network_label = "Stable" if signals.trust >= 65 else "Evolving"

    radar_axes = [
        {"axis_id": "connection", "label": "Connection", "score": signals.connection},
        {"axis_id": "trust", "label": "Trust", "score": signals.trust},
        {"axis_id": "communication", "label": "Communication", "score": signals.communication},
        {"axis_id": "support", "label": "Support", "score": signals.support},
        {"axis_id": "presence", "label": "Presence", "score": signals.presence},
        {"axis_id": "growth", "label": "Growth", "score": signals.growth},
    ]

    insight_body = (
        runtime.runtime_summary
        if runtime and runtime.runtime_summary
        else "Your relationship patterns are emerging from connection and support logs."
    )
    captured_count = ctx.connection_count + ctx.support_count + ctx.experience_count

    return {
        "hero_title": "Relationship Health",
        "hero_subtitle": (
            runtime.runtime_summary
            if runtime and runtime.runtime_summary
            else "Building stronger connections with intention."
        ),
        "vitality_label": energy,
        "vitality_trend": "↑ Rising" if bond >= 70 else "→ Steady",
        "bond_rate_percent": bond,
        "bond_rate_suffix": status,
        "connection_signals_title": "Connection Signals",
        "pattern_insight_title": "Pattern Insight",
        "pattern_insight_body": insight_body,
        "identity_label": identity,
        "focus_label": focus,
        "vitality_section_label": "Relationship Energy",
        "bond_rate_section_label": "Bond Index",
        "network_stability_label": network_label,
        "bond_section_label": "Bond Index",
        "network_section_label": "Support Network",
        "connection_signals": {
            "captured_count": captured_count,
            "high_bond_count": max(0, ctx.connection_count),
        },
        "horizon_trajectory": profile.current_relationship_state if profile else "Connected",
        "horizon_opportunity": (
            profile.primary_relationship_opportunity if profile else "Quality Time"
        ),
        "dashboard_card": {
            "moment_id": str(moment.id),
            "moment_name": moment.title or moment_type_name(_RS),
            "moment_type_code": _RS,
            "kpis": [
                {"kpi_id": "bond", "label": "Bond Index", "value": str(bond)},
                {"kpi_id": "connections", "label": "Connections", "value": str(ctx.connection_count)},
            ],
            "recent_items": recent_items,
            "empty_recent_message": "No activity yet. Log your first relationship moment.",
        },
        "metrics": {
            "bond_index": bond,
            "bond_index_delta_month": None,
            "status_band": status.upper().replace(" ", "_"),
            "network_stability_label": network_label,
            "radar_axes": radar_axes,
            "hero_stats": {
                "connections": ctx.connection_count,
                "support": ctx.support_count,
                "experiences": ctx.experience_count,
                "spend_minor": spend_minor,
            },
            "signal_chips": [
                {"signal_id": "connection", "label": "Connection", "trend": "UP" if signals.connection >= 70 else "STABLE"},
                {"signal_id": "trust", "label": "Trust", "trend": "UP" if signals.trust >= 70 else "STABLE"},
                {"signal_id": "support", "label": "Support", "trend": "UP" if signals.support >= 70 else "STABLE"},
                {"signal_id": "growth", "label": "Growth", "trend": "UP" if signals.growth >= 70 else "STABLE"},
            ],
            "connection_count": ctx.connection_count,
            "spend_minor": spend_minor,
            "recent_activity": recent_items,
            "financial_segments": financial_segments,
            "trends_30d": build_trends_30d(ctx.timeline),
            "gauges": [
                {"gauge_id": "connection", "percent": signals.connection},
                {"gauge_id": "trust", "percent": signals.trust},
                {"gauge_id": "support", "percent": signals.support},
                {"gauge_id": "presence", "percent": signals.presence},
            ],
            "opportunity": {
                "title": "Deepen Connection",
                "body": (
                    profile.primary_relationship_opportunity
                    if profile and profile.primary_relationship_opportunity
                    else "More intentional connection time will lift bond index fastest."
                ),
                "cta_label": "Log Connection",
                "impact_chips": ["Trust", "Presence", "Fulfillment"],
            },
            "intelligence": {
                "body": (
                    runtime.runtime_summary
                    if runtime
                    else "Your relationship patterns are emerging from connection and support logs."
                ),
                "confidence_percent": min(95, 40 + ctx.timeline_count * 4),
            },
            "analysis_signals": [
                {"signal_id": "connection", "label": "Connection", "icon": "group"},
                {"signal_id": "trust", "label": "Trust", "icon": "favorite"},
                {"signal_id": "support", "label": "Support", "icon": "volunteer_activism"},
                {"signal_id": "growth", "label": "Growth", "icon": "trending_up"},
            ],
            "quick_capture_actions": [
                {"action_code": "CONNECTION", "label": "Conversation", "is_primary": True},
                {"action_code": "SUPPORT", "label": "Support", "is_primary": False},
                {"action_code": "SHARED_EXPERIENCE", "label": "Shared Experience", "is_primary": False},
                {"action_code": "RELATIONSHIP_INVESTMENT", "label": "Gift", "is_primary": False},
                {"action_code": "ADJUST", "label": "Reflection", "is_primary": False},
            ],
        },
    }
