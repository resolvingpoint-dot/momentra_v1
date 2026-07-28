"""Shared helpers for Shared Experience pulse / moments / memory projections."""
from __future__ import annotations

from datetime import date, datetime, timezone

from app.domains.group import moment_store as store
from app.domains.group.templates.shared_experience.context import SharedExperienceContext

_BOOKING_CONFIRMED = frozenset({"confirmed", "booked", "reserved", "done", "completed"})
_BOOKING_CANCELLED = frozenset({"cancelled", "canceled"})
_ACTIVITY_BOOKING_TYPES = frozenset({"activity", "activities", "experience", "event"})


def booking_status(row: dict) -> str:
    """Writers store `booking_status`; older seeds used `status`."""
    return str(row.get("booking_status") or row.get("status") or "").lower()


def booking_is_confirmed(row: dict) -> bool:
    return booking_status(row) in _BOOKING_CONFIRMED


def booking_is_cancelled(row: dict) -> bool:
    return booking_status(row) in _BOOKING_CANCELLED


def booking_is_activity_type(row: dict) -> bool:
    return str(row.get("booking_type") or "").lower() in _ACTIVITY_BOOKING_TYPES


def format_money(minor: int, currency: str = "INR") -> str:
    rupees = float(minor) / 100.0
    if currency.upper() == "INR":
        if rupees >= 10_000_000:
            n = rupees / 10_000_000
            s = f"{n:.1f}".rstrip("0").rstrip(".")
            return f"₹{s}Cr"
        if rupees >= 100_000:
            n = rupees / 100_000
            s = f"{n:.1f}".rstrip("0").rstrip(".")
            return f"₹{s}L"
        if rupees >= 1_000:
            return f"₹{rupees:,.0f}"
        return f"₹{rupees:.0f}"
    symbol = f"{currency} "
    if rupees >= 1_000:
        return f"{symbol}{rupees:,.0f}"
    return f"{symbol}{rupees:.0f}"


def relative_time_label(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        minutes = int(delta.total_seconds() // 60)
        if minutes < 1:
            return "Just now"
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        if days == 1:
            return "Yesterday"
        return f"{days}d ago"
    except (ValueError, TypeError):
        return ""


def parse_date(value) -> date | None:
    if not value:
        return None
    try:
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def days_remaining(end_date) -> int | None:
    end = parse_date(end_date)
    if end is None:
        return None
    return max(0, (end - date.today()).days)


def readiness_score(ctx: SharedExperienceContext) -> float:
    score = 10.0
    participants = max(ctx.guest_count, ctx.active_member_count)
    score += min(25, participants * 4)
    score += min(20, ctx.confirmed_booking_count * 8)
    score += min(20, ctx.plan_count * 4)
    if ctx.budget_minor > 0 and ctx.expense_total_minor > 0:
        score += min(15, (ctx.expense_total_minor / max(1, ctx.budget_minor)) * 15)
    if ctx.memory_count:
        score += min(10, ctx.memory_count * 3)
    return min(100.0, round(score, 1))


def participation_percent(ctx: SharedExperienceContext) -> float:
    total = ctx.active_member_count + ctx.pending_member_count + ctx.inactive_member_count
    if total <= 0:
        total = ctx.guest_count
    if total <= 0:
        return 0.0
    return min(100.0, round(ctx.active_member_count / total * 100, 1))


def _clamp_pct(value: float) -> float:
    return max(0.0, min(100.0, round(float(value), 1)))


def health_dimensions(ctx: SharedExperienceContext) -> list[dict]:
    bookings_pct = _clamp_pct(ctx.confirmed_booking_count * 25.0) if ctx.booking_count else 0.0
    participation_pct = _clamp_pct(participation_percent(ctx))
    budget_pct = 0.0
    if ctx.budget_minor > 0:
        if ctx.expense_total_minor > ctx.budget_minor:
            # Overspend: never report negative health (was e.g. -3300%).
            budget_pct = 0.0
        else:
            budget_pct = _clamp_pct(
                (1 - abs(ctx.budget_minor - ctx.expense_total_minor) / ctx.budget_minor) * 100
            )
    timeline_pct = 0.0
    if ctx.plan_count:
        timeline_pct = _clamp_pct(ctx.plan_count * 12.0)
    return [
        {"label": "Bookings", "percent": bookings_pct, "status": f"{int(bookings_pct)}%", "accent": "primary"},
        {"label": "Participation", "percent": participation_pct, "status": f"{int(participation_pct)}%", "accent": "primary"},
        {"label": "Budget", "percent": budget_pct, "status": f"{int(budget_pct)}%", "accent": "primary"},
        {"label": "Timeline", "percent": timeline_pct, "status": f"{int(timeline_pct)}%", "accent": "primary"},
    ]


def experience_health_percent(ctx: SharedExperienceContext) -> float:
    dims = health_dimensions(ctx)
    if not any(d["percent"] for d in dims):
        return _clamp_pct(readiness_score(ctx))
    return _clamp_pct(sum(float(d["percent"]) for d in dims) / len(dims))


def attention_items(ctx: SharedExperienceContext) -> list[dict]:
    items: list[dict] = []
    pending_bookings = [
        b
        for b in ctx.bookings
        if not booking_is_cancelled(b) and not booking_is_confirmed(b)
    ]
    if pending_bookings:
        items.append(
            {
                "id": "booking-pending",
                "title": "Hotel booking pending" if len(pending_bookings) == 1 else f"{len(pending_bookings)} bookings pending",
                "icon": "hotel",
                "accent": "error",
                "action": "bookings",
            }
        )
    outstanding = max(0, ctx.expense_total_minor - ctx.contribution_total_minor)
    if outstanding > 0:
        items.append(
            {
                "id": "balance-pending",
                "title": "Balance collection pending",
                "icon": "account_balance_wallet",
                "accent": "tertiary",
                "action": "contributions",
            }
        )
    open_polls = [p for p in ctx.polls if str(p.get("status", "open")).lower() not in {"closed", "resolved"}]
    if open_polls:
        items.append(
            {
                "id": str(open_polls[0].get("id") or "poll-open"),
                "title": str(open_polls[0].get("question") or open_polls[0].get("title") or "Poll awaiting decision"),
                "icon": "how_to_vote",
                "accent": "secondary",
                "action": "polls",
            }
        )
    return items[:5]


def next_best_action(ctx: SharedExperienceContext) -> dict | None:
    if ctx.guest_count == 0 and ctx.active_member_count == 0:
        return {
            "title": "Invite your group",
            "subtitle": "Add participants to build momentum.",
            "action": "participant",
            "impact_labels": ["+8 Health", "+15 Progress", "+10 Participation"],
        }
    outstanding = max(0, ctx.expense_total_minor - ctx.contribution_total_minor)
    if outstanding > 0:
        return {
            "title": f"Collect remaining {format_money(outstanding, ctx.currency_code)}",
            "subtitle": "Close the balance gap across the group.",
            "action": "contribution",
            "impact_labels": ["+6 Health", "+12 Progress", "+5 Participation"],
        }
    if ctx.confirmed_booking_count < max(1, ctx.booking_count):
        return {
            "title": "Confirm pending bookings",
            "subtitle": "Finalize reservations to stabilize the plan.",
            "action": "booking",
            "impact_labels": ["+5 Health", "+8 Progress"],
        }
    if ctx.plan_count == 0:
        return {
            "title": "Add your first plan item",
            "subtitle": "Shape the itinerary for the group.",
            "action": "planning",
            "impact_labels": ["+4 Health", "+10 Progress"],
        }
    if ctx.memory_count == 0 and ctx.is_active:
        return {
            "title": "Capture the first memory",
            "subtitle": "Start the shared story for this trip.",
            "action": "memory",
            "impact_labels": ["+3 Participation"],
        }
    return {
        "title": "Review trip progress",
        "subtitle": "Check bookings, budget, and group activity.",
        "action": "hub",
        "impact_labels": ["+2 Health"],
    }


def insights(ctx: SharedExperienceContext) -> list[dict]:
    out: list[dict] = []
    if ctx.active_member_count >= 2:
        out.append(
            {
                "id": "participation",
                "title": "Participation increasing",
                "subtitle": f"{ctx.active_member_count} active members",
                "icon": "trending_up",
                "accent": "primary",
            }
        )
    if ctx.budget_minor > 0 and ctx.expense_total_minor <= ctx.budget_minor:
        out.append(
            {
                "id": "budget",
                "title": "Budget under control",
                "subtitle": f"Spent {format_money(ctx.expense_total_minor, ctx.currency_code)} of {format_money(ctx.budget_minor, ctx.currency_code)}",
                "icon": "savings",
                "accent": "primary",
            }
        )
    if ctx.plan_count > 0:
        out.append(
            {
                "id": "planning",
                "title": "Planning pace stable",
                "subtitle": f"{ctx.plan_count} plan items tracked",
                "icon": "cloud",
                "accent": "primary",
            }
        )
    return out[:3]


def dashboard_recent_items(ctx: SharedExperienceContext) -> list[dict]:
    items: list[dict] = []
    for a in ctx.activities[:5]:
        activity_id = str(a.get("id") or "").strip()
        if not activity_id:
            continue
        items.append(
            {
                "id": activity_id,
                "activity_type": str(a.get("activity_type") or "UPDATE"),
                "title": str(a.get("title") or "Activity"),
                "subtitle": str(a.get("subtitle") or ""),
                "occurred_at": str(a.get("occurred_at") or ""),
                "relative_time": relative_time_label(a.get("occurred_at")),
                "icon": str(a.get("icon") or "auto_awesome"),
            }
        )
    return items


def stat_tiles(ctx: SharedExperienceContext) -> list[dict]:
    participants = max(ctx.guest_count, ctx.active_member_count + ctx.pending_member_count)
    return [
        {"label": "Participants", "value": str(participants), "highlight": False},
        {"label": "Bookings", "value": str(ctx.booking_count), "highlight": False},
        {"label": "Activities", "value": str(ctx.plan_count), "highlight": False},
        {
            "label": "Expenses",
            "value": format_money(ctx.expense_total_minor, ctx.currency_code) if ctx.expense_total_minor else "—",
            "highlight": ctx.expense_total_minor > 0,
        },
    ]


def money_columns(ctx: SharedExperienceContext) -> list[dict]:
    budget = ctx.budget_minor
    spent = ctx.expense_total_minor
    pending = max(0, budget - spent) if budget else 0
    outstanding = max(0, spent - ctx.contribution_total_minor)
    return [
        {"label": "Budget", "value": format_money(budget, ctx.currency_code) if budget else "—", "highlight": False},
        {"label": "Spent", "value": format_money(spent, ctx.currency_code) if spent else "—", "highlight": True},
        {"label": "Pending", "value": format_money(pending, ctx.currency_code) if pending else "—", "highlight": False},
        {"label": "Outstanding", "value": format_money(outstanding, ctx.currency_code) if outstanding else "—", "highlight": outstanding > 0},
    ]


def focus_items(ctx: SharedExperienceContext) -> list[dict]:
    items: list[dict] = []
    if ctx.booking_count:
        items.append({"label": "Finalize transport logistics", "is_complete": ctx.confirmed_booking_count >= ctx.booking_count})
    outstanding = max(0, ctx.expense_total_minor - ctx.contribution_total_minor)
    items.append({"label": "Collect remaining balances", "is_complete": outstanding == 0})
    items.append({"label": "Confirm group activities", "is_complete": ctx.plan_count > 0})
    return items[:5]


def _memory_image_url(memory: dict) -> str | None:
    """Resolve a displayable image URL from store fields when present."""
    from app.core.storage import resolve_memory_image_url

    return resolve_memory_image_url(memory)


def build_memory_hub(ctx: SharedExperienceContext) -> dict:
    memories = ctx.memories
    participants = max(ctx.guest_count, ctx.active_member_count)
    milestones = _milestone_wall(ctx)
    timeline = _memory_timeline(ctx)
    gallery = [
        {
            "memory_id": str(m.get("id") or ""),
            "title": str(m.get("title") or "Memory"),
            "image_url": _memory_image_url(m),
        }
        for m in memories[:8]
    ]
    people_impact = _people_impact(ctx)
    budget_reflection = None
    if ctx.budget_minor > 0 and ctx.expense_total_minor > 0:
        accuracy = min(100, round((1 - abs(ctx.budget_minor - ctx.expense_total_minor) / ctx.budget_minor) * 100))
        saved = max(0, ctx.budget_minor - ctx.expense_total_minor)
        budget_reflection = {
            "planned_budget": format_money(ctx.budget_minor, ctx.currency_code),
            "actual_spend": format_money(ctx.expense_total_minor, ctx.currency_code),
            "budget_accuracy": f"{accuracy}%",
            "best_controlled": "Food" if ctx.expense_count else None,
            "highest_variance": "Activities" if ctx.plan_count else None,
            "summary": f"Saved {format_money(saved, ctx.currency_code)} against plan" if saved > 0 else "",
        }
    intelligence_metrics = []
    pct = participation_percent(ctx)
    if pct:
        intelligence_metrics.append({"label": "Participation", "value": f"+{int(pct)}%"})
    if ctx.contribution_total_minor:
        intelligence_metrics.append({"label": "Contributions", "value": format_money(ctx.contribution_total_minor, ctx.currency_code)})
    if ctx.is_active:
        intelligence_metrics.append({"label": "Completion", "value": f"{int(readiness_score(ctx))}%"})
    insight = ""
    if ctx.plan_count and ctx.confirmed_booking_count:
        insight = "Your strongest pattern is early planning. The group enjoys immersive and inclusive trips."
    elif ctx.memory_count:
        insight = "Consistency in contributions leads to smoother execution."
    return {
        "hero": {
            "moment_name": ctx.moment_name,
            "cover_image_url": ctx.setup_payload.get("cover_image_url"),
            "chips": [
                {"icon": "photo_library", "label": f"{len(memories)} Memories"},
                {"icon": "group", "label": f"{participants} Participants"},
                {"icon": "military_tech", "label": f"{len(milestones)} Milestones"},
            ],
            "hero_icon": "travel_explore",
        },
        "timeline": timeline,
        "milestone_wall": milestones,
        "people_impact": people_impact,
        "gallery": gallery,
        "lessons_pattern": "Trips succeed when bookings are finalized early." if ctx.booking_count else "",
        "group_identity": str(ctx.setup_payload.get("audience_tags", ["Adventure Seekers"])[0])
        if ctx.setup_payload.get("audience_tags")
        else (ctx.profile_badge or "Adventure Seekers"),
        "highlights": _memory_highlights(memories),
        "intelligence": {"metrics": intelligence_metrics, "insight": insight},
        "budget_reflection": budget_reflection,
    }


def _memory_timeline(ctx: SharedExperienceContext) -> list[dict]:
    """Prefer plans + bookings as itinerary day steps; fall back to lifecycle milestones."""
    day_steps: list[dict] = []
    for index, plan in enumerate(ctx.plans[:6]):
        details = plan.get("details") if isinstance(plan.get("details"), dict) else {}
        raw_date = (
            details.get("date")
            or details.get("scheduled_at")
            or details.get("start_at")
            or plan.get("scheduled_at")
            or plan.get("created_at")
            or ""
        )
        title = str(plan.get("title") or plan.get("name") or f"Day {index + 1}")
        if not title.lower().startswith("day"):
            title = f"Day {index + 1} — {title}"
        day_steps.append(
            {
                "event_id": f"plan-{plan.get('id') or index}",
                "title": title,
                "date_label": _date_label(raw_date),
                "is_complete": str(plan.get("status", "")).lower() in {"done", "complete", "completed"},
            }
        )
    for booking in ctx.bookings[:4]:
        raw_date = booking.get("check_in") or booking.get("start_at") or booking.get("created_at") or ""
        name = str(booking.get("title") or booking.get("name") or booking.get("vendor") or "Booking")
        day_steps.append(
            {
                "event_id": f"booking-{booking.get('id') or name}",
                "title": name,
                "date_label": _date_label(raw_date),
                "is_complete": booking_is_confirmed(booking),
            }
        )
    if day_steps:
        return day_steps[:8]

    events: list[dict] = []
    created = ctx.moment.created_at
    if created:
        events.append(
            {
                "event_id": "created",
                "title": "Moment Created",
                "date_label": created.strftime("%d %b %Y") if hasattr(created, "strftime") else str(created)[:10],
                "is_complete": True,
            }
        )
    for g in ctx.guests[:1]:
        events.append(
            {
                "event_id": f"guest-{g.get('id')}",
                "title": "First Member Joined",
                "date_label": relative_time_label(g.get("created_at")) or "—",
                "is_complete": True,
            }
        )
    for b in ctx.bookings[:1]:
        events.append(
            {
                "event_id": f"booking-{b.get('id')}",
                "title": "First Booking",
                "date_label": str(b.get("check_in") or b.get("created_at") or "—")[:10],
                "is_complete": booking_is_confirmed(b),
            }
        )
    if ctx.is_active:
        events.append({"event_id": "activated", "title": "Trip Activated", "date_label": "—", "is_complete": True})
    for m in ctx.memories[:1]:
        events.append(
            {
                "event_id": f"memory-{m.get('id')}",
                "title": "Major Milestone",
                "date_label": relative_time_label(m.get("created_at")) or "—",
                "is_complete": True,
            }
        )
    return events[:8]


def _date_label(raw: object) -> str:
    if raw is None:
        return "—"
    if hasattr(raw, "strftime"):
        try:
            return raw.strftime("%d %b • %I:%M %p").lstrip("0").replace(" 0", " ")
        except Exception:
            pass
    text = str(raw).strip()
    if not text:
        return "—"
    return text[:16] if len(text) > 16 and "T" in text else text[:24]


def _milestone_wall(ctx: SharedExperienceContext) -> list[dict]:
    wall: list[dict] = []
    if ctx.is_active:
        wall.append({"milestone_id": "activated", "label": "Activated", "icon": "star"})
    if ctx.confirmed_booking_count:
        wall.append({"milestone_id": "hotel", "label": "Hotel", "icon": "hotel"})
    if ctx.memory_count:
        wall.append({"milestone_id": "memories", "label": "Memories", "icon": "photo_library"})
    if str(ctx.moment.status or "").upper() == "COMPLETED":
        wall.append({"milestone_id": "completed", "label": "Completed", "icon": "check_circle"})
    return wall[:6]


def _people_impact(ctx: SharedExperienceContext) -> list[dict]:
    labels = ["Most Active", "Most Helpful", "Top Contributor"]
    roster = ctx.members or ctx.guests
    out: list[dict] = []
    for idx, person in enumerate(roster[:3]):
        name = str(person.get("display_name") or person.get("full_name") or "Member")
        out.append(
            {
                "user_id": str(person.get("user_id") or person.get("id") or ""),
                "display_name": name,
                "impact_label": labels[idx] if idx < len(labels) else "Contributor",
                "avatar_url": person.get("avatar_url"),
            }
        )
    return out


def _memory_highlights(memories: list[dict]) -> list[dict]:
    if not memories:
        return []
    highlights = [{"highlight_id": "latest", "label": f"Latest: {memories[0].get('title')}", "icon": "favorite"}]
    if len(memories) > 1:
        highlights.append(
            {"highlight_id": "earlier", "label": f"Earlier: {memories[1].get('title')}", "icon": "event_available"}
        )
    return highlights
