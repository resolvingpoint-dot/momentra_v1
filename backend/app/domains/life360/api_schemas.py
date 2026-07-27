"""Response DTOs for the Life360 API.

Every field is copied straight from the ``life360_snapshots`` snapshot table
(populated by ``sp_refresh_life360_snapshots``); the service performs no scoring
in Python.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.domains.life360.schemas import Life360SnapshotsSchema


class Life360DimensionStat(BaseModel):
    dimension: str
    score: Decimal | None = None
    status: str | None = None


class Life360EnergyAllocation(BaseModel):
    personal_pct: Decimal | None = None
    group_pct: Decimal | None = None
    business_pct: Decimal | None = None


class Life360TrendPoint(BaseModel):
    snapshot_date: date
    life_alignment_score: Decimal


class Life360SummaryResponse(BaseModel):
    snapshot_date: date | None = None
    life_alignment_score: Decimal | None = None
    life_phase: str | None = None
    momentum_score: Decimal | None = None
    momentum_status: str | None = None
    strongest_driver: str | None = None
    biggest_tension: str | None = None
    reflection_summary: str | None = None
    active_dimensions_count: int | None = None


class Life360AnalyticsResponse(BaseModel):
    snapshot_date: date | None = None
    life_alignment_score: Decimal | None = None
    signal_confidence_score: Decimal | None = None
    momentum_score: Decimal | None = None
    momentum_status: str | None = None
    strongest_driver: str | None = None
    biggest_tension: str | None = None
    dimensions: list[Life360DimensionStat] = []
    energy: Life360EnergyAllocation = Life360EnergyAllocation()
    domain_scores: dict[str, Decimal | None] = {}
    trend: list[Life360TrendPoint] = []


class Life360RefreshResponse(BaseModel):
    refreshed: bool
    snapshot: Life360SnapshotsSchema | None = None
