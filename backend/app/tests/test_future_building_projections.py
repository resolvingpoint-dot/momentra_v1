"""Future Building projection builder, mappers, signals, and setup contract."""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import ValidationError
from app.domains.personal.future_building.signals import (
    FutureSignals,
    derive_future_signals,
    life_dimension_boosts,
)
from app.domains.personal.templates.future_building.moments_mapper import (
    build_future_building_moments,
)
from app.domains.personal.templates.future_building.projection_builder import (
    FutureBuildingProjectionContext,
)
from app.domains.personal.templates.future_building.pulse_mapper import (
    build_future_building_pulse,
)
from app.domains.personal.templates.future_building.setup_schema import (
    FUTURE_BUILDING_TEMPLATE_CONTRACT,
)


def _profile(**kwargs):
    defaults = {
        "future_theme": "Career Growth",
        "current_momentum_state": "Just Starting",
        "future_values": ["Growth"],
        "friction_sources": ["Lack Of Time"],
        "momentum_drivers": ["Learning"],
        "future_confidence": "Hopeful",
        "future_identity": "Growth Architect",
        "primary_opportunity_label": "Deep Skill Development",
        "largest_friction_label": "Lack Of Time",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _moment(status: str = "ACTIVE"):
    return SimpleNamespace(
        id=uuid4(),
        moment_type="FUTURE_BUILDING",
        title="My Future",
        description=None,
        status=status,
        setup_state="ACTIVE",
        updated_at=datetime.now(timezone.utc),
    )


def _runtime(primary_score: float = 72.0):
    return SimpleNamespace(
        primary_score=primary_score,
        runtime_summary="Building momentum through learning.",
        runtime_state_label="Building",
    )


def _ctx(**overrides) -> FutureBuildingProjectionContext:
    moment = overrides["moment"] if "moment" in overrides else _moment()
    signals = None
    if moment is not None:
        signals = derive_future_signals(
            runtime=overrides.get("runtime", _runtime()),
            metrics=overrides.get("metrics", []),
            profile=overrides.get("profile", _profile()),
            timeline_count=overrides.get("timeline_count", 3),
            learning_count=overrides.get("learning_count", 2),
            milestone_count=overrides.get("milestone_count", 1),
            opportunity_count=overrides.get("opportunity_count", 1),
        )
    return FutureBuildingProjectionContext(
        user_id=overrides.get("user_id", uuid4()),
        moment=moment,
        profile=overrides.get("profile", _profile() if moment else None),
        runtime=overrides.get("runtime", _runtime() if moment else None),
        metrics=overrides.get("metrics", []),
        timeline=overrides.get("timeline", []),
        money_events=overrides.get("money_events", []),
        highlights=overrides.get("highlights", []),
        turning_points=overrides.get("turning_points", []),
        catalog=overrides.get("catalog", {}),
        timeline_count=overrides.get("timeline_count", 3),
        learning_count=overrides.get("learning_count", 2),
        milestone_count=overrides.get("milestone_count", 1),
        opportunity_count=overrides.get("opportunity_count", 1),
        signals=overrides.get("signals", signals),
    )


def test_future_signals_clamped():
    signals = derive_future_signals(
        runtime=_runtime(primary_score=150),
        metrics=[],
        profile=_profile(),
        timeline_count=0,
    )
    assert isinstance(signals, FutureSignals)
    assert 0 <= signals.momentum <= 100
    assert signals.confidence <= 100


def test_life_dimension_boosts_from_signals():
    signals = FutureSignals(
        confidence=80,
        discipline=70,
        consistency=75,
        momentum=82,
        resilience=68,
        growth=77,
        clarity=72,
    )
    boosts = life_dimension_boosts(signals)
    assert "goal_momentum" in boosts
    assert boosts["goal_momentum"] > 0


def test_setup_contract_validates_required_chips():
    with pytest.raises(ValidationError):
        FUTURE_BUILDING_TEMPLATE_CONTRACT.validate(
            {
                "building_focus": "CAREER_GROWTH",
                "current_state": "JUST_STARTING",
                "values": [],
                "friction_sources": ["LACK_OF_TIME"],
                "momentum_drivers": ["LEARNING"],
                "future_feeling": "HOPEFUL",
            }
        )


def test_setup_contract_normalizes_and_maps_profile_fields():
    answers = {
        "building_focus": "LEARNING_SKILLS",
        "current_state": "MAKING_PROGRESS",
        "values": ["GROWTH", "PURPOSE"],
        "friction_sources": ["BURNOUT"],
        "momentum_drivers": ["LEARNING"],
        "future_feeling": "CONFIDENT",
    }
    FUTURE_BUILDING_TEMPLATE_CONTRACT.validate(answers)
    fields = FUTURE_BUILDING_TEMPLATE_CONTRACT.to_profile_fields(answers)
    assert fields["future_theme"] == "Learning & Skills"
    assert fields["future_identity"] == "Growth Architect"
    assert "Growth" in fields["future_values"]


def test_pulse_mapper_active_shape():
    pulse = build_future_building_pulse(_ctx())
    assert pulse is not None
    assert pulse["hero_title"] == "Future Momentum"
    assert pulse["dashboard_card"]["moment_type_code"] == "FUTURE_BUILDING"
    metrics = pulse["metrics"]
    assert "axis_scores" in metrics
    assert "gauges" in metrics
    assert metrics["momentum_index"] >= 0


def test_moments_mapper_active_projection():
    envelope = build_future_building_moments(_ctx())
    assert envelope["status"] == "ACTIVE"
    assert envelope["moment_type_code"] == "FUTURE_BUILDING"
    mp = envelope["moment_projection"]
    assert mp is not None
    for key in ("journey_hero", "journey_timeline", "money_journey", "best_moments", "turning_points"):
        assert key in mp


def test_moments_mapper_empty_when_no_moment():
    envelope = build_future_building_moments(
        FutureBuildingProjectionContext(user_id=uuid4(), moment=None)
    )
    assert envelope["status"] == "EMPTY"
    assert envelope["moment_projection"] is None
