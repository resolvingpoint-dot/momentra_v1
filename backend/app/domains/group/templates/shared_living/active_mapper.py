"""Map Shared Living projections to mobile/web active surface contracts."""
from __future__ import annotations

from app.domains.group import moment_store as store
from app.domains.group.templates.shared_living.context import SharedLivingContext
from app.domains.group.templates.shared_living.life_mapper import build_life
from app.domains.group.templates.shared_living.memory_mapper import build_memory_projection
from app.domains.group.templates.shared_living.moments_mapper import build_moments
from app.domains.group.templates.shared_living.projection_helpers import activities_newest
from app.domains.group.templates.shared_living.pulse_mapper import build_pulse


def _pulse_score(ctx: SharedLivingContext) -> float:
    score = 15.0
    score += min(35, ctx.resident_count * 12)
    score += min(25, ctx.expense_count * 8)
    score += min(15, ctx.task_count * 5)
    if ctx.contribution_total_minor > 0:
        score += 10
    return min(100.0, score)


def map_active_pulse(ctx: SharedLivingContext) -> dict:
    pulse = build_pulse(ctx)
    stats = pulse.get("stats") or {}
    score = _pulse_score(ctx)
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_LIVING",
        "moment_profile": ctx.profile.code,
        "moment_name": ctx.moment_name,
        "status": ctx.moment.status or "ACTIVE",
        "stage": ctx.stage_badge,
        "pulse_data": {
            "pulse_score": score,
            "active_members": stats.get("residents_joined", 0),
            "active_tasks": stats.get("tasks_open", 0),
            "completion_percentage": pulse.get("health_percent", score),
            "readiness_title": pulse.get("readiness_title"),
            "readiness_narrative": pulse.get("readiness_narrative"),
            "expenses_total_minor": pulse.get("expenses_total_minor", 0),
            "resident_count": pulse.get("resident_count", 0),
        },
        "health_data": {
            "health_score": score,
            "health_status": pulse.get("readiness_title") or "Home rhythm",
            "people_score": min(100, ctx.resident_count * 20),
            "money_score": min(100, ctx.expense_count * 15),
            "activity_score": min(100, len(ctx.activities) * 10),
        },
        "signals": [
            {
                "signal_id": "household",
                "signal_type": "HOUSEHOLD",
                "signal_category": "PULSE",
                "signal_title": pulse.get("readiness_title") or "Home rhythm",
                "signal_description": pulse.get("readiness_narrative"),
                "priority": "MEDIUM",
                "signal_score": score,
            }
        ],
        "recommendations": [
            {
                "recommendation_id": "invite",
                "recommendation_type": "ACTION",
                "recommendation_category": "PEOPLE",
                "title": "Invite residents",
                "description": "Add the people you live with.",
                "priority": "HIGH",
                "recommendation_score": 90,
            }
        ]
        if ctx.resident_count == 0
        else [],
        "recent_events": [
            {
                "event_id": str(a.get("id") or ""),
                "module_code": str(a.get("activity_type") or "UPDATE"),
                "event_action": str(a.get("title") or ""),
                "event_time": a.get("occurred_at"),
            }
            for a in ctx.activities[:10]
        ],
        "next_best_action": pulse.get("next_best_action"),
        "alerts": pulse.get("alerts", []),
    }


def map_active_moments(ctx: SharedLivingContext) -> dict:
    moments = build_moments(ctx)
    hub = moments.get("operations_hub") or {}
    memories = [m for m in store.list_items(ctx.moment, "memories") if not m.get("deleted")]
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_LIVING",
        "moment_profile": ctx.profile.code,
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
            for a in activities_newest(ctx.activities, limit=10)
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
            for a in activities_newest(ctx.activities, limit=5)
        ],
        "operations_hub": hub,
        "memory_hero": moments.get("memory_hub", {}).get("hero"),
        "journey_hero": {"title": ctx.moment_name, "subtitle": ctx.home_description or "Your shared home journey"},
        "expense_timeline": moments.get("expense_timeline", []),
        "chore_timeline": moments.get("chore_timeline", []),
    }


def map_active_memory(ctx: SharedLivingContext) -> dict:
    projection = build_memory_projection(ctx)
    sections = projection.get("sections") or {}
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_LIVING",
        "moment_profile": ctx.profile.code,
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
        "insights": projection.get("insights", []),
        "memory_projection": projection,
        "prompts": projection.get("prompts", []),
        "ai_summary": projection.get("ai_summary"),
    }


def map_active_life(ctx: SharedLivingContext) -> dict:
    life = build_life(ctx)
    return {
        "is_empty": False,
        "active_moment_count": 1,
        "moments": [
            {
                "moment_id": str(ctx.moment.id),
                "moment_type": "SHARED_LIVING",
                "moment_profile": ctx.profile.code,
                "moment_name": ctx.moment_name,
                "status": ctx.moment.status or "ACTIVE",
                "stage": ctx.stage_badge,
                "health_data": life.get("stats", {}),
                "journey_data": {"settlement_preview": life.get("settlement_preview")},
                "dimensions": {
                    "household_harmony": life.get("household_harmony"),
                    "expense_fairness": life.get("expense_fairness"),
                    "chore_balance": life.get("chore_balance"),
                },
            }
        ],
        "insights": life.get("recommendations", []),
        "settlement_preview": life.get("settlement_preview"),
    }
