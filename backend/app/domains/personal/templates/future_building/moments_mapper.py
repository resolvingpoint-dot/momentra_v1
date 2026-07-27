"""Future Building moments tab projection mapper."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.domains.personal.catalog import moment_type_id, moment_type_name, normalize_moment_type_code
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.templates.future_building.projection_builder import (
    FutureBuildingProjectionContext,
)
from app.domains.personal.templates.future_building.series_helpers import (
    build_money_journey_series,
    money_journey_highlights,
)

_FB = "FUTURE_BUILDING"
_ACTIVE = {"ACTIVE"}


def _map_moment(ctx: FutureBuildingProjectionContext) -> dict[str, Any] | None:
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


def _setup_summary(ctx: FutureBuildingProjectionContext) -> dict[str, Any]:
    profile = ctx.profile
    if profile is not None:
        return {
            "future_theme": profile.future_theme,
            "current_momentum_state": profile.current_momentum_state,
            "future_values": list(profile.future_values or []),
            "friction_sources": list(profile.friction_sources or []),
            "momentum_drivers": list(profile.momentum_drivers or []),
            "identity_chips": [profile.future_identity] if profile.future_identity else [],
        }
    return {
        "future_theme": "Career Growth",
        "current_momentum_state": "Just Starting",
        "future_values": [],
        "friction_sources": [],
        "momentum_drivers": [],
        "identity_chips": ["Future Builder"],
    }


def _progress_blocks(ctx: FutureBuildingProjectionContext) -> dict[str, Any]:
    signals = ctx.signals
    momentum = signals.momentum if signals else 70
    runtime = ctx.runtime
    label = runtime.runtime_state_label if runtime else "Getting started"
    return {
        "label": label,
        "subtitle": runtime.runtime_summary if runtime else "Log progress to build your future picture.",
        "blocks": [
            {"key": "momentum", "label": "Momentum", "value": str(momentum), "tone": "positive" if momentum >= 70 else "neutral"},
            {"key": "learning", "label": "Learning", "value": str(ctx.learning_count), "tone": "neutral"},
            {"key": "milestones", "label": "Milestones", "value": str(ctx.milestone_count), "tone": "neutral"},
        ],
    }


def _build_moment_projection(ctx: FutureBuildingProjectionContext) -> dict[str, Any]:
    signals = ctx.signals
    momentum = signals.momentum if signals else 70
    runtime = ctx.runtime
    status = "ACCELERATING" if momentum >= 80 else "BUILDING" if momentum >= 65 else "EXPLORING"
    status_label = status.title()

    money_by_qa = money_events_by_quick_add(ctx.money_events)
    journey_timeline = [
        map_timeline_to_recent_item(
            item, money=money_by_qa.get(item.quick_add_event_id), catalog=ctx.catalog
        )
        for item in ctx.timeline[:12]
    ]

    invested_minor = sum(
        _money_minor(e)
        for e in ctx.money_events
        if (e.direction or "").upper() == "DEBIT"
    )

    journey_hero = {
        "journey_score": momentum,
        "status_band": status,
        "status_label": status_label,
        "phases": [
            {"phase_id": "exploring", "label": "Exploring", "is_active": status == "EXPLORING"},
            {"phase_id": "building", "label": "Building", "is_active": status == "BUILDING"},
            {"phase_id": "accelerating", "label": "Accelerating", "is_active": status == "ACCELERATING"},
        ],
        "insight_body": runtime.runtime_summary if runtime else "Your future growth journey is taking shape.",
        "milestones": ctx.milestone_count,
        "learning_events": ctx.learning_count,
        "invested_minor": invested_minor,
        "opportunities": ctx.opportunity_count,
    }

    best_moments = [
        {
            "card_id": str(h.moment_highlight_id),
            "title": h.highlight_title,
            "period_label": h.impact_label or h.highlight_type,
            "impact_lines": [h.impact_label] if h.impact_label else [],
            "icon": "milestone",
        }
        for h in ctx.highlights[:6]
    ]
    if not best_moments and ctx.timeline:
        best_moments = [
            {
                "card_id": str(ctx.timeline[0].timeline_id),
                "title": "Recent progress",
                "period_label": "This week",
                "impact_lines": ["Momentum logged"],
                "icon": "trending_up",
            }
        ]

    turning_points = [
        {
            "turning_point_id": str(tp.turning_point_id),
            "title": tp.turning_point_title,
            "subtitle": tp.turning_point_description or tp.turning_point_type,
            "icon": (tp.turning_point_type or "pivot").lower(),
            "period_label": tp.occurred_at.strftime("%b %Y") if tp.occurred_at else None,
        }
        for tp in ctx.turning_points[:6]
    ]

    highest_month, highest_area = money_journey_highlights(ctx.money_events)
    money_journey = {
        "title": "Money Journey",
        "period_label": "Last 6 Months",
        "series": build_money_journey_series(ctx.money_events),
        "total_invested_minor": invested_minor,
        "highest_month": highest_month,
        "highest_area": highest_area,
    }

    return {
        "journey_hero": journey_hero,
        "journey_timeline": journey_timeline,
        "money_journey": money_journey,
        "best_moments": best_moments,
        "turning_points": turning_points,
    }


def build_future_building_moments(
    ctx: FutureBuildingProjectionContext,
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
            "moment_type_code": _FB,
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
        "moment_type_code": _FB,
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


def build_future_building_moments_detail(ctx: FutureBuildingProjectionContext) -> dict[str, Any]:
    """Aggregate moments/home detail block for mobile clients."""
    base = build_future_building_moments(ctx)
    projection = base.get("moment_projection")
    if projection is None:
        return {"metrics": None}
    return {"metrics": projection}
