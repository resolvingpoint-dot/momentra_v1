"""Handlers subscribed to ``moment.created``.

Sync handlers run in-process (same request transaction when a session is
present on the event). Celery handlers only enqueue background jobs.
"""
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
from app.domains.moment_engine.handlers.sync.update_module_state import (
    UpdateModuleStateHandler,
)
from app.shared.events.base import DomainEvent
from app.shared.events.bus import subscribe

MOMENT_CREATED_HANDLERS: tuple[EventHandler, ...] = (
    UpdateModuleStateHandler(),
    RefreshBootstrapCacheHandler(),
    RefreshProjectionCacheHandler(),
    QueueSnapshotRefreshHandler(),
    QueueMemoryRefreshHandler(),
    QueueAnalyticsRefreshHandler(),
)


async def _on_moment_created(event: DomainEvent) -> None:
    await dispatch(MOMENT_CREATED_HANDLERS, event)


def register_moment_created_handlers() -> None:
    subscribe("moment.created", _on_moment_created)
