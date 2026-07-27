"""ADJUST → personal_relationship_adjust_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalRelationshipAdjustEvents
from app.domains.personal.quick_add.enum_utils import normalize_choice
from app.domains.personal.relationships.quick_add.handlers.base import notes_for, payload_for
from app.domains.personal.relationships.quick_add.handlers.mappings import (
    ADJUSTMENT_AREAS,
    CONFIDENCE_LEVELS,
    PRIORITY_LEVELS,
    RELATIONSHIP_FOCUSES,
)


class AdjustHandler:
    event_type = "ADJUST"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        focus = normalize_choice(
            data.get("relationship_focus"),
            RELATIONSHIP_FOCUSES,
            "Friend",
        )
        area = normalize_choice(
            data.get("adjustment_area"),
            ADJUSTMENT_AREAS,
            "More Time Together",
        )
        priority = normalize_choice(
            data.get("priority_level"),
            PRIORITY_LEVELS,
            "Medium",
        )
        confidence = normalize_choice(
            data.get("confidence_level"),
            CONFIDENCE_LEVELS,
            "Somewhat Sure",
        )
        row = PersonalRelationshipAdjustEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            relationship_focus=focus,
            adjustment_area=area,
            priority_level=priority,
            confidence_level=confidence,
            note=notes_for(ctx, data),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{area} · {focus}",
            impact_labels={"adjustment_area": area, "relationship_focus": focus},
        )
