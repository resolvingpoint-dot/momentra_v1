"""FCM / push helpers for business notifications."""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.firebase import init_firebase
from app.domains.users.models import UserDeviceToken

logger = logging.getLogger(__name__)


async def list_tokens_for_user(session: AsyncSession, user_id: UUID) -> list[str]:
    result = await session.execute(
        select(UserDeviceToken.fcm_token).where(UserDeviceToken.user_id == user_id)
    )
    return [row[0] for row in result.all() if row[0]]


def send_fcm_to_tokens(
    tokens: list[str],
    *,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Send FCM multicast. Returns counts; never raises to callers."""
    if not tokens:
        return {"success": 0, "failure": 0, "skipped": True}
    try:
        init_firebase()
        from firebase_admin import messaging

        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(title=title[:200], body=(body or "")[:1000]),
            data={k: str(v) for k, v in (data or {}).items()},
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    channel_id="momentra_business",
                    click_action="FLUTTER_NOTIFICATION_CLICK",
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default", badge=1),
                )
            ),
        )
        response = messaging.send_each_for_multicast(message)
        return {
            "success": response.success_count,
            "failure": response.failure_count,
            "skipped": False,
        }
    except Exception:
        logger.exception("FCM send failed")
        return {"success": 0, "failure": len(tokens), "error": True}
