from __future__ import annotations

from app.domains.module_states.service import ModuleStateService
from app.shared.events.base import DomainEvent

_REGISTERED_CONTEXTS = frozenset({"MY_MONEY", "GROUP", "BUSINESS"})


class UpdateModuleStateHandler:
    """Flip module states when a shared moment is created."""

    async def handle(self, event: DomainEvent) -> None:
        if event.name != "moment.created" or event.context not in _REGISTERED_CONTEXTS:
            return
        session = event.payload.get("session")
        if session is None:
            return
        setup_state = event.payload.get("setup_state", "ACTIVE")
        modules = ModuleStateService(session)
        await modules.set_state(
            event.user_id, event.context, setup_state, "moment_created"
        )
        await modules.set_state(event.user_id, "MOMENTS", "ACTIVE", "moment_created")
        await modules.set_state(event.user_id, "PULSE", "ACTIVE", "moment_created")
