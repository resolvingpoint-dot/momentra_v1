"""Redis-backed projection slice cache with version-aware keys."""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from app.core import cache as core_cache
from app.domains.personal.projection.cache import current_version

logger = logging.getLogger(__name__)

SLICE_TTL_SECONDS = 300


def _slice_key(user_id: UUID, template: str, slice_type: str) -> str:
    version = current_version(user_id)
    return f"projection_slice:{user_id}:{template.upper()}:{slice_type}:v{version}"


def _user_prefix(user_id: UUID) -> str:
    return f"projection_slice:{user_id}:"


async def get_slice(
    user_id: UUID, template: str, slice_type: str
) -> dict[str, Any] | None:
    key = _slice_key(user_id, template, slice_type)
    payload = await core_cache.get_cached(key)
    if isinstance(payload, dict):
        return payload
    return None


async def set_slice(
    user_id: UUID,
    template: str,
    slice_type: str,
    payload: dict[str, Any],
    *,
    ttl: int = SLICE_TTL_SECONDS,
) -> None:
    key = _slice_key(user_id, template, slice_type)
    await core_cache.set_cached(key, payload, ttl=ttl)


async def invalidate_user_slices(user_id: UUID) -> None:
    """Drop all projection slice keys for a user (best-effort pattern delete)."""
    prefix = _user_prefix(user_id)
    await core_cache.delete_cached_prefix(prefix)
