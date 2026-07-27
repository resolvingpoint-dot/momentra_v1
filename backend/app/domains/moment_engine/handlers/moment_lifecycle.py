"""Celery-only handlers for post-create lifecycle events."""
from __future__ import annotations

from app.domains.moment_engine.handlers.base import EventHandler, dispatch
from app.domains.moment_engine.handlers.celery.queue_analytics_refresh import (
    QueueAnalyticsRefreshHandler,
)
from app.domains.moment_engine.handlers.celery.queue_memory_refresh import (
    QueueMemoryRefreshHandler,
)
from app.domains.moment_engine.handlers.celery.queue_snapshot_refresh import (
    QueueSnapshotRefreshHandler,
)
from app.domains.moment_engine.handlers.sync.refresh_bootstrap_cache import (
    RefreshBootstrapCacheHandler,
)
from app.domains.moment_engine.handlers.sync.refresh_projection_cache import (
    RefreshProjectionCacheHandler,
)
from app.shared.events.base import DomainEvent
from app.shared.events.bus import subscribe

LIFECYCLE_EVENTS = (
    "moment.updated",
    "moment.activated",
    "moment.paused",
    "moment.completed",
    "moment.archived",
)

LIFECYCLE_CELERY_HANDLERS: tuple[EventHandler, ...] = (
    QueueSnapshotRefreshHandler(),
    QueueMemoryRefreshHandler(),
    QueueAnalyticsRefreshHandler(),
)

_cache_handler = RefreshBootstrapCacheHandler()
_projection_cache_handler = RefreshProjectionCacheHandler()


async def _on_lifecycle_event(event: DomainEvent) -> None:
    await _cache_handler.handle(event)
    await _projection_cache_handler.handle(event)
    await dispatch(LIFECYCLE_CELERY_HANDLERS, event)


async def _on_moment_deleted(event: DomainEvent) -> None:
    await _cache_handler.handle(event)
    await _projection_cache_handler.handle(event)


def register_lifecycle_handlers() -> None:
    for name in LIFECYCLE_EVENTS:
        subscribe(name, _on_lifecycle_event)
    subscribe("moment.deleted", _on_moment_deleted)
