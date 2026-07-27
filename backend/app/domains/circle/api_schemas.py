"""Response DTOs for the Circle API.

All values originate from the circle snapshot tables (``circle_participants``,
``circle_participant_stats``, ``circle_suggestions``, ``circle_participant_sources``)
populated by ``sp_refresh_circle``. The service only selects/orders/counts these
rows; it never recomputes participation scores or rankings.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.domains.circle.schemas import (
    CircleParticipantsSchema,
    CircleParticipantStatsSchema,
    CircleSuggestionsSchema,
)


class CircleParticipantEntry(BaseModel):
    participant: CircleParticipantsSchema
    stats: CircleParticipantStatsSchema | None = None
    is_group_participant: bool = False
    is_business_participant: bool = False


class CircleRecentActivityItem(BaseModel):
    source_type: str
    source_moment_id: UUID
    source_moment_name: str | None = None
    source_moment_type: str | None = None
    participant_count: int = 0
    last_activity_date: date | None = None


class CircleTopParticipant(BaseModel):
    circle_participant_id: UUID
    participant_name: str
    participation_score: Decimal | None = None
    shared_moment_count: int | None = None
    active_moment_count: int | None = None
    rank_order: int | None = None


class CircleReadResponse(BaseModel):
    participants: list[CircleParticipantEntry] = []
    suggestions: list[CircleSuggestionsSchema] = []
    recent_activity: list[CircleRecentActivityItem] = []


class CircleAnalyticsResponse(BaseModel):
    total_participants: int
    active_participants: int
    suggestion_count: int
    top_participants: list[CircleTopParticipant] = []


class CircleSummaryResponse(BaseModel):
    participant_count: int
    active_participant_count: int
    suggestion_count: int
    top_participant: CircleTopParticipant | None = None


class CircleRefreshResponse(BaseModel):
    refreshed: bool
    participant_count: int
    suggestion_count: int
