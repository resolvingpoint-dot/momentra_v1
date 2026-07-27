"""Lifestyle signal model — consumed by Life projection and template mappers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.domains.personal.models import (
    PersonalLifestyleProfile,
    PersonalMetricSnapshots,
    PersonalRuntimeSnapshots,
)


@dataclass(frozen=True)
class LifestyleSignals:
    health: int
    energy: int
    routine: int
    balance: int
    social: int
    environment: int
    wellbeing: int
    consistency: int
    momentum: int

    def as_dict(self) -> dict[str, int]:
        return {
            "health": self.health,
            "energy": self.energy,
            "routine": self.routine,
            "balance": self.balance,
            "social": self.social,
            "environment": self.environment,
            "wellbeing": self.wellbeing,
            "consistency": self.consistency,
            "momentum": self.momentum,
        }


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def _metric(metrics: list[PersonalMetricSnapshots], code: str, default: int) -> int:
    upper = code.upper()
    for m in metrics:
        if (m.metric_code or "").upper() == upper and m.metric_value is not None:
            return _clamp(int(round(float(m.metric_value))))
    return default


def derive_lifestyle_signals(
    *,
    runtime: PersonalRuntimeSnapshots | None,
    metrics: list[PersonalMetricSnapshots],
    profile: PersonalLifestyleProfile | None,
    timeline_count: int,
    experience_count: int = 0,
    wellbeing_count: int = 0,
    discovery_count: int = 0,
    expression_count: int = 0,
) -> LifestyleSignals:
    primary = _clamp(int(round(float(runtime.primary_score)))) if runtime and runtime.primary_score else 68
    energy_label = (profile.lifestyle_energy or "Steady") if profile else "Steady"
    energy_boost = {
        "High": 10,
        "Steady": 4,
        "Low": -8,
        "Variable": 0,
    }.get(energy_label, 0)

    health = _metric(metrics, "HEALTH_SCORE", _clamp(58 + wellbeing_count * 4))
    energy = _metric(metrics, "ENERGY_SCORE", _clamp(primary + energy_boost))
    routine = _metric(metrics, "ROUTINE_SCORE", _clamp(55 + timeline_count))
    balance = _metric(metrics, "BALANCE_SCORE", _clamp(60 + experience_count * 2))
    social = _metric(metrics, "SOCIAL_SCORE", _clamp(58 + experience_count * 3))
    environment = _metric(metrics, "ENVIRONMENT_SCORE", _clamp(62 + discovery_count * 3))
    wellbeing = _metric(metrics, "WELLBEING_SCORE", _clamp(60 + wellbeing_count * 5))
    consistency = _metric(metrics, "CONSISTENCY_SCORE", _clamp(55 + timeline_count * 2))
    momentum = _metric(metrics, "MOMENTUM_SCORE", _clamp((health + energy + routine) // 3))

    return LifestyleSignals(
        health=health,
        energy=energy,
        routine=routine,
        balance=balance,
        social=social,
        environment=environment,
        wellbeing=wellbeing,
        consistency=consistency,
        momentum=momentum,
    )


def life_dimension_boosts(signals: LifestyleSignals) -> dict[str, Any]:
    """Normalized boosts for shared Life projection."""
    return {
        "vitality": _clamp((signals.health + signals.energy) // 2),
        "fulfillment": _clamp((signals.wellbeing + signals.balance) // 2),
        "experience_depth": _clamp((signals.social + signals.environment) // 2),
        "routine_strength": signals.routine,
        "lifestyle_momentum": signals.momentum,
    }
