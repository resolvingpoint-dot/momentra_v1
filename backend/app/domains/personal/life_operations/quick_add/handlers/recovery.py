"""RECOVERY → personal_life_recovery_events."""
from __future__ import annotations

from decimal import Decimal

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalLifeRecoveryEvents

_ENERGY_MAP = {
    "LOW": "LOW",
    "MODERATE": "MODERATE",
    "HIGH": "HIGH",
    "LOW_ENERGY": "LOW",
    "HIGH_ENERGY": "HIGH",
}

_DURATION_BUCKETS = {
    15: "<30",
    30: "30_60",
    60: "1_2_HOURS",
    120: "2_PLUS_HOURS",
}


def _duration_bucket(minutes: int) -> str | None:
    if minutes <= 0:
        return None
    if minutes < 30:
        return "<30"
    if minutes <= 60:
        return "30_60" if minutes <= 60 else "1_2_HOURS"
    if minutes <= 120:
        return "1_2_HOURS"
    return "2_PLUS_HOURS"


def _energy_impact(raw: str | None) -> str:
    if not raw:
        return "MODERATE"
    key = raw.strip().upper().replace(" ", "_")
    return _ENERGY_MAP.get(key, "MODERATE")


class RecoveryHandler:
    event_type = "RECOVERY"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = ctx.body.get("recovery") or {}
        recovery_type = str(data.get("recovery_type") or "REST")[:100]
        energy = _energy_impact(
            str(data.get("recovery_intensity") or data.get("energy_impact") or "")
        )
        minutes = int(data.get("duration_minutes") or 0)
        note = str(data.get("notes") or data.get("note") or "").strip() or None

        score_map = {"LOW": 35, "MODERATE": 65, "HIGH": 90}
        row = PersonalLifeRecoveryEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            recovery_type=recovery_type,
            energy_impact=energy,
            duration_bucket=_duration_bucket(minutes),
            note=note,
            recovery_score=Decimal(str(score_map.get(energy, 65))),
        )
        ctx.session.add(row)
        await ctx.session.flush()

        subtitle = recovery_type.replace("_", " ").title()
        if minutes:
            subtitle = f"{subtitle} · {minutes} min"
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=subtitle,
            impact_labels={"energy_impact": energy},
        )
