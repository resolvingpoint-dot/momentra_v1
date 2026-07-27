"""SHARED_EXPERIENCE → personal_relationship_experience_events (+ optional money)."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.life_operations.quick_add.handlers.mappings import parse_amount
from app.domains.personal.models import PersonalRelationshipExperienceEvents
from app.domains.personal.quick_add.enum_utils import normalize_choice
from app.domains.personal.quick_add.money import (
    amount_minor_from_data,
    insert_money_event,
    optional_account_id,
)
from app.domains.personal.relationships.quick_add.handlers.base import notes_for, payload_for
from app.domains.personal.relationships.quick_add.handlers.mappings import (
    EXPERIENCE_TYPES,
    RELATIONSHIP_TYPE_ALIASES,
    RELATIONSHIP_TYPES,
    VALUE_RECEIVED,
)


class SharedExperienceHandler:
    event_type = "SHARED_EXPERIENCE"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        experience_type = normalize_choice(
            data.get("experience_type"),
            EXPERIENCE_TYPES,
            "Other",
        )
        relationship_type = normalize_choice(
            data.get("relationship_type"),
            RELATIONSHIP_TYPES,
            "Friend",
            aliases=RELATIONSHIP_TYPE_ALIASES,
        )
        value = normalize_choice(
            data.get("value_received"),
            VALUE_RECEIVED,
            "Okay",
        )
        cost = parse_amount(data.get("amount")) if data.get("amount") else None
        row = PersonalRelationshipExperienceEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            experience_type=experience_type,
            relationship_type=relationship_type,
            value_received=value,
            spend_category=data.get("spend_category"),
            cost_amount=cost,
            note=notes_for(ctx, data),
        )
        ctx.session.add(row)
        await ctx.session.flush()

        amount_minor = amount_minor_from_data(data)
        if amount_minor > 0:
            expense = ctx.body.get("expense") or {}
            merged = {**data, **expense}
            await insert_money_event(
                ctx,
                source_event_type="SHARED_EXPERIENCE",
                money_event_type="SHARED_EXPERIENCE_COST",
                data=merged,
                account_id=optional_account_id(merged),
            )

        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{experience_type} · {value}",
            display_amount=float(cost) if cost else None,
            impact_labels={
                "experience_type": experience_type,
                "relationship_type": relationship_type,
            },
        )
