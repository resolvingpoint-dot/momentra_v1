"""Invalidate projection caches after moment mutations."""
from __future__ import annotations

from app.domains.personal.projection.cache import invalidate_projection_cache
from app.domains.personal.projection.redis_slice_cache import invalidate_user_slices
from app.shared.events.base import DomainEvent

_CACHE_INVALIDATION_EVENTS = frozenset(
    {
        "moment.created",
        "moment.deleted",
        "moment.updated",
        "moment.activated",
        "moment.completed",
        "moment.archived",
        "personal.quick_add.created",
        "personal.quick_add.updated",
        "personal.quick_add.deleted",
    }
)


class RefreshProjectionCacheHandler:
    """Bump projection version and clear Redis slice cache after mutations."""

    async def handle(self, event: DomainEvent) -> None:
        if event.name not in _CACHE_INVALIDATION_EVENTS:
            return
        invalidate_projection_cache(event.user_id)
        await invalidate_user_slices(event.user_id)
