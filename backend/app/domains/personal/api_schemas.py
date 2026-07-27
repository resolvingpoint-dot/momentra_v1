"""Request/response DTOs for the Personal module router.

Kept separate from the generated per-table read schemas (``schemas.py``) so the
router has explicit, validated input contracts and composite response shapes for
rich OpenAPI documentation. The service layer still returns only schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domains.personal.schemas import (
    PersonalInsightsSchema,
    PersonalMemoryDriverRankingsSchema,
    PersonalMemoryEmotionalDnaSchema,
    PersonalMemoryEvolutionSnapshotsSchema,
    PersonalMemoryIdentitySnapshotsSchema,
    PersonalMemoryPatternsSchema,
    PersonalMetricSnapshotsSchema,
    PersonalRecommendationsSchema,
)

MomentTypeCode = Literal["LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS"]
MomentStatus = Literal["DRAFT", "ACTIVE", "PAUSED", "ARCHIVED"]


class PersonalMomentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    moment_type_id: UUID
    moment_name: str = Field(min_length=1, max_length=150)


class PersonalMomentProfileCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity_label: str = Field(min_length=1, max_length=100)
    identity_description: str = Field(min_length=1)
    primary_focus_label: str = Field(min_length=1, max_length=100)
    setup_payload: dict[str, Any]
    energy_label: str | None = Field(default=None, max_length=100)
    primary_gap_label: str | None = Field(default=None, max_length=100)
    primary_opportunity_label: str | None = Field(default=None, max_length=150)
    horizon_current_label: str | None = Field(default=None, max_length=100)
    horizon_target_label: str | None = Field(default=None, max_length=100)
    horizon_gap_label: str | None = Field(default=None, max_length=100)
    horizon_potential_label: Literal["LOW", "MODERATE", "HIGH"] | None = None


class PersonalQuickAddRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    moment_type_code: MomentTypeCode
    quick_add_tab_code: str = Field(min_length=1, max_length=50)
    event_type: str = Field(min_length=1, max_length=80)
    raw_payload: dict[str, Any]
    event_occurred_at: datetime | None = None


class PersonalMomentCounts(BaseModel):
    total: int = 0
    draft: int = 0
    active: int = 0
    paused: int = 0
    archived: int = 0


class PersonalAnalyticsResponse(BaseModel):
    counts: PersonalMomentCounts
    insights: list[PersonalInsightsSchema] = []
    recommendations: list[PersonalRecommendationsSchema] = []
    metrics: list[PersonalMetricSnapshotsSchema] = []


class PersonalMemoryOverviewResponse(BaseModel):
    identity_snapshots: list[PersonalMemoryIdentitySnapshotsSchema] = []
    patterns: list[PersonalMemoryPatternsSchema] = []
    emotional_dna: list[PersonalMemoryEmotionalDnaSchema] = []
    driver_rankings: list[PersonalMemoryDriverRankingsSchema] = []
    evolution_snapshots: list[PersonalMemoryEvolutionSnapshotsSchema] = []
