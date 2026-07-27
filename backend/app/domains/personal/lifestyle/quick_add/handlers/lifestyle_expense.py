"""LIFESTYLE_EXPENSE → personal_money_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.lifestyle.quick_add.handlers.base import payload_for
from app.domains.personal.quick_add.money import (
    insert_money_event,
    money_timeline_draft,
    optional_account_id,
)


class LifestyleExpenseHandler:
    event_type = "LIFESTYLE_EXPENSE"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        expense = ctx.body.get("expense") or {}
        merged = {**data, **expense}
        _, amount = await insert_money_event(
            ctx,
            source_event_type="LIFESTYLE_EXPENSE",
            money_event_type="EXPENSE",
            data=merged,
            account_id=optional_account_id(merged),
        )
        subtitle = str(data.get("spend_category") or "Lifestyle expense")
        return money_timeline_draft(ctx, amount=amount, subtitle=subtitle)
