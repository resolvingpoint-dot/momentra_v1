"""In-process projection cache keyed by user with monotonic version."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domains.personal.projection.context import ProjectionContext


@dataclass
class CachedProjection:
    version: int
    generated_at: datetime
    context: ProjectionContext


_versions: dict[UUID, int] = {}
_cache: dict[UUID, CachedProjection] = {}


def current_version(user_id: UUID) -> int:
    return _versions.get(user_id, 1)


def invalidate_projection_cache(user_id: UUID) -> int:
    """Bump projection version and drop cached context for a user."""
    next_ver = _versions.get(user_id, 0) + 1
    _versions[user_id] = next_ver
    _cache.pop(user_id, None)
    return next_ver


def get_cached(user_id: UUID) -> CachedProjection | None:
    cached = _cache.get(user_id)
    if cached is None:
        return None
    if cached.version != _versions.get(user_id, 1):
        return None
    return cached


def set_cached(user_id: UUID, cached: CachedProjection) -> None:
    _versions[user_id] = cached.version
    _cache[user_id] = cached


def reset_projection_cache_for_tests() -> None:
    _versions.clear()
    _cache.clear()
