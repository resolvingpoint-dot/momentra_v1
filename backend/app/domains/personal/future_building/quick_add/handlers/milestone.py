"""MILESTONE → personal_future_milestone_events."""
from __future__ import annotations

from app.domains.personal.future_building.quick_add.handlers.base import payload_for
from app.domains.personal.future_building.quick_add.handlers.mappings import (
    IMPACT_LEVELS,
    MILESTONE_NATURES,
)
from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalFutureMilestoneEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


class MilestoneHandler:
    event_type = "MILESTONE"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        nature = normalize_choice(
            data.get("milestone_nature"),
            MILESTONE_NATURES,
            "Achievement",
        )
        impact = normalize_choice(
            data.get("impact_level"),
            IMPACT_LEVELS,
            "Meaningful",
        )
        row = PersonalFutureMilestoneEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            milestone_nature=nature,
            impact_level=impact,
            celebration_level=data.get("celebration_level"),
            outcome_value=data.get("outcome_value"),
            note=as_note(data.get("notes")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{nature} · {impact}",
            impact_labels={"milestone_nature": nature, "impact_level": impact},
        )
