"""Map Shared Experience projections to mobile/web active surface contracts."""
from __future__ import annotations

from app.domains.group import moment_store as store
from app.domains.group.templates.shared_experience.context import SharedExperienceContext
from app.domains.group.templates.shared_experience.memory_mapper import build_memory_projection
from app.domains.group.templates.shared_experience.moments_mapper import build_moments
from app.domains.group.templates.shared_experience.pulse_mapper import build_pulse
from app.domains.group.templates.shared_experience.life_mapper import build_life


def _pulse_score(ctx: SharedExperienceContext) -> float:
    score = 15.0
    score += min(40, ctx.guest_count * 8)
    score += min(25, ctx.plan_count * 5)
    score += min(20, ctx.memory_count * 4)
    if ctx.expense_total_minor > 0:
        score += 10
    return min(100.0, score)


def map_active_pulse(ctx: SharedExperienceContext) -> dict:
    pulse = build_pulse(ctx)
    stats = pulse.get("stats") or {}
    score = _pulse_score(ctx)
    return wrap_trip_pulse_to_active(
        pulse,
        moment_type=ctx.moment.moment_type or "SHARED_EXPERIENCE",
        moment_profile=ctx.experience_type.code,
        status=ctx.moment.status or "ACTIVE",
        stage=ctx.stage_badge,
        plan_count=ctx.plan_count,
        guest_count=ctx.guest_count,
        activity_count=len(ctx.activities),
        score=score,
        recent_events=[
            {
                "event_id": str(a.get("id") or ""),
                "module_code": str(a.get("activity_type") or "UPDATE"),
                "event_action": str(a.get("title") or ""),
                "event_time": a.get("occurred_at"),
            }
            for a in ctx.activities[:10]
        ],
        recommendations=(
            [
                {
                    "recommendation_id": "invite",
                    "recommendation_type": "ACTION",
                    "recommendation_category": "PEOPLE",
                    "title": "Invite your group",
                    "description": "Add participants to build momentum.",
                    "priority": "HIGH",
                    "recommendation_score": 90,
                }
            ]
            if ctx.guest_count == 0
            else []
        ),
    )


def wrap_trip_pulse_to_active(
    pulse: dict,
    *,
    moment_type: str = "SHARED_EXPERIENCE",
    moment_profile: str = "",
    status: str = "ACTIVE",
    stage: str | None = None,
    plan_count: int = 0,
    guest_count: int | None = None,
    activity_count: int = 0,
    score: float | None = None,
    recent_events: list | None = None,
    recommendations: list | None = None,
) -> dict:
    """Derive active pulse contract from cached trip pulse without a full rebuild."""
    stats = pulse.get("stats") or {}
    guests = guest_count if guest_count is not None else int(stats.get("guests_joined") or 0)
    plans = plan_count or int(stats.get("active_plan_items") or 0)
    expenses = int(stats.get("total_expenses_minor") or 0)
    if score is None:
        score = 15.0 + min(40, guests * 8) + min(25, plans * 5)
        if expenses > 0:
            score += 10
        score = min(100.0, score)
    return {
        "moment_id": pulse.get("moment_id"),
        "moment_type": moment_type,
        "moment_profile": moment_profile,
        "moment_name": pulse.get("trip_name") or pulse.get("moment_name"),
        "status": status,
        "stage": stage or pulse.get("stage_badge"),
        "pulse_data": {
            "pulse_score": score,
            "active_members": guests,
            "active_tasks": plans,
            "completion_percentage": score,
            "readiness_title": pulse.get("readiness_title"),
            "readiness_narrative": pulse.get("readiness_narrative"),
            "total_expenses_minor": expenses,
            "contributions_minor": stats.get("contributions_minor", 0),
        },
        "health_data": {
            "health_score": score,
            "health_status": pulse.get("readiness_title") or "Getting started",
            "people_score": min(100, guests * 15),
            "money_score": min(100, expenses // 1000),
            "activity_score": min(100, activity_count * 10),
        },
        "signals": [
            {
                "signal_id": "readiness",
                "signal_type": "READINESS",
                "signal_category": "PULSE",
                "signal_title": str(pulse.get("readiness_title") or "Getting started"),
                "signal_description": pulse.get("readiness_narrative"),
                "priority": "MEDIUM",
                "signal_score": score,
            }
        ],
        "recommendations": recommendations if recommendations is not None else [],
        "recent_events": recent_events or [],
    }


def map_active_moments(ctx: SharedExperienceContext) -> dict:
    moments = build_moments(ctx)
    hub = moments.get("operations_hub") or {}
    memories = store.list_items(ctx.moment, "memories")
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": ctx.moment.moment_type or "SHARED_EXPERIENCE",
        "moment_profile": ctx.experience_type.code,
        "moment_name": ctx.moment_name,
        "status": ctx.moment.status or "ACTIVE",
        "stage": ctx.stage_badge,
        "memories": [
            {
                "memory_id": str(m.get("id") or ""),
                "memory_type": "NOTE",
                "category": "HIGHLIGHT",
                "title": str(m.get("title") or "Memory"),
                "description": m.get("note"),
                "memory_date": m.get("created_at"),
                "created_at": m.get("created_at"),
                "highlight_score": 0.8,
            }
            for m in memories
        ],
        "recent_events": [
            {
                "event_id": str(a.get("id") or ""),
                "module_code": str(a.get("activity_type") or "UPDATE"),
                "event_action": str(a.get("title") or ""),
                "event_time": a.get("occurred_at"),
            }
            for a in ctx.activities[:10]
        ],
        "updates": [
            {
                "update_id": str(a.get("id") or ""),
                "category": str(a.get("activity_type") or "UPDATE"),
                "title": str(a.get("title") or ""),
                "description": str(a.get("subtitle") or ""),
                "status": "posted",
                "created_at": a.get("occurred_at"),
            }
            for a in ctx.activities[:5]
        ],
        "operations_hub": hub,
        "memory_hero": moments.get("memory_hero"),
    }


def map_active_memory(ctx: SharedExperienceContext) -> dict:
    projection = build_memory_projection(ctx)
    sections = projection.get("sections") or {}
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": ctx.moment.moment_type or "SHARED_EXPERIENCE",
        "moment_profile": ctx.experience_type.code,
        "moment_name": ctx.moment_name,
        "status": ctx.moment.status or "ACTIVE",
        "stage": ctx.stage_badge,
        "memories": [
            {
                "memory_id": str(m.get("id") or ""),
                "memory_type": "NOTE",
                "category": "HIGHLIGHT",
                "title": str(m.get("title") or "Memory"),
                "description": m.get("note"),
                "memory_date": m.get("created_at"),
                "created_at": m.get("created_at"),
                "highlight_score": 0.8,
            }
            for m in sections.get("best_moments", [])
        ],
        "patterns": [],
        "insights": [],
        "memory_projection": projection,
        "prompts": projection.get("prompts", []),
    }


def map_active_life(ctx: SharedExperienceContext) -> dict:
    life = build_life(ctx)
    return {
        "is_empty": False,
        "active_moment_count": 1,
        "moments": [
            {
                "moment_id": str(ctx.moment.id),
                "moment_type": ctx.moment.moment_type or "SHARED_EXPERIENCE",
                "moment_profile": ctx.experience_type.code,
                "moment_name": ctx.moment_name,
                "status": ctx.moment.status or "ACTIVE",
                "stage": ctx.stage_badge,
                "health_data": life.get("stats", {}),
                "journey_data": {"settlement_preview": life.get("settlement_preview")},
            }
        ],
        "insights": [],
        "settlement_preview": life.get("settlement_preview"),
    }
