"""Shared payload helpers for Relationships handlers."""
from __future__ import annotations

from typing import Any

from app.domains.personal.life_operations.quick_add.handlers.base import QuickAddContext
from app.domains.personal.quick_add.enum_utils import as_note


def payload_for(ctx: QuickAddContext) -> dict:
    for key in ("relationships", "emotional_security"):
        nested = ctx.body.get(key)
        if isinstance(nested, dict):
            return nested
    return ctx.body


def notes_for(ctx: QuickAddContext, data: dict[str, Any]) -> str | None:
    """Prefer notes; fall back to event_title so narrative is never lost."""
    return as_note(data.get("notes") or ctx.event_title)
