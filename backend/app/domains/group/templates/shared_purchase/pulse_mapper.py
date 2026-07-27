"""Pulse projection mapper for Shared Purchase."""
from __future__ import annotations

from app.domains.group.settlements.service import cheap_life_preview
from app.domains.group.templates.shared_purchase.context import SharedPurchaseContext
from app.domains.group.templates.shared_purchase.projection_helpers import (
    attention_items,
    dashboard_recent_items,
    experience_health_percent,
    format_money,
    health_dimensions,
    insights,
    next_best_action,
    participation_percent,
    readiness_score,
    relative_time_label,
)


def build_pulse(ctx: SharedPurchaseContext) -> dict:
    created = ctx.moment.updated_at or ctx.moment.created_at
    updated_label = ""
    if created and hasattr(created, "isoformat"):
        updated_label = relative_time_label(created.isoformat())
    nba = next_best_action(ctx)
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_PURCHASE",
        "purchase_name": ctx.moment_name,
        "moment_name": ctx.moment_name,
        "purchase_goal": ctx.purchase_goal,
        "target_amount_minor": ctx.target_amount_minor,
        "currency_code": ctx.currency_code,
        "total_contributed_minor": ctx.contribution_total_minor,
        "amount_remaining_minor": ctx.amount_remaining_minor,
        "contribution_progress_percent": ctx.contribution_progress_percent,
        "participant_count": ctx.contributor_count,
        "contributor_balance": {
            "contributions_minor": ctx.contribution_total_minor,
            "payments_minor": ctx.payment_total_minor,
            "expenses_minor": ctx.expense_total_minor,
        },
        "upcoming_installments": [
            {
                "id": i.get("id"),
                "title": i.get("title"),
                "amount_minor": i.get("amount_minor", 0),
                "due_date": i.get("due_date"),
            }
            for i in ctx.installments[:5]
        ],
        "recent_activity": dashboard_recent_items(ctx),
        "pending_decisions": [
            {"id": d.get("id"), "title": d.get("title"), "status": d.get("status", "open")}
            for d in ctx.decisions
            if d.get("status", "open") != "closed"
        ][:5],
        "ownership_summary": {
            "count": ctx.ownership_count,
            "items": ctx.ownership_shares[:5],
        },
        "settlement_preview": _settlement_preview(ctx),
        "next_best_action": nba,
        "alerts": _alerts(ctx),
        "attention_items": attention_items(ctx),
        "insights": insights(ctx),
        "health_dimensions": health_dimensions(ctx),
        "experience_health_percent": experience_health_percent(ctx),
        "participation_percent": participation_percent(ctx),
        "participation_breakdown": {
            "active": ctx.active_contributor_count,
            "pending": ctx.pending_contributor_count,
            "inactive": ctx.inactive_contributor_count,
        },
        "participant_avatars": ctx.participant_avatars,
        "readiness_score": readiness_score(ctx),
        "profile_badge": ctx.profile_badge,
        "stage_badge": ctx.stage_badge,
        "status_badge": ctx.status_badge,
        "readiness_title": ctx.profile.pulse_readiness_title,
        "readiness_narrative": ctx.profile.pulse_readiness_narrative,
        "stats": {
            "contributors_joined": ctx.contributor_count,
            "plan_items": ctx.expense_count + ctx.milestone_count,
            "vendors": ctx.vendor_count,
            "open_polls": ctx.poll_count,
            "total_expenses_minor": ctx.expense_total_minor,
            "contributions_minor": ctx.contribution_total_minor,
            "ownership_status": "Assigned" if ctx.ownership_count else "Unassigned",
            "items_finalized": ctx.milestone_count or ctx.item_count,
            "target_amount_minor": ctx.target_amount_minor,
            "remaining_amount_minor": ctx.amount_remaining_minor,
            "updated_at_display": {"label": updated_label or "Just now", "minutes_ago": 0},
        },
        "metric_tiles": [
            {"label": "Target", "value": format_money(ctx.target_amount_minor, ctx.currency_code) if ctx.target_amount_minor else "—"},
            {"label": "Collected", "value": format_money(ctx.contribution_total_minor, ctx.currency_code) if ctx.contribution_total_minor else "—"},
            {"label": "Remaining", "value": format_money(ctx.amount_remaining_minor, ctx.currency_code) if ctx.amount_remaining_minor else "—"},
            {"label": "Contributors", "value": str(ctx.contributor_count)},
        ],
        "funded_amount_minor": ctx.contribution_total_minor,
        "funding_percent": ctx.contribution_progress_percent,
        "contributor_count": ctx.contributor_count,
        "dashboard_card": {
            "title": ctx.moment_name,
            "subtitle": ctx.purchase_goal or "Shared purchase",
            "funding_percent": ctx.contribution_progress_percent,
            "recent_items": dashboard_recent_items(ctx),
        },
        "health_trend": {"label": "Funding", "value": int(ctx.contribution_progress_percent), "direction": "up"},
    }


def _alerts(ctx: SharedPurchaseContext) -> list[dict]:
    alerts: list[dict] = []
    if ctx.contributor_count == 0:
        alerts.append({"type": "people", "message": "No contributors yet"})
    if ctx.target_amount_minor and ctx.amount_remaining_minor > 0:
        alerts.append({"type": "funding", "message": "Funding target not reached"})
    return alerts


def _settlement_preview(ctx: SharedPurchaseContext) -> dict:
    """Projection-correct settlement preview — never invent harmony."""
    computed = cheap_life_preview(ctx.moment)
    if computed:
        return computed
    return {
        "status": "preview",
        "currency_code": ctx.currency_code,
        "total_spent_minor": ctx.expense_total_minor,
        "harmony_label": "In harmony" if ctx.expense_total_minor == 0 else "Tracking",
        "balance_insight": "Nobody owes anything yet — log an expense to get started."
        if ctx.expense_total_minor == 0
        else f"{ctx.currency_code} {ctx.expense_total_minor / 100:.0f} tracked across the group",
        "pending_count": 0,
    }
