"""Pulse projection mapper for Shared Experience."""
from __future__ import annotations

from app.domains.group import trip_schemas as t
from app.domains.group.templates.shared_experience.context import SharedExperienceContext
from app.domains.group.templates.shared_experience.projection_helpers import (
    attention_items,
    booking_is_activity_type,
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


def build_pulse(ctx: SharedExperienceContext) -> dict:
    score = readiness_score(ctx)
    participants = max(ctx.guest_count, ctx.active_member_count + ctx.pending_member_count)
    health_pct = experience_health_percent(ctx)
    updated_label = relative_time_label(
        ctx.moment.updated_at.isoformat() if ctx.moment.updated_at else None
    )
    activity_items = ctx.plan_count + sum(1 for b in ctx.bookings if booking_is_activity_type(b))
    stats = t.TripPulseStats(
        participants_joined=participants,
        members_joined=ctx.active_member_count,
        guests_joined=ctx.guest_count,
        participants_expected=int(ctx.setup_payload.get("expected_participants") or 0) or None,
        active_plan_items=activity_items,
        # Hero tile is labeled "Bookings" (all active bookings), not only confirmed.
        confirmed_bookings=ctx.booking_count,
        total_expenses_minor=ctx.expense_total_minor,
        total_expenses_currency=ctx.currency_code,
        total_budget_minor=ctx.budget_minor,
        contributions_minor=ctx.contribution_total_minor,
        contributions_currency=ctx.currency_code,
        corpus_balance_minor=ctx.corpus_balance_minor,
        open_polls=ctx.open_poll_count,
        memories_count=ctx.memory_count,
        memory_contributor_avatars=ctx.participant_avatars,
    ).model_dump(mode="json")
    stats["updated_at_display"] = {"label": updated_label or "Just now", "minutes_ago": 0}

    payload = t.TripPulseResponse(
        moment_id=str(ctx.moment.id),
        trip_name=ctx.moment_name,
        cover_image_url=ctx.setup_payload.get("cover_image_url"),
        profile_badge=ctx.profile_badge,
        stage_badge=ctx.stage_badge,
        status_badge=ctx.status_badge,
        readiness_score=score,
        readiness_title=ctx.experience_type.pulse_readiness_title,
        readiness_narrative=ctx.experience_type.pulse_readiness_narrative,
        stats=t.TripPulseStats(**{k: v for k, v in stats.items() if k != "updated_at_display"}),
        attention_items=attention_items(ctx),
        experience_health_percent=health_pct,
        participation_percent=participation_percent(ctx),
        participant_avatars=ctx.participant_avatars,
        health_dimensions=health_dimensions(ctx),
        insights=insights(ctx),
        days_remaining=ctx.days_remaining,
        participation_breakdown={
            "active": ctx.active_member_count or ctx.guest_count,
            "pending": ctx.pending_member_count,
            "inactive": ctx.inactive_member_count,
        },
        health_trend={"label": "Stable", "value": 0, "direction": "up"},
        next_best_action=next_best_action(ctx),
        dashboard_card={
            "moment_id": str(ctx.moment.id),
            "moment_name": ctx.moment_name,
            "moment_type_code": ctx.moment.moment_type or "SHARED_EXPERIENCE",
            "kpis": [
                {"kpi_id": "participants", "label": "Participants", "value": str(participants)},
                {"kpi_id": "bookings", "label": "Bookings", "value": str(ctx.booking_count)},
                {"kpi_id": "activities", "label": "Activities", "value": str(activity_items)},
                {
                    "kpi_id": "budget",
                    "label": "Budget",
                    "value": format_money(ctx.budget_minor, ctx.currency_code) if ctx.budget_minor else "—",
                },
                {
                    "kpi_id": "spent",
                    "label": "Spent",
                    "value": format_money(ctx.expense_total_minor, ctx.currency_code)
                    if ctx.expense_total_minor
                    else "—",
                },
                {"kpi_id": "readiness", "label": "Readiness", "value": f"{int(score)}%"},
            ],
            "recent_items": dashboard_recent_items(ctx),
            "recent_section_title": "Recent Activity",
            "empty_recent_message": "No activity yet",
        },
    ).model_dump(mode="json")
    payload["stats"] = stats
    from app.domains.group.settlements.trip_payload import build_trip_settlement_payload

    settlement = build_trip_settlement_payload(ctx.moment)
    payload["settlement_widget"] = settlement.get("settlement_widget")
    payload["settlement_preview"] = {
        "harmony_label": settlement.get("harmony_label"),
        "balance_insight": settlement.get("balance_insight"),
        "currency_code": settlement.get("currency_code"),
        "total_spent_minor": settlement.get("total_expenses_minor"),
        "pending_count": settlement.get("members_needing_settlement"),
        "suggested_transfer": settlement.get("suggested_transfer"),
        "total_paid_minor": settlement.get("total_paid_minor"),
        "pending_settlement_minor": settlement.get("pending_settlement_minor"),
    }
    return payload
