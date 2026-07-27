"""OPPORTUNITY → personal_future_opportunity_events."""
from __future__ import annotations

from app.domains.personal.future_building.quick_add.handlers.base import payload_for
from app.domains.personal.future_building.quick_add.handlers.mappings import (
    OPPORTUNITY_SOURCES,
    OPPORTUNITY_STATUSES,
    POTENTIAL_LEVELS,
)
from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalFutureOpportunityEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


class OpportunityHandler:
    event_type = "OPPORTUNITY"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        source = normalize_choice(
            data.get("opportunity_source"),
            OPPORTUNITY_SOURCES,
            "Other",
        )
        status = normalize_choice(
            data.get("opportunity_status"),
            OPPORTUNITY_STATUSES,
            "Captured",
        )
        potential = normalize_choice(
            data.get("confidence_level") or data.get("potential_level"),
            POTENTIAL_LEVELS,
            "Moderate",
        )
        row = PersonalFutureOpportunityEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            opportunity_source=source,
            opportunity_status=status,
            potential_level=potential,
            note=as_note(data.get("notes")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{source} · {status}",
            impact_labels={"opportunity_source": source, "opportunity_status": status},
        )
