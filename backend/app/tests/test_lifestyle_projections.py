"""Lifestyle projection builder, mappers, signals, and setup contract."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import ValidationError
from app.domains.personal.templates.lifestyle.projection_builder import (
    LifestyleProjectionBuilder,
    LifestyleProjectionContext,
)
from app.domains.personal.templates.lifestyle.pulse_mapper import build_lifestyle_pulse
from app.domains.personal.templates.lifestyle.moments_mapper import (
    build_lifestyle_moments_detail,
)
from app.domains.personal.templates.lifestyle.memory_mapper import (
    build_lifestyle_memory_aggregate,
)
from app.domains.personal.templates.lifestyle.setup_schema import (
    LIFESTYLE_TEMPLATE_CONTRACT,
)
from app.domains.personal.templates.lifestyle.signals import (
    derive_lifestyle_signals,
    life_dimension_boosts,
)


def test_lifestyle_setup_contract_validates_priorities():
    with pytest.raises(ValidationError):
        LIFESTYLE_TEMPLATE_CONTRACT.validate({"want_more": [], "neglected": ["REST"]})


def test_lifestyle_setup_maps_profile_fields():
    fields = LIFESTYLE_TEMPLATE_CONTRACT.to_profile_fields(
        {
            "lifestyle_style": "BALANCED",
            "current_lifestyle_state": "STEADY",
            "current_energy": "HIGH",
            "want_more": ["JOY", "HEALTH"],
            "neglected": ["REST"],
            "richer_life": "MORE_EXPERIENCES",
        }
    )
    assert fields["lifestyle_style"] == "Balanced"
    assert fields["desired_lifestyle_vectors"]
    assert fields["lifestyle_identity"]


def test_lifestyle_signals_and_life_boosts():
    signals = derive_lifestyle_signals(
        runtime=None,
        metrics=[],
        profile=None,
        timeline_count=3,
        experience_count=2,
        wellbeing_count=1,
    )
    boosts = life_dimension_boosts(signals)
    assert boosts["vitality"] >= 0
    assert boosts["lifestyle_momentum"] == signals.momentum


def test_lifestyle_pulse_mapper_empty_without_moment():
    ctx = LifestyleProjectionContext(user_id=uuid4(), moment=None)
    assert build_lifestyle_pulse(ctx) is None


def test_lifestyle_moments_detail_active_shape():
    moment = SimpleNamespace(
        id=uuid4(),
        moment_type="LIFESTYLE",
        title="My Lifestyle",
        description=None,
        status="ACTIVE",
        setup_state="ACTIVE",
        updated_at=None,
    )
    from app.domains.personal.templates.lifestyle.signals import LifestyleSignals

    ctx = LifestyleProjectionContext(
        user_id=uuid4(),
        moment=moment,
        signals=LifestyleSignals(
            health=70,
            energy=72,
            routine=65,
            balance=68,
            social=74,
            environment=66,
            wellbeing=71,
            consistency=69,
            momentum=70,
        ),
    )
    detail = build_lifestyle_moments_detail(ctx)
    assert detail["metrics"] is not None
    hero = detail["metrics"]["journey_hero"]
    assert "experience_count" in hero
    assert "lifestyle_spend_minor" in hero


def test_lifestyle_memory_aggregate_wrapper():
    moment = SimpleNamespace(
        id=uuid4(),
        moment_type="LIFESTYLE",
        title="Lifestyle",
        description=None,
        status="ACTIVE",
        setup_state="ACTIVE",
        updated_at=None,
    )
    from app.domains.personal.templates.lifestyle.signals import LifestyleSignals

    ctx = LifestyleProjectionContext(
        user_id=uuid4(),
        moment=moment,
        signals=LifestyleSignals(
            health=70,
            energy=72,
            routine=65,
            balance=68,
            social=74,
            environment=66,
            wellbeing=71,
            consistency=69,
            momentum=70,
        ),
        timeline_count=2,
    )
    block = build_lifestyle_memory_aggregate(ctx)
    assert block["section_label"] == "Lifestyle Memory"
    assert block["metrics"] is not None
