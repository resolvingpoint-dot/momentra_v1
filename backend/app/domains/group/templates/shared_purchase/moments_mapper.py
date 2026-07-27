"""Moments projection mapper for Shared Purchase."""
from __future__ import annotations

from app.domains.group import trip_schemas as t
from app.domains.group.templates.shared_purchase.context import SharedPurchaseContext
from app.domains.group.templates.shared_purchase.projection_helpers import (
    build_memory_hub,
    focus_items,
    format_money,
    money_columns,
    next_best_action,
    stat_tiles,
)


def _money_progress(ctx: SharedPurchaseContext) -> tuple[str, float]:
    if ctx.target_amount_minor <= 0 and ctx.contribution_total_minor <= 0:
        return "No funding yet", 0.0
    pct = ctx.contribution_progress_percent
    if ctx.target_amount_minor > 0:
        return f"Funding progress at {int(pct)}%", pct
    return f"{format_money(ctx.contribution_total_minor, ctx.currency_code)} funded", 55.0


def _activity_ops(ctx: SharedPurchaseContext) -> list[dict]:
    return [
        {"tile_id": "shortlisted", "label": "Shortlisted", "value": str(ctx.shortlisted_count or ctx.item_count), "icon": "bookmark"},
        {"tile_id": "in_progress", "label": "In Progress", "value": str(ctx.in_progress_count), "icon": "pending"},
        {"tile_id": "pending", "label": "Pending", "value": str(ctx.pending_item_count), "icon": "hourglass_empty"},
    ]


def _assets(ctx: SharedPurchaseContext) -> list[dict]:
    return [
        {"asset_id": "assets", "label": "Assets", "count": ctx.item_count or ctx.expense_count, "icon": "inventory_2"},
        {"asset_id": "ownership", "label": "Ownership", "count": ctx.ownership_count, "icon": "supervised_user_circle"},
        {"asset_id": "invoices", "label": "Invoices", "count": ctx.invoice_count or ctx.document_count, "icon": "receipt_long"},
        {"asset_id": "receipts", "label": "Receipts", "count": ctx.receipt_count, "icon": "receipt"},
    ]


def _decisions(ctx: SharedPurchaseContext) -> list[dict]:
    rows: list[dict] = []
    for poll in ctx.polls[:3]:
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
    for decision in ctx.decisions[:4]:
        if decision.get("deleted"):
            continue
        status = str(decision.get("status") or "open").lower()
        active = status not in {"closed", "resolved", "done"}
        rows.append(
            {
                "decision_id": str(decision.get("id") or ""),
                "title": str(decision.get("title") or "Decision"),
                "status_label": str(decision.get("status_label") or ("VOTES PENDING" if active else "AWAITING OWNER")),
                "icon": "gavel",
                "is_active": active,
                "action": "decision",
            }
        )
    if not rows and ctx.vendor_count:
        rows.append(
            {
                "decision_id": "vendor-selection",
                "title": "Vendor Selection",
                "status_label": "VOTES PENDING",
                "icon": "storefront",
                "is_active": True,
                "action": "vendor",
            }
        )
    return rows[:6]


def build_moments(ctx: SharedPurchaseContext) -> dict:
    progress_label, progress_pct = _money_progress(ctx)
    memory_hub_data = build_memory_hub(ctx)
    nba = next_best_action(ctx)
    return {
        "moment_id": str(ctx.moment.id),
        "moment_type": "SHARED_PURCHASE",
        "moment_name": ctx.moment_name,
        "stage_badge": ctx.stage_badge,
        "status_badge": ctx.status_badge,
        "profile_badge": ctx.profile_badge,
        "journey_hero": {
            "title": ctx.moment_name,
            "subtitle": ctx.purchase_goal or "Your shared purchase journey",
            "funding_percent": progress_pct,
        },
        "contribution_timeline": [
            {"id": c.get("id"), "title": c.get("title"), "amount_minor": c.get("amount_minor"), "created_at": c.get("created_at")}
            for c in ctx.contributions[:20]
        ],
        "payment_timeline": [
            {"id": p.get("id"), "title": p.get("title"), "amount_minor": p.get("amount_minor"), "created_at": p.get("created_at")}
            for p in ctx.payments[:20]
        ],
        "purchase_milestones": ctx.milestones[:10],
        "ownership_changes": ctx.ownership_shares[:10],
        "important_decisions": ctx.decisions[:10],
        "turning_points": ctx.milestones[:5],
        "recent_activity": ctx.activities[:10],
        "purchase_completion_status": {
            "funding_percent": progress_pct,
            "target_amount_minor": ctx.target_amount_minor,
            "funded_amount_minor": ctx.contribution_total_minor,
        },
        "memory_hero_title": ctx.moment_name,
        "memory_hero_subtitle": "Your shared purchase story starts here."
        if ctx.memory_count == 0
        else f"{ctx.memory_count} memories captured",
        "next_best_action": nba,
        "funding_percent": progress_pct,
        "funded_amount_minor": ctx.contribution_total_minor,
        "contributor_count": ctx.contributor_count,
        "target_amount_minor": ctx.target_amount_minor,
        "operations_hub": t.GroupMomentsOperationsHub(
            core_summary=t.GroupMomentsCoreSummary(
                eyebrow="SHARED PURCHASE",
                eyebrow_icon="shopping_cart",
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
                hero_icon="shopping_cart",
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
