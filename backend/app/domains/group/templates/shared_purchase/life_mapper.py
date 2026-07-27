"""Life projection mapper for Shared Purchase."""
from __future__ import annotations

from app.domains.group.settlements.service import cheap_life_preview
from app.domains.group.templates.shared_purchase.context import SharedPurchaseContext


def _settlement_preview(ctx: SharedPurchaseContext) -> dict:
    computed = cheap_life_preview(ctx.moment)
    if computed:
        return computed
    return {
        "status": "preview",
        "harmony_label": "In harmony" if ctx.expense_total_minor == 0 else "Tracking",
        "balance_insight": "Nobody owes anything yet — log an expense to get started."
        if ctx.expense_total_minor == 0
        else f"{ctx.currency_code} {ctx.expense_total_minor / 100:.0f} tracked across the group",
        "currency_code": ctx.currency_code,
        "total_spent_minor": ctx.expense_total_minor,
    }


def build_life(ctx: SharedPurchaseContext) -> dict:
    fairness = 100.0 if ctx.contributor_count <= 1 else max(40.0, 100.0 - abs(ctx.contribution_total_minor - ctx.expense_total_minor) / 100)
    return {
        "moment_id": str(ctx.moment.id),
        "moment_name": ctx.moment_name,
        "moment_type": "SHARED_PURCHASE",
        "profile_badge": ctx.profile_badge,
        "stage_badge": ctx.stage_badge,
        "status_badge": ctx.status_badge,
        "financial_alignment": {"score": min(100.0, ctx.contribution_progress_percent), "label": "Funding alignment"},
        "contribution_fairness": {"score": fairness, "label": "Contribution fairness"},
        "decision_balance": {"score": 80.0 if ctx.decision_count else 50.0, "label": "Decision balance"},
        "ownership_clarity": {"score": 90.0 if ctx.ownership_count else 40.0, "label": "Ownership clarity"},
        "responsibility_distribution": {"score": min(100.0, ctx.contributor_count * 20), "label": "Responsibility"},
        "planning_load": {"score": min(100.0, ctx.milestone_count * 15 + 30), "label": "Planning load"},
        "group_trust": {"score": 75.0, "label": "Group trust"},
        "shared_commitment": {"score": min(100.0, ctx.contribution_progress_percent + 10), "label": "Shared commitment"},
        "recommendations": _recommendations(ctx),
        "stats": {
            "contributors": ctx.contributor_count,
            "expenses_minor": ctx.expense_total_minor,
            "contributions_minor": ctx.contribution_total_minor,
            "memories": ctx.memory_count,
            "milestones": ctx.milestone_count,
        },
        "settlement_preview": _settlement_preview(ctx),
    }


def _recommendations(ctx: SharedPurchaseContext) -> list[dict]:
    recs: list[dict] = []
    if ctx.contributor_count == 0:
        recs.append({"title": "Invite contributors", "description": "Add people to fund this purchase.", "priority": "HIGH"})
    if ctx.ownership_count == 0:
        recs.append({"title": "Define ownership", "description": "Clarify who owns what.", "priority": "MEDIUM"})
    return recs
