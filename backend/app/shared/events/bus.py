from __future__ import annotations

import inspect
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable

from app.shared.events.base import DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[DomainEvent], Awaitable[None] | None]

_bus: "EventBus | None" = None


class EventBus:
    """Simple in-process pub/sub. Handlers may be sync or async."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        handlers = list(self._handlers.get(event.name, []))
        handlers.extend(self._handlers.get("*", []))
        for handler in handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                logger.exception(
                    "Event handler %s failed for %s (moment=%s)",
                    getattr(handler, "__name__", handler),
                    event.name,
                    event.moment_id,
                )


def get_event_bus() -> EventBus:
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus


def subscribe(event_name: str, handler: EventHandler) -> None:
    get_event_bus().subscribe(event_name, handler)
