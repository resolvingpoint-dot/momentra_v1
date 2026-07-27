"""Dispatch Relationships quick-add events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.relationships.quick_add.handlers.adjust import AdjustHandler
from app.domains.personal.relationships.quick_add.handlers.connection import (
    ConnectionHandler,
)
from app.domains.personal.relationships.quick_add.handlers.relationship_investment import (
    RelationshipInvestmentHandler,
)
from app.domains.personal.relationships.quick_add.handlers.shared_experience import (
    SharedExperienceHandler,
)
from app.domains.personal.relationships.quick_add.handlers.support import SupportHandler

_HANDLERS = {
    h.event_type: h
    for h in (
        SharedExperienceHandler(),
        ConnectionHandler(),
        SupportHandler(),
        RelationshipInvestmentHandler(),
        AdjustHandler(),
    )
}


async def dispatch(ctx: QuickAddContext) -> TimelineDraft:
    handler = _HANDLERS.get(ctx.event_type)
    if handler is None:
        from app.domains.quick_add_contract.errors import QuickAddActionNotSupported

        raise QuickAddActionNotSupported(
            f"Unsupported quick-add event type: {ctx.event_type}",
        )
    return await handler.handle(ctx)
