"""LEARNING → personal_future_learning_events."""
from __future__ import annotations

from app.domains.personal.future_building.quick_add.handlers.base import payload_for
from app.domains.personal.future_building.quick_add.handlers.mappings import (
    APPLICATION_STATUSES,
    LEARNING_TYPES,
    RELEVANCE_LEVELS,
)
from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalFutureLearningEvents
from app.domains.personal.quick_add.enum_utils import as_note, normalize_choice


def resolve_application_status(value: object) -> str | None:
    """Only persist known enum statuses; free-text application stays in note."""
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    if raw in APPLICATION_STATUSES:
        return raw
    upper = raw.upper()
    for candidate in APPLICATION_STATUSES:
        if candidate.upper() == upper:
            return candidate
    return None


class LearningHandler:
    event_type = "LEARNING"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        learning_type = normalize_choice(
            data.get("learning_type"),
            LEARNING_TYPES,
            "Insight",
        )
        relevance = normalize_choice(
            data.get("relevance"),
            RELEVANCE_LEVELS,
            "Useful",
        )
        application_raw = data.get("application")
        application_status = resolve_application_status(application_raw)
        application_note = None if application_status else application_raw
        row = PersonalFutureLearningEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            learning_type=learning_type,
            relevance_level=relevance,
            application_status=application_status,
            note=as_note(
                data.get("learning_topic"),
                application_note,
                data.get("notes"),
            ),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{learning_type} · {relevance}",
            impact_labels={"learning_type": learning_type, "relevance_level": relevance},
        )
