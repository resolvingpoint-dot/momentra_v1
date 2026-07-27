"""DISCOVERY → personal_lifestyle_discovery_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.lifestyle.quick_add.handlers.base import payload_for
from app.domains.personal.lifestyle.quick_add.handlers.mappings import (
    DISCOVERY_IMPACTS,
    DISCOVERY_TYPES,
)
from app.domains.personal.models import PersonalLifestyleDiscoveryEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


class DiscoveryHandler:
    event_type = "DISCOVERY"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        discovery_type = normalize_choice(
            data.get("discovery_type"),
            DISCOVERY_TYPES,
            "Other",
        )
        impact = normalize_choice(
            data.get("discovery_impact"),
            DISCOVERY_IMPACTS,
            "Interesting",
        )
        row = PersonalLifestyleDiscoveryEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            discovery_type=discovery_type,
            impact_level=impact,
            curiosity_level=data.get("curiosity_level"),
            note=as_note(data.get("notes")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{discovery_type} · {impact}",
            impact_labels={"discovery_type": discovery_type, "impact_level": impact},
        )
