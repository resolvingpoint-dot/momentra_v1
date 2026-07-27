"""RHYTHM → personal_life_adjust_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalLifeAdjustEvents

_VALID_SIGNALS = {"UP", "DOWN", "STABLE"}


def _signal(raw: str | None) -> str | None:
    if not raw:
        return None
    upper = raw.strip().upper()
    return upper if upper in _VALID_SIGNALS else "STABLE"


class RhythmHandler:
    event_type = "RHYTHM"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = ctx.body.get("rhythm") or {}
        actions_raw = data.get("rhythm_actions") or data.get("rhythm_action")
        areas: list[str] = []
        if isinstance(actions_raw, list):
            areas = [str(a)[:100] for a in actions_raw if a]
        elif actions_raw:
            areas = [str(actions_raw)[:100]]
        if not areas:
            areas = ["More Balance"]

        signals = data.get("runtime_signals") or {}
        if not isinstance(signals, dict):
            signals = {}

        priority = str(
            data.get("new_runtime_priority")
            or data.get("recommended_runtime_priority")
            or data.get("new_runtime_mode")
            or "MEDIUM"
        )[:150]
        note = str(data.get("new_runtime_mode") or "").strip() or None

        row = PersonalLifeAdjustEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            adjustment_areas=areas,
            pressure_signal=_signal(str(signals.get("pressure") or "")),
            recovery_signal=_signal(str(signals.get("recovery") or "")),
            focus_signal=_signal(str(signals.get("focus") or "")),
            momentum_signal=_signal(str(signals.get("momentum") or "")),
            recommended_runtime_priority=priority,
            note=note,
        )
        ctx.session.add(row)
        await ctx.session.flush()

        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=", ".join(areas[:2]),
            impact_labels={"runtime_mode": data.get("new_runtime_mode")},
        )
