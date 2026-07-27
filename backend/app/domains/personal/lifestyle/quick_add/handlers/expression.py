"""EXPRESSION → personal_lifestyle_expression_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.lifestyle.quick_add.handlers.base import payload_for
from app.domains.personal.lifestyle.quick_add.handlers.mappings import (
    CREATION_TYPES,
    SATISFACTION_LEVELS,
)
from app.domains.personal.models import PersonalLifestyleExpressionEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


class ExpressionHandler:
    event_type = "EXPRESSION"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        creation_type = normalize_choice(
            data.get("creation_type"),
            CREATION_TYPES,
            "Other",
        )
        satisfaction = normalize_choice(
            data.get("satisfaction_level"),
            SATISFACTION_LEVELS,
            "Moderate",
        )
        row = PersonalLifestyleExpressionEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            creation_type=creation_type,
            satisfaction_level=satisfaction,
            time_invested_bucket=data.get("time_invested"),
            note=as_note(data.get("notes")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{creation_type} · {satisfaction}",
            impact_labels={"creation_type": creation_type, "satisfaction_level": satisfaction},
        )
