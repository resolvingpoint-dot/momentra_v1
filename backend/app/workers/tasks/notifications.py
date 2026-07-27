"""Notification delivery task.

Delivers a queued ``business_notifications`` row over its channel (delivery is
stubbed with a log line; wire push/email/SMS here). Idempotent on two levels:
a Redis marker short-circuits duplicate submissions, and the DB update only
transitions rows still in ``queued``/``failed`` -- so a redelivery is a no-op.
The marker is written only after a successful commit, so a failed attempt that
is retried still runs.
"""
from __future__ import annotations

import logging
from uuid import UUID

from app.domains.business.repository import BusinessNotificationsRepository
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session
from app.workers.idempotency import is_done, mark_done

logger = logging.getLogger(__name__)

_TERMINAL = {"sent", "read", "archived"}


@celery_app.task(name="notifications.deliver", bind=True, **RETRY_OPTS)
def deliver_notification(self, notification_id: str) -> dict:
    return run_async(_deliver(UUID(str(notification_id))))


async def _deliver(notification_id: UUID) -> dict:
    marker = f"notification:{notification_id}"
    if is_done(marker):
        return {"notification_id": str(notification_id), "status": "already_delivered"}

    async with worker_session() as session:
        repo = BusinessNotificationsRepository(session)
        note = await repo.get_by_id(notification_id)
        if note is None:
            return {"notification_id": str(notification_id), "status": "not_found"}
        if note.notification_status in _TERMINAL:
            mark_done(marker)
            return {"notification_id": str(notification_id), "status": f"already_{note.notification_status}"}

        # --- actual delivery side effect (stub) -------------------------------
        logger.info(
            "Delivering notification %s to %s via %s",
            notification_id, note.recipient_user_id, note.delivery_channel,
        )
        # ----------------------------------------------------------------------

        updated = await repo.update_where(
            {"notification_id": notification_id, "notification_status__in": ["queued", "failed"]},
            {"notification_status": "sent"},
        )
        await session.commit()

    mark_done(marker)
    return {"notification_id": str(notification_id), "delivered": updated, "status": "sent"}
