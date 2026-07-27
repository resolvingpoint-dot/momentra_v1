"""Future Building quick-add orchestration."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.future_building.quick_add.constants import EVENT_TO_TAB
from app.domains.personal.future_building.quick_add.handlers import registry as handlers
from app.domains.personal.future_building.quick_add.options_builder import (
    FutureBuildingQuickAddOptionsBuilder,
)
from app.domains.personal.quick_add.base_service import TemplateQuickAddService


class FutureBuildingQuickAddService(TemplateQuickAddService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session,
            moment_type_code="FUTURE_BUILDING",
            event_to_tab=EVENT_TO_TAB,
            event_aliases={},
            options_builder=FutureBuildingQuickAddOptionsBuilder(),
            dispatch_fn=handlers.dispatch,
        )
