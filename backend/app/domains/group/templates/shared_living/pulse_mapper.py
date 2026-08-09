"""Pulse projection mapper for Shared Living."""
from __future__ import annotations

from app.domains.group.settlements.trip_payload import build_trip_settlement_payload
from app.domains.group.templates.shared_living.context import SharedLivingContext
from app.domains.group.templates.shared_living.projection_helpers import (
    attention_items,
    contribution_coverage_percent,
    dashboard_recent_items,
    experience_health_percent,
    format_money,
    health_dimensions,
    insights,
    next_best_action,
    open_task_count,
    outstanding_minor,
    participation_percent,
    readiness_score,
    relative_time_label,
)


def _resident_metric_value(ctx: SharedLivingContext) -> str:
    """"3 of 5" when setup declared an expected headcount, else the raw joined count."""
    if ctx.expected_resident_count and ctx.expected_resident_count > 0:
        return f"{ctx.resident_count} of {ctx.expected_resident_count}"
    return str(ctx.resident_count)


def build_pulse(ctx: SharedLivingContext) -> dict:
    created = ctx.moment.updated_at or ctx.moment.created_at
    updated_label = ""
    if created and hasattr(created, "isoformat"):
        updated_label = relative_time_label(created.isoformat())
    nba = next_best_action(ctx)
    health = experience_health_percent(ctx)
    open_tasks = open_task_count(ctx)
    settlement = build_trip_settlement_payload(ctx.moment)
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_LIVING",
        "living_name": ctx.moment_name,
        "moment_name": ctx.moment_name,
        "home_description": ctx.home_description,
        "currency_code": ctx.currency_code,
        "expenses_total_minor": ctx.expense_total_minor,
        "contributions_total_minor": ctx.contribution_total_minor,
        "outstanding_minor": outstanding_minor(ctx),
        "resident_count": ctx.resident_count,
        "expected_residents": ctx.expected_resident_count,
        "health_percent": health,
        "experience_health_percent": health,
        "participation_percent": participation_percent(ctx),
        "participation_breakdown": {
            "active": ctx.active_resident_count,
            "pending": ctx.pending_resident_count,
            "inactive": ctx.inactive_resident_count,
        },
        "participant_avatars": ctx.participant_avatars,
        "readiness_score": readiness_score(ctx),
        "recent_activity": dashboard_recent_items(ctx),
        "pending_chores": [
            {"id": t.get("id"), "title": t.get("title"), "status": t.get("status", "open")}
            for t in ctx.chores
            if str(t.get("status", "open")).lower() not in {"done", "completed", "closed"}
        ][:5],
        "open_polls": [
            {"id": p.get("id"), "question": p.get("question"), "status": p.get("status", "open")}
            for p in ctx.polls
            if str(p.get("status", "open")).lower() not in {"closed", "resolved"}
        ][:5],
        "settlement_widget": settlement.get("settlement_widget"),
        "settlement_preview": {
            "harmony_label": settlement.get("harmony_label"),
            "balance_insight": settlement.get("balance_insight"),
            "currency_code": settlement.get("currency_code"),
            "total_spent_minor": settlement.get("total_expenses_minor"),
            "pending_count": settlement.get("members_needing_settlement"),
            "suggested_transfer": settlement.get("suggested_transfer"),
            "total_paid_minor": settlement.get("total_paid_minor"),
            "pending_settlement_minor": settlement.get("pending_settlement_minor"),
        },
        "next_best_action": nba,
        "alerts": _alerts(ctx),
        "attention_items": attention_items(ctx),
        "insights": insights(ctx),
        "health_dimensions": health_dimensions(ctx),
        "profile_badge": ctx.profile_badge,
        "stage_badge": ctx.stage_badge,
        "status_badge": ctx.status_badge,
        "readiness_title": ctx.profile.pulse_readiness_title,
        "readiness_narrative": ctx.profile.pulse_readiness_narrative,
        "stats": {
            "residents_joined": ctx.resident_count,
            "expenses_logged": ctx.expense_count,
            "total_expenses_minor": ctx.expense_total_minor,
            "contributions_minor": ctx.contribution_total_minor,
            "open_polls": ctx.poll_count,
            "tasks_open": open_tasks,
            "rules_count": ctx.rules_count,
            "assets_count": ctx.assets_count,
            "updated_at_display": {"label": updated_label or "Just now", "minutes_ago": 0},
        },
        "metric_tiles": [
            {"label": "Residents", "value": _resident_metric_value(ctx)},
            {
                "label": "Monthly Spend",
                "value": format_money(ctx.expense_total_minor, ctx.currency_code) if ctx.expense_total_minor else "—",
            },
            {
                "label": "Contributions",
                "value": format_money(ctx.contribution_total_minor, ctx.currency_code)
                if ctx.contribution_total_minor
                else "—",
            },
            {"label": "Open Tasks", "value": str(open_tasks)},
        ],
        "dashboard_card": {
            "title": ctx.moment_name,
            "subtitle": ctx.home_description or "Shared living",
            "funding_percent": contribution_coverage_percent(ctx),
            "recent_items": dashboard_recent_items(ctx),
        },
        "health_trend": {
            "label": "Home Health",
            "value": int(health),
            "direction": "up",
        },
        "operations_progress": {
            "label": "Home Operations",
            "percent": max(0.0, 100.0 - open_tasks * 15.0) if ctx.task_count else (40.0 if ctx.is_active else 0.0),
            "subtitle": f"{open_tasks} open tasks" if open_tasks else ("All clear" if ctx.task_count else "Add chores"),
        },
    }


def _alerts(ctx: SharedLivingContext) -> list[dict]:
    alerts: list[dict] = []
    if ctx.resident_count == 0:
        alerts.append({"type": "people", "message": "No residents yet"})
    if ctx.expense_count == 0:
        alerts.append({"type": "money", "message": "No expenses logged yet"})
    if outstanding_minor(ctx) > 0:
        alerts.append({"type": "contributions", "message": "Contribution gap open"})
    return alerts
