from __future__ import annotations

from app.shared.events.base import DomainEvent

_CACHE_INVALIDATION_EVENTS = frozenset(
    {
        "moment.created",
        "moment.deleted",
        "moment.updated",
        "moment.activated",
        "moment.completed",
        "moment.archived",
    }
)


class RefreshBootstrapCacheHandler:
    """Invalidate the user's bootstrap cache after moment mutations."""

    async def handle(self, event: DomainEvent) -> None:
        if event.name not in _CACHE_INVALIDATION_EVENTS:
            return
        session = event.payload.get("session")
        if session is None:
            return
        from app.domains.app_bootstrap.service import AppBootstrapService

        await AppBootstrapService(session).invalidate_cache(event.user_id)
