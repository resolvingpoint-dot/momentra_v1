from __future__ import annotations

import logging
from typing import Protocol

from app.shared.events.base import DomainEvent

logger = logging.getLogger(__name__)


class EventPublisher(Protocol):
    """Publish domain events.

    Today: in-process dispatch to subscribed handlers.
    Future: swap to :class:`OutboxEventPublisher` without changing services or
    the moment engine — only this factory changes.
    """

    async def publish(self, event: DomainEvent) -> None: ...


class InProcessEventPublisher:
    """Dispatch events immediately via the in-process :class:`EventBus`."""

    async def publish(self, event: DomainEvent) -> None:
        from app.shared.events.bus import get_event_bus

        await get_event_bus().publish(event)


class OutboxEventPublisher:
    """Transactional outbox (not implemented).

    Future flow: persist event in the same DB transaction as the domain write,
    then a dedicated outbox worker drains rows and calls ``EventBus.publish``.
      Commit → outbox row → worker → EventBus → Celery
    """

    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError(
            "OutboxEventPublisher is reserved for a future migration; "
            "use InProcessEventPublisher (get_event_publisher()) today."
        )


_publisher: EventPublisher | None = None


def get_event_publisher() -> EventPublisher:
    global _publisher
    if _publisher is None:
        _publisher = InProcessEventPublisher()
    return _publisher


def set_event_publisher(publisher: EventPublisher) -> None:
    """Replace the global publisher (tests or future outbox rollout)."""
    global _publisher
    _publisher = publisher
