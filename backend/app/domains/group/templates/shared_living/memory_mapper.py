"""Memory projection mapper for Shared Living."""
from __future__ import annotations

from app.domains.group import trip_schemas as t
from app.domains.group.templates.shared_living.context import SharedLivingContext
from app.domains.group.templates.shared_living.projection_helpers import build_memory_hub


def build_memory_projection(ctx: SharedLivingContext) -> dict:
    memories = ctx.memories
    hub = build_memory_hub(ctx)
    best = [
        {
            "id": str(m.get("id") or ""),
            "title": str(m.get("title") or "Memory"),
            "note": m.get("note"),
            "created_at": str(m.get("created_at") or ""),
            "created_by_name": str(m.get("created_by_name") or "Someone"),
        }
        for m in memories[:5]
    ]
    return {
        "moment_id": str(ctx.moment.id),
        "moment_name": ctx.moment_name,
        "moment_type": "SHARED_LIVING",
        "profile_badge": ctx.profile_badge,
        "memory_count": len(memories),
        "home_story": best[:3],
        "expense_story": [
            {
                "id": e.get("id"),
                "title": e.get("description"),
                "amount_minor": e.get("amount_minor"),
                "created_at": e.get("created_at"),
            }
            for e in ctx.expenses[:5]
        ],
        "chore_story": ctx.chores[:5],
        "resident_highlights": [
            {
                "id": r.get("id"),
                "full_name": r.get("full_name") or r.get("display_name") or r.get("name"),
                "role": r.get("assigned_role") or r.get("resident_role") or r.get("role"),
            }
            for r in ctx.residents[:10]
        ],
        "house_updates": ctx.updates[:5],
        "lessons": [hub.get("lessons_pattern")] if hub.get("lessons_pattern") else [],
        "insights": [{"insight": hub.get("intelligence", {}).get("insight")}]
        if hub.get("intelligence", {}).get("insight")
        else [],
        "ai_summary": {"status": "stub", "summary": hub.get("intelligence", {}).get("insight")},
        "hero": hub.get("hero") or t.GroupMemoryHero(moment_name=ctx.moment_name).model_dump(mode="json"),
        "timeline": hub.get("timeline", []),
        "milestone_wall": hub.get("milestone_wall", []),
        "people_impact": hub.get("people_impact", []),
        "gallery": hub.get("gallery", []),
        "lessons_pattern": hub.get("lessons_pattern", ""),
        "group_identity": hub.get("group_identity", ""),
        "highlights": hub.get("highlights", []),
        "intelligence": hub.get("intelligence", {"metrics": [], "insight": ""}),
        "budget_reflection": hub.get("budget_reflection"),
        "sections": {
            "photos": {"count": len(hub.get("gallery") or []), "items": hub.get("gallery") or []},
            "best_moments": best,
            "milestones": hub.get("milestone_wall") or [],
            "timeline_replay": hub.get("timeline") or [],
            "ai_recap": {
                "status": "stub",
                "summary": hub.get("intelligence", {}).get("insight"),
                "lessons": [hub.get("lessons_pattern")] if hub.get("lessons_pattern") else [],
            },
        },
        "prompts": list(ctx.profile.memory_prompts),
    }
