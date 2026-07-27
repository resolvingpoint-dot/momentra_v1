"""Life projection mapper for Shared Living."""
from __future__ import annotations

from app.domains.group.settlements.service import cheap_life_preview
from app.domains.group.templates.shared_living.context import SharedLivingContext


def _settlement_preview(ctx: SharedLivingContext) -> dict:
    computed = cheap_life_preview(ctx.moment)
    if computed:
        return computed
    return {
        "status": "preview",
        "harmony_label": "In harmony" if ctx.expense_total_minor == 0 else "Tracking",
        "balance_insight": "Nobody owes anything yet — log an expense to get started."
        if ctx.expense_total_minor == 0
        else f"{ctx.currency_code} {ctx.expense_total_minor / 100:.0f} tracked across the household",
        "currency_code": ctx.currency_code,
        "total_spent_minor": ctx.expense_total_minor,
    }


def build_life(ctx: SharedLivingContext) -> dict:
    fairness = 100.0 if ctx.resident_count <= 1 else max(40.0, 100.0 - abs(ctx.contribution_total_minor - ctx.expense_total_minor) / 100)
    return {
        "moment_id": str(ctx.moment.id),
        "moment_name": ctx.moment_name,
        "moment_type": "SHARED_LIVING",
        "profile_badge": ctx.profile_badge,
        "stage_badge": ctx.stage_badge,
        "status_badge": ctx.status_badge,
        "household_harmony": {"score": min(100.0, 50 + ctx.resident_count * 10), "label": "Household harmony"},
        "expense_fairness": {"score": fairness, "label": "Expense fairness"},
        "chore_balance": {"score": 80.0 if ctx.task_count else 50.0, "label": "Chore balance"},
        "rules_clarity": {"score": 90.0 if ctx.rules_count else 40.0, "label": "Rules clarity"},
        "maintenance_health": {"score": min(100.0, 60 + ctx.maintenance_count * 10), "label": "Maintenance health"},
        "resident_engagement": {"score": min(100.0, ctx.resident_count * 20), "label": "Resident engagement"},
        "shared_commitment": {"score": min(100.0, 30 + ctx.expense_count * 10), "label": "Shared commitment"},
        "recommendations": _recommendations(ctx),
        "stats": {
            "residents": ctx.resident_count,
            "expenses_minor": ctx.expense_total_minor,
            "contributions_minor": ctx.contribution_total_minor,
            "memories": ctx.memory_count,
            "chores": ctx.task_count,
        },
        "settlement_preview": _settlement_preview(ctx),
    }


def _recommendations(ctx: SharedLivingContext) -> list[dict]:
    recs: list[dict] = []
    if ctx.resident_count == 0:
        recs.append({"title": "Invite residents", "description": "Add people who live in this home.", "priority": "HIGH"})
    if ctx.rules_count == 0:
        recs.append({"title": "Set house rules", "description": "Clarify expectations for everyone.", "priority": "MEDIUM"})
    return recs
