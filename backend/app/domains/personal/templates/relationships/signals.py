"""Relationships signal model — consumed by template mappers and shared Life projection."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.domains.personal.models import (
    PersonalMetricSnapshots,
    PersonalRelationshipsProfile,
    PersonalRuntimeSnapshots,
)


@dataclass(frozen=True)
class RelationshipsSignals:
    connection: int
    trust: int
    communication: int
    support: int
    presence: int
    quality_time: int
    social_strength: int
    relationship_health: int
    growth: int

    def as_dict(self) -> dict[str, int]:
        return {
            "connection": self.connection,
            "trust": self.trust,
            "communication": self.communication,
            "support": self.support,
            "presence": self.presence,
            "quality_time": self.quality_time,
            "social_strength": self.social_strength,
            "relationship_health": self.relationship_health,
            "growth": self.growth,
        }


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def _metric(metrics: list[PersonalMetricSnapshots], code: str, default: int) -> int:
    upper = code.upper()
    for m in metrics:
        if (m.metric_code or "").upper() == upper and m.metric_value is not None:
            return _clamp(int(round(float(m.metric_value))))
    return default


def derive_relationships_signals(
    *,
    runtime: PersonalRuntimeSnapshots | None,
    metrics: list[PersonalMetricSnapshots],
    profile: PersonalRelationshipsProfile | None,
    timeline_count: int,
    connection_count: int = 0,
    support_count: int = 0,
    experience_count: int = 0,
    investment_count: int = 0,
    adjust_count: int = 0,
) -> RelationshipsSignals:
    primary = (
        _clamp(int(round(float(runtime.primary_score))))
        if runtime and runtime.primary_score
        else 68
    )
    energy_label = (profile.relationship_energy or "Steady") if profile else "Steady"
    energy_boost = {
        "High": 8,
        "Steady": 4,
        "Low": -6,
        "Variable": 0,
    }.get(energy_label, 0)

    connection = _metric(metrics, "CONNECTION_SCORE", _clamp(58 + connection_count * 5))
    trust = _metric(metrics, "TRUST_SCORE", _clamp(55 + support_count * 4 + connection_count * 2))
    communication = _metric(
        metrics, "COMMUNICATION_SCORE", _clamp(56 + connection_count * 4)
    )
    support = _metric(metrics, "SUPPORT_SCORE", _clamp(54 + support_count * 6))
    presence = _metric(
        metrics, "PRESENCE_SCORE", _clamp(52 + experience_count * 4 + connection_count * 2)
    )
    quality_time = _metric(
        metrics, "QUALITY_TIME_SCORE", _clamp(50 + experience_count * 5)
    )
    social_strength = _metric(
        metrics, "SOCIAL_STRENGTH_SCORE", _clamp(primary + energy_boost)
    )
    relationship_health = _metric(
        metrics,
        "RELATIONSHIP_HEALTH_SCORE",
        _clamp((connection + trust + support) // 3),
    )
    growth = _metric(metrics, "GROWTH_SCORE", _clamp(52 + adjust_count * 5 + timeline_count))

    return RelationshipsSignals(
        connection=connection,
        trust=trust,
        communication=communication,
        support=support,
        presence=presence,
        quality_time=quality_time,
        social_strength=social_strength,
        relationship_health=relationship_health,
        growth=growth,
    )


def life_dimension_boosts(signals: RelationshipsSignals) -> dict[str, Any]:
    """Boosts for shared Personal Life dimensions (not a standalone signal block)."""
    return {
        "connection": signals.connection,
        "resilience": _clamp((signals.support + signals.trust) // 2),
        "fulfillment": _clamp((signals.quality_time + signals.presence) // 2),
        "growth": signals.growth,
        "belonging": _clamp((signals.social_strength + signals.connection) // 2),
        "relationship_health": signals.relationship_health,
    }
