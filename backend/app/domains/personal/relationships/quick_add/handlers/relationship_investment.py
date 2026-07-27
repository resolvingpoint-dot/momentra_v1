"""RELATIONSHIP_INVESTMENT → personal_relationship_investment_events (+ optional money)."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.life_operations.quick_add.handlers.mappings import parse_amount
from app.domains.personal.models import PersonalRelationshipInvestmentEvents
from app.domains.personal.quick_add.enum_utils import normalize_choice
from app.domains.personal.quick_add.money import (
    amount_minor_from_data,
    insert_money_event,
    money_timeline_draft,
    optional_account_id,
)
from app.domains.personal.relationships.quick_add.handlers.base import notes_for, payload_for
from app.domains.personal.relationships.quick_add.handlers.mappings import (
    INVESTMENT_PURPOSES,
    INVESTMENT_TYPES,
    PERCEIVED_VALUES,
    RELATIONSHIP_TYPE_ALIASES,
    RELATIONSHIP_TYPES,
)


class RelationshipInvestmentHandler:
    event_type = "RELATIONSHIP_INVESTMENT"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        investment_type = normalize_choice(
            data.get("investment_type"),
            INVESTMENT_TYPES,
            "Other",
        )
        relationship_type = normalize_choice(
            data.get("relationship_type"),
            RELATIONSHIP_TYPES,
            "Friend",
            aliases=RELATIONSHIP_TYPE_ALIASES,
        )
        purpose = normalize_choice(
            data.get("investment_purpose"),
            INVESTMENT_PURPOSES,
            "Care",
        )
        perceived = normalize_choice(
            data.get("perceived_value"),
            PERCEIVED_VALUES,
            "Moderate",
        )
        amount = parse_amount(data.get("amount") or 0)
        row = PersonalRelationshipInvestmentEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            investment_type=investment_type,
            relationship_type=relationship_type,
            investment_purpose=purpose,
            perceived_value=perceived,
            amount=amount,
            financial_support_flag=amount > 0,
            note=notes_for(ctx, data),
        )
        ctx.session.add(row)
        await ctx.session.flush()

        amount_minor = amount_minor_from_data(data)
        display_amount = float(amount)
        if amount_minor > 0:
            expense = ctx.body.get("expense") or {}
            merged = {**data, **expense}
            _, display_amount = await insert_money_event(
                ctx,
                source_event_type="RELATIONSHIP_INVESTMENT",
                money_event_type="GIFT",
                data=merged,
                account_id=optional_account_id(merged),
            )

        return money_timeline_draft(
            ctx,
            amount=display_amount,
            subtitle=f"{investment_type} · {purpose}",
            impact={"investment_type": investment_type, "perceived_value": perceived},
        )
