"""Relationships projection builder, mappers, signals, and setup contract."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import ValidationError
from app.domains.personal.templates.relationships.projection_builder import (
    RelationshipsProjectionContext,
)
from app.domains.personal.templates.relationships.pulse_mapper import build_relationships_pulse
from app.domains.personal.templates.relationships.moments_mapper import (
    build_relationships_moments_detail,
)
from app.domains.personal.templates.relationships.memory_mapper import (
    build_relationships_memory_aggregate,
)
from app.domains.personal.templates.relationships.setup_schema import (
    RELATIONSHIPS_TEMPLATE_CONTRACT,
)
from app.domains.personal.templates.relationships.signals import (
    derive_relationships_signals,
    life_dimension_boosts,
)
from app.domains.personal.templates.registry import get_template_projection_registry


def test_relationships_registered_in_template_registry():
    from app.domains.personal.templates.registry import register_template_projection_handlers

    register_template_projection_handlers()
    assert get_template_projection_registry().is_registered("RELATIONSHIPS")


def test_relationships_setup_contract_validates_priorities():
    with pytest.raises(ValidationError):
        RELATIONSHIPS_TEMPLATE_CONTRACT.validate({"want_more": [], "neglected": ["CHECK_INS"]})


def test_relationships_setup_maps_profile_fields():
    fields = RELATIONSHIPS_TEMPLATE_CONTRACT.to_profile_fields(
        {
            "relationship_focus": "FAMILY",
            "current_state": "CONNECTED",
            "want_more": ["QUALITY_TIME", "TRUST"],
            "neglected": ["CHECK_INS"],
            "strength_drivers": ["CONSISTENCY"],
            "investment_areas": ["LISTENING"],
        }
    )
    assert fields["relationship_focus"] == "Family"
    assert fields["desired_connection_types"]
    assert fields["relationship_identity"]


def test_relationships_signals_and_life_boosts():
    signals = derive_relationships_signals(
        runtime=None,
        metrics=[],
        profile=None,
        timeline_count=3,
        connection_count=2,
        support_count=1,
    )
    boosts = life_dimension_boosts(signals)
    assert boosts["connection"] >= 0
    assert boosts["resilience"] >= 0
    assert boosts["fulfillment"] >= 0


def test_relationships_pulse_mapper_empty_without_moment():
    ctx = RelationshipsProjectionContext(user_id=uuid4(), moment=None)
    assert build_relationships_pulse(ctx) is None


def test_relationships_pulse_mapper_contract_fields():
    moment = SimpleNamespace(
        id=uuid4(),
        moment_type="RELATIONSHIPS",
        title="My Relationships",
        description=None,
        status="ACTIVE",
        setup_state="ACTIVE",
        updated_at=None,
    )
    from app.domains.personal.templates.relationships.signals import RelationshipsSignals

    signals = RelationshipsSignals(
        connection=70,
        trust=68,
        communication=66,
        support=72,
        presence=65,
        quality_time=64,
        social_strength=69,
        relationship_health=71,
        growth=60,
    )
    ctx = RelationshipsProjectionContext(
        user_id=uuid4(),
        moment=moment,
        signals=signals,
        connection_count=2,
        support_count=1,
        experience_count=1,
    )
    pulse = build_relationships_pulse(ctx)
    assert pulse is not None
    for key in (
        "connection_signals_title",
        "pattern_insight_title",
        "pattern_insight_body",
        "vitality_section_label",
        "bond_rate_section_label",
        "connection_signals",
    ):
        assert key in pulse, f"missing pulse field: {key}"
    assert pulse["metrics"] is not None
    assert "trust" in pulse["metrics"]["trends_30d"]
    assert "connection" in pulse["metrics"]["trends_30d"]


def test_relationships_moments_detail_active_shape():
    moment = SimpleNamespace(
        id=uuid4(),
        moment_type="RELATIONSHIPS",
        title="My Relationships",
        description=None,
        status="ACTIVE",
        setup_state="ACTIVE",
        updated_at=None,
    )
    from app.domains.personal.templates.relationships.signals import RelationshipsSignals

    signals = RelationshipsSignals(
        connection=70,
        trust=68,
        communication=66,
        support=72,
        presence=65,
        quality_time=64,
        social_strength=69,
        relationship_health=71,
        growth=60,
    )
    ctx = RelationshipsProjectionContext(
        user_id=uuid4(),
        moment=moment,
        signals=signals,
        connection_count=2,
        support_count=1,
        experience_count=1,
    )
    detail = build_relationships_moments_detail(ctx)
    assert detail["metrics"] is not None
    assert "journey_hero" in detail["metrics"]
    assert "journey_timeline" in detail["metrics"]
    assert "highest_month" in detail["metrics"]["money_journey"]


def test_relationships_memory_aggregate_shape():
    moment = SimpleNamespace(
        id=uuid4(),
        moment_type="RELATIONSHIPS",
        title="Relationships",
        description=None,
        status="ACTIVE",
        setup_state="ACTIVE",
        updated_at=None,
    )
    from app.domains.personal.templates.relationships.signals import RelationshipsSignals

    profile = SimpleNamespace(
        relationship_identity="Family Builder",
        relationship_focus="Family",
        current_relationship_state="Connected",
        primary_relationship_opportunity="Quality Time",
        relationship_potential="HIGH",
        primary_relationship_gap="Check-ins",
    )
    signals = RelationshipsSignals(
        connection=75,
        trust=70,
        communication=68,
        support=72,
        presence=66,
        quality_time=74,
        social_strength=71,
        relationship_health=73,
        growth=62,
    )
    ctx = RelationshipsProjectionContext(
        user_id=uuid4(),
        moment=moment,
        profile=profile,
        signals=signals,
        timeline_count=4,
    )
    block = build_relationships_memory_aggregate(ctx)
    assert block["section_label"] == "Relationships Memory"
    assert block["metrics"] is not None
    assert block["metrics"]["identity_snapshot"]["title"]
