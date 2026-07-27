"""Build projection slices by wrapping existing template handlers and mappers."""
from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.catalog import moment_type_name, normalize_moment_type_code
from app.domains.personal.projection.service import ProjectionService
from app.domains.personal.templates.registry import get_template_projection_registry
from app.domains.projections import projection_cache
from app.domains.projections.projection_keys import PERSONAL_LIFE_TEMPLATE
from app.domains.projections.projection_metrics import build_timer

logger = logging.getLogger(__name__)


class ProjectionSliceBuilder:
    """Orchestrates existing projection code — no duplicate SQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build_pulse(
        self, user_id: UUID, template: str, *, reason: str | None = None
    ) -> dict[str, Any]:
        code = normalize_moment_type_code(template)
        with build_timer() as timer:
            handler = get_template_projection_registry().resolve(code)
            timer.mark("recommendations")
            payload = await handler.pulse(self.session, user_id)
            timer.mark("dto")
            envelope = await projection_cache.set(user_id, code, "pulse", payload)
            timer.mark("redis")
            stages = timer.finish()
            size_bytes = len(json.dumps(payload, default=str))
            timer.log(reason=reason, size_bytes=size_bytes)
            return envelope.payload

    async def build_moments(
        self, user_id: UUID, template: str, *, reason: str | None = None
    ) -> dict[str, Any]:
        code = normalize_moment_type_code(template)
        with build_timer() as timer:
            handler = get_template_projection_registry().resolve(code)
            timer.mark("recommendations")
            payload = await handler.moments(self.session, user_id)
            timer.mark("dto")
            envelope = await projection_cache.set(user_id, code, "moments", payload)
            timer.mark("redis")
            timer.finish()
            timer.log(reason=reason, size_bytes=len(json.dumps(payload, default=str)))
            return envelope.payload

    async def build_memory(
        self, user_id: UUID, template: str, *, reason: str | None = None
    ) -> dict[str, Any]:
        code = normalize_moment_type_code(template)
        with build_timer() as timer:
            handler = get_template_projection_registry().resolve(code)
            timer.mark("recommendations")
            payload = await handler.memory(self.session, user_id)
            timer.mark("dto")
            envelope = await projection_cache.set(user_id, code, "memory", payload)
            timer.mark("redis")
            timer.finish()
            timer.log(reason=reason, size_bytes=len(json.dumps(payload, default=str)))
            return envelope.payload

    async def build_template_life(
        self, user_id: UUID, template: str, *, reason: str | None = None
    ) -> dict[str, Any]:
        code = normalize_moment_type_code(template)
        with build_timer() as timer:
            handler = get_template_projection_registry().resolve(code)
            timer.mark("recommendations")
            payload = await handler.life(self.session, user_id)
            timer.mark("dto")
            envelope = await projection_cache.set(user_id, code, "life", payload)
            timer.mark("redis")
            timer.finish()
            timer.log(reason=reason, size_bytes=len(json.dumps(payload, default=str)))
            return envelope.payload

    async def build_personal_life(
        self, user_id: UUID, *, reason: str | None = None, force_refresh: bool = False
    ) -> dict[str, Any]:
        from datetime import datetime, timezone

        from app.domains.personal.projection.mappers.life_projection import (
            build_life_projection,
        )

        with build_timer() as timer:
            timer.mark("timeline")
            service = ProjectionService(self.session)
            cached = await service.get_cached_context(user_id, force_refresh=force_refresh)
            timer.mark("recommendations")
            active_count = len(cached.context.active_moments)
            is_empty = active_count == 0
            projection = None if is_empty else build_life_projection(cached.context)
            payload = {
                "projection_version": cached.version,
                "generated_at": cached.generated_at.isoformat(),
                "active_moment_count": active_count,
                "is_empty": is_empty,
                "date_range_label": datetime.now(timezone.utc).strftime("%B %Y"),
                "life_projection": projection,
                "metrics": projection,
            }
            timer.mark("dto")
            envelope = await projection_cache.set(
                user_id, PERSONAL_LIFE_TEMPLATE, "life", payload
            )
            timer.mark("redis")
            timer.finish()
            timer.log(reason=reason, size_bytes=len(json.dumps(payload, default=str)))
            return envelope.payload


def extract_aggregate_pulse_block(
    template: str, slice_payload: dict[str, Any]
) -> dict[str, Any] | None:
    """Map template pulse slice to aggregate /personal/pulse field."""
    code = normalize_moment_type_code(template)
    if slice_payload.get("status") != "ACTIVE":
        return None
    pulse = slice_payload.get("pulse")
    if pulse is None:
        return None
    if code == "LIFE_OPERATIONS":
        return pulse
    if code == "FUTURE_BUILDING":
        return pulse
    return pulse


def compose_aggregate_pulse(
    blocks: dict[str, dict[str, Any] | None],
    *,
    active_count: int,
) -> dict[str, dict[str, Any] | None]:
    """Compose aggregate pulse response fields from per-template slices."""
    return {
        "life_operations": blocks.get("LIFE_OPERATIONS"),
        "future_building": blocks.get("FUTURE_BUILDING"),
        "lifestyle": blocks.get("LIFESTYLE"),
        "emotional_security": blocks.get("RELATIONSHIPS"),
        "overall_rhythm_state": "ACTIVE" if active_count else "EMPTY",
        "active_moment_count": active_count,
        "is_empty": active_count == 0,
    }
