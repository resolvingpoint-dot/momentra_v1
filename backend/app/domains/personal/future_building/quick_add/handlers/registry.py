"""Dispatch Future Building quick-add events."""
from __future__ import annotations

from app.domains.personal.future_building.quick_add.handlers.contribution import (
    ContributionHandler,
)
from app.domains.personal.future_building.quick_add.handlers.learning import (
    LearningHandler,
)
from app.domains.personal.future_building.quick_add.handlers.milestone import (
    MilestoneHandler,
)
from app.domains.personal.future_building.quick_add.handlers.opportunity import (
    OpportunityHandler,
)
from app.domains.personal.future_building.quick_add.handlers.pivot import PivotHandler
from app.domains.personal.future_building.quick_add.handlers.progress import (
    ProgressHandler,
)
from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)

_HANDLERS = {
    h.event_type: h
    for h in (
        ContributionHandler(),
        MilestoneHandler(),
        OpportunityHandler(),
        PivotHandler(),
        ProgressHandler(),
        LearningHandler(),
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
