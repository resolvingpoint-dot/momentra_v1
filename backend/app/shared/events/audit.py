"""Persist published domain events to domain_event_log for debugging and audit."""
from __future__ import annotations

import logging
from datetime import timezone

from sqlalchemy.dialects.postgresql import insert

from app.core.database import async_session_factory
from app.shared.events.base import DomainEvent
from app.shared.events.bus import subscribe
from app.shared.events.models import DomainEventLog

logger = logging.getLogger(__name__)

_registered = False


def _serializable_payload(payload: dict) -> dict:
    """Strip non-JSON values (e.g. SQLAlchemy sessions) before persistence."""
    out: dict = {}
    for key, value in payload.items():
        if key == "session":
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            out[key] = value
        else:
            out[key] = str(value)
    return out


async def persist_domain_event(event: DomainEvent) -> None:
    if async_session_factory is None:
        logger.debug("Skipping domain event audit (no database configured)")
        return
    occurred = event.occurred_at
    if occurred.tzinfo is not None:
        occurred = occurred.astimezone(timezone.utc).replace(tzinfo=None)
    row = {
        "name": event.name,
        "user_id": event.user_id,
        "moment_id": event.moment_id,
        "context": event.context,
        "moment_type": event.moment_type,
        "payload": _serializable_payload(event.payload),
        "created_at": occurred,
    }
    try:
        async with async_session_factory() as session:
            await session.execute(insert(DomainEventLog).values(**row))
            await session.commit()
    except Exception:
        logger.exception("Failed to persist domain event %s", event.name)


def register_event_audit() -> None:
    global _registered
    if _registered:
        return
    subscribe("*", persist_domain_event)
    _registered = True
