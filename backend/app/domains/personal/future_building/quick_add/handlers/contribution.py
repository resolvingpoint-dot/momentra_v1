"""CONTRIBUTION → personal_money_events (expense handler pattern)."""
from __future__ import annotations

from app.domains.personal.future_building.quick_add.handlers.base import payload_for
from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.quick_add.money import (
    insert_money_event,
    money_timeline_draft,
    optional_account_id,
)


class ContributionHandler:
    event_type = "CONTRIBUTION"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        expense = ctx.body.get("expense") or {}
        merged = {**data, **expense}
        _, amount = await insert_money_event(
            ctx,
            source_event_type="CONTRIBUTION",
            money_event_type="CONTRIBUTION",
            data=merged,
            impact_label=str(data.get("impact_level") or "")[:80] or None,
            account_id=optional_account_id(merged),
        )
        subtitle = str(data.get("category_name") or data.get("impact_level") or "Contribution")
        return money_timeline_draft(
            ctx,
            amount=amount,
            subtitle=subtitle,
            impact={"impact_level": data.get("impact_level")},
        )
