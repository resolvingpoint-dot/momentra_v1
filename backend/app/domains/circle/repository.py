"""Circle domain repositories (circle_* tables).

One async repository per table. Each inherits the full operation set from
``app.core.repository.AsyncRepository``: create, update, delete, get-by-id,
list, search, pagination, filtering, transactions, bulk insert/update and soft
delete (where the model exposes a soft-delete column). Database access only --
no business logic, no HTTP, no FastAPI.
"""
from __future__ import annotations

from app.core.repository import AsyncRepository
from app.domains.circle.models import (
    CircleParticipantSources,
    CircleParticipantStats,
    CircleParticipants,
    CircleSuggestions,)


class CircleParticipantSourcesRepository(AsyncRepository[CircleParticipantSources]):
    model = CircleParticipantSources


class CircleParticipantStatsRepository(AsyncRepository[CircleParticipantStats]):
    model = CircleParticipantStats


class CircleParticipantsRepository(AsyncRepository[CircleParticipants]):
    model = CircleParticipants

    def _detect_soft_delete(self) -> tuple[str, str] | None:
        # ``is_active`` is a Circle filter flag, not a soft-delete column.
        return None


class CircleSuggestionsRepository(AsyncRepository[CircleSuggestions]):
    model = CircleSuggestions
