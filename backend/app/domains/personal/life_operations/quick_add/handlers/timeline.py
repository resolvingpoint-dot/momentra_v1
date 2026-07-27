"""Shared timeline row builder."""
from __future__ import annotations

from decimal import Decimal

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalActivityTimeline


async def insert_timeline_row(
    ctx: QuickAddContext, draft: TimelineDraft
) -> PersonalActivityTimeline:
    row = PersonalActivityTimeline(
        quick_add_event_id=ctx.quick_add_event_id,
        moment_id=ctx.moment_id,
        user_id=ctx.user_id,
        moment_type_code=ctx.moment_type_code,
        event_type=ctx.event_type,
        display_title=draft.display_title[:150],
        display_subtitle=(draft.display_subtitle[:250] if draft.display_subtitle else None),
        display_amount=(
            Decimal(str(draft.display_amount)) if draft.display_amount is not None else None
        ),
        impact_labels_json=draft.impact_labels,
        event_occurred_at=ctx.occurred_at,
    )
    ctx.session.add(row)
    await ctx.session.flush()
    return row
