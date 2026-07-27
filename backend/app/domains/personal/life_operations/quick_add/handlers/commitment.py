"""COMMITMENT → personal_life_attention_events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalLifeAttentionEvents

_VALID_INTENSITY = {"LIGHT", "MODERATE", "HEAVY"}
_VALID_STATUS = {"COMPLETED", "IN_PROGRESS", "DELAYED"}


class CommitmentHandler:
    event_type = "COMMITMENT"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = ctx.body.get("commitment") or {}
        intensity = str(data.get("intensity") or "MODERATE").upper()
        if intensity not in _VALID_INTENSITY:
            intensity = "MODERATE"
        status = str(data.get("commitment_status") or "IN_PROGRESS").upper()
        if status not in _VALID_STATUS:
            status = "IN_PROGRESS"
        category = str(
            data.get("commitment_type") or data.get("focus_area") or "General"
        )[:100]
        note_parts = [str(data.get("commitment_name") or "").strip()]
        if data.get("focus_area"):
            note_parts.append(str(data["focus_area"]))
        note = " · ".join(p for p in note_parts if p) or None

        row = PersonalLifeAttentionEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            attention_category=category,
            intensity_level=intensity,
            status=status,
            note=note,
        )
        ctx.session.add(row)
        await ctx.session.flush()

        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{category} · {status.replace('_', ' ').title()}",
            impact_labels={"intensity": intensity, "status": status},
        )
