"""Register personal quick-add event handlers on the event bus."""
from __future__ import annotations

import logging

from app.domains.moment_engine.handlers.base import enqueue_celery
from app.domains.personal.life_operations.quick_add.events import (
    QUICK_ADD_CREATED,
    QUICK_ADD_DELETED,
    QUICK_ADD_UPDATED,
)
from app.shared.events.base import DomainEvent
from app.shared.events.bus import subscribe
from app.workers.tasks.snapshots import refresh_snapshots

logger = logging.getLogger(__name__)

_registered = False


async def _on_quick_add_created(event: DomainEvent) -> None:
    logger.debug(
        "personal quick-add created moment=%s type=%s",
        event.moment_id,
        event.payload.get("event_type"),
    )
    enqueue_celery(refresh_snapshots, str(event.user_id))


async def _on_quick_add_updated(event: DomainEvent) -> None:
    logger.debug("personal quick-add updated moment=%s", event.moment_id)


async def _on_quick_add_deleted(event: DomainEvent) -> None:
    logger.debug("personal quick-add deleted moment=%s", event.moment_id)


def register_quick_add_handlers() -> None:
    global _registered
    if _registered:
        return
    subscribe(QUICK_ADD_CREATED, _on_quick_add_created)
    subscribe(QUICK_ADD_UPDATED, _on_quick_add_updated)
    subscribe(QUICK_ADD_DELETED, _on_quick_add_deleted)
    _registered = True
