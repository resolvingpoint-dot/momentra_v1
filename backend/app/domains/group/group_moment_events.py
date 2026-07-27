"""Redis pub/sub helpers for Group Trip projection invalidate push (SSE)."""
from __future__ import annotations

import json
import logging
from uuid import UUID

from app.core import cache as core_cache

logger = logging.getLogger(__name__)

CHANNEL_PREFIX = "group:moment:"
_DEFAULT_SLICES = ("pulse", "moments", "memory", "life", "live_hub")


def invalidate_channel(moment_id: UUID | str) -> str:
    return f"{CHANNEL_PREFIX}{moment_id}:invalidate"


async def publish_group_moment_invalidate(
    moment_id: UUID,
    *,
    reason: str = "group_activity",
    slices: tuple[str, ...] | list[str] = _DEFAULT_SLICES,
) -> None:
    """PUBLISH invalidate notice. Never raises — Redis down must not fail writes."""
    redis = await core_cache.get_redis()
    if redis is None:
        logger.debug(
            "Redis unavailable; skip group moment invalidate publish moment=%s",
            moment_id,
        )
        return
    payload = {
        "moment_id": str(moment_id),
        "slices": list(slices),
        "reason": reason,
    }
    channel = invalidate_channel(moment_id)
    try:
        await redis.publish(channel, json.dumps(payload, default=str))
    except Exception:
        logger.warning(
            "Redis publish failed for %s reason=%s",
            channel,
            reason,
            exc_info=True,
        )
