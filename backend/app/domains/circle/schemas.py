"""Circle domain read schemas (one per table, from_attributes).

Generated from the SQLAlchemy models -- returned by the service layer so that
services never expose ORM models.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CircleParticipantSourcesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_id: UUID
    circle_participant_id: UUID
    user_id: UUID
    source_type: str
    source_moment_id: UUID
    source_moment_name: str | None = None
    source_moment_type: str | None = None
    participation_date: date | None = None
    is_active_source: bool | None = None
    created_at: datetime | None = None


class CircleParticipantStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stats_id: UUID
    circle_participant_id: UUID
    user_id: UUID
    shared_moment_count: int | None = None
    active_moment_count: int | None = None
    recent_activity_count: int | None = None
    participation_score: Decimal | None = None
    rank_order: int | None = None
    last_activity_date: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CircleParticipantsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    circle_participant_id: UUID
    user_id: UUID
    participant_name: str
    participant_user_id: UUID | None = None
    participant_phone: str | None = None
    participant_email: str | None = None
    first_seen_date: date | None = None
    last_seen_date: date | None = None
    is_active: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CircleSuggestionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    suggestion_id: UUID
    user_id: UUID
    suggestion_type: str
    participant_ids_json: Any
    suggestion_title: str
    suggestion_description: str
    confidence_score: Decimal | None = None
    cta_label: str | None = None
    target_create_flow: str | None = None
    is_active: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
