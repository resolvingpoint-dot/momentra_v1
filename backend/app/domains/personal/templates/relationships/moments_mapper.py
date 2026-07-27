"""Relationships moments tab projection mapper."""
from __future__ import annotations

from datetime import timezone
from typing import Any

from app.domains.personal.catalog import moment_type_id, moment_type_name, normalize_moment_type_code
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.templates.relationships.constants import MOMENT_TYPE_CODE
from app.domains.personal.templates.relationships.projection_builder import (
    RelationshipsProjectionContext,
)
from app.domains.personal.templates.relationships.series_helpers import (
    build_money_journey_series,
    money_journey_highlights,
)

_RS = MOMENT_TYPE_CODE
_ACTIVE = {"ACTIVE"}


def _map_relationships_timeline_item(
    item: Any,
    *,
    money: Any | None = None,
    catalog: Any | None = None,
) -> dict[str, Any]:
    mapped = map_timeline_to_recent_item(item, money=money, catalog=catalog)
    event_type = mapped.get("activity_type") or getattr(item, "event_type", "")
    return {
        "id": mapped["id"],
        "event_type": event_type,
        "category_label": (event_type or "Activity").replace("_", " ").title(),
        "detail_line": mapped.get("impact_label") or mapped.get("title") or "",
        "relative_time": mapped.get("relative_time") or "Recent",
        "captured_at": mapped.get("occurred_at")
        or getattr(item, "event_occurred_at", "").isoformat(),
        "edit_event_type": event_type,
        "can_edit": True,
        "can_delete": True,
        "image_url": None,
    }


def _map_moment(ctx: RelationshipsProjectionContext) -> dict[str, Any] | None:
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


def _setup_summary(ctx: RelationshipsProjectionContext) -> dict[str, Any]:
    profile = ctx.profile
    if profile is not None:
        return {
            "relationship_focus": profile.relationship_focus,
            "current_relationship_state": profile.current_relationship_state,
            "desired_connection_types": list(profile.desired_connection_types or []),
            "neglected_areas": list(profile.neglected_relationship_areas or []),
            "strength_factors": list(profile.relationship_strength_factors or []),
            "investment_areas": list(profile.relationship_investment_areas or []),
            "identity_chips": [profile.relationship_identity] if profile.relationship_identity else [],
        }
    return {
        "relationship_focus": "Family",
        "current_relationship_state": "Connected",
        "desired_connection_types": [],
        "neglected_areas": [],
        "strength_factors": [],
        "investment_areas": [],
        "identity_chips": ["Connection Builder"],
    }


def _progress_blocks(ctx: RelationshipsProjectionContext) -> dict[str, Any]:
    signals = ctx.signals
    bond = signals.relationship_health if signals else 68
    runtime = ctx.runtime
    label = runtime.runtime_state_label if runtime else "Getting started"
    return {
        "label": label,
        "subtitle": runtime.runtime_summary if runtime else "Log relationship moments to shape your journey.",
        "blocks": [
            {"key": "bond", "label": "Bond", "value": str(bond), "tone": "positive" if bond >= 70 else "neutral"},
            {"key": "connections", "label": "Connections", "value": str(ctx.connection_count), "tone": "neutral"},
            {"key": "support", "label": "Support", "value": str(ctx.support_count), "tone": "neutral"},
        ],
    }


def _build_moment_projection(ctx: RelationshipsProjectionContext) -> dict[str, Any]:
    signals = ctx.signals
    bond = signals.relationship_health if signals else 68
    runtime = ctx.runtime
    status = "THRIVING" if bond >= 80 else "CONNECTED" if bond >= 65 else "BUILDING"
    status_label = status.title()

    money_by_qa = money_events_by_quick_add(ctx.money_events)
    journey_timeline = [
        _map_relationships_timeline_item(
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
        "journey_score": bond,
        "status_band": status,
        "phases": [
            {"phase_id": "building", "label": "Building", "is_active": status == "BUILDING"},
            {"phase_id": "connected", "label": "Connected", "is_active": status == "CONNECTED"},
            {"phase_id": "thriving", "label": "Thriving", "is_active": status == "THRIVING"},
        ],
        "insight_body": runtime.runtime_summary if runtime else "Your relationship journey is taking shape.",
        "connections": ctx.connection_count,
        "support": ctx.support_count,
        "experiences": ctx.experience_count,
        "spend_minor": spend_minor,
    }

    best_moments = [
        {
            "card_id": str(h.moment_highlight_id),
            "title": h.highlight_title,
            "period_label": h.impact_label or h.highlight_type,
            "tag_label": h.highlight_type or "Moment",
            "star_rating": 5,
            "image_url": None,
            "impact_lines": [h.impact_label] if h.impact_label else [],
            "icon": "favorite",
        }
        for h in ctx.highlights[:6]
    ]
    if not best_moments and ctx.timeline:
        best_moments = [
            {
                "card_id": str(ctx.timeline[0].timeline_id),
                "title": "Recent relationship moment",
                "period_label": "This week",
                "tag_label": "Connection",
                "star_rating": 4,
                "image_url": None,
                "impact_lines": ["Connection logged"],
                "icon": "group",
            }
        ]

    turning_points = [
        {
            "turning_point_id": str(tp.turning_point_id),
            "title": tp.turning_point_title,
            "subtitle": tp.turning_point_description or tp.turning_point_type,
            "icon": (tp.turning_point_type or "shift").lower(),
            "date_label": tp.occurred_at.strftime("%b %Y") if tp.occurred_at else None,
            "accent_color": "primary",
        }
        for tp in ctx.turning_points[:6]
    ]

    highest_month, highest_area = money_journey_highlights(ctx.money_events)
    money_journey = {
        "title": "Relationship Spend Journey",
        "period_label": "Last 6 Months",
        "series": build_money_journey_series(ctx.money_events),
        "total_spend_minor": spend_minor,
        "highest_month": highest_month,
        "lowest_month": {"label": "—", "amount_minor": 0},
        "highest_area_label": highest_area.get("label", "—"),
        "highest_area_amount_minor": highest_area.get("amount_minor", 0),
        "lowest_return_label": "—",
        "lowest_return_amount_minor": 0,
    }

    important_conversations = [
        item for item in journey_timeline
        if (item.get("event_type") or "").upper() == "CONNECTION"
    ][:6]

    milestones = [
        item for item in journey_timeline
        if (item.get("event_type") or "").upper() in {"RELATIONSHIP_INVESTMENT", "SHARED_EXPERIENCE"}
    ][:6]

    shared_memories = [
        item for item in journey_timeline
        if (item.get("event_type") or "").upper() == "SHARED_EXPERIENCE"
    ][:6]

    return {
        "journey_hero": journey_hero,
        "journey_timeline": journey_timeline,
        "money_journey": money_journey,
        "best_moments": best_moments,
        "turning_points": turning_points,
        "milestones": milestones,
        "important_conversations": important_conversations,
        "relationship_journey": journey_timeline[:8],
        "shared_memories": shared_memories,
    }


def build_relationships_moments(
    ctx: RelationshipsProjectionContext,
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
            "moment_type_code": _RS,
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
        "moment_type_code": _RS,
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


def build_relationships_moments_detail(ctx: RelationshipsProjectionContext) -> dict[str, Any]:
    base = build_relationships_moments(ctx)
    projection = base.get("moment_projection")
    if projection is None:
        return {"metrics": None}
    return {"metrics": projection}
