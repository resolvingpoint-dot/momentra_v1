"""Publish auth security events onto the domain event bus for audit."""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from app.shared.events.base import USER_SCOPED_MOMENT_ID, DomainEvent
from app.shared.events.bus import get_event_bus

logger = logging.getLogger(__name__)


async def emit_auth_event(
    name: str,
    *,
    user_id: UUID,
    payload: dict[str, Any] | None = None,
) -> None:
    """Best-effort auth audit event (never raises to callers)."""
    try:
        await get_event_bus().publish(
            DomainEvent(
                name=name,
                user_id=user_id,
                context="AUTH",
                moment_id=USER_SCOPED_MOMENT_ID,
                payload=payload or {},
            )
        )
    except Exception:  # noqa: BLE001 - audit must not break auth flows
        logger.exception("Failed to emit auth event %s", name)
