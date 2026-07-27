"""ADJUST → personal_lifestyle_adjust_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.lifestyle.quick_add.handlers.base import payload_for
from app.domains.personal.lifestyle.quick_add.handlers.mappings import (
    ADJUSTMENT_AREAS,
    CONFIDENCE_LEVELS,
    PRIORITY_LEVELS,
)
from app.domains.personal.models import PersonalLifestyleAdjustEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


class AdjustHandler:
    event_type = "ADJUST"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        area = normalize_choice(
            data.get("adjustment_area"),
            ADJUSTMENT_AREAS,
            "More Balance",
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
        row = PersonalLifestyleAdjustEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            adjustment_area=area,
            priority_level=priority,
            confidence_level=confidence,
            note=as_note(data.get("notes")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{area} · {priority}",
            impact_labels={"adjustment_area": area, "priority_level": priority},
        )
