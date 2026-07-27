"""Memory projection mapper for Shared Purchase."""
from __future__ import annotations

from app.domains.group import moment_store as store
from app.domains.group import trip_schemas as t
from app.domains.group.templates.shared_purchase.context import SharedPurchaseContext


def build_memory_projection(ctx: SharedPurchaseContext) -> dict:
    memories = [m for m in store.list_items(ctx.moment, "memories") if not m.get("deleted")]
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
        "moment_type": "SHARED_PURCHASE",
        "profile_badge": ctx.profile_badge,
        "memory_count": len(memories),
        "purchase_story": best[:3],
        "contribution_story": [
            {"id": c.get("id"), "title": c.get("title"), "amount_minor": c.get("amount_minor"), "created_at": c.get("created_at")}
            for c in ctx.contributions[:5]
        ],
        "decision_story": ctx.decisions[:5],
        "ownership_story": ctx.ownership_shares[:5],
        "milestone_timeline": ctx.milestones[:10],
        "participant_highlights": store.guest_summaries(ctx.moment)[:10],
        "spending_patterns": {"expenses_minor": ctx.expense_total_minor, "contributions_minor": ctx.contribution_total_minor},
        "lessons": [],
        "insights": [],
        "ai_summary": {"status": "stub", "summary": None},
        "hero": t.GroupMemoryHero(moment_name=ctx.moment_name).model_dump(mode="json"),
        "sections": {
            "photos": {"count": 0, "items": []},
            "best_moments": best,
            "milestones": ctx.milestones[:5],
            "timeline_replay": [
                {"id": a.get("id"), "title": a.get("title"), "occurred_at": a.get("occurred_at")}
                for a in ctx.activities[:20]
            ],
            "ai_recap": {"status": "stub", "summary": None, "lessons": []},
        },
        "prompts": list(ctx.profile.memory_prompts),
    }
