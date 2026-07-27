"""REFLECTION → personal_life_mood_events."""
from __future__ import annotations

from decimal import Decimal

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalLifeMoodEvents

_MOOD_SCORES = {
    "GREAT": 90,
    "GOOD": 75,
    "OKAY": 60,
    "LOW": 35,
    "STRESSED": 25,
}


class ReflectionHandler:
    event_type = "REFLECTION"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = ctx.body.get("reflection") or {}
        mood_state = str(data.get("feeling_state") or "OKAY")[:50]
        reflection = str(data.get("reflection_note") or "").strip() or None
        tag = data.get("reflection_tag")
        tags: list[str] | None = None
        if tag:
            tags = [str(tag)] if isinstance(tag, str) else [str(t) for t in tag]

        score = _MOOD_SCORES.get(mood_state.upper(), 60)
        row = PersonalLifeMoodEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            mood_state=mood_state,
            reflection_text=reflection,
            mood_tags=tags,
            mood_score=Decimal(str(score)),
        )
        ctx.session.add(row)
        await ctx.session.flush()

        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=mood_state.replace("_", " ").title(),
            impact_labels={"mood_state": mood_state},
        )
