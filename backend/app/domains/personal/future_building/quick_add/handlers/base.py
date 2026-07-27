"""Shared payload helpers for Future Building handlers."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import QuickAddContext


def payload_for(ctx: QuickAddContext) -> dict:
    nested = ctx.body.get("future_building")
    if isinstance(nested, dict):
        return nested
    return ctx.body
