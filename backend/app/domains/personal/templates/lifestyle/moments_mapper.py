"""Lifestyle moments tab projection mapper."""
from __future__ import annotations

from datetime import timezone
from typing import Any

from app.domains.personal.catalog import moment_type_id, moment_type_name, normalize_moment_type_code
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.templates.lifestyle.constants import MOMENT_TYPE_CODE
from app.domains.personal.templates.lifestyle.projection_builder import (
    LifestyleProjectionContext,
)
from app.domains.personal.templates.lifestyle.series_helpers import (
    build_money_journey_series,
    money_journey_highlights,
)

_LS = MOMENT_TYPE_CODE
_ACTIVE = {"ACTIVE"}


def _map_lifestyle_timeline_item(
    item: Any,
    *,
    money: Any | None = None,
    catalog: Any | None = None,
) -> dict[str, Any]:
    mapped = map_timeline_to_recent_item(item, money=money, catalog=catalog)
    return {
        "id": mapped["id"],
        "event_type": mapped.get("activity_type") or getattr(item, "event_type", ""),
        "title": mapped["title"],
        "group_label": mapped.get("relative_time") or "Recent",
        "impact_line": mapped.get("impact_label"),
        "impact_tone": "positive" if mapped.get("impact_label") else "neutral",
        "thumbnail_url": None,
        "captured_at": mapped.get("occurred_at")
        or getattr(item, "event_occurred_at", "").isoformat(),
    }


def _map_moment(ctx: LifestyleProjectionContext) -> dict[str, Any] | None:
    moment = ctx.moment
    if moment is None:
        return None
    code = normalize_moment_type_code(moment.moment_type or "")
    is_active = moment.status in _ACTIVE
    return {
        "moment_id": str(moment.id),
        "moment_type_id": moment_type_id(code),
        "moment_type_code": code or None,
        "moment_name": moment.title or moment_type_name(code) or "Untitled",
        "moment_description": moment.description,
        "status": moment.status,
        "current_runtime_state": moment.setup_state,
        "activated_at": (
            moment.updated_at.isoformat() if is_active and moment.updated_at else None
        ),
    }


def _setup_summary(ctx: LifestyleProjectionContext) -> dict[str, Any]:
    profile = ctx.profile
    if profile is not None:
        return {
            "lifestyle_style": profile.lifestyle_style,
            "current_lifestyle_state": profile.current_lifestyle_state,
            "desired_vectors": list(profile.desired_lifestyle_vectors or []),
            "neglected_areas": list(profile.neglected_lifestyle_areas or []),
            "enrichment_factors": list(profile.lifestyle_enrichment_factors or []),
            "identity_chips": [profile.lifestyle_identity] if profile.lifestyle_identity else [],
        }
    return {
        "lifestyle_style": "Balanced",
        "current_lifestyle_state": "Steady",
        "desired_vectors": [],
        "neglected_areas": [],
        "enrichment_factors": [],
        "identity_chips": ["Lifestyle Curator"],
    }


def _progress_blocks(ctx: LifestyleProjectionContext) -> dict[str, Any]:
    signals = ctx.signals
    vitality = signals.momentum if signals else 68
    runtime = ctx.runtime
    label = runtime.runtime_state_label if runtime else "Getting started"
    return {
        "label": label,
        "subtitle": runtime.runtime_summary if runtime else "Log lifestyle moments to shape your journey.",
        "blocks": [
            {"key": "vitality", "label": "Vitality", "value": str(vitality), "tone": "positive" if vitality >= 70 else "neutral"},
            {"key": "experiences", "label": "Experiences", "value": str(ctx.experience_count), "tone": "neutral"},
            {"key": "wellbeing", "label": "Wellbeing", "value": str(ctx.wellbeing_count), "tone": "neutral"},
        ],
    }


def _build_moment_projection(ctx: LifestyleProjectionContext) -> dict[str, Any]:
    signals = ctx.signals
    vitality = signals.momentum if signals else 68
    runtime = ctx.runtime
    status = "THRIVING" if vitality >= 80 else "BALANCED" if vitality >= 65 else "BUILDING"
    status_label = status.title()

    money_by_qa = money_events_by_quick_add(ctx.money_events)
    journey_timeline = [
        _map_lifestyle_timeline_item(
            item, money=money_by_qa.get(item.quick_add_event_id), catalog=ctx.catalog
        )
        for item in ctx.timeline[:12]
    ]

    spend_minor = sum(
        _money_minor(e)
        for e in ctx.money_events
        if (e.direction or "").upper() == "DEBIT"
    )

    journey_hero = {
        "journey_score": vitality,
        "status_band": status,
        "status_label": status_label,
        "phases": [
            {"phase_id": "building", "label": "Building", "is_active": status == "BUILDING"},
            {"phase_id": "balanced", "label": "Balanced", "is_active": status == "BALANCED"},
            {"phase_id": "thriving", "label": "Thriving", "is_active": status == "THRIVING"},
        ],
        "insight_body": runtime.runtime_summary if runtime else "Your lifestyle journey is taking shape.",
        "experience_count": ctx.experience_count,
        "discovery_count": ctx.discovery_count,
        "creative_session_count": ctx.expression_count,
        "lifestyle_spend_minor": spend_minor,
    }

    best_moments = [
        {
            "card_id": str(h.moment_highlight_id),
            "title": h.highlight_title,
            "period_label": h.impact_label or h.highlight_type,
            "impact_lines": [h.impact_label] if h.impact_label else [],
            "icon": "experience",
        }
        for h in ctx.highlights[:6]
    ]
    if not best_moments and ctx.timeline:
        best_moments = [
            {
                "card_id": str(ctx.timeline[0].timeline_id),
                "title": "Recent lifestyle moment",
                "period_label": "This week",
                "impact_lines": ["Experience logged"],
                "icon": "spa",
            }
        ]

    turning_points = [
        {
            "turning_point_id": str(tp.turning_point_id),
            "title": tp.turning_point_title,
            "subtitle": tp.turning_point_description or tp.turning_point_type,
            "icon": (tp.turning_point_type or "shift").lower(),
            "occurred_label": tp.occurred_at.strftime("%b %Y") if tp.occurred_at else None,
        }
        for tp in ctx.turning_points[:6]
    ]

    _highest_month, highest_area = money_journey_highlights(ctx.money_events)
    money_journey = {
        "title": "Lifestyle Spend Journey",
        "period_label": "Last 6 Months",
        "series": build_money_journey_series(ctx.money_events),
        "total_spend_minor": spend_minor,
        "highest_month": _highest_month,
        "lowest_month": {"label": "—", "amount_minor": 0},
        "highest_area_label": highest_area.get("label", "—"),
        "highest_area_amount_minor": highest_area.get("amount_minor", 0),
        "lowest_return_label": "—",
        "lowest_return_amount_minor": 0,
    }

    return {
        "journey_hero": journey_hero,
        "journey_timeline": journey_timeline,
        "money_journey": money_journey,
        "best_moments": best_moments,
        "turning_points": turning_points,
    }


def build_lifestyle_moments(
    ctx: LifestyleProjectionContext,
    *,
    accounts_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    accounts_summary = accounts_summary or {
        "total_accounts": 0,
        "active_accounts": 0,
        "accounts": [],
    }
    if ctx.moment is None:
        return {
            "moment_type_code": _LS,
            "status": "EMPTY",
            "moment": None,
            "setup_summary": _setup_summary(ctx),
            "recent_events": [],
            "accounts_summary": accounts_summary,
            "timeline_count": 0,
            "last_activity_at": None,
            "progress": _progress_blocks(ctx),
            "moment_projection": None,
        }

    moment = ctx.moment
    status = "ACTIVE" if moment.status in _ACTIVE else "SETUP"
    money_by_qa = money_events_by_quick_add(ctx.money_events)
    recent_events = [
        map_timeline_to_recent_item(
            item, money=money_by_qa.get(item.quick_add_event_id), catalog=ctx.catalog
        )
        for item in ctx.timeline[:8]
    ]

    last_at: str | None = None
    if ctx.timeline:
        when = ctx.timeline[0].event_occurred_at
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        last_at = when.isoformat()

    projection = _build_moment_projection(ctx) if status == "ACTIVE" else None

    return {
        "moment_type_code": _LS,
        "status": status,
        "moment": _map_moment(ctx),
        "setup_summary": _setup_summary(ctx),
        "recent_events": recent_events,
        "accounts_summary": accounts_summary,
        "timeline_count": ctx.timeline_count,
        "last_activity_at": last_at,
        "progress": _progress_blocks(ctx),
        "moment_projection": projection,
    }


def build_lifestyle_moments_detail(ctx: LifestyleProjectionContext) -> dict[str, Any]:
    base = build_lifestyle_moments(ctx)
    projection = base.get("moment_projection")
    if projection is None:
        return {"metrics": None}
    return {"metrics": projection}
