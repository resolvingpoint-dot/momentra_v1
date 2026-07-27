"""Business Run 10 — Operations projection section trees, Life slices, Memory allowlist."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from app.domains.business.activity.handlers._helpers import minor_to_decimal
from app.domains.business.life.mapper import OPS_SLICES, build_ops_slices, map_life
from app.domains.business.memory.mapper import MEMORY_ACTION_ALLOWLIST, map_memory, map_memory_event
from app.domains.business.templates.business_operations.moments_mapper import build_moments
from app.domains.business.templates.business_operations.pulse_mapper import build_pulse
from app.domains.business.templates.business_operations.section_helpers import (
    rule_based_operations_health,
)
from app.domains.business.templates.business_operations.series_helpers import budget_usage_pct
from app.domains.business.templates.business_operations.projector import OpsProjectionBundle


PULSE_SECTIONS = (
    "hero",
    "operations_health",
    "kpis",
    "budget_usage",
    "approvals",
    "issues",
    "vendors",
    "improvements",
    "monitoring",
    "attention_items",
    "signals",
    "recent_activity",
    "next_best_action",
)

MOMENTS_SECTIONS = (
    "journey_hero",
    "summary_stats",
    "spend_timeline",
    "approval_timeline",
    "issue_timeline",
    "vendor_timeline",
    "improvement_timeline",
    "milestones",
    "key_decisions",
    "timeline",
    "recent_activity",
)


def _empty_ctx(**overrides):
    base = dict(
        moment_id=uuid4(),
        moment_type="BUSINESS_OPERATIONS",
        moment_name="",
        operations_name="",
        status="ACTIVE",
        is_active=True,
        activity_count=0,
        activities=[],
        operating_currency="INR",
        operations_scope=None,
        operating_model=None,
        owner_name=None,
        last_updated=None,
        monitoring_level=None,
        monthly_budget_minor=0,
        total_spend_minor=0,
        total_budget_minor=0,
        remaining_minor=0,
        budget_usage_pct=0.0,
        unallocated_minor=0,
        allocations=[],
        over_budget_allocations=[],
        vendor_count=0,
        critical_vendor_count=0,
        pending_approvals=0,
        overdue_approval_count=0,
        approved_recently=0,
        rejected_recently=0,
        amount_awaiting_minor=None,
        open_issue_count=0,
        critical_issue_count=0,
        overdue_issue_count=0,
        unassigned_issue_count=0,
        resolved_recently=0,
        improvement_count=0,
        planned_improvement_count=0,
        in_progress_improvement_count=0,
        completed_improvement_count=0,
        overdue_improvement_count=0,
        activated_at=None,
        projection=None,
        stage_timings_ms={},
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_sparse_pulse_always_has_deterministic_sections():
    pulse = build_pulse(_empty_ctx())
    for key in PULSE_SECTIONS:
        assert key in pulse, f"missing pulse section {key}"
        assert "state" in pulse[key]
    assert pulse["operations_health"]["band"] == "EMPTY"
    assert pulse["next_best_action"]["item"] is None


def test_sparse_moments_sections():
    moments = build_moments(_empty_ctx())
    for key in MOMENTS_SECTIONS:
        assert key in moments, f"missing moments section {key}"
        assert "state" in moments[key]


def test_spend_updates_budget_usage_math():
    assert budget_usage_pct(50_000_00, 100_000_00) == 50.0
    assert budget_usage_pct(120_000_00, 100_000_00) == 100.0


def test_pulse_reflects_spend_and_budget():
    ctx = _empty_ctx(
        monthly_budget_minor=100_000_00,
        total_budget_minor=100_000_00,
        total_spend_minor=40_000_00,
        remaining_minor=60_000_00,
        budget_usage_pct=40.0,
        operations_name="Ops A",
    )
    pulse = build_pulse(ctx)
    assert pulse["kpis"]["spent_minor"] == 40_000_00
    assert pulse["budget_usage"]["total_spend_minor"] == 40_000_00
    assert pulse["stats"]["budget_usage_percent"] == 40.0


def test_vendor_and_approval_and_issue_counts():
    ctx = _empty_ctx(
        vendor_count=2,
        pending_approvals=3,
        open_issue_count=1,
        critical_issue_count=1,
        monthly_budget_minor=10_000,
        total_spend_minor=1,
        budget_usage_pct=10.0,
        projection=OpsProjectionBundle(
            attention_items=[{"kind": "critical_issues", "label": "1 critical", "count": 1}],
            signal_items=[],
            recommended_action={
                "action_id": "issue_risk",
                "renderer_id": "ops.issue",
                "title": "Review issues",
                "subtitle": "1 open",
                "reason": "open_issues",
                "metadata": {},
            },
        ),
    )
    pulse = build_pulse(ctx)
    assert pulse["vendors"]["active"] == 2
    assert pulse["approvals"]["pending"] == 3
    assert pulse["issues"]["critical"] == 1
    assert pulse["next_best_action"]["item"]["renderer_id"] == "ops.issue"


def test_improvement_status_reflected():
    ctx = _empty_ctx(
        planned_improvement_count=1,
        in_progress_improvement_count=2,
        completed_improvement_count=3,
    )
    pulse = build_pulse(ctx)
    assert pulse["improvements"]["completed"] == 3
    assert pulse["improvements"]["in_progress"] == 2


def test_moments_timelines_split_by_action():
    mid = str(uuid4())
    activities = [
        {"event_id": str(uuid4()), "action_type": "SPEND_ENTRY", "title": "Rent", "occurred_at": "2026-07-01T10:00:00", "source_moment_id": mid},
        {"event_id": str(uuid4()), "action_type": "OPS_APPROVAL_REQUEST", "title": "Approve spend", "occurred_at": "2026-07-02T10:00:00", "source_moment_id": mid},
        {"event_id": str(uuid4()), "action_type": "ISSUE_RISK", "title": "Vendor delay", "occurred_at": "2026-07-03T10:00:00", "source_moment_id": mid},
        {"event_id": str(uuid4()), "action_type": "VENDOR_UPDATE", "title": "Vendor X", "occurred_at": "2026-07-04T10:00:00", "source_moment_id": mid},
        {"event_id": str(uuid4()), "action_type": "OPERATIONAL_IMPROVEMENT", "title": "Process", "occurred_at": "2026-07-05T10:00:00", "source_moment_id": mid},
    ]
    moments = build_moments(_empty_ctx(activities=activities, activity_count=5, is_active=True))
    assert len(moments["spend_timeline"]["items"]) == 1
    assert len(moments["approval_timeline"]["items"]) == 1
    assert len(moments["issue_timeline"]["items"]) == 1
    assert len(moments["vendor_timeline"]["items"]) == 1
    assert len(moments["improvement_timeline"]["items"]) == 1
    assert len(moments["timeline"]["items"]) == 5
    assert len(moments["recent_activity"]["items"]) <= 10
    assert moments["timeline"] is not moments["recent_activity"]


def test_rule_based_health_no_fabricated_scores():
    empty = rule_based_operations_health(
        monthly_budget_minor=0,
        spent_minor=0,
        budget_usage_percent=0,
        open_issue_count=0,
        critical_issue_count=0,
        pending_approval_count=0,
        overdue_approval_count=0,
    )
    assert empty["band"] == "EMPTY"
    assert "score" not in empty

    at_risk = rule_based_operations_health(
        monthly_budget_minor=100,
        spent_minor=100,
        budget_usage_percent=100,
        open_issue_count=0,
        critical_issue_count=0,
        pending_approval_count=0,
        overdue_approval_count=0,
    )
    assert at_risk["band"] == "AT_RISK"


def test_ops_life_slices_and_map_life():
    slices = build_ops_slices(
        moment_id=str(uuid4()),
        moment_name="Ops",
        activities=[],
        budget_usage_percent=55,
        open_issue_count=1,
        health_band="NEEDS_ATTENTION",
    )
    for key in OPS_SLICES:
        assert key in slices
    life = map_life([], ops_contributions=[{"moment_id": "x", "slices": slices}])
    assert "operational_health" in life["slices"]
    assert life["slices"]["budget_discipline"]["budget_usage_percent"] == 55


def test_memory_ops_allowlist_and_buckets():
    for action in (
        "SPEND_ENTRY",
        "VENDOR_UPDATE",
        "OPS_APPROVAL_REQUEST",
        "ISSUE_RISK",
        "OPERATIONAL_IMPROVEMENT",
    ):
        assert action in MEMORY_ACTION_ALLOWLIST

    mid = str(uuid4())
    events = [
        {
            "event_id": str(uuid4()),
            "action_type": "SPEND_ENTRY",
            "title": "Major spend",
            "occurred_at": "2026-07-01T00:00:00",
            "source_moment_id": mid,
        },
        {
            "event_id": str(uuid4()),
            "action_type": "ISSUE_RISK",
            "title": "Resolved issue",
            "occurred_at": "2026-07-02T00:00:00",
            "source_moment_id": mid,
            "payload": {"issue_status": "resolved"},
        },
        {
            "event_id": str(uuid4()),
            "action_type": "ISSUE_RISK",
            "title": "Open issue",
            "occurred_at": "2026-07-03T00:00:00",
            "source_moment_id": mid,
            "payload": {"issue_status": "open"},
        },
    ]
    open_item = map_memory_event(events[2], moment_id=mid, moment_name="Ops")
    assert open_item is None
    resolved = map_memory_event(events[1], moment_id=mid, moment_name="Ops")
    assert resolved is not None

    moment = SimpleNamespace(moment_id=mid, moment_type="BUSINESS_OPERATIONS", moment_name="Ops", status="active")
    # coerce uuid for map_memory
    moment.moment_id = type("U", (), {"__str__": lambda self: mid})()
    # simpler: use real uuid object
    from uuid import UUID

    moment.moment_id = UUID(mid)
    mem = map_memory([moment], events=events)
    assert "major_spend" in mem["buckets"]
    assert mem["buckets"]["major_spend"]["state"] == "complete"
    assert mem["buckets"]["resolved_issues"]["state"] == "complete"


def test_jpy_kwd_minor_helpers():
    assert minor_to_decimal(1000, currency="JPY") == 1000
    assert float(minor_to_decimal(1000, currency="KWD")) == 1.0


def test_coexistence_keys_with_team_and_runway_actions():
    """Ops memory allowlist does not remove Team/Runway actions."""
    assert "APPROVAL_REQUEST" in MEMORY_ACTION_ALLOWLIST
    assert "CASH_INFLOW" in MEMORY_ACTION_ALLOWLIST
    assert "SPEND_ENTRY" in MEMORY_ACTION_ALLOWLIST
