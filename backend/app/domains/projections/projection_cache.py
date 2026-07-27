"""Versioned Redis projection slice cache with stale retention."""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core import cache as core_cache
from app.domains.projections.projection_keys import (
    building_lock_key,
    slice_key,
    stale_key,
    user_slice_prefix,
    user_stale_prefix,
    user_version_prefix,
    version_counter_key,
)

logger = logging.getLogger(__name__)

# Disaster-recovery TTL only — consistency is event-driven.
SLICE_TTL_SECONDS = 86400
LOCK_TTL_SECONDS = 30

_in_memory_slices: dict[str, tuple[float, dict[str, Any]]] = {}
_in_memory_stale: dict[str, tuple[float, dict[str, Any]]] = {}
_in_memory_versions: dict[str, int] = {}


@dataclass
class ProjectionEnvelope:
    version: int
    updated_at: str
    payload: dict[str, Any]
    stale: bool = False

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "version": self.version,
            "updated_at": self.updated_at,
            "payload": self.payload,
        }
        if self.stale:
            out["stale"] = True
        return out

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectionEnvelope | None:
        if not isinstance(data, dict) or "payload" not in data:
            return None
        return cls(
            version=int(data.get("version", 0)),
            updated_at=str(data.get("updated_at", "")),
            payload=data["payload"],
            stale=bool(data.get("stale", False)),
        )


def _memory_get(store: dict[str, tuple[float, dict[str, Any]]], key: str) -> dict[str, Any] | None:
    entry = store.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if expires_at <= time.monotonic():
        store.pop(key, None)
        return None
    return value


def _memory_set(
    store: dict[str, tuple[float, dict[str, Any]]],
    key: str,
    value: dict[str, Any],
    ttl: int,
) -> None:
    store[key] = (time.monotonic() + ttl, value)


async def _next_version(user_id: UUID, template: str, slice_type: str) -> int:
    vkey = version_counter_key(user_id, template, slice_type)
    redis = await core_cache.get_redis()
    if redis:
        try:
            return int(await redis.incr(vkey))
        except Exception:
            logger.warning("Redis INCR failed for %s", vkey)
    current = _in_memory_versions.get(vkey, 0) + 1
    _in_memory_versions[vkey] = current
    return current


async def _get_active_raw(user_id: UUID, template: str, slice_type: str) -> dict[str, Any] | None:
    key = slice_key(user_id, template, slice_type)
    redis = await core_cache.get_redis()
    raw: Any = None
    if redis:
        try:
            val = await redis.get(key)
            raw = json.loads(val) if val else None
        except Exception:
            raw = _memory_get(_in_memory_slices, key)
    else:
        raw = _memory_get(_in_memory_slices, key)
    return raw if isinstance(raw, dict) else None


async def get(
    user_id: UUID, template: str, slice_type: str
) -> ProjectionEnvelope | None:
    raw = await _get_active_raw(user_id, template, slice_type)
    if isinstance(raw, dict):
        return ProjectionEnvelope.from_dict(raw)
    stale = await get_stale(user_id, template, slice_type)
    if stale is not None:
        stale.stale = True
        return stale
    return None


async def get_stale(
    user_id: UUID, template: str, slice_type: str
) -> ProjectionEnvelope | None:
    key = stale_key(user_id, template, slice_type)
    redis = await core_cache.get_redis()
    raw: Any = None
    if redis:
        try:
            val = await redis.get(key)
            raw = json.loads(val) if val else None
        except Exception:
            raw = _memory_get(_in_memory_stale, key)
    else:
        raw = _memory_get(_in_memory_stale, key)
    if isinstance(raw, dict):
        env = ProjectionEnvelope.from_dict(raw)
        if env is not None:
            env.stale = True
        return env
    return None


async def set(
    user_id: UUID,
    template: str,
    slice_type: str,
    payload: dict[str, Any],
    *,
    ttl: int = SLICE_TTL_SECONDS,
) -> ProjectionEnvelope:
    version = await _next_version(user_id, template, slice_type)
    envelope = ProjectionEnvelope(
        version=version,
        updated_at=datetime.now(timezone.utc).isoformat(),
        payload=payload,
    )
    key = slice_key(user_id, template, slice_type)
    data = envelope.to_dict()
    redis = await core_cache.get_redis()
    _memory_set(_in_memory_slices, key, data, ttl)
    if redis:
        try:
            await redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception:
            logger.warning("Redis set failed for projection slice %s", key)
    stale_k = stale_key(user_id, template, slice_type)
    _in_memory_stale.pop(stale_k, None)
    if redis:
        try:
            await redis.delete(stale_k)
        except Exception:
            pass
    return envelope


async def mark_stale(user_id: UUID, template: str, slice_type: str) -> None:
    """Copy active envelope to stale store, then delete active key."""
    raw = await _get_active_raw(user_id, template, slice_type)
    current = ProjectionEnvelope.from_dict(raw) if raw else None
    if current is None:
        current = await get_stale(user_id, template, slice_type)
    if current is not None:
        stale_env = ProjectionEnvelope(
            version=current.version,
            updated_at=current.updated_at,
            payload=current.payload,
            stale=True,
        )
        sk = stale_key(user_id, template, slice_type)
        data = stale_env.to_dict()
        _memory_set(_in_memory_stale, sk, data, SLICE_TTL_SECONDS)
        redis = await core_cache.get_redis()
        if redis:
            try:
                await redis.setex(sk, SLICE_TTL_SECONDS, json.dumps(data, default=str))
            except Exception:
                pass
    await delete(user_id, template, slice_type)


async def delete(user_id: UUID, template: str, slice_type: str) -> None:
    key = slice_key(user_id, template, slice_type)
    _in_memory_slices.pop(key, None)
    redis = await core_cache.get_redis()
    if redis:
        try:
            await redis.delete(key)
        except Exception:
            logger.warning("Redis delete failed for %s", key)


async def purge(user_id: UUID, template: str, slice_type: str) -> None:
    """Delete active + stale keys (force_refresh must not SWR-serve marked-stale)."""
    await delete(user_id, template, slice_type)
    stale_k = stale_key(user_id, template, slice_type)
    _in_memory_stale.pop(stale_k, None)
    redis = await core_cache.get_redis()
    if redis:
        try:
            await redis.delete(stale_k)
        except Exception:
            logger.warning("Redis stale delete failed for %s", stale_k)


async def exists(user_id: UUID, template: str, slice_type: str) -> bool:
    env = await get(user_id, template, slice_type)
    return env is not None


async def ttl(user_id: UUID, template: str, slice_type: str) -> int | None:
    key = slice_key(user_id, template, slice_type)
    redis = await core_cache.get_redis()
    if redis:
        try:
            remaining = await redis.ttl(key)
            return int(remaining) if remaining >= 0 else None
        except Exception:
            pass
    entry = _in_memory_slices.get(key)
    if entry is None:
        return None
    expires_at, _ = entry
    remaining = int(expires_at - time.monotonic())
    return max(0, remaining)


async def delete_user_slices(user_id: UUID) -> None:
    prefix = user_slice_prefix(user_id)
    for key in list(_in_memory_slices.keys()):
        if key.startswith(prefix):
            _in_memory_slices.pop(key, None)
    await core_cache.delete_cached_prefix(prefix)


async def delete_user_stale(user_id: UUID) -> None:
    prefix = user_stale_prefix(user_id)
    for key in list(_in_memory_stale.keys()):
        if key.startswith(prefix):
            _in_memory_stale.pop(key, None)
    await core_cache.delete_cached_prefix(prefix)


async def mark_all_stale(user_id: UUID, templates: list[str], slices: list[str]) -> None:
    for template in templates:
        for slice_type in slices:
            await mark_stale(user_id, template, slice_type)
    await mark_stale(user_id, "personal", "life")


async def acquire_build_lock(user_id: UUID, template: str, slice_type: str) -> bool:
    return await core_cache.acquire_lock(
        building_lock_key(user_id, template, slice_type), ttl=LOCK_TTL_SECONDS
    )


async def release_build_lock(user_id: UUID, template: str, slice_type: str) -> None:
    await core_cache.release_lock(building_lock_key(user_id, template, slice_type))


def reset_projection_cache_for_tests() -> None:
    _in_memory_slices.clear()
    _in_memory_stale.clear()
    _in_memory_versions.clear()
    core_cache.reset_cache_for_tests()
