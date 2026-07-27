"""PROGRESS → personal_future_progress_events."""
from __future__ import annotations

from app.domains.personal.future_building.quick_add.handlers.base import payload_for
from app.domains.personal.future_building.quick_add.handlers.mappings import (
    EFFORT_LEVELS,
    PROGRESS_LEVELS,
)
from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.life_operations.quick_add.handlers.mappings import parse_amount
from app.domains.personal.models import PersonalFutureProgressEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


class ProgressHandler:
    event_type = "PROGRESS"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        progress_type = str(data.get("progress_type") or "General")[:80]
        progress_level = normalize_choice(
            data.get("progress_level") or data.get("progress_type"),
            PROGRESS_LEVELS,
            "Small Step",
        )
        effort = normalize_choice(
            data.get("effort_level"),
            EFFORT_LEVELS,
            "Medium",
            aliases={"MODERATE": "Medium"},
        )
        money_raw = data.get("amount") or data.get("money_invested_amount")
        money_amount = parse_amount(money_raw) if money_raw else None
        row = PersonalFutureProgressEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            progress_type=progress_type,
            progress_level=progress_level,
            effort_level=effort,
            time_invested_bucket=data.get("time_invested"),
            money_invested_amount=money_amount,
            note=as_note(data.get("notes")),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        display_amount = float(money_amount) if money_amount else None
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{progress_type} · {progress_level}",
            display_amount=display_amount,
            impact_labels={"progress_type": progress_type, "effort_level": effort},
        )
