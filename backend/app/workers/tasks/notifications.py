"""Notification delivery task — in-app is already marked sent; push uses FCM."""
from __future__ import annotations

import logging
import re
from uuid import UUID

from app.domains.business.repository import BusinessNotificationsRepository
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session
from app.workers.idempotency import is_done, mark_done

logger = logging.getLogger(__name__)

_TERMINAL = {"sent", "read", "archived"}
_DEEPLINK_RE = re.compile(r"\[deeplink:([^\]]+)\]")


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
            return {
                "notification_id": str(notification_id),
                "status": f"already_{note.notification_status}",
            }

        channel = (note.delivery_channel or "in_app").lower()
        fcm_result: dict = {"skipped": True}
        if channel == "push":
            from app.domains.business.push import list_tokens_for_user, send_fcm_to_tokens
            from app.domains.personal.preferences_service import PersonalPreferencesService

            prefs = await PersonalPreferencesService(session).get_by_user_id(
                note.recipient_user_id
            )
            if prefs is not None and not prefs.notification_enabled:
                logger.info(
                    "Skipping push %s — notifications disabled for %s",
                    notification_id,
                    note.recipient_user_id,
                )
                await repo.update_where(
                    {
                        "notification_id": notification_id,
                        "notification_status__in": ["queued", "failed"],
                    },
                    {"notification_status": "sent"},
                )
                await session.commit()
                mark_done(marker)
                return {
                    "notification_id": str(notification_id),
                    "status": "skipped_notifications_disabled",
                }

            tokens = await list_tokens_for_user(session, note.recipient_user_id)
            deep = None
            m = _DEEPLINK_RE.search(note.message or "")
            if m:
                deep = m.group(1)
            fcm_result = send_fcm_to_tokens(
                tokens,
                title=note.title,
                body=_DEEPLINK_RE.sub("", note.message or "").strip(),
                data={
                    "notification_id": str(notification_id),
                    "moment_id": str(note.moment_id),
                    "type": note.notification_type,
                    "priority": note.priority or "medium",
                    **({"deep_link": deep} if deep else {}),
                    **(
                        {"action_center": "1"}
                        if "critical" in (note.notification_type or "").lower()
                        or (note.priority or "") == "critical"
                        else {}
                    ),
                },
            )
            logger.info(
                "Push notification %s to %s: %s",
                notification_id,
                note.recipient_user_id,
                fcm_result,
            )
        else:
            logger.info(
                "Delivering notification %s to %s via %s",
                notification_id,
                note.recipient_user_id,
                channel,
            )

        status = "sent"
        if channel == "push" and fcm_result.get("error"):
            status = "failed"

        updated = await repo.update_where(
            {
                "notification_id": notification_id,
                "notification_status__in": ["queued", "failed"],
            },
            {"notification_status": status},
        )
        await session.commit()

    if status == "sent":
        mark_done(marker)
    return {
        "notification_id": str(notification_id),
        "delivered": updated,
        "status": status,
        "fcm": fcm_result,
    }
