from __future__ import annotations

from app.domains.moment_engine.handlers.base import enqueue_celery, should_refresh, worker_context
from app.shared.events.base import DomainEvent


class QueueAnalyticsRefreshHandler:
    """Enqueue per-moment analytics / orchestration refresh."""

    async def handle(self, event: DomainEvent) -> None:
        if not should_refresh(event):
            return
        from app.workers.tasks.analytics import refresh_analytics

        enqueue_celery(
            refresh_analytics,
            worker_context(event),
            str(event.moment_id),
            str(event.user_id),
        )
