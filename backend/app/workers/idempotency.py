"""Redis-backed idempotency markers for Celery tasks.

Tasks that perform side effects which the database cannot naturally dedupe
(notification delivery, media processing) use a marker so a *duplicate
submission* of the same logical job is skipped. The marker is written only
*after* the work succeeds, so a failed attempt that is retried still re-runs.

If Redis is unavailable the helpers degrade safely: :func:`is_done` returns
``False`` (never skip) and :func:`mark_done` is a no-op, so tasks still execute
and rely on their database-level guards for correctness.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_KEY_PREFIX = "momentra:job:done:"
_DEFAULT_TTL = 24 * 3600

_client: Optional["object"] = None
_attempted = False


def _redis():
    global _client, _attempted
    if _client is not None:
        return _client
    if _attempted:
        return None
    _attempted = True
    url = settings.redis_url or settings.effective_celery_broker
    if not url:
        return None
    try:
        import redis  # sync client (Celery tasks are synchronous)

        _client = redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        _client.ping()
        return _client
    except Exception:  # noqa: BLE001 - idempotency must never break the task
        logger.warning("Redis unavailable for idempotency markers; proceeding without dedupe")
        _client = None
        return None


def _key(name: str) -> str:
    return f"{_KEY_PREFIX}{name}"


def is_done(name: str) -> bool:
    client = _redis()
    if client is None:
        return False
    try:
        return bool(client.exists(_key(name)))
    except Exception:  # noqa: BLE001
        return False


def mark_done(name: str, ttl: int = _DEFAULT_TTL) -> None:
    client = _redis()
    if client is None:
        return
    try:
        client.set(_key(name), "1", ex=ttl)
    except Exception:  # noqa: BLE001
        logger.warning("Failed to write idempotency marker %s", name)
