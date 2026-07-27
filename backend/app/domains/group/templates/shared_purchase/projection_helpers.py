"""Shared helpers for Shared Purchase pulse / moments / memory projections."""
from __future__ import annotations

from datetime import datetime, timezone

from app.domains.group import moment_store as store
from app.domains.group.templates.shared_purchase.context import SharedPurchaseContext


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


def readiness_score(ctx: SharedPurchaseContext) -> float:
    score = 10.0
    score += min(25, ctx.contributor_count * 5)
    if ctx.target_amount_minor > 0:
        score += min(30, ctx.contribution_progress_percent * 0.3)
    score += min(15, ctx.vendor_count * 8)
    score += min(10, ctx.ownership_count * 5)
    score += min(10, ctx.milestone_count * 4)
    if ctx.memory_count:
        score += min(10, ctx.memory_count * 3)
    return min(100.0, round(score, 1))


def participation_percent(ctx: SharedPurchaseContext) -> float:
    total = ctx.active_contributor_count + ctx.pending_contributor_count + ctx.inactive_contributor_count
    if total <= 0:
        total = ctx.contributor_count
    if total <= 0:
        return 0.0
    return min(100.0, round(ctx.active_contributor_count / total * 100, 1))


def health_dimensions(ctx: SharedPurchaseContext) -> list[dict]:
    funding_pct = ctx.contribution_progress_percent
    participation_pct = participation_percent(ctx)
    vendor_pct = min(100.0, ctx.vendor_count * 40.0) if ctx.vendor_count else 0.0
    ownership_pct = min(100.0, ctx.ownership_count * 50.0) if ctx.ownership_count else 0.0
    return [
        {"label": "Funding", "percent": funding_pct, "status": f"{int(funding_pct)}%", "accent": "primary"},
        {"label": "Participation", "percent": participation_pct, "status": f"{int(participation_pct)}%", "accent": "primary"},
        {"label": "Vendor", "percent": vendor_pct, "status": f"{int(vendor_pct)}%", "accent": "primary"},
        {"label": "Ownership", "percent": ownership_pct, "status": f"{int(ownership_pct)}%", "accent": "primary"},
    ]


def experience_health_percent(ctx: SharedPurchaseContext) -> float:
    dims = health_dimensions(ctx)
    if not any(d["percent"] for d in dims):
        return readiness_score(ctx)
    return round(sum(d["percent"] for d in dims) / len(dims), 1)


def attention_items(ctx: SharedPurchaseContext) -> list[dict]:
    items: list[dict] = []
    if ctx.target_amount_minor and ctx.amount_remaining_minor > 0:
        items.append(
            {
                "id": "funding-gap",
                "title": "Funding target not reached",
                "subtitle": f"{format_money(ctx.amount_remaining_minor, ctx.currency_code)} remaining",
                "icon": "account_balance_wallet",
                "accent": "error",
                "action": "contribution",
            }
        )
    if ctx.vendor_count == 0:
        items.append(
            {
                "id": "vendor-missing",
                "title": "Vendor selection pending",
                "subtitle": "Add vendors to compare quotes",
                "icon": "storefront",
                "accent": "tertiary",
                "action": "vendor",
            }
        )
    if ctx.ownership_count == 0 and ctx.contribution_total_minor > 0:
        items.append(
            {
                "id": "ownership-pending",
                "title": "Ownership not assigned",
                "subtitle": "Finalize ownership shares",
                "icon": "supervised_user_circle",
                "accent": "secondary",
                "action": "ownership",
            }
        )
    open_decisions = [d for d in ctx.decisions if str(d.get("status", "open")).lower() not in {"closed", "resolved"}]
    if open_decisions:
        items.append(
            {
                "id": str(open_decisions[0].get("id") or "decision-open"),
                "title": str(open_decisions[0].get("title") or "Decision awaiting vote"),
                "subtitle": "Resolve open purchase decisions",
                "icon": "how_to_vote",
                "accent": "secondary",
                "action": "decision",
            }
        )
    return items[:5]


def next_best_action(ctx: SharedPurchaseContext) -> dict:
    if ctx.contributor_count == 0:
        return {
            "title": "Invite contributors",
            "subtitle": "Add people who will fund this purchase.",
            "action": "participant",
            "impact_labels": ["+8 Health", "+15 Progress", "+10 Participation"],
        }
    if ctx.contribution_total_minor == 0:
        return {
            "title": "Log first contribution",
            "subtitle": "Track funding progress.",
            "action": "contribution",
            "impact_labels": ["+6 Health", "+12 Progress"],
        }
    if ctx.target_amount_minor and ctx.amount_remaining_minor > 0:
        return {
            "title": f"Collect remaining {format_money(ctx.amount_remaining_minor, ctx.currency_code)}",
            "subtitle": "Close the funding gap across contributors.",
            "action": "contribution",
            "impact_labels": ["+6 Health", "+12 Progress", "+5 Participation"],
        }
    if ctx.vendor_count == 0:
        return {
            "title": "Add a vendor",
            "subtitle": "Compare quotes before purchase.",
            "action": "vendor",
            "impact_labels": ["+4 Health", "+8 Progress"],
        }
    if ctx.ownership_count == 0:
        return {
            "title": "Assign ownership",
            "subtitle": "Clarify who owns what after purchase.",
            "action": "ownership",
            "impact_labels": ["+5 Health"],
        }
    if ctx.memory_count == 0 and ctx.is_active:
        return {
            "title": "Capture the first memory",
            "subtitle": "Start the shared story for this purchase.",
            "action": "memory",
            "impact_labels": ["+3 Participation"],
        }
    return {
        "title": "Review purchase progress",
        "subtitle": "Check funding, vendors, and ownership.",
        "action": "hub",
        "impact_labels": ["+2 Health"],
    }


def insights(ctx: SharedPurchaseContext) -> list[dict]:
    out: list[dict] = []
    if ctx.active_contributor_count >= 2:
        out.append(
            {
                "id": "participation",
                "title": "Contributors engaged",
                "subtitle": f"{ctx.active_contributor_count} active contributors",
                "icon": "trending_up",
                "accent": "primary",
            }
        )
    if ctx.target_amount_minor > 0 and ctx.contribution_progress_percent >= 50:
        out.append(
            {
                "id": "funding",
                "title": "Funding on track",
                "subtitle": f"{int(ctx.contribution_progress_percent)}% of target collected",
                "icon": "savings",
                "accent": "primary",
            }
        )
    if ctx.vendor_count > 0:
        out.append(
            {
                "id": "vendors",
                "title": "Vendor options ready",
                "subtitle": f"{ctx.vendor_count} vendors tracked",
                "icon": "storefront",
                "accent": "primary",
            }
        )
    return out[:3]


def dashboard_recent_items(ctx: SharedPurchaseContext) -> list[dict]:
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


def stat_tiles(ctx: SharedPurchaseContext) -> list[dict]:
    return [
        {"label": "Target", "value": format_money(ctx.target_amount_minor, ctx.currency_code) if ctx.target_amount_minor else "—", "highlight": False},
        {"label": "Collected", "value": format_money(ctx.contribution_total_minor, ctx.currency_code) if ctx.contribution_total_minor else "—", "highlight": True},
        {"label": "Contributors", "value": str(ctx.contributor_count), "highlight": False},
        {"label": "Items", "value": str(ctx.item_count or ctx.milestone_count), "highlight": False},
    ]


def money_columns(ctx: SharedPurchaseContext) -> list[dict]:
    target = ctx.target_amount_minor
    collected = ctx.contribution_total_minor
    remaining = ctx.amount_remaining_minor
    return [
        {"label": "Target", "value": format_money(target, ctx.currency_code) if target else "—", "highlight": False},
        {"label": "Collected", "value": format_money(collected, ctx.currency_code) if collected else "—", "highlight": True},
        {"label": "Remaining", "value": format_money(remaining, ctx.currency_code) if remaining else "—", "highlight": remaining > 0},
        {
            "label": "Spent",
            "value": format_money(ctx.expense_total_minor, ctx.currency_code) if ctx.expense_total_minor else "—",
            "highlight": False,
        },
    ]


def focus_items(ctx: SharedPurchaseContext) -> list[dict]:
    return [
        {"label": "Reach funding target", "is_complete": ctx.amount_remaining_minor == 0 and ctx.target_amount_minor > 0},
        {"label": "Confirm vendor selection", "is_complete": ctx.vendor_count > 0},
        {"label": "Assign ownership shares", "is_complete": ctx.ownership_count > 0},
    ][:5]


def build_memory_hub(ctx: SharedPurchaseContext) -> dict:
    memories = ctx.memories
    contributors = ctx.contributor_count
    milestones = _milestone_wall(ctx)
    timeline = _memory_timeline(ctx)
    gallery = [
        {
            "memory_id": str(m.get("id") or store.new_id()),
            "title": str(m.get("title") or "Memory"),
            "image_url": m.get("image_url") or m.get("cover_url"),
        }
        for m in memories[:8]
    ]
    people_impact = _people_impact(ctx)
    budget_reflection = None
    if ctx.target_amount_minor > 0 and ctx.contribution_total_minor > 0:
        accuracy = min(100, round(ctx.contribution_progress_percent))
        remaining = ctx.amount_remaining_minor
        budget_reflection = {
            "planned_budget": format_money(ctx.target_amount_minor, ctx.currency_code),
            "actual_spend": format_money(ctx.expense_total_minor, ctx.currency_code)
            if ctx.expense_total_minor
            else format_money(ctx.contribution_total_minor, ctx.currency_code),
            "budget_accuracy": f"{accuracy}%",
            "best_controlled": "Contributions" if ctx.contribution_total_minor else None,
            "highest_variance": "Expenses" if ctx.expense_count else None,
            "summary": f"{format_money(remaining, ctx.currency_code)} remaining to target" if remaining > 0 else "Funding target reached",
        }
    intelligence_metrics = []
    pct = participation_percent(ctx)
    if pct:
        intelligence_metrics.append({"label": "Participation", "value": f"+{int(pct)}%"})
    if ctx.contribution_total_minor:
        intelligence_metrics.append({"label": "Raised", "value": format_money(ctx.contribution_total_minor, ctx.currency_code)})
    if ctx.is_active:
        intelligence_metrics.append({"label": "Completion", "value": f"{int(readiness_score(ctx))}%"})
    insight = ""
    if ctx.contribution_progress_percent >= 80:
        insight = "Strong funding velocity. The group closes gaps quickly when ownership is clear."
    elif ctx.memory_count:
        insight = "Consistent contributions and shared memories build purchase confidence."
    elif ctx.vendor_count:
        insight = "Vendor comparison early reduces purchase risk."
    return {
        "hero": {
            "moment_name": ctx.moment_name,
            "cover_image_url": ctx.setup_payload.get("cover_image_url"),
            "chips": [
                {"icon": "group", "label": f"{contributors} Contributors"},
                {
                    "icon": "savings",
                    "label": f"{format_money(ctx.contribution_total_minor, ctx.currency_code)} raised"
                    if ctx.contribution_total_minor
                    else "Funding started",
                },
                {
                    "icon": "military_tech",
                    "label": "Asset Acquired" if ctx.ownership_count or str(ctx.moment.status or "").upper() == "COMPLETED" else f"{len(milestones)} Milestones",
                },
            ],
            "hero_icon": "shopping_cart",
        },
        "timeline": timeline,
        "milestone_wall": milestones,
        "people_impact": people_impact,
        "gallery": gallery,
        "lessons_pattern": "Purchases succeed when funding and ownership are finalized early." if ctx.contribution_total_minor else "",
        "group_identity": str(ctx.setup_payload.get("audience_tags", ["Collaborative Buyers"])[0])
        if ctx.setup_payload.get("audience_tags")
        else (ctx.profile_badge or "Collaborative Buyers"),
        "highlights": _memory_highlights(memories),
        "intelligence": {"metrics": intelligence_metrics, "insight": insight},
        "budget_reflection": budget_reflection,
    }


def _memory_timeline(ctx: SharedPurchaseContext) -> list[dict]:
    events: list[dict] = []
    created = ctx.moment.created_at
    if created:
        events.append(
            {
                "event_id": "created",
                "title": "Purchase Created",
                "date_label": created.strftime("%d %b %Y") if hasattr(created, "strftime") else str(created)[:10],
                "is_complete": True,
            }
        )
    for g in ctx.guests[:1]:
        events.append(
            {
                "event_id": f"guest-{g.get('id')}",
                "title": "First Contributor Joined",
                "date_label": relative_time_label(g.get("created_at")) or "—",
                "is_complete": True,
            }
        )
    for c in ctx.contributions[:1]:
        events.append(
            {
                "event_id": f"contrib-{c.get('id')}",
                "title": "First Contribution",
                "date_label": relative_time_label(c.get("created_at")) or "—",
                "is_complete": True,
            }
        )
    if ctx.is_active:
        events.append({"event_id": "activated", "title": "Purchase Activated", "date_label": "—", "is_complete": True})
    if ctx.ownership_count:
        events.append({"event_id": "ownership", "title": "Ownership Assigned", "date_label": "—", "is_complete": True})
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


def _milestone_wall(ctx: SharedPurchaseContext) -> list[dict]:
    wall: list[dict] = []
    if ctx.contribution_progress_percent >= 100 and ctx.target_amount_minor > 0:
        wall.append({"milestone_id": "funding", "label": "Funding Reached", "icon": "savings"})
    elif ctx.contribution_total_minor > 0:
        wall.append({"milestone_id": "funding-started", "label": "Funding Started", "icon": "trending_up"})
    if ctx.expense_count or ctx.item_count:
        wall.append({"milestone_id": "purchased", "label": "Asset Purchased", "icon": "shopping_bag"})
    if ctx.ownership_count:
        wall.append({"milestone_id": "ownership", "label": "Ownership Assigned", "icon": "supervised_user_circle"})
    if ctx.is_active:
        wall.append({"milestone_id": "activated", "label": "Activated", "icon": "star"})
    if str(ctx.moment.status or "").upper() == "COMPLETED":
        wall.append({"milestone_id": "completed", "label": "Completed", "icon": "check_circle"})
    return wall[:6]


def _people_impact(ctx: SharedPurchaseContext) -> list[dict]:
    labels = ["Most Active", "Top Contributor", "Most Helpful"]
    roster = ctx.guests
    out: list[dict] = []
    for idx, person in enumerate(roster[:3]):
        name = str(person.get("display_name") or person.get("full_name") or "Contributor")
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
