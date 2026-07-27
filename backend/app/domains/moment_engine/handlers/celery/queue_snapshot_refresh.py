from __future__ import annotations

from app.domains.moment_engine.handlers.base import enqueue_celery, should_refresh
from app.shared.events.base import DomainEvent


class QueueSnapshotRefreshHandler:
    """Enqueue user-scoped snapshot refresh (Circle, Life360, personal life)."""

    async def handle(self, event: DomainEvent) -> None:
        if not should_refresh(event):
            return
        from app.workers.tasks.snapshots import refresh_snapshots

        enqueue_celery(refresh_snapshots, str(event.user_id))
