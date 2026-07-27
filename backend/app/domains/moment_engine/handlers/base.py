from __future__ import annotations

import logging
from typing import Protocol

from app.shared.events.base import DomainEvent

logger = logging.getLogger(__name__)

REFRESH_EVENTS = frozenset(
    {
        "moment.created",
        "moment.updated",
        "moment.activated",
        "moment.paused",
        "moment.completed",
        "moment.archived",
    }
)

WORKER_CONTEXT: dict[str, str] = {
    "MY_MONEY": "personal",
    "PERSONAL": "personal",
    "GROUP": "group",
    "BUSINESS": "business",
}


class EventHandler(Protocol):
    async def handle(self, event: DomainEvent) -> None: ...


def should_refresh(event: DomainEvent) -> bool:
    if not event.payload.get("refresh", True):
        return False
    return event.name in REFRESH_EVENTS


def worker_context(event: DomainEvent) -> str:
    if event.payload.get("worker_context"):
        return str(event.payload["worker_context"])
    return WORKER_CONTEXT.get(event.context, event.context.lower())


def enqueue_celery(task, *args: object) -> None:
    """Enqueue a Celery task; never fail the HTTP request if the broker is down."""
    from app.core.config import settings

    if not settings.effective_celery_broker:
        logger.debug(
            "Skipping enqueue %s (no Celery broker configured)",
            getattr(task, "name", task),
        )
        return
    try:
        task.delay(*args)
    except Exception as exc:
        logger.warning("Failed to enqueue %s: %s", getattr(task, "name", task), exc)


async def dispatch(handlers: tuple[EventHandler, ...], event: DomainEvent) -> None:
    for handler in handlers:
        await handler.handle(event)
