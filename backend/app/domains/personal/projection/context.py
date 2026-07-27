"""Normalized projection context — single in-memory view after one SQL load pass."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.domains.moments.models import MomentModel
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalLifeAggregateSnapshots,
    PersonalLifeConnections,
    PersonalLifeDriftAlerts,
    PersonalLifeHealthSnapshots,
    PersonalLifeJourneyEvents,
    PersonalLifeMonthlyChanges,
    PersonalLifeOperationsProfile,
    PersonalMemoryDriverRankings,
    PersonalMemoryEmotionalDna,
    PersonalMemoryEvolutionSnapshots,
    PersonalMemoryIdentitySnapshots,
    PersonalMemoryPatterns,
    PersonalMetricSnapshots,
    PersonalMomentHighlights,
    PersonalMomentTurningPoints,
    PersonalMoneyEvents,
    PersonalRecommendations,
    PersonalRuntimeSnapshots,
)
from app.domains.reference_data.catalog import ReferenceCatalog


@dataclass
class MomentContext:
    moment: MomentModel
    timeline: list[PersonalActivityTimeline] = field(default_factory=list)
    timeline_count: int = 0
    money_events: list[PersonalMoneyEvents] = field(default_factory=list)
    runtime: PersonalRuntimeSnapshots | None = None
    metrics: list[PersonalMetricSnapshots] = field(default_factory=list)
    profile: PersonalLifeOperationsProfile | None = None
    highlights: list[PersonalMomentHighlights] = field(default_factory=list)
    turning_points: list[PersonalMomentTurningPoints] = field(default_factory=list)


@dataclass
class ProjectionContext:
    user_id: UUID
    visible_moments: list[MomentModel]
    active_moments: list[MomentModel]
    moments_by_type: dict[str, MomentContext]
    catalog: ReferenceCatalog
    # User-level memory intelligence (aggregated across active templates)
    identity_snapshots: list[PersonalMemoryIdentitySnapshots] = field(default_factory=list)
    memory_patterns: list[PersonalMemoryPatterns] = field(default_factory=list)
    driver_rankings: list[PersonalMemoryDriverRankings] = field(default_factory=list)
    emotional_dna: list[PersonalMemoryEmotionalDna] = field(default_factory=list)
    evolution_snapshots: list[PersonalMemoryEvolutionSnapshots] = field(default_factory=list)
    memory_recommendations: list[PersonalRecommendations] = field(default_factory=list)
    # User-level personal life
    life_health: PersonalLifeHealthSnapshots | None = None
    life_aggregate: PersonalLifeAggregateSnapshots | None = None
    life_connections: list[PersonalLifeConnections] = field(default_factory=list)
    drift_alerts: list[PersonalLifeDriftAlerts] = field(default_factory=list)
    journey_events: list[PersonalLifeJourneyEvents] = field(default_factory=list)
    monthly_changes: list[PersonalLifeMonthlyChanges] = field(default_factory=list)
    life_recommendations: list[PersonalRecommendations] = field(default_factory=list)
    runtime_scores_by_type: dict[str, int] = field(default_factory=dict)
