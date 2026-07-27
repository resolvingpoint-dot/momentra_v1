"""Moments projection mapper for Shared Experience."""
from __future__ import annotations

from app.domains.group import trip_schemas as t
from app.domains.group.templates.shared_experience.context import SharedExperienceContext
from app.domains.group.templates.shared_experience.projection_helpers import (
    build_memory_hub,
    focus_items,
    format_money,
    money_columns,
    stat_tiles,
    _date_label,
)


def _money_progress(ctx: SharedExperienceContext) -> tuple[str, float]:
    if ctx.budget_minor <= 0 and ctx.expense_total_minor <= 0:
        return "No expenses yet", 0.0
    if ctx.budget_minor > 0:
        pct = min(100.0, round(ctx.expense_total_minor / ctx.budget_minor * 100, 1))
        return f"Trip progress at {int(pct)}%", pct
    return f"{format_money(ctx.expense_total_minor, ctx.currency_code)} tracked", 55.0


def _activity_ops(ctx: SharedExperienceContext) -> list[dict]:
    return [
        {"tile_id": "bookings", "label": "Bookings", "value": str(ctx.booking_count), "icon": "hotel"},
        {"tile_id": "planned", "label": "Planned", "value": str(ctx.plan_count), "icon": "event"},
        {"tile_id": "vendors", "label": "Vendors", "value": str(ctx.vendor_count), "icon": "store"},
    ]


def _assets(ctx: SharedExperienceContext) -> list[dict]:
    docs = ctx.document_count
    bookings = ctx.booking_count
    return [
        {"asset_id": "travel-docs", "label": "Travel Docs", "count": docs, "icon": "description"},
        {"asset_id": "reservations", "label": "Reservations", "count": bookings, "icon": "bookmark"},
        {"asset_id": "tickets", "label": "Tickets", "count": ctx.plan_count, "icon": "confirmation_number"},
        {"asset_id": "shared-files", "label": "Shared Files", "count": docs, "icon": "folder"},
    ]


def _decisions(ctx: SharedExperienceContext) -> list[dict]:
    rows: list[dict] = []
    for poll in ctx.polls[:5]:
        active = str(poll.get("status", "open")).lower() not in {"closed", "resolved"}
        rows.append(
            {
                "decision_id": str(poll.get("id") or ""),
                "title": str(poll.get("question") or poll.get("title") or "Poll"),
                "status_label": "ACTIVE POLL" if active else "DECISION CLOSED",
                "icon": "how_to_vote",
                "is_active": active,
                "action": "poll",
            }
        )
    for decision in store_decisions(ctx):
        rows.append(decision)
    return rows[:6]


def store_decisions(ctx: SharedExperienceContext) -> list[dict]:
    from app.domains.group import moment_store as store

    out: list[dict] = []
    for row in store.list_items(ctx.moment, "decisions"):
        if row.get("deleted"):
            continue
        out.append(
            {
                "decision_id": str(row.get("id") or ""),
                "title": str(row.get("title") or "Decision"),
                "status_label": str(row.get("status_label") or "DECISION CLOSED"),
                "icon": "check_circle",
                "is_active": False,
                "action": "decision",
            }
        )
    return out


def build_moments(ctx: SharedExperienceContext) -> dict:
    progress_label, progress_pct = _money_progress(ctx)
    memory_hub_data = build_memory_hub(ctx)
    return t.TripMomentsViewResponse(
        moment_id=str(ctx.moment.id),
        trip_name=ctx.moment_name,
        stage_badge=ctx.stage_badge,
        status_badge=ctx.status_badge,
        memory_hero=t.TripMomentsMemoryHero(
            eyebrow=ctx.profile_badge,
            title=ctx.moment_name,
            subtitle="Your shared story starts here."
            if ctx.memory_count == 0
            else f"{ctx.memory_count} memories captured",
        ),
        operations_hub=t.GroupMomentsOperationsHub(
            core_summary=t.GroupMomentsCoreSummary(
                eyebrow="SHARED EXPERIENCE",
                eyebrow_icon="palette",
                moment_name=ctx.moment_name,
                stage_badge=ctx.stage_badge,
                stat_tiles=[t.GroupMomentsStatTile(**tile) for tile in stat_tiles(ctx)],
            ),
            people_roles=t.GroupMomentsPeopleRoles(
                primary=ctx.primary_organizer,
                role_counts=ctx.role_counts,
                view_all_action="members",
            ),
            money_status=t.GroupMomentsMoneyStatus(
                progress_label=progress_label,
                progress_percent=progress_pct,
                columns=[t.GroupMomentsMoneyColumn(**col) for col in money_columns(ctx)],
            ),
            activity_ops=_activity_ops(ctx),
            assets=_assets(ctx),
            decisions=_decisions(ctx),
            current_state=t.GroupMomentsCurrentState(
                stage_label=ctx.stage_badge,
                focus_items=focus_items(ctx),
                cta_label="TAKE NEXT ACTION",
                cta_action="hub",
                hero_icon="flight_takeoff",
            ),
        ),
        memory_hub=t.GroupMomentsMemoryHub(
            hero=t.GroupMemoryHero(**memory_hub_data["hero"]),
            timeline=memory_hub_data.get("timeline", []),
            milestone_wall=memory_hub_data.get("milestone_wall", []),
            people_impact=memory_hub_data.get("people_impact", []),
            gallery=memory_hub_data.get("gallery", []),
            lessons_pattern=memory_hub_data.get("lessons_pattern", ""),
            group_identity=memory_hub_data.get("group_identity", ""),
            highlights=memory_hub_data.get("highlights", []),
            intelligence=memory_hub_data.get("intelligence", {"metrics": [], "insight": ""}),
            budget_reflection=memory_hub_data.get("budget_reflection"),
        ),
        memory_feed=_upcoming_memory_feed(ctx),
    ).model_dump(mode="json")


def _upcoming_memory_feed(ctx: SharedExperienceContext) -> list[dict]:
    """Bookings/plans surfaced as Upcoming Events (existing memory_feed field)."""
    accents = ("primary", "secondary", "tertiary")
    feed: list[dict] = []
    for index, plan in enumerate(ctx.plans):
        if str(plan.get("status", "")).lower() in {"done", "complete", "completed"}:
            continue
        details = plan.get("details") if isinstance(plan.get("details"), dict) else {}
        raw_date = details.get("date") or details.get("scheduled_at") or plan.get("created_at") or ""
        category = str(plan.get("category") or "activities").lower()
        icon = {
            "stay": "hotel",
            "travel": "flight_takeoff",
            "activities": "event",
            "food": "restaurant",
        }.get(category, "event")
        feed.append(
            {
                "id": f"plan-{plan.get('id') or index}",
                "timestamp_label": _feed_date_label(raw_date),
                "icon": icon,
                "accent": accents[index % 3],
                "title": str(plan.get("title") or "Plan item"),
                "subtitle": category.title() if category else "",
                "activity_type": "plan",
            }
        )
    from app.domains.group.templates.shared_experience.projection_helpers import (
        booking_is_cancelled,
        booking_status,
    )

    for index, booking in enumerate(ctx.bookings):
        status = booking_status(booking)
        if booking_is_cancelled(booking) or status == "completed":
            continue
        raw_date = booking.get("check_in") or booking.get("start_at") or booking.get("created_at") or ""
        feed.append(
            {
                "id": f"booking-{booking.get('id') or index}",
                "timestamp_label": _feed_date_label(raw_date),
                "icon": "hotel",
                "accent": accents[(len(feed) + index) % 3],
                "title": str(booking.get("title") or booking.get("name") or "Booking"),
                "subtitle": status.title() if status else "Booking",
                "activity_type": "booking",
            }
        )
    return feed[:8]


def _feed_date_label(raw: object) -> str:
    label = _date_label(raw)
    return "" if label == "—" else label
