"""Shared helpers for Shared Living pulse / moments / memory projections."""
from __future__ import annotations

from datetime import datetime, timezone

from app.domains.group import moment_store as store
from app.domains.group.templates.shared_living.context import SharedLivingContext
from app.core.storage import resolve_memory_image_url


def _memory_image_url(memory: dict) -> str | None:
    return resolve_memory_image_url(memory)


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


def open_task_count(ctx: SharedLivingContext) -> int:
    return len([t for t in ctx.chores if str(t.get("status", "open")).lower() not in {"done", "completed", "closed"}])


def open_maintenance_count(ctx: SharedLivingContext) -> int:
    return len(
        [
            m
            for m in ctx.maintenance
            if str(m.get("status", "open")).lower() not in {"done", "completed", "resolved", "closed"}
        ]
    )


def contribution_coverage_percent(ctx: SharedLivingContext) -> float:
    if ctx.expense_total_minor <= 0:
        return 100.0 if ctx.contribution_total_minor > 0 else 0.0
    return min(100.0, round(ctx.contribution_total_minor / ctx.expense_total_minor * 100, 1))


def outstanding_minor(ctx: SharedLivingContext) -> int:
    return max(0, ctx.expense_total_minor - ctx.contribution_total_minor)


def readiness_score(ctx: SharedLivingContext) -> float:
    score = 10.0
    score += min(25, ctx.resident_count * 8)
    if ctx.expense_count:
        score += min(20, 10 + contribution_coverage_percent(ctx) * 0.1)
    score += min(15, open_task_count(ctx) * 0 + (15 if ctx.task_count else 0))
    # Prefer completed rhythm: reward having tasks logged and few open
    open_tasks = open_task_count(ctx)
    if ctx.task_count:
        done_pct = max(0, 100 - (open_tasks / max(1, ctx.task_count) * 100))
        score += min(15, done_pct * 0.15)
    score += min(10, ctx.rules_count * 4)
    score += min(10, ctx.assets_count * 3)
    if ctx.memory_count:
        score += min(10, ctx.memory_count * 3)
    return min(100.0, round(score, 1))


def participation_percent(ctx: SharedLivingContext) -> float:
    total = ctx.active_resident_count + ctx.pending_resident_count + ctx.inactive_resident_count
    if total <= 0:
        total = ctx.resident_count
    if total <= 0:
        return 0.0
    return min(100.0, round(ctx.active_resident_count / total * 100, 1))


def health_dimensions(ctx: SharedLivingContext) -> list[dict]:
    contrib_pct = contribution_coverage_percent(ctx)
    open_tasks = open_task_count(ctx)
    task_pct = 100.0 if ctx.task_count and open_tasks == 0 else (
        max(0.0, 100.0 - open_tasks * 25.0) if ctx.task_count else 0.0
    )
    maint_open = open_maintenance_count(ctx)
    maint_pct = 100.0 if ctx.maintenance_count and maint_open == 0 else (
        max(0.0, 100.0 - maint_open * 30.0) if ctx.maintenance_count else (50.0 if ctx.is_active else 0.0)
    )
    participation_pct = participation_percent(ctx)
    return [
        {"label": "Contributions", "percent": contrib_pct, "status": f"{int(contrib_pct)}%", "accent": "primary"},
        {"label": "Tasks", "percent": task_pct, "status": f"{int(task_pct)}%", "accent": "primary"},
        {"label": "Maintenance", "percent": maint_pct, "status": f"{int(maint_pct)}%", "accent": "primary"},
        {"label": "Participation", "percent": participation_pct, "status": f"{int(participation_pct)}%", "accent": "primary"},
    ]


def experience_health_percent(ctx: SharedLivingContext) -> float:
    dims = health_dimensions(ctx)
    if not any(d["percent"] for d in dims):
        return readiness_score(ctx)
    return round(sum(d["percent"] for d in dims) / len(dims), 1)


def attention_items(ctx: SharedLivingContext) -> list[dict]:
    items: list[dict] = []
    for m in ctx.maintenance:
        status = str(m.get("status", "open")).lower()
        if status in {"done", "completed", "resolved", "closed"}:
            continue
        items.append(
            {
                "id": str(m.get("id") or "maintenance"),
                "title": str(m.get("title") or m.get("description") or "Maintenance needed"),
                "subtitle": str(m.get("priority") or "Open maintenance"),
                "icon": "build",
                "accent": "error",
                "action": "maintenance",
            }
        )
        if len(items) >= 5:
            break
    for chore in ctx.chores:
        status = str(chore.get("status", "open")).lower()
        if status in {"done", "completed", "closed"}:
            continue
        due = chore.get("due_date") or chore.get("next_due_date")
        items.append(
            {
                "id": str(chore.get("id") or "chore"),
                "title": str(chore.get("title") or "Open chore"),
                "subtitle": f"Due {due}" if due else "Task still open",
                "icon": "checklist",
                "accent": "tertiary",
                "action": "tasks",
            }
        )
        if len(items) >= 5:
            break
    outstanding = outstanding_minor(ctx)
    if outstanding > 0:
        items.append(
            {
                "id": "contribution-gap",
                "title": "Pending contributions",
                "subtitle": f"{format_money(outstanding, ctx.currency_code)} outstanding vs spend",
                "icon": "payments",
                "accent": "secondary",
                "action": "contributions",
            }
        )
    if ctx.resident_count == 0:
        items.append(
            {
                "id": "residents-missing",
                "title": "No residents yet",
                "subtitle": "Invite the people you live with",
                "icon": "group_add",
                "accent": "error",
                "action": "residents",
            }
        )
    return items[:5]


def next_best_action(ctx: SharedLivingContext) -> dict:
    if ctx.resident_count == 0:
        return {
            "title": "Invite residents",
            "subtitle": "Add the people you live with.",
            "action": "residents",
            "impact_labels": ["+8 Health", "+15 Participation"],
        }
    if ctx.expense_count == 0:
        return {
            "title": "Log first expense",
            "subtitle": "Track shared household costs.",
            "action": "expenses",
            "impact_labels": ["+6 Health", "+12 Progress"],
        }
    if open_task_count(ctx) == 0 and ctx.task_count == 0:
        return {
            "title": "Add a chore",
            "subtitle": "Keep the home running smoothly.",
            "action": "tasks",
            "impact_labels": ["+5 Health", "+8 Progress"],
        }
    if outstanding_minor(ctx) > 0:
        return {
            "title": f"Collect {format_money(outstanding_minor(ctx), ctx.currency_code)}",
            "subtitle": "Close the contribution gap this month.",
            "action": "contributions",
            "impact_labels": ["+6 Health", "+10 Progress"],
        }
    if open_maintenance_count(ctx) > 0:
        return {
            "title": "Resolve maintenance",
            "subtitle": "Clear open home issues.",
            "action": "maintenance",
            "impact_labels": ["+5 Health"],
        }
    if ctx.memory_count == 0 and ctx.is_active:
        return {
            "title": "Capture a home memory",
            "subtitle": "Start the shared living story.",
            "action": "memory",
            "impact_labels": ["+3 Participation"],
        }
    return {
        "title": "Review home rhythm",
        "subtitle": "Check expenses, chores, and participation.",
        "action": "review",
        "impact_labels": ["+2 Health"],
    }


def insights(ctx: SharedLivingContext) -> list[dict]:
    out: list[dict] = []
    if ctx.active_resident_count >= 2:
        out.append(
            {
                "id": "participation",
                "title": "Household engaged",
                "subtitle": f"{ctx.active_resident_count} active residents",
                "icon": "trending_up",
                "accent": "primary",
            }
        )
    coverage = contribution_coverage_percent(ctx)
    if ctx.expense_total_minor > 0 and coverage >= 80:
        out.append(
            {
                "id": "contributions",
                "title": "Contributions on track",
                "subtitle": f"{int(coverage)}% of spend covered",
                "icon": "savings",
                "accent": "primary",
            }
        )
    if ctx.task_count and open_task_count(ctx) == 0:
        out.append(
            {
                "id": "chores",
                "title": "Chores cleared",
                "subtitle": "No open tasks right now",
                "icon": "task_alt",
                "accent": "primary",
            }
        )
    if ctx.rules_count:
        out.append(
            {
                "id": "rules",
                "title": "House rules set",
                "subtitle": f"{ctx.rules_count} rules active",
                "icon": "gavel",
                "accent": "primary",
            }
        )
    return out[:3]


def dashboard_recent_items(ctx: SharedLivingContext) -> list[dict]:
    items: list[dict] = []
    for a in ctx.activities[:5]:
        activity_id = str(a.get("id") or "").strip()
        if not activity_id:
            # Skip unpersisted rows — never invent ids that GET /activity/{id} cannot resolve.
            continue
        items.append(
            {
                "id": activity_id,
                "activity_type": str(a.get("activity_type") or "UPDATE"),
                "title": str(a.get("title") or "Activity"),
                "subtitle": str(a.get("subtitle") or ""),
                "occurred_at": str(a.get("occurred_at") or ""),
                "relative_time": relative_time_label(a.get("occurred_at")),
                "icon": str(a.get("icon") or "home"),
            }
        )
    return items


def stat_tiles(ctx: SharedLivingContext) -> list[dict]:
    return [
        {"label": "Residents", "value": str(ctx.resident_count), "highlight": False},
        {
            "label": "Monthly Spend",
            "value": format_money(ctx.expense_total_minor, ctx.currency_code) if ctx.expense_total_minor else "—",
            "highlight": True,
        },
        {
            "label": "Contributions",
            "value": format_money(ctx.contribution_total_minor, ctx.currency_code) if ctx.contribution_total_minor else "—",
            "highlight": False,
        },
        {"label": "Open Tasks", "value": str(open_task_count(ctx)), "highlight": open_task_count(ctx) > 0},
    ]


def money_columns(ctx: SharedLivingContext) -> list[dict]:
    return [
        {
            "label": "Monthly Spend",
            "value": format_money(ctx.expense_total_minor, ctx.currency_code) if ctx.expense_total_minor else "—",
            "highlight": False,
        },
        {
            "label": "Collected",
            "value": format_money(ctx.contribution_total_minor, ctx.currency_code) if ctx.contribution_total_minor else "—",
            "highlight": True,
        },
        {
            "label": "Outstanding",
            "value": format_money(outstanding_minor(ctx), ctx.currency_code) if outstanding_minor(ctx) else "—",
            "highlight": outstanding_minor(ctx) > 0,
        },
    ]


def focus_items(ctx: SharedLivingContext) -> list[dict]:
    return [
        {"label": "Invite all residents", "is_complete": ctx.resident_count > 0},
        {"label": "Cover monthly spend", "is_complete": outstanding_minor(ctx) == 0 and ctx.expense_total_minor > 0},
        {"label": "Clear open chores", "is_complete": open_task_count(ctx) == 0 and ctx.task_count > 0},
    ][:5]


def build_memory_hub(ctx: SharedLivingContext) -> dict:
    memories = ctx.memories
    timeline = _memory_timeline(ctx)
    milestones = _milestone_wall(ctx)
    gallery = [
        {
            "memory_id": str(m.get("id") or store.new_id()),
            "title": str(m.get("title") or "Memory"),
            "image_url": _memory_image_url(m),
        }
        for m in memories[:8]
    ]
    people_impact = _people_impact(ctx)
    budget_reflection = None
    if ctx.expense_total_minor > 0:
        budget_reflection = {
            "planned_budget": format_money(ctx.expense_total_minor, ctx.currency_code),
            "actual_spend": format_money(ctx.expense_total_minor, ctx.currency_code),
            "budget_accuracy": f"{int(contribution_coverage_percent(ctx))}%",
            "best_controlled": "Contributions" if ctx.contribution_total_minor else None,
            "highest_variance": "Expenses" if outstanding_minor(ctx) else None,
            "summary": f"{format_money(outstanding_minor(ctx), ctx.currency_code)} outstanding"
            if outstanding_minor(ctx)
            else "Household contributions cover spend",
        }
    intelligence_metrics = []
    pct = participation_percent(ctx)
    if pct:
        intelligence_metrics.append({"label": "Harmony", "value": f"+{int(pct)}%"})
    if ctx.contribution_total_minor:
        intelligence_metrics.append(
            {"label": "Savings", "value": format_money(ctx.contribution_total_minor, ctx.currency_code)}
        )
    if ctx.is_active:
        intelligence_metrics.append({"label": "Goals", "value": f"{int(readiness_score(ctx))}%"})
    insight = ""
    if contribution_coverage_percent(ctx) >= 80 and ctx.expense_total_minor:
        insight = "Strong contribution rhythm. Shared living stays calm when money is visible."
    elif ctx.memory_count:
        insight = "Shared memories deepen household belonging beyond chores and bills."
    elif ctx.task_count:
        insight = "Clear chore ownership keeps participation high."
    return {
        "hero": {
            "moment_name": ctx.moment_name,
            "cover_image_url": ctx.setup_payload.get("cover_image_url"),
            "chips": [
                {"icon": "group", "label": f"{ctx.resident_count} Residents"},
                {"icon": "auto_awesome", "label": f"{ctx.memory_count} Shared Moments"},
                {"icon": "military_tech", "label": f"{len(milestones)} Milestones"},
            ],
            "hero_icon": "home",
        },
        "timeline": timeline,
        "milestone_wall": milestones,
        "people_impact": people_impact,
        "gallery": gallery,
        "lessons_pattern": "Homes thrive when chores, contributions, and communication stay in sync."
        if ctx.expense_count or ctx.task_count
        else "",
        "group_identity": str(ctx.setup_payload.get("audience_tags", [ctx.profile_badge or "Cooperative Household"])[0])
        if ctx.setup_payload.get("audience_tags")
        else (ctx.profile_badge or "Cooperative Household"),
        "highlights": _memory_highlights(memories),
        "intelligence": {"metrics": intelligence_metrics, "insight": insight},
        "budget_reflection": budget_reflection,
    }


def _memory_timeline(ctx: SharedLivingContext) -> list[dict]:
    events: list[dict] = []
    created = ctx.moment.created_at
    if created:
        events.append(
            {
                "event_id": "created",
                "title": "Home Created",
                "date_label": created.strftime("%d %b %Y") if hasattr(created, "strftime") else str(created)[:10],
                "is_complete": True,
            }
        )
    for r in ctx.residents[:1]:
        events.append(
            {
                "event_id": f"resident-{r.get('id')}",
                "title": "First Resident Joined",
                "date_label": relative_time_label(r.get("created_at")) or "—",
                "is_complete": True,
            }
        )
    for e in ctx.expenses[:1]:
        events.append(
            {
                "event_id": f"expense-{e.get('id')}",
                "title": "First Expense Logged",
                "date_label": relative_time_label(e.get("created_at")) or "—",
                "is_complete": True,
            }
        )
    if ctx.is_active:
        events.append({"event_id": "activated", "title": "Home Activated", "date_label": "—", "is_complete": True})
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


def _milestone_wall(ctx: SharedLivingContext) -> list[dict]:
    wall: list[dict] = []
    if ctx.resident_count:
        wall.append({"milestone_id": "residents", "label": "Residents Settled", "icon": "group"})
    if ctx.expense_count:
        wall.append({"milestone_id": "expenses", "label": "Spend Tracking", "icon": "payments"})
    if ctx.task_count:
        wall.append({"milestone_id": "chores", "label": "Chore Rhythm", "icon": "checklist"})
    if ctx.rules_count:
        wall.append({"milestone_id": "rules", "label": "House Rules", "icon": "gavel"})
    if ctx.is_active:
        wall.append({"milestone_id": "activated", "label": "Activated", "icon": "star"})
    if str(ctx.moment.status or "").upper() == "COMPLETED":
        wall.append({"milestone_id": "completed", "label": "Completed", "icon": "check_circle"})
    return wall[:6]


def _people_impact(ctx: SharedLivingContext) -> list[dict]:
    labels = ["Most Active", "Most Helpful", "Steady Contributor"]
    out: list[dict] = []
    for idx, person in enumerate(ctx.residents[:3]):
        name = str(person.get("display_name") or person.get("full_name") or person.get("name") or "Resident")
        out.append(
            {
                "user_id": str(person.get("user_id") or person.get("id") or ""),
                "display_name": name,
                "impact_label": labels[idx] if idx < len(labels) else "Resident",
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
