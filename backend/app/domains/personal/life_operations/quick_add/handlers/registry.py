"""Dispatch quick-add events to typed handlers."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    QuickAddHandler,
    TimelineDraft,
)
from app.domains.personal.life_operations.quick_add.handlers.commitment import (
    CommitmentHandler,
)
from app.domains.personal.life_operations.quick_add.handlers.expense import (
    ExpenseHandler,
)
from app.domains.personal.life_operations.quick_add.handlers.recovery import (
    RecoveryHandler,
)
from app.domains.personal.life_operations.quick_add.handlers.reflection import (
    ReflectionHandler,
)
from app.domains.personal.life_operations.quick_add.handlers.rhythm import (
    RhythmHandler,
)

_HANDLERS: dict[str, QuickAddHandler] = {
    h.event_type: h
    for h in (
        ExpenseHandler(),
        CommitmentHandler(),
        RecoveryHandler(),
        ReflectionHandler(),
        RhythmHandler(),
    )
}


def get_handler(event_type: str) -> QuickAddHandler | None:
    return _HANDLERS.get(event_type.upper())


async def dispatch(ctx: QuickAddContext) -> TimelineDraft:
    handler = get_handler(ctx.event_type)
    if handler is None:
        from app.domains.quick_add_contract.errors import QuickAddActionNotSupported

        raise QuickAddActionNotSupported(
            f"Unsupported quick-add event type: {ctx.event_type}",
        )
    return await handler.handle(ctx)


def list_registered_handlers() -> list[dict[str, str]]:
    """Return registered quick-add handler metadata for debug introspection."""
    return [
        {
            "event_type": event_type,
            "handler": type(handler).__name__,
        }
        for event_type, handler in sorted(_HANDLERS.items())
    ]
