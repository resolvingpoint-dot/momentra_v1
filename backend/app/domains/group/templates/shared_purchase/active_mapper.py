"""Map Shared Purchase projections to mobile/web active surface contracts."""
from __future__ import annotations

from app.domains.group import moment_store as store
from app.domains.group.templates.shared_purchase.context import SharedPurchaseContext
from app.domains.group.templates.shared_purchase.life_mapper import build_life
from app.domains.group.templates.shared_purchase.memory_mapper import build_memory_projection
from app.domains.group.templates.shared_purchase.moments_mapper import build_moments
from app.domains.group.templates.shared_purchase.pulse_mapper import build_pulse


def _pulse_score(ctx: SharedPurchaseContext) -> float:
    score = 15.0
    score += min(35, ctx.contributor_count * 10)
    score += min(30, ctx.contribution_progress_percent * 0.3)
    score += min(15, ctx.milestone_count * 5)
    if ctx.expense_total_minor > 0:
        score += 10
    return min(100.0, score)


def map_active_pulse(ctx: SharedPurchaseContext) -> dict:
    pulse = build_pulse(ctx)
    stats = pulse.get("stats") or {}
    score = _pulse_score(ctx)
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_PURCHASE",
        "moment_profile": ctx.profile.code,
        "moment_name": ctx.moment_name,
        "status": ctx.moment.status or "ACTIVE",
        "stage": ctx.stage_badge,
        "pulse_data": {
            "pulse_score": score,
            "active_members": stats.get("contributors_joined", 0),
            "active_tasks": stats.get("plan_items", 0),
            "completion_percentage": pulse.get("contribution_progress_percent", score),
            "readiness_title": pulse.get("readiness_title"),
            "readiness_narrative": pulse.get("readiness_narrative"),
            "target_amount_minor": pulse.get("target_amount_minor", 0),
            "total_contributed_minor": pulse.get("total_contributed_minor", 0),
            "amount_remaining_minor": pulse.get("amount_remaining_minor", 0),
            "funding_percent": pulse.get("funding_percent", 0),
        },
        "health_data": {
            "health_score": score,
            "health_status": pulse.get("readiness_title") or "Getting funded",
            "people_score": min(100, ctx.contributor_count * 20),
            "money_score": min(100, int(pulse.get("contribution_progress_percent", 0))),
            "activity_score": min(100, len(ctx.activities) * 10),
        },
        "signals": [
            {
                "signal_id": "funding",
                "signal_type": "FUNDING",
                "signal_category": "PULSE",
                "signal_title": pulse.get("readiness_title") or "Getting funded",
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
                "title": "Invite contributors",
                "description": "Add people who will fund this purchase.",
                "priority": "HIGH",
                "recommendation_score": 90,
            }
        ]
        if ctx.contributor_count == 0
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
        "settlement_preview": pulse.get("settlement_preview"),
        "next_best_action": pulse.get("next_best_action"),
        "alerts": pulse.get("alerts", []),
    }


def map_active_moments(ctx: SharedPurchaseContext) -> dict:
    moments = build_moments(ctx)
    hub = moments.get("operations_hub") or {}
    memories = [m for m in store.list_items(ctx.moment, "memories") if not m.get("deleted")]
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_PURCHASE",
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
        "memory_hero": moments.get("memory_hub", {}).get("hero"),
        "journey_hero": moments.get("journey_hero"),
        "contribution_timeline": moments.get("contribution_timeline", []),
        "purchase_milestones": moments.get("purchase_milestones", []),
    }


def map_active_memory(ctx: SharedPurchaseContext) -> dict:
    projection = build_memory_projection(ctx)
    sections = projection.get("sections") or {}
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_PURCHASE",
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


def map_active_life(ctx: SharedPurchaseContext) -> dict:
    life = build_life(ctx)
    return {
        "is_empty": False,
        "active_moment_count": 1,
        "moments": [
            {
                "moment_id": str(ctx.moment.id),
                "moment_type": "SHARED_PURCHASE",
                "moment_profile": ctx.profile.code,
                "moment_name": ctx.moment_name,
                "status": ctx.moment.status or "ACTIVE",
                "stage": ctx.stage_badge,
                "health_data": life.get("stats", {}),
                "journey_data": {"settlement_preview": life.get("settlement_preview")},
                "dimensions": {
                    "financial_alignment": life.get("financial_alignment"),
                    "contribution_fairness": life.get("contribution_fairness"),
                    "ownership_clarity": life.get("ownership_clarity"),
                },
            }
        ],
        "insights": life.get("recommendations", []),
        "settlement_preview": life.get("settlement_preview"),
    }
