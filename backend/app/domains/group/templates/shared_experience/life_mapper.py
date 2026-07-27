"""Life projection mapper for Shared Experience (group life tab)."""
from __future__ import annotations

from app.domains.group.settlements.service import cheap_life_preview
from app.domains.group.templates.shared_experience.context import SharedExperienceContext


def _settlement_preview(ctx: SharedExperienceContext) -> dict:
    computed = cheap_life_preview(ctx.moment)
    if computed:
        return computed
    return {
        "status": "preview",
        "harmony_label": "In harmony" if ctx.expense_total_minor == 0 else "Tracking",
        "balance_insight": "Nobody owes anything yet — log an expense to get started."
        if ctx.expense_total_minor == 0
        else f"₹{ctx.expense_total_minor / 100:.0f} tracked across the group",
    }


def build_life(ctx: SharedExperienceContext) -> dict:
    return {
        "moment_id": str(ctx.moment.id),
        "moment_name": ctx.moment_name,
        "profile_badge": ctx.profile_badge,
        "stage_badge": ctx.stage_badge,
        "status_badge": ctx.status_badge,
        "experience_type": ctx.experience_type.code,
        "stats": {
            "guests": ctx.guest_count,
            "expenses_minor": ctx.expense_total_minor,
            "contributions_minor": ctx.contribution_total_minor,
            "memories": ctx.memory_count,
            "plans": ctx.plan_count,
        },
        "settlement_preview": _settlement_preview(ctx),
    }
