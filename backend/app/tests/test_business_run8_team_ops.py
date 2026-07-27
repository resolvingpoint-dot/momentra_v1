"""Business Run 8.1 — Team Ops projection section trees, Life slices, Memory allowlist."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domains.business.life.mapper import ALL_LIFE_SLICES, TEAM_OPS_SLICES, build_team_ops_slices, map_life
from app.domains.business.memory.mapper import MEMORY_ACTION_ALLOWLIST, map_memory, map_memory_event
from app.domains.business.templates.team_operations.moments_mapper import build_moments
from app.domains.business.templates.team_operations.pulse_mapper import build_pulse
from app.domains.business.templates.team_operations.section_helpers import rule_based_team_health
from app.domains.business.templates.team_operations.signals import derive_signals


PULSE_SECTIONS = (
    "hero",
    "health_drivers",
    "kpis",
    "approvals",
    "participation",
    "issues",
    "recognition",
    "recent_activity",
    "attention",
    "signals",
    "next_action",
)

MOMENTS_SECTIONS = (
    "journey_hero",
    "progress_snapshot",
    "highlights",
    "milestones",
    "meetings",
    "approvals",
    "recognition",
    "issues",
    "team_changes",
    "timeline",
    "recent_activity",
)


def _empty_ctx(**overrides):
    base = dict(
        moment_id=uuid4(),
        moment_type="TEAM_OPERATIONS",
        moment_name="",
        team_name="",
        status="ACTIVE",
        is_active=True,
        member_count=0,
        activity_count=0,
        activities=[],
        operating_currency="INR",
        open_issues=0,
        pending_approvals=0,
        recognition_count=0,
        meeting_count=0,
        escalation_count=0,
        participation_count=0,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_pulse_always_has_deterministic_sections():
    pulse = build_pulse(_empty_ctx())
    for key in PULSE_SECTIONS:
        assert key in pulse, f"missing pulse section {key}"
        assert "state" in pulse[key]
    assert pulse["stats"]["open_issues"] == 0
    assert pulse["recent_activity"]["state"] == "empty"
    assert pulse["recent_activity"]["items"] == []
    assert pulse["hero"]["overall_team_health"]["band"] == "empty"


def test_moments_sections_distinct_from_pulse_recent():
    mid = str(uuid4())
    activities = [
        {
            "event_id": str(uuid4()),
            "action_type": "MEETING",
            "title": "Sync",
            "occurred_at": "2026-07-01T10:00:00",
            "source_moment_id": mid,
        },
        {
            "event_id": str(uuid4()),
            "action_type": "ISSUE",
            "title": "Risk",
            "occurred_at": "2026-07-02T10:00:00",
            "source_moment_id": mid,
        },
        {
            "event_id": str(uuid4()),
            "action_type": "TEAM_UPDATE",
            "title": "Update",
            "occurred_at": "2026-07-03T10:00:00",
            "source_moment_id": mid,
        },
    ]
    ctx = _empty_ctx(
        moment_name="Alpha",
        team_name="Alpha",
        activities=activities,
        activity_count=3,
        meeting_count=1,
        open_issues=1,
    )
    moments = build_moments(ctx)
    for key in MOMENTS_SECTIONS:
        assert key in moments, f"missing moments section {key}"
        assert "state" in moments[key]

    # Timeline includes all; recent_activity is a shorter window — same source, separate keys
    assert len(moments["timeline"]["items"]) == 3
    assert len(moments["recent_activity"]["items"]) == 3
    assert moments["timeline"] is not moments["recent_activity"]
    assert moments["meetings"]["items"][0]["action_type"] == "MEETING"
    assert moments["issues"]["items"][0]["action_type"] == "ISSUE"
    assert moments["team_changes"]["items"][0]["action_type"] == "TEAM_UPDATE"


def test_rule_based_health_no_weighted_engine():
    healthy = rule_based_team_health(
        member_count=5, open_issues=0, pending_approvals=0, escalation_count=0
    )
    assert healthy["band"] == "healthy"
    assert "inputs" in healthy

    attention = rule_based_team_health(
        member_count=5, open_issues=2, pending_approvals=0, escalation_count=0
    )
    assert attention["band"] == "needs_attention"

    risk = rule_based_team_health(
        member_count=5, open_issues=0, pending_approvals=0, escalation_count=1
    )
    assert risk["band"] == "at_risk"


def test_signals_from_counts():
    assert derive_signals(_empty_ctx()) == []
    signals = derive_signals(_empty_ctx(open_issues=2, pending_approvals=1, escalation_count=1))
    kinds = {s["signal_type"] for s in signals}
    assert kinds == {"open_issues", "pending_approvals", "escalations"}


def test_create_activity_shapes_pulse_and_moments():
    activities = [
        {
            "event_id": str(uuid4()),
            "action_type": "APPROVAL_REQUEST",
            "title": "Budget",
            "occurred_at": "2026-07-01",
        },
        {
            "event_id": str(uuid4()),
            "action_type": "RECOGNITION",
            "title": "Shoutout",
            "occurred_at": "2026-07-02",
        },
    ]
    pulse = build_pulse(
        _empty_ctx(
            team_name="Ops",
            moment_name="Ops",
            member_count=3,
            pending_approvals=1,
            recognition_count=1,
            activities=activities,
            activity_count=2,
        )
    )
    assert pulse["approvals"]["pending_count"] == 1
    assert pulse["approvals"]["items"][0]["title"] == "Budget"
    assert pulse["recognition"]["count"] == 1
    assert pulse["next_action"]["item"]["action_id"] == "approval"

    moments = build_moments(
        _empty_ctx(
            team_name="Ops",
            pending_approvals=1,
            recognition_count=1,
            activities=activities,
            activity_count=2,
        )
    )
    assert moments["approvals"]["items"]
    assert moments["recognition"]["items"]


def test_life_slices_always_present():
    slices = build_team_ops_slices(
        moment_id=str(uuid4()),
        moment_name="Team",
        activities=[],
    )
    assert set(slices.keys()) == set(TEAM_OPS_SLICES)
    for key in TEAM_OPS_SLICES:
        assert slices[key]["state"] == "empty"

    filled = build_team_ops_slices(
        moment_id=str(uuid4()),
        moment_name="Team",
        activities=[
            {"event_id": "1", "action_type": "ISSUE", "title": "Bug", "occurred_at": "t"},
            {"event_id": "2", "action_type": "RECOGNITION", "title": "Nice", "occurred_at": "t"},
        ],
        open_issues=1,
        member_count=2,
    )
    assert filled["issues"]["count"] >= 1
    assert filled["recognition"]["count"] == 1
    assert filled["team_health"]["band"] in {"needs_attention", "at_risk", "healthy"}

    life = map_life([], team_ops_contributions=[{"moment_id": "x", "slices": filled}])
    assert set(life["slices"].keys()) == set(ALL_LIFE_SLICES)
    for key in TEAM_OPS_SLICES:
        assert life["slices"][key]["count"] >= filled[key]["count"] or filled[key]["count"] == 0


def test_memory_allowlist_only_no_narrative():
    assert "NOTE" not in MEMORY_ACTION_ALLOWLIST
    assert map_memory_event(
        {"action_type": "NOTE", "title": "secret"}, moment_id="m", moment_name="T"
    ) is None
    assert map_memory_event(
        {"action_type": "RECOGNITION", "event_id": "1", "title": "Win", "occurred_at": "t"},
        moment_id="m",
        moment_name="T",
    )["action_type"] == "RECOGNITION"
    # Open issues excluded from memory
    assert map_memory_event(
        {"action_type": "ISSUE", "resolution_status": "open", "title": "Open"},
        moment_id="m",
        moment_name="T",
    ) is None
    # Missing resolution defaults to open → excluded
    assert map_memory_event(
        {"action_type": "ISSUE", "title": "No status"},
        moment_id="m",
        moment_name="T",
    ) is None
    # Resolved issues allowed
    assert map_memory_event(
        {
            "action_type": "ISSUE",
            "resolution_status": "resolved",
            "event_id": "3",
            "title": "Fixed",
            "occurred_at": "t",
        },
        moment_id="m",
        moment_name="T",
    ) is not None

    mem = map_memory([], events=[
        {
            "event_id": "1",
            "action_type": "MEETING",
            "title": "Retro",
            "occurred_at": "t",
            "source_moment_id": "m",
        },
        {
            "event_id": "2",
            "action_type": "PARTICIPATION",
            "title": "Check-in",
            "occurred_at": "t",
            "source_moment_id": "m",
        },
    ])
    assert len(mem["events"]) == 1
    assert mem["buckets"]["meetings"]["items"]
    assert "narrative" not in mem
    assert "ai_recap" not in mem
    # Factual summary only — no composite strength score
    assert "summary" in mem
    assert "score" not in (mem.get("summary") or {})
    assert mem["summary"]["event_count"] == 1
    assert mem["playbooks"] == []


def test_life_enrichment_band_only_no_score():
    from app.domains.business.life.signals import (
        aggregate_life_band,
        build_life_dimensions,
        build_life_journey,
        derive_life_signals,
    )

    slices = {
        "team_health": {
            "key": "team_health",
            "band": "needs_attention",
            "count": 2,
            "state": "partial",
            "inputs": {"open_issues": 2, "pending_approvals": 1},
            "items": [
                {
                    "event_id": "e1",
                    "action_type": "MEETING",
                    "title": "Standup",
                    "occurred_at": "2024-01-10T10:00:00Z",
                },
            ],
        },
        "financial_health": {"key": "financial_health", "band": "empty", "count": 0, "state": "empty", "items": []},
        "operational_health": {"key": "operational_health", "band": "healthy", "count": 1, "state": "complete", "items": []},
        "issues": {"key": "issues", "band": "needs_attention", "count": 3, "state": "partial", "items": []},
    }
    dims = build_life_dimensions(slices)
    assert any(d["key"] == "team_health" and d["band"] == "needs_attention" for d in dims)
    health = aggregate_life_band(dims)
    assert "score" not in health
    assert health["band"] in {"needs_attention", "at_risk", "healthy", "empty", "critical"}
    assert health["label"]
    journey = build_life_journey(slices)
    assert any(j["kind"] == "MEETING" for j in journey)
    assert any(j["kind"] == "FIRST_ACTIVITY" for j in journey)
    signals = derive_life_signals([], slices=slices)
    assert any(s["signal_type"] == "team_attention" for s in signals)
    assert any(s["signal_type"] == "issue_load" for s in signals)

    life = map_life([], team_ops_contributions=[{"moment_id": "x", "slices": slices}])
    assert "health" in life
    assert "score" not in life["health"]
    assert "dimensions" in life
    assert "journey" in life
    assert "signals" in life
    assert "ai_recap" not in life


def test_memory_summary_filters_patterns_evidence_only():
    from app.domains.business.memory.patterns import (
        build_memory_source_filters,
        build_memory_summary,
        derive_memory_patterns,
        derive_success_and_risk_memory,
    )

    moments = [
        SimpleNamespace(moment_id="a", moment_type="TEAM_OPERATIONS", moment_name="Team", status="active", created_at=None),
        SimpleNamespace(moment_id="b", moment_type="BUSINESS_RUNWAY", moment_name="Runway", status="active", created_at=None),
        SimpleNamespace(moment_id="c", moment_type="BUSINESS_OPERATIONS", moment_name="Ops", status="active", created_at=None),
    ]
    events = [
        {"event_id": "1", "action_type": "MEETING", "occurred_at": "2024-01-01T00:00:00Z", "source_moment_type": "TEAM_OPERATIONS"},
        {"event_id": "2", "action_type": "MEETING", "occurred_at": "2024-02-01T00:00:00Z", "source_moment_type": "TEAM_OPERATIONS"},
        {"event_id": "3", "action_type": "MEETING", "occurred_at": "2024-03-01T00:00:00Z", "source_moment_type": "TEAM_OPERATIONS"},
        {"event_id": "4", "action_type": "RECOGNITION", "occurred_at": "2024-03-02T00:00:00Z", "source_moment_type": "TEAM_OPERATIONS"},
        {"event_id": "5", "action_type": "RECOGNITION", "occurred_at": "2024-03-03T00:00:00Z", "source_moment_type": "TEAM_OPERATIONS"},
        {"event_id": "6", "action_type": "RUNWAY_RISK", "occurred_at": "2024-03-04T00:00:00Z", "source_moment_type": "BUSINESS_RUNWAY"},
    ]
    summary = build_memory_summary(moments, events)
    assert summary["active_moment_count"] == 3
    assert summary["event_count"] == 6
    assert summary["months_active"] >= 1
    assert "score" not in summary
    assert "confidence" not in summary

    filters = build_memory_source_filters(moments)
    keys = {f["key"] for f in filters}
    assert keys == {"all", "team", "runway", "ops"}

    patterns = derive_memory_patterns(moments, events=events)
    assert any(p.get("pattern_type") == "meeting_cadence" for p in patterns)
    success, risk = derive_success_and_risk_memory(events)
    assert any(s["kind"] == "recognition_momentum" for s in success)
    assert any(r["kind"] == "runway_risk" for r in risk)

    mem = map_memory(moments, events=events)
    assert mem["summary"]["event_count"] == 6
    assert len(mem["source_filters"]) == 4
    assert mem["patterns"]
    assert mem["success_memory"]
    assert mem["risk_memory"]
    assert mem["journey"]
    assert mem["playbooks"] == []
    assert "ai_recap" not in mem
    assert "strength_score" not in mem


def test_invalidate_helper_importable():
    from app.domains.business.projection_cache import (
        MOMENT_SLICES,
        USER_AGG_SLICES,
        USER_AGG_TEMPLATE,
        invalidate_business_projections,
    )

    assert callable(invalidate_business_projections)
    assert MOMENT_SLICES == ("pulse", "moments", "quick_add")
    assert USER_AGG_SLICES == ("life", "memory")
    assert USER_AGG_TEMPLATE == "BUSINESS_USER"


def test_no_fabricated_health_scores_or_nba_copy():
    pulse = build_pulse(_empty_ctx(member_count=3, open_issues=0, pending_approvals=0))
    health = pulse["hero"]["overall_team_health"]
    assert "score" not in health
    assert "composite" not in health
    assert health["band"] == "healthy"
    assert health["rule"] == "escalations_or_issues_thresholds"
    # next_action is rule-based recommendation from counts — not marketing copy engine
    nxt = pulse["next_action"]["item"]
    assert nxt is None or {"action_id", "label", "reason"} <= set(nxt.keys())


def test_sparse_pulse_mapper_no_fake_stats_compat():
    """Run 6 compatibility: zeros stay honest."""
    pulse = build_pulse(_empty_ctx())
    assert pulse["stats"]["open_issues"] == 0
    assert pulse["member_count"] == 0
    assert pulse["kpis"]["open_issues"] == 0


def test_pulse_enriched_when_projection_present():
    from decimal import Decimal

    from app.domains.business.templates.team_operations.projector import TeamOpsProjectionBundle

    bundle = TeamOpsProjectionBundle(
        health_score=Decimal("82"),
        health_label="On track",
        health_band="healthy",
        health_drivers=[
            {
                "driver_code": "participation",
                "driver_name": "Participation",
                "score": 88.0,
                "status": "excellent",
                "delta": 12.0,
                "trend": "up",
                "weight": 25.0,
            }
        ],
        attention_items=[
            {
                "attention_type": "pending_approvals",
                "severity": "high",
                "title": "2 pending approvals",
                "description": "Needs review",
                "kind": "pending_approvals",
                "count": 2,
            }
        ],
        signal_items=[
            {
                "signal_type": "approval_request",
                "title": "Approval requests increasing",
                "summary": "2 in last 7 days vs 1 prior week",
                "change_percent": 100.0,
                "impact_level": "medium",
            }
        ],
        recommended_action={
            "action_id": "approval",
            "label": "Review 2 pending approvals",
            "reason": "pending_approvals",
            "cta_label": "Take Action",
            "target_screen": "action_center",
            "priority": "high",
        },
        progress_snapshots=[
            {
                "metric_code": "participation",
                "metric_name": "Participation",
                "score": 88.0,
                "delta": 12.0,
                "status": "excellent",
                "trend": "up",
            }
        ],
        highlights=[],
    )
    ctx = _empty_ctx(member_count=5, pending_approvals=2, projection=bundle)
    pulse = build_pulse(ctx)
    assert pulse["hero"]["overall_team_health"]["score"] == 82.0
    assert pulse["health_drivers"]["items"][0]["driver_code"] == "participation"
    assert pulse["attention"]["items"][0]["severity"] == "high"
    assert pulse["signals"]["items"][0]["change_percent"] == 100.0
    assert pulse["next_action"]["item"]["cta_label"] == "Take Action"

    moments = build_moments(ctx)
    assert moments["progress_snapshot"]["items"][0]["metric_code"] == "participation"
    assert "highlights" in moments
