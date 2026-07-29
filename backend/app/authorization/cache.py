"""Short-TTL AuthZ decision cache (≤60s). Do not cache permissions longer."""
from __future__ import annotations

import logging

from app.core.cache import get_cached, set_cached

logger = logging.getLogger(__name__)

AUTHZ_TTL_SECONDS = 45  # under the 60s platform ceiling


def _key(user_id: str, resource_kind: str, resource_id: str, action: str) -> str:
    return f"authz:{user_id}:{resource_kind}:{resource_id}:{action}"


async def get_cached_decision(
    user_id: str, resource_kind: str, resource_id: str, action: str
) -> bool | None:
    try:
        raw = await get_cached(_key(user_id, resource_kind, resource_id, action))
    except Exception:  # noqa: BLE001
        return None
    if raw is None:
        return None
    if raw in ("1", "true", True, 1):
        return True
    if raw in ("0", "false", False, 0):
        return False
    return None


async def set_cached_decision(
    user_id: str,
    resource_kind: str,
    resource_id: str,
    action: str,
    *,
    allowed: bool,
) -> None:
    try:
        await set_cached(
            _key(user_id, resource_kind, resource_id, action),
            "1" if allowed else "0",
            ttl=AUTHZ_TTL_SECONDS,
        )
    except Exception:  # noqa: BLE001
        logger.debug("authz cache write failed", exc_info=True)


async def invalidate_authz_for_user_resource(
    user_id: str, resource_kind: str, resource_id: str
) -> None:
    """Best-effort note — short TTL is the primary safety net for membership changes."""
    logger.debug(
        "authz invalidate requested user=%s kind=%s id=%s (TTL-based expiry)",
        user_id,
        resource_kind,
        resource_id,
    )
