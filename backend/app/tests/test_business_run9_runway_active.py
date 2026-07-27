"""Business Run 9 — Runway projection section trees, Life slices, Memory allowlist."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domains.business.life.mapper import RUNWAY_SLICES, build_runway_slices, map_life
from app.domains.business.memory.mapper import MEMORY_ACTION_ALLOWLIST, map_memory, map_memory_event
from app.domains.business.templates.business_runway.moments_mapper import build_moments
from app.domains.business.templates.business_runway.pulse_mapper import build_pulse
from app.domains.business.templates.business_runway.section_helpers import rule_based_runway_health
from app.domains.business.templates.business_runway.signals import derive_signals
from app.domains.business.templates.business_runway.series_helpers import runway_months


PULSE_SECTIONS = (
    "hero",
    "runway_health",
    "cash_position",
    "monthly_burn",
    "revenue_trend",
    "collection_rate",
    "runway_months",
    "cash_movement",
    "kpis",
    "forecast",
    "attention_items",
    "trends",
    "signals",
    "recent_activity",
    "next_best_action",
)

MOMENTS_SECTIONS = (
    "journey_hero",
    "cash_available",
    "runway_months",
    "timeline",
    "revenue_updates",
    "forecast_changes",
    "expense_events",
    "inflow_events",
    "funding_events",
    "invoices",
    "payroll",
    "milestones",
    "recent_activity",
)


def _empty_ctx(**overrides):
    base = dict(
        moment_id=uuid4(),
        moment_type="BUSINESS_RUNWAY",
        moment_name="",
        runway_name="",
        status="ACTIVE",
        is_active=True,
        activity_count=0,
        activities=[],
        operating_currency="INR",
        total_inflow_minor=0,
        total_burn_minor=0,
        net_burn_minor=0,
        monthly_burn_setup_minor=0,
        monthly_revenue_minor=0,
        collection_rate_percent=None,
        runway_goal_months=None,
        alert_threshold_months=6.0,
        revenue_status=None,
        runway_months=None,
        cash_available_minor=0,
        risk_count=0,
        decision_count=0,
        financial_update_count=0,
        projection=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_pulse_always_has_deterministic_sections():
    pulse = build_pulse(_empty_ctx())
    for key in PULSE_SECTIONS:
        assert key in pulse, f"missing pulse section {key}"
        assert "state" in pulse[key]
    assert pulse["hero"]["runway_health"]["band"] == "empty"
    assert pulse["recent_activity"]["state"] == "empty"


def test_moments_sections_distinct_from_pulse_recent():
    activities = [
        {
            "event_id": str(uuid4()),
            "action_type": "CASH_INFLOW",
            "title": "Funding round",
            "occurred_at": "2026-07-01T10:00:00",
            "source_moment_id": str(uuid4()),
        },
        {
            "event_id": str(uuid4()),
            "action_type": "EXPENSE_BURN",
            "title": "Payroll",
            "occurred_at": "2026-07-02T10:00:00",
            "source_moment_id": str(uuid4()),
        },
        {
            "event_id": str(uuid4()),
            "action_type": "FINANCIAL_UPDATE",
            "title": "Revenue forecast",
            "occurred_at": "2026-07-03T10:00:00",
            "source_moment_id": str(uuid4()),
        },
    ]
    ctx = _empty_ctx(
        runway_name="Acme Runway",
        activities=activities,
        activity_count=3,
        cash_available_minor=500_000_00,
        monthly_burn_setup_minor=100_000_00,
        runway_months=5.0,
    )
    moments = build_moments(ctx)
    for key in MOMENTS_SECTIONS:
        assert key in moments, f"missing moments section {key}"
        assert "state" in moments[key]

    assert len(moments["timeline"]["items"]) == 3
    assert moments["inflow_events"]["items"][0]["action_type"] == "CASH_INFLOW"
    assert moments["invoices"]["state"] == "empty"
    assert moments["payroll"]["state"] == "empty"


def test_runway_months_math_from_setup_cash():
    assert runway_months(600_000_00, 100_000_00) == 6.0
    assert runway_months(100_000_00, 0) is None


def test_rule_based_health_no_fabricated_scores():
    healthy = rule_based_runway_health(
        runway_months=12.0,
        risk_count=0,
        alert_threshold_months=6,
        cash_available_minor=1_000_000_00,
        monthly_burn_minor=50_000_00,
    )
    assert healthy["band"] == "healthy"

    critical = rule_based_runway_health(
        runway_months=0.5,
        risk_count=0,
        alert_threshold_months=6,
        cash_available_minor=50_000_00,
        monthly_burn_minor=100_000_00,
    )
    assert critical["band"] == "critical"


def test_signals_from_runway_counts():
    assert derive_signals(_empty_ctx()) == []
    signals = derive_signals(
        _empty_ctx(runway_months=2.0, risk_count=1, alert_threshold_months=6)
    )
    kinds = {s["signal_type"] for s in signals}
    assert "low_runway" in kinds
    assert "runway_risks" in kinds


def test_runway_life_slices_always_seven_keys():
    slices = build_runway_slices(
        moment_id=str(uuid4()),
        moment_name="Runway",
        activities=[],
        cash_available_minor=100_000_00,
        monthly_burn_minor=20_000_00,
        runway_months=5.0,
    )
    for key in RUNWAY_SLICES:
        assert key in slices


def test_memory_allowlist_includes_runway_actions():
    for action in ("CASH_INFLOW", "EXPENSE_BURN", "FINANCIAL_UPDATE", "RUNWAY_RISK"):
        assert action in MEMORY_ACTION_ALLOWLIST


def test_memory_maps_runway_funding_event():
    item = map_memory_event(
        {
            "event_id": str(uuid4()),
            "action_type": "CASH_INFLOW",
            "title": "Series A funding",
            "occurred_at": "2026-07-01",
        },
        moment_id=str(uuid4()),
        moment_name="Runway",
    )
    assert item is not None
    mem = map_memory([], events=[{**item, "source_moment_id": item["source_moment_id"]}])
    assert mem["buckets"]["funding"]["state"] == "complete"


def test_map_life_includes_runway_slice_keys():
    life = map_life([], runway_contributions=[{
        "slices": build_runway_slices(
            moment_id=str(uuid4()),
            moment_name="R",
            activities=[],
            cash_available_minor=1,
            monthly_burn_minor=1,
            runway_months=1.0,
        ),
    }])
    for key in RUNWAY_SLICES:
        assert key in life["slices"]
