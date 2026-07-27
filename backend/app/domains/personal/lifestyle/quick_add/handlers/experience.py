"""EXPERIENCE → personal_lifestyle_experience_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.life_operations.quick_add.handlers.mappings import parse_amount
from app.domains.personal.lifestyle.quick_add.handlers.base import payload_for
from app.domains.personal.lifestyle.quick_add.handlers.mappings import (
    ENERGY_IMPACTS,
    EXPERIENCE_QUALITIES,
    EXPERIENCE_TYPES,
    VALUE_RECEIVED,
)
from app.domains.personal.models import PersonalLifestyleExperienceEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


class ExperienceHandler:
    event_type = "EXPERIENCE"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        experience_type = normalize_choice(
            data.get("experience_type"),
            EXPERIENCE_TYPES,
            "Other",
        )
        quality = normalize_choice(
            data.get("experience_quality"),
            EXPERIENCE_QUALITIES,
            "Enjoyable",
        )
        energy = normalize_choice(
            data.get("energy_impact"),
            ENERGY_IMPACTS,
            "Neutral",
        )
        value = normalize_choice(
            data.get("value_received"),
            VALUE_RECEIVED,
            "Okay",
        )
        cost = parse_amount(data.get("amount")) if data.get("amount") else None
        row = PersonalLifestyleExperienceEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            experience_type=experience_type,
            experience_quality=quality,
            energy_impact=energy,
            people_context=data.get("people_context"),
            location_context=data.get("location_context"),
            spend_category=data.get("spend_category"),
            value_received=value,
            cost_amount=cost,
            note=as_note(data.get("notes")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{experience_type} · {quality}",
            display_amount=float(cost) if cost else None,
            impact_labels={"experience_type": experience_type, "energy_impact": energy},
        )
