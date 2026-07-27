"""PIVOT → personal_future_pivot_events."""
from __future__ import annotations

from app.domains.personal.future_building.quick_add.handlers.base import payload_for
from app.domains.personal.future_building.quick_add.handlers.mappings import (
    CONFIDENCE_LEVELS,
    PIVOT_ADJUSTMENTS,
    PIVOT_REASONS,
)
from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalFuturePivotEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


class PivotHandler:
    event_type = "PIVOT"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        adjustment = normalize_choice(
            data.get("pivot_change") or data.get("adjustment_type"),
            PIVOT_ADJUSTMENTS,
            "Change Direction",
        )
        reason = normalize_choice(
            data.get("pivot_reason"),
            PIVOT_REASONS,
            "Personal Decision",
        )
        confidence = normalize_choice(
            data.get("confidence_level"),
            CONFIDENCE_LEVELS,
            "Medium",
        )
        row = PersonalFuturePivotEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            adjustment_type=adjustment,
            pivot_reason=reason,
            confidence_level=confidence,
            note=as_note(data.get("notes"), data.get("pivot_change")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{adjustment} · {reason}",
            impact_labels={"adjustment_type": adjustment, "pivot_reason": reason},
        )
