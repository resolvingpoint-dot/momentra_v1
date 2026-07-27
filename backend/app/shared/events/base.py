from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


# Nil UUID for user-scoped events that are not tied to a moment (e.g. preferences).
USER_SCOPED_MOMENT_ID = UUID(int=0)


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Immutable domain event published on the in-process bus."""

    name: str
    user_id: UUID
    context: str
    # Required for moment-scoped events; defaults to nil UUID for user-scoped ones
    # (preferences, logout, etc.) so callers cannot omit it by accident after schema churn.
    moment_id: UUID = USER_SCOPED_MOMENT_ID
    moment_type: str | None = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = field(default_factory=dict)
