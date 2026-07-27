"""Lifestyle quick-add orchestration."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.lifestyle.quick_add.constants import EVENT_ALIASES, EVENT_TO_TAB
from app.domains.personal.lifestyle.quick_add.handlers import registry as handlers
from app.domains.personal.lifestyle.quick_add.options_builder import (
    LifestyleQuickAddOptionsBuilder,
)
from app.domains.personal.quick_add.base_service import TemplateQuickAddService


class LifestyleQuickAddService(TemplateQuickAddService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            session,
            moment_type_code="LIFESTYLE",
            event_to_tab=EVENT_TO_TAB,
            event_aliases=EVENT_ALIASES,
            options_builder=LifestyleQuickAddOptionsBuilder(),
            dispatch_fn=handlers.dispatch,
        )
