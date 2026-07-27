"""EventBus handlers for projection cache invalidation and async refresh."""
from __future__ import annotations

import logging

from app.domains.personal.life_operations.quick_add.events import (
    QUICK_ADD_CREATED,
    QUICK_ADD_DELETED,
    QUICK_ADD_UPDATED,
)
from app.domains.projections.invalidation import (
    invalidate_for_delete,
    invalidate_for_lifecycle,
    invalidate_for_preferences,
    invalidate_for_quick_add,
    invalidate_for_setup,
)
from app.shared.events.base import DomainEvent
from app.shared.events.bus import subscribe

logger = logging.getLogger(__name__)

_registered = False

SETUP_COMPLETED = "setup.completed"
PREFERENCES_UPDATED = "preferences.updated"

_LIFECYCLE = frozenset(
    {
        "moment.created",
        "moment.updated",
        "moment.activated",
        "moment.completed",
        "moment.archived",
    }
)


async def _on_moment_lifecycle(event: DomainEvent) -> None:
    template = event.moment_type or event.payload.get("moment_type_code", "")
    if not template:
        return
    await invalidate_for_lifecycle(event.user_id, template, reason=event.name)


async def _on_moment_deleted(event: DomainEvent) -> None:
    await invalidate_for_delete(event.user_id)


async def _on_quick_add(event: DomainEvent) -> None:
    if event.payload.get("skip_projection_invalidation"):
        return
    event_type = str(event.payload.get("event_type", ""))
    template = event.moment_type or "LIFE_OPERATIONS"
    await invalidate_for_quick_add(event.user_id, template, event_type)


async def _on_setup_completed(event: DomainEvent) -> None:
    template = event.moment_type or event.payload.get("moment_type_code", "")
    if template:
        await invalidate_for_setup(event.user_id, str(template))


async def _on_preferences_updated(event: DomainEvent) -> None:
    await invalidate_for_preferences(event.user_id)


def register_projection_handlers() -> None:
    global _registered
    if _registered:
        return
    for name in _LIFECYCLE:
        subscribe(name, _on_moment_lifecycle)
    subscribe("moment.deleted", _on_moment_deleted)
    subscribe(QUICK_ADD_CREATED, _on_quick_add)
    subscribe(QUICK_ADD_UPDATED, _on_quick_add)
    subscribe(QUICK_ADD_DELETED, _on_quick_add)
    subscribe(SETUP_COMPLETED, _on_setup_completed)
    subscribe(PREFERENCES_UPDATED, _on_preferences_updated)
    _registered = True
