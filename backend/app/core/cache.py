from __future__ import annotations

import json
import logging
import time
import asyncio
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# In-memory fallback (used only when Redis is unavailable). Values are stored as
# ``(expires_at_monotonic, value)`` so the fallback honours TTLs and cannot grow
# unbounded — expired entries are purged on access.
_in_memory: dict[str, tuple[float, Any]] = {}
_redis_client: "Optional[Redis]" = None
_redis_attempted = False
_redis_loop_id: int | None = None


def _purge_expired(now: float) -> None:
    expired = [k for k, (exp, _) in _in_memory.items() if exp <= now]
    for k in expired:
        _in_memory.pop(k, None)


async def _close_redis_client() -> None:
    global _redis_client, _redis_attempted, _redis_loop_id
    client = _redis_client
    _redis_client = None
    _redis_attempted = False
    _redis_loop_id = None
    if client is None:
        return
    try:
        await client.aclose()
    except Exception:
        pass


def reset_redis_client() -> None:
    """Drop the cached async Redis client (Celery ``asyncio.run`` / new event loop)."""
    global _redis_client, _redis_attempted, _redis_loop_id
    _redis_client = None
    _redis_attempted = False
    _redis_loop_id = None


async def get_redis():
    """Return a Redis client bound to the *current* event loop.

    Celery tasks call ``asyncio.run`` per job, so a module-level client from a
    previous loop must not be reused (INCR/GET then fail with loop/connection
    errors and fall back to in-memory version counters).
    """
    global _redis_client, _redis_attempted, _redis_loop_id
    loop_id = id(asyncio.get_running_loop())
    if _redis_client is not None and _redis_loop_id == loop_id:
        return _redis_client
    if _redis_client is not None:
        await _close_redis_client()
    # Only skip reconnect for a failed attempt on *this* loop.
    if _redis_attempted and _redis_loop_id == loop_id:
        return None

    from app.core.config import settings

    if not settings.redis_url:
        _redis_attempted = True
        _redis_loop_id = loop_id
        return None

    _redis_attempted = True
    _redis_loop_id = loop_id
    try:
        import redis.asyncio as aioredis

        _redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        await _redis_client.ping()
        logger.info("Redis connected")
        return _redis_client
    except Exception:
        logger.warning("Redis unavailable, using in-memory cache")
        _redis_client = None
        return None


def _memory_get(key: str) -> Any:
    entry = _in_memory.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if expires_at <= time.monotonic():
        _in_memory.pop(key, None)
        return None
    return value


async def get_cached(key: str) -> Any:
    from app.core.request_context import set_cache_hit

    redis = await get_redis()
    result: Any = None
    if redis:
        try:
            val = await redis.get(key)
            result = json.loads(val) if val else None
        except Exception:
            logger.warning("Redis get failed for %s, using in-memory fallback", key)
            result = _memory_get(key)
    else:
        result = _memory_get(key)
    set_cache_hit(result is not None)
    return result


async def set_cached(key: str, value: Any, ttl: int = 30) -> None:
    now = time.monotonic()
    _purge_expired(now)
    _in_memory[key] = (now + ttl, value)
    redis = await get_redis()
    if redis:
        try:
            await redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            logger.warning("Redis set failed for %s, kept in-memory only", key)


async def delete_cached(key: str) -> None:
    _in_memory.pop(key, None)
    redis = await get_redis()
    if redis:
        try:
            await redis.delete(key)
        except Exception:
            logger.warning("Redis delete failed for %s, cleared in-memory only", key)


async def delete_cached_prefix(prefix: str) -> None:
    """Delete in-memory keys and Redis keys matching a prefix."""
    for key in list(_in_memory.keys()):
        if key.startswith(prefix):
            _in_memory.pop(key, None)
    redis = await get_redis()
    if redis:
        try:
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor=cursor, match=f"{prefix}*", count=100)
                if keys:
                    await redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            logger.warning("Redis prefix delete failed for %s", prefix)


_locks: dict[str, float] = {}


async def acquire_lock(key: str, ttl: int = 30) -> bool:
    """Acquire a distributed lock (Redis SET NX EX) with in-memory fallback."""
    now = time.monotonic()
    _purge_expired(now)
    redis = await get_redis()
    if redis:
        try:
            return bool(await redis.set(key, "1", nx=True, ex=ttl))
        except Exception:
            logger.warning("Redis lock failed for %s, using in-memory fallback", key)
    expires = _locks.get(key)
    if expires is not None and expires > now:
        return False
    _locks[key] = now + ttl
    return True


async def release_lock(key: str) -> None:
    _locks.pop(key, None)
    redis = await get_redis()
    if redis:
        try:
            await redis.delete(key)
        except Exception:
            logger.warning("Redis lock release failed for %s", key)


async def wait_for_cached(
    key: str,
    *,
    timeout: float = 15.0,
    poll_interval: float = 0.05,
) -> Any:
    """Poll until a cache key appears or timeout elapses."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = await get_cached(key)
        if value is not None:
            return value
        await asyncio.sleep(poll_interval)
    return None


def reset_cache_for_tests() -> None:
    """Clear in-memory cache and locks (test isolation)."""
    _in_memory.clear()
    _locks.clear()
    reset_redis_client()
