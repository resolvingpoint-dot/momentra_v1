"""Business Run 7 — Action Center catalog + renderer metadata."""
from __future__ import annotations

from app.domains.business.action_catalog import (
    TEAM_OPERATIONS_CATALOG,
    RUNWAY_CATALOG,
    OPERATIONS_CATALOG,
    build_action_catalog_payload,
    build_renderer_metadata,
    catalog_for_moment_type,
    get_action_entry,
)


def test_catalog_counts_match_brief():
    assert len(TEAM_OPERATIONS_CATALOG) == 10
    assert len(RUNWAY_CATALOG) == 5
    assert len(OPERATIONS_CATALOG) == 6
    assert len(catalog_for_moment_type("TEAM_OPERATIONS")) == 10
    assert len(catalog_for_moment_type("BUSINESS_RUNWAY")) == 5
    assert len(catalog_for_moment_type("BUSINESS_OPERATIONS")) == 6


def test_catalog_payload_has_categories_and_renderer_ids():
    payload = build_action_catalog_payload(
        moment_id="00000000-0000-0000-0000-000000000001",
        moment_type="TEAM_OPERATIONS",
        members=[],
    )
    assert payload["template_id"] == "business.team_ops"
    assert payload["categories"]
    assert len(payload["actions"]) == 10
    assert all(a.get("renderer_id") for a in payload["actions"])
    labels = {a["label"] for a in payload["actions"]}
    assert "Team Update" in labels
    assert "Recognition" in labels
    assert "Note" in labels


def test_runway_and_ops_labels():
    runway = build_action_catalog_payload(
        moment_id="m", moment_type="BUSINESS_RUNWAY"
    )
    assert {a["label"] for a in runway["actions"]} >= {
        "Cash Inflow",
        "Burn Expense",
        "Runway Risk",
        "Financial Update",
        "Strategic Decision",
    }
    ops = build_action_catalog_payload(
        moment_id="m", moment_type="BUSINESS_OPERATIONS"
    )
    assert {a["label"] for a in ops["actions"]} >= {
        "Spend entry",
        "Vendor update",
        "Approval request",
        "Issue",
        "Operational improvement",
        "General update",
    }
    assert all(a.get("subtitle") for a in ops["actions"])
    approval = next(a for a in ops["actions"] if a["action_id"] == "ops_approval")
    assert approval["cta_label"] == "Send approval request"


def test_ops_approval_fields_include_approvers():
    meta = build_renderer_metadata("BUSINESS_OPERATIONS", "ops_approval")
    assert meta is not None
    keys = {f["key"] for f in meta["fields"]}
    assert "approver_ids" in keys
    assert "request_type" in keys
    assert "approver_ids" in meta["required_fields"]


def test_renderer_metadata_by_action_id_and_type():
    meta = build_renderer_metadata("TEAM_OPERATIONS", "recognition")
    assert meta is not None
    assert meta["renderer_id"] == "team_ops.recognition"
    assert meta["fields"]
    assert "title" in meta["required_fields"]

    meta2 = build_renderer_metadata("BUSINESS_RUNWAY", "CASH_INFLOW")
    assert meta2 is not None
    assert meta2["renderer_id"] == "runway.cash_inflow"
    assert any(f["key"] == "amount_minor" for f in meta2["fields"])


def test_unknown_action_returns_none():
    assert get_action_entry("TEAM_OPERATIONS", "NOT_A_THING") is None
    assert build_renderer_metadata("TEAM_OPERATIONS", "NOT_A_THING") is None
