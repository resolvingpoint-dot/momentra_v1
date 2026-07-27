"""Future Building signal model — consumed by Life projection and template mappers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.domains.personal.models import (
    PersonalFutureBuildingProfile,
    PersonalMetricSnapshots,
    PersonalRuntimeSnapshots,
)


@dataclass(frozen=True)
class FutureSignals:
    confidence: int
    discipline: int
    consistency: int
    momentum: int
    resilience: int
    growth: int
    clarity: int

    def as_dict(self) -> dict[str, int]:
        return {
            "confidence": self.confidence,
            "discipline": self.discipline,
            "consistency": self.consistency,
            "momentum": self.momentum,
            "resilience": self.resilience,
            "growth": self.growth,
            "clarity": self.clarity,
        }


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def _metric(metrics: list[PersonalMetricSnapshots], code: str, default: int) -> int:
    upper = code.upper()
    for m in metrics:
        if (m.metric_code or "").upper() == upper and m.metric_value is not None:
            return _clamp(int(round(float(m.metric_value))))
    return default


def derive_future_signals(
    *,
    runtime: PersonalRuntimeSnapshots | None,
    metrics: list[PersonalMetricSnapshots],
    profile: PersonalFutureBuildingProfile | None,
    timeline_count: int,
    learning_count: int = 0,
    milestone_count: int = 0,
    opportunity_count: int = 0,
) -> FutureSignals:
    primary = _clamp(int(round(float(runtime.primary_score)))) if runtime and runtime.primary_score else 70
    confidence = primary
    if profile and profile.future_confidence:
        feeling_boost = {
            "Exciting": 8,
            "Hopeful": 6,
            "Confident": 10,
            "Unclear": -6,
            "Stuck": -10,
            "Overwhelming": -8,
        }.get(profile.future_confidence, 0)
        confidence = _clamp(primary + feeling_boost)

    discipline = _metric(metrics, "EXECUTION_SCORE", _clamp(60 + timeline_count))
    consistency = _metric(metrics, "LEARNING_SCORE", _clamp(55 + learning_count * 3))
    momentum = _metric(metrics, "MOMENTUM_SCORE", primary)
    resilience = _metric(metrics, "RESILIENCE_SCORE", _clamp(65 + milestone_count * 2))
    growth = _metric(metrics, "GROWTH_SCORE", _clamp(60 + milestone_count * 4))
    clarity = _metric(
        metrics,
        "CLARITY_SCORE",
        _clamp(58 + opportunity_count * 3),
    )

    return FutureSignals(
        confidence=confidence,
        discipline=discipline,
        consistency=consistency,
        momentum=momentum,
        resilience=resilience,
        growth=growth,
        clarity=clarity,
    )


def life_dimension_boosts(signals: FutureSignals) -> dict[str, Any]:
    """Normalized boosts for shared Life projection (no template-specific API fields)."""
    return {
        "future_readiness": _clamp((signals.confidence + signals.growth) // 2),
        "savings_confidence": _clamp((signals.discipline + signals.consistency) // 2),
        "investment_health": _clamp((signals.growth + signals.momentum) // 2),
        "goal_momentum": signals.momentum,
        "planning_consistency": signals.consistency,
    }
