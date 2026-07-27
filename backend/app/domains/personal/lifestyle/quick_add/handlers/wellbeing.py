"""WELLBEING → personal_lifestyle_wellbeing_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.lifestyle.quick_add.handlers.base import payload_for
from app.domains.personal.lifestyle.quick_add.handlers.mappings import WELLBEING_STATES
from app.domains.personal.models import PersonalLifestyleWellbeingEvents
from app.domains.personal.quick_add.enum_utils import as_list, as_note, normalize_choice


class WellbeingHandler:
    event_type = "WELLBEING"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        state = normalize_choice(
            data.get("wellbeing_state"),
            WELLBEING_STATES,
            "Moderate",
        )
        areas = as_list(
            data.get("wellbeing_areas") or data.get("wellbeing_area"),
            default=["Balance"],
        )
        contributors = as_list(data.get("contributors")) or None
        row = PersonalLifestyleWellbeingEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            wellbeing_areas=areas,
            wellbeing_state=state,
            contributors=contributors,
            note=as_note(data.get("notes")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{state} · {', '.join(areas[:2])}",
            impact_labels={"wellbeing_state": state, "wellbeing_areas": areas},
        )
