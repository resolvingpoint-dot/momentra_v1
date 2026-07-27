from __future__ import annotations

from app.domains.moment_engine.handlers.base import enqueue_celery, should_refresh, worker_context
from app.shared.events.base import DomainEvent


class QueueMemoryRefreshHandler:
    """Enqueue per-moment memory intelligence refresh."""

    async def handle(self, event: DomainEvent) -> None:
        if not should_refresh(event):
            return
        from app.workers.tasks.memory import refresh_memory

        enqueue_celery(
            refresh_memory,
            worker_context(event),
            str(event.moment_id),
        )
