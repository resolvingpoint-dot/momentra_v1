"""Quick-add handler protocol and shared context."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(slots=True)
class QuickAddContext:
    session: AsyncSession
    user_id: UUID
    moment_id: UUID
    moment_type_code: str
    quick_add_event_id: UUID
    event_type: str
    event_title: str
    body: dict[str, Any]
    occurred_at: datetime
    timeline: "TimelineDraft | None" = None


@dataclass(slots=True)
class TimelineDraft:
    display_title: str
    display_subtitle: str | None = None
    display_amount: float | None = None
    impact_labels: dict[str, Any] | None = None


class QuickAddHandler(Protocol):
    event_type: str

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft: ...
