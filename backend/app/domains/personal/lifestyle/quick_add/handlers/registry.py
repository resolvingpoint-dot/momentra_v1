"""Dispatch Lifestyle quick-add events."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.lifestyle.quick_add.handlers.adjust import AdjustHandler
from app.domains.personal.lifestyle.quick_add.handlers.discovery import DiscoveryHandler
from app.domains.personal.lifestyle.quick_add.handlers.experience import ExperienceHandler
from app.domains.personal.lifestyle.quick_add.handlers.expression import ExpressionHandler
from app.domains.personal.lifestyle.quick_add.handlers.lifestyle_expense import (
    LifestyleExpenseHandler,
)
from app.domains.personal.lifestyle.quick_add.handlers.wellbeing import WellbeingHandler

_HANDLERS = {
    h.event_type: h
    for h in (
        LifestyleExpenseHandler(),
        ExperienceHandler(),
        WellbeingHandler(),
        DiscoveryHandler(),
        ExpressionHandler(),
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
