"""SUPPORT → personal_relationship_support_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalRelationshipSupportEvents
from app.domains.personal.quick_add.enum_utils import normalize_choice
from app.domains.personal.relationships.quick_add.handlers.base import notes_for, payload_for
from app.domains.personal.relationships.quick_add.handlers.mappings import (
    RELATIONSHIP_TYPE_ALIASES,
    RELATIONSHIP_TYPES,
    SUPPORT_DIRECTIONS,
    SUPPORT_IMPACTS,
    SUPPORT_TYPES,
)


class SupportHandler:
    event_type = "SUPPORT"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        support_type = normalize_choice(
            data.get("support_type"),
            SUPPORT_TYPES,
            "Other",
        )
        relationship_type = normalize_choice(
            data.get("relationship_type"),
            RELATIONSHIP_TYPES,
            "Friend",
            aliases=RELATIONSHIP_TYPE_ALIASES,
        )
        direction = normalize_choice(
            data.get("support_direction"),
            SUPPORT_DIRECTIONS,
            "Given",
        )
        impact = normalize_choice(
            data.get("support_impact"),
            SUPPORT_IMPACTS,
            "Meaningful",
        )
        row = PersonalRelationshipSupportEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            support_type=support_type,
            relationship_type=relationship_type,
            support_direction=direction,
            impact_level=impact,
            note=notes_for(ctx, data),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{support_type} · {direction}",
            impact_labels={"support_type": support_type, "support_direction": direction},
        )
