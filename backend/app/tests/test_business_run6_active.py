"""Business Run 6 — activity engine, registry, runway calc, sparse projections."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domains.business.activity.handlers._helpers import minor_to_decimal
from app.domains.business.activity.registry import ACTION_REGISTRY
from app.domains.business.activity.types import (
    BUSINESS_OPERATIONS_ACTIONS,
    BUSINESS_RUNWAY_ACTIONS,
    TEAM_OPERATIONS_ACTIONS,
    ActionType,
    moment_type_for_action,
)
from app.domains.business.projection_cache import parse_template_key, template_key
from app.domains.business.templates.business_operations.series_helpers import budget_usage_pct
from app.domains.business.templates.business_runway.series_helpers import net_burn_minor, runway_months
from app.domains.business.templates.registry import builders_for


def test_action_registry_covers_v1_counts():
    assert len(TEAM_OPERATIONS_ACTIONS) == 10
    assert len(BUSINESS_RUNWAY_ACTIONS) == 5
    assert len(BUSINESS_OPERATIONS_ACTIONS) == 5
    assert len(ACTION_REGISTRY) == 20
    for action in ActionType:
        assert action in ACTION_REGISTRY
        meta = ACTION_REGISTRY[action]
        assert "handler" in meta
        assert "affected_slices" in meta


def test_moment_type_for_action():
    assert moment_type_for_action(ActionType.TEAM_UPDATE) == "TEAM_OPERATIONS"
    assert moment_type_for_action(ActionType.CASH_INFLOW) == "BUSINESS_RUNWAY"
    assert moment_type_for_action(ActionType.SPEND_ENTRY) == "BUSINESS_OPERATIONS"


def test_runway_zero_burn_returns_null_months():
    assert runway_months(1_000_00, 0) is None
    assert runway_months(1_000_00, -50) is None
    assert runway_months(3_000_00, 1_000_00) == 3.0


def test_net_burn_minor():
    assert net_burn_minor(1000, 2500) == 1500
    assert net_burn_minor(2500, 1000) == -1500


def test_budget_usage_from_real_spend():
    assert budget_usage_pct(0, 10_000) == 0.0
    assert budget_usage_pct(5_000, 10_000) == 50.0
    assert budget_usage_pct(12_000, 10_000) == 100.0
    assert budget_usage_pct(100, 0) == 0.0


def test_minor_to_decimal_jpy_kwd():
    assert minor_to_decimal(1500, currency="JPY") == Decimal("1500")
    assert minor_to_decimal(1500, currency="INR") == Decimal("15.00")
    assert minor_to_decimal(1500, currency="KWD") == Decimal("1.5")


def test_template_key_round_trip():
    mid = uuid4()
    key = template_key("BUSINESS_RUNWAY", mid)
    mt, parsed = parse_template_key(key)
    assert mt == "BUSINESS_RUNWAY"
    assert parsed == mid


def test_builders_for_known_and_unknown():
    assert builders_for("TEAM_OPERATIONS", None) is not None
    assert builders_for("team_operations", None) is not None
    assert builders_for("business_runway", None) is not None
    assert builders_for("business_operations", None) is not None
    assert builders_for("UNKNOWN", None) is None


def test_sparse_pulse_mapper_no_fake_stats():
    from app.domains.business.templates.team_operations.pulse_mapper import build_pulse

    ctx = SimpleNamespace(
        moment_id=uuid4(),
        moment_type="TEAM_OPERATIONS",
        moment_name=None,
        team_name=None,
        status="ACTIVE",
        is_active=True,
        member_count=0,
        activity_count=0,
        operating_currency="INR",
        open_issues=0,
        pending_approvals=0,
        recognition_count=0,
        meeting_count=0,
    )
    pulse = build_pulse(ctx)
    assert pulse["stats"]["open_issues"] == 0
    assert pulse["member_count"] == 0


def test_runway_pulse_sparse_null_runway():
    from app.domains.business.templates.business_runway.pulse_mapper import build_pulse

    ctx = SimpleNamespace(
        moment_id=uuid4(),
        moment_type="BUSINESS_RUNWAY",
        moment_name="Runway",
        status="ACTIVE",
        is_active=True,
        operating_currency="INR",
        cash_available_minor=0,
        total_inflow_minor=0,
        total_burn_minor=0,
        net_burn_minor=0,
        runway_months=None,
        risk_count=0,
        decision_count=0,
    )
    pulse = build_pulse(ctx)
    assert pulse["stats"]["runway_months"] is None


@pytest.mark.asyncio
async def test_idempotent_client_request_id(monkeypatch):
    """Engine returns existing DTO when client_request_id already stored."""
    from app.domains.business.activity import engine as eng_mod
    from app.domains.business.activity.engine import BusinessActivityEngine

    moment_id = uuid4()
    user_id = uuid4()
    existing = SimpleNamespace(
        event_id=uuid4(),
        business_moment_id=moment_id,
        user_id=user_id,
        moment_type_code="TEAM_OPERATIONS",
        action_type="NOTE",
        title="Hello",
        subtitle=None,
        occurred_at=datetime.now(timezone.utc).replace(tzinfo=None),
        created_by=user_id,
        source="quick_add",
        payload={},
        client_request_id="req-1",
        is_voided=False,
    )

    class FakeSession:
        async def execute(self, *a, **k):
            class R:
                def scalar_one_or_none(self_inner):
                    return SimpleNamespace(moment_id=moment_id, moment_type="team_operations")

            return R()

    async def fake_member(*a, **k):
        return SimpleNamespace(role="Team Lead", member_status="active", is_team_lead=True)

    async def fake_find(*a, **k):
        return existing

    monkeypatch.setattr(eng_mod, "can_create_activity", fake_member)
    monkeypatch.setattr(eng_mod, "find_by_client_request_id", fake_find)

    result = await BusinessActivityEngine(FakeSession()).create(
        user_id,
        moment_id,
        "NOTE",
        "Hello",
        client_request_id="req-1",
    )
    assert result["idempotent_replay"] is True
    assert result["event_id"] == str(existing.event_id)
