"""Memory projection mapper — first-class memory sections for Shared Experience."""
from __future__ import annotations

from app.domains.group import moment_store as store
from app.domains.group import trip_schemas as t
from app.domains.group.templates.shared_experience.context import SharedExperienceContext


def build_memory_projection(ctx: SharedExperienceContext) -> dict:
    memories = store.list_items(ctx.moment, "memories")
    guests = store.guest_summaries(ctx.moment)
    best_moments = [
        {
            "id": str(m.get("id") or ""),
            "title": str(m.get("title") or "Memory"),
            "note": m.get("note"),
            "created_at": str(m.get("created_at") or ""),
            "created_by_name": str(m.get("created_by_name") or "Someone"),
        }
        for m in memories[:5]
    ]
    attendance = [
        {"id": g["id"], "name": g["full_name"], "status": g.get("status", "invited")}
        for g in guests
    ]
    return {
        "moment_id": str(ctx.moment.id),
        "moment_name": ctx.moment_name,
        "profile_badge": ctx.profile_badge,
        "memory_count": len(memories),
        "hero": t.GroupMemoryHero(moment_name=ctx.moment_name).model_dump(mode="json"),
        "sections": {
            "photos": {"count": 0, "items": []},
            "best_moments": best_moments,
            "attendance": attendance,
            "timeline_replay": [
                {"id": a.get("id"), "title": a.get("title"), "occurred_at": a.get("occurred_at")}
                for a in ctx.activities[:20]
            ],
            "highlights": best_moments[:3],
            "ai_recap": {"status": "stub", "summary": None, "lessons": []},
            "shared_feed": best_moments,
        },
        "prompts": list(ctx.experience_type.memory_prompts),
    }


def build_memory_list(ctx: SharedExperienceContext) -> list[dict]:
    return [
        t.GroupMomentMemoryResponse(
            id=str(row.get("id") or ""),
            moment_id=str(ctx.moment.id),
            created_by_user_id=str(row.get("created_by_user_id") or ""),
            created_by_name=str(row.get("created_by_name") or "Someone"),
            title=str(row.get("title") or "Memory"),
            note=row.get("note"),
            created_at=str(row.get("created_at") or ""),
        ).model_dump(mode="json")
        for row in store.list_items(ctx.moment, "memories")
    ]
