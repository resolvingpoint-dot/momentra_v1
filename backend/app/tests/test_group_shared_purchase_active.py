"""Tests for Shared Purchase ACTIVE backend."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create_and_activate_purchase(client: TestClient) -> str:
    created = client.post(
        "/api/v1/group/shared-purchase/moments",
        json={"purchase_profile": "GIFT_POOL"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]
    draft = client.put(
        f"/api/v1/group/shared-purchase/moments/{moment_id}/setup/draft",
        json={"purchase_profile": "GIFT_POOL", "moment_name": "Birthday Gift", "target_amount_major": 5000},
        headers=AUTH,
    )
    assert draft.status_code == 200, draft.text
    activate = client.post(
        f"/api/v1/group/shared-purchase/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["lifecycle_status"] == "active"
    return moment_id


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_active_projections_after_activate(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_purchase(client)

    pulse = client.get(f"/api/v1/group/shared-purchase/moments/{moment_id}/pulse", headers=AUTH)
    assert pulse.status_code == 200, pulse.text
    body = pulse.json()
    assert body["moment_name"] == "Birthday Gift"
    assert "contributors_joined" in body["stats"]

    active_pulse = client.get(f"/api/v1/group/active/pulse/{moment_id}", headers=AUTH)
    assert active_pulse.status_code == 200, active_pulse.text
    assert active_pulse.json()["moment_type"] == "SHARED_PURCHASE"

    moments = client.get(f"/api/v1/group/active/moments/{moment_id}", headers=AUTH)
    assert moments.status_code == 200, moments.text
    assert moments.json()["moment_type"] == "SHARED_PURCHASE"

    memory = client.get(f"/api/v1/group/active/memory/{moment_id}", headers=AUTH)
    assert memory.status_code == 200, memory.text

    life = client.get("/api/v1/group/active/life", headers=AUTH)
    assert life.status_code == 200, life.text
    assert life.json().get("active_moment_count", 0) >= 1


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_expense_context_includes_creator_after_activate(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_purchase(client)

    ctx = client.get(
        f"/api/v1/group/shared-purchase/moments/{moment_id}/quick-add/expenses/context",
        headers=AUTH,
    )
    assert ctx.status_code == 200, ctx.text
    data = ctx.json()
    payers = data.get("payers") or []
    members = data.get("members") or data.get("participants") or []
    assert payers or members, "creator must appear in purchase expense context after activate"
    uid = str(sample_user.id)
    roster = payers or members
    assert any(str(p.get("id") or p.get("user_id") or "") == uid for p in roster)
    assert data.get("default_paid_by_participant_id") == uid


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_contribution_persists(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_purchase(client)

    created = client.post(
        f"/api/v1/group/shared-purchase/moments/{moment_id}/quick-add/updates",
        json={"body": "Funding started", "title": "Update"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    assert created.json().get("id")

    pulse = client.get(f"/api/v1/group/shared-purchase/moments/{moment_id}/pulse", headers=AUTH)
    assert pulse.status_code == 200


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_vendor_quick_add(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_purchase(client)

    created = client.post(
        f"/api/v1/group/shared-purchase/moments/{moment_id}/quick-add/vendors",
        json={"vendor_name": "Best Buy"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    pulse = client.get(f"/api/v1/group/shared-purchase/moments/{moment_id}/pulse", headers=AUTH)
    assert pulse.status_code == 200
    assert pulse.json()["stats"]["vendors"] >= 1


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_quick_add_config(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_purchase(client)

    cfg = client.get(f"/api/v1/group/quickadd/{moment_id}", headers=AUTH)
    assert cfg.status_code == 200, cfg.text
    assert cfg.json()["moment_type"] == "SHARED_PURCHASE"
    assert len(cfg.json().get("categories") or []) > 0


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_pulse_enriched_with_runtime(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_purchase(client)

    from app.domains.group import moment_store as store

    moment = mock_db._get_from_store("moments", moment_id)
    store.append_item(
        moment,
        "guests",
        {"id": "g1", "full_name": "Priya", "status": "active", "assigned_role": "Primary Owner", "created_at": store.now_iso()},
    )
    store.append_item(
        moment,
        "contributions",
        {"id": "c1", "title": "Seed", "amount_minor": 150000, "created_at": store.now_iso()},
    )
    store.append_item(moment, "vendors", {"id": "v1", "vendor_name": "Best Buy", "status": "evaluating"})
    store.append_activity(
        moment,
        {"id": "a1", "title": "Contribution logged", "activity_type": "contribution", "occurred_at": store.now_iso()},
    )

    pulse = client.get(f"/api/v1/group/shared-purchase/moments/{moment_id}/pulse", headers=AUTH)
    assert pulse.status_code == 200, pulse.text
    body = pulse.json()
    assert body["contributor_count"] >= 1
    assert body["funded_amount_minor"] >= 150000
    assert body["health_dimensions"]
    assert body["attention_items"] is not None
    assert body["next_best_action"]
    assert body["metric_tiles"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_moments_operations_hub(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_purchase(client)

    from app.domains.group import moment_store as store

    moment = mock_db._get_from_store("moments", moment_id)
    store.append_item(moment, "guests", {"id": "g1", "full_name": "Sarah", "status": "active", "assigned_role": "Owner"})
    store.append_item(moment, "contributions", {"id": "c1", "amount_minor": 200000})
    store.append_item(moment, "vendors", {"id": "v1", "vendor_name": "Apple"})
    store.append_item(moment, "decisions", {"id": "d1", "title": "Vendor Selection", "status": "open"})
    store.append_item(moment, "memories", {"id": "m1", "title": "Unboxing day"})

    resp = client.get(f"/api/v1/group/shared-purchase/moments/{moment_id}/moments-view", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    hub = data["operations_hub"]
    assert hub["core_summary"]["moment_name"] == "Birthday Gift"
    assert hub["core_summary"]["stat_tiles"]
    assert hub["money_status"]["columns"]
    assert hub["activity_ops"]
    assert hub["assets"]
    mem = data["memory_hub"]
    assert mem["hero"]["moment_name"] == "Birthday Gift"
    assert mem["timeline"] or mem["milestone_wall"] or mem["gallery"] is not None


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_pulse_settlement_widget_and_trip_context(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    from app.domains.group import moment_store as store

    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_purchase(client)
    moment = mock_db._get_from_store("moments", moment_id)
    state = store.read_state(moment)
    member_a = store.new_id()
    member_b = store.new_id()
    state["runtime"]["guests"] = [
        {"id": member_a, "full_name": "Alice", "status": "confirmed"},
        {"id": member_b, "full_name": "Bob", "status": "confirmed"},
    ]
    state["runtime"]["expenses"] = [
        {
            "id": store.new_id(),
            "description": "Gift item",
            "amount_minor": 10000,
            "currency_code": "INR",
            "paid_by_user_id": member_a,
            "participant_ids": [member_a, member_b],
            "split_type": "equal",
            "created_at": store.now_iso(),
            "deleted": False,
        }
    ]
    store.write_state(moment, state)

    pulse = client.get(
        f"/api/v1/group/shared-purchase/moments/{moment_id}/pulse?force_refresh=true",
        headers=AUTH,
    )
    assert pulse.status_code == 200, pulse.text
    body = pulse.json()
    widget = body.get("settlement_widget") or {}
    assert widget.get("total_paid_minor", 0) > 0
    assert widget.get("members_needing_settlement", 0) >= 1
    assert body.get("settlement_preview", {}).get("pending_count", 0) >= 1

    ctx = client.get(f"/api/v1/group/trips/{moment_id}/settlements/context", headers=AUTH)
    assert ctx.status_code == 200, ctx.text
    assert ctx.json()["pending_balances"]
