"""Circle domain services (one per table).

Each service inherits the full orchestration + business-logic skeleton
from app.core.service.BaseService (validation, permission checks,
workflow/state transitions, snapshot refresh, cache invalidation, event
creation) and always returns schemas -- never SQLAlchemy models. No HTTP.
"""
from __future__ import annotations

from app.core.service import BaseService
from app.domains.circle.repository import (
    CircleParticipantSourcesRepository,
    CircleParticipantStatsRepository,
    CircleParticipantsRepository,
    CircleSuggestionsRepository,
)
from app.domains.circle.schemas import (
    CircleParticipantSourcesSchema,
    CircleParticipantStatsSchema,
    CircleParticipantsSchema,
    CircleSuggestionsSchema,
)


class CircleParticipantSourcesService(BaseService):
    repository_class = CircleParticipantSourcesRepository
    schema = CircleParticipantSourcesSchema


class CircleParticipantStatsService(BaseService):
    repository_class = CircleParticipantStatsRepository
    schema = CircleParticipantStatsSchema


class CircleParticipantsService(BaseService):
    repository_class = CircleParticipantsRepository
    schema = CircleParticipantsSchema


class CircleSuggestionsService(BaseService):
    repository_class = CircleSuggestionsRepository
    schema = CircleSuggestionsSchema
