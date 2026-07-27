"""Moments projection mapper for Shared Living."""
from __future__ import annotations

from app.domains.group import trip_schemas as t
from app.domains.group.templates.shared_living.context import SharedLivingContext
from app.domains.group.templates.shared_living.projection_helpers import (
    build_memory_hub,
    contribution_coverage_percent,
    focus_items,
    format_money,
    money_columns,
    next_best_action,
    open_maintenance_count,
    open_task_count,
    outstanding_minor,
    stat_tiles,
)


def _money_progress(ctx: SharedLivingContext) -> tuple[str, float]:
    if ctx.expense_total_minor <= 0 and ctx.contribution_total_minor <= 0:
        return "No spend tracked yet", 0.0
    pct = contribution_coverage_percent(ctx)
    if ctx.expense_total_minor > 0:
        return f"Collection progress at {int(pct)}%", pct
    return f"{format_money(ctx.contribution_total_minor, ctx.currency_code)} collected", 55.0


def _activity_ops(ctx: SharedLivingContext) -> list[dict]:
    return [
        {"tile_id": "open_tasks", "label": "Open Tasks", "value": str(open_task_count(ctx)), "icon": "checklist"},
        {
            "tile_id": "maintenance",
            "label": "Maintenance",
            "value": str(open_maintenance_count(ctx)),
            "icon": "build",
        },
        {"tile_id": "rules", "label": "Active Rules", "value": str(ctx.rules_count), "icon": "gavel"},
    ]


def _assets(ctx: SharedLivingContext) -> list[dict]:
    furniture = len([a for a in ctx.assets if "furniture" in str(a.get("asset_type") or a.get("type") or "").lower()])
    appliances = len([a for a in ctx.assets if "appliance" in str(a.get("asset_type") or a.get("type") or "").lower()])
    shared = max(0, ctx.assets_count - furniture - appliances)
    docs = len(ctx.rules)  # house docs often live alongside rules/notes
    return [
        {"asset_id": "furniture", "label": "Furniture", "count": furniture or ctx.assets_count, "icon": "chair"},
        {"asset_id": "appliances", "label": "Appliances", "count": appliances, "icon": "kitchen"},
        {"asset_id": "shared", "label": "Shared", "count": shared, "icon": "inventory_2"},
        {"asset_id": "docs", "label": "Docs", "count": docs, "icon": "description"},
    ]


def _decisions(ctx: SharedLivingContext) -> list[dict]:
    rows: list[dict] = []
    for poll in ctx.polls[:6]:
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
    return rows[:6]


def build_moments(ctx: SharedLivingContext) -> dict:
    progress_label, progress_pct = _money_progress(ctx)
    memory_hub_data = build_memory_hub(ctx)
    nba = next_best_action(ctx)
    health = progress_pct if ctx.expense_total_minor else min(100.0, 20.0 + ctx.resident_count * 15)
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_LIVING",
        "moment_name": ctx.moment_name,
        "stage_badge": ctx.stage_badge,
        "status_badge": ctx.status_badge,
        "profile_badge": ctx.profile_badge,
        "health_percent": health,
        "expenses_total_minor": ctx.expense_total_minor,
        "resident_count": ctx.resident_count,
        "contribution_coverage_percent": progress_pct,
        "outstanding_minor": outstanding_minor(ctx),
        "expense_timeline": [
            {
                "id": e.get("id"),
                "title": e.get("description"),
                "amount_minor": e.get("amount_minor"),
                "created_at": e.get("created_at"),
            }
            for e in ctx.expenses[:20]
        ],
        "contribution_timeline": [
            {
                "id": c.get("id"),
                "title": c.get("title"),
                "amount_minor": c.get("amount_minor"),
                "created_at": c.get("created_at"),
            }
            for c in ctx.contributions[:20]
        ],
        "chore_timeline": ctx.chores[:10],
        "house_updates": ctx.updates[:10],
        "recent_activity": ctx.activities[:10],
        "memory_hero_title": ctx.moment_name,
        "memory_hero_subtitle": "Your home's shared story starts here."
        if ctx.memory_count == 0
        else f"{ctx.memory_count} memories captured",
        "next_best_action": nba,
        "operations_hub": t.GroupMomentsOperationsHub(
            core_summary=t.GroupMomentsCoreSummary(
                eyebrow="SHARED LIVING",
                eyebrow_icon="home",
                moment_name=ctx.moment_name,
                stage_badge=ctx.stage_badge,
                stat_tiles=[t.GroupMomentsStatTile(**tile) for tile in stat_tiles(ctx)],
            ),
            people_roles=t.GroupMomentsPeopleRoles(
                primary=ctx.primary_organizer,
                role_counts=ctx.role_counts,
                view_all_action="residents",
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
                hero_icon="home",
            ),
        ).model_dump(mode="json"),
        "memory_hub": t.GroupMomentsMemoryHub(
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
        ).model_dump(mode="json"),
    }
