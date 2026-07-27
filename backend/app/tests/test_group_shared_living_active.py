"""Tests for Shared Living ACTIVE backend."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create_and_activate_living(client: TestClient) -> str:
    created = client.post(
        "/api/v1/group/shared-living/moments",
        json={"living_type": "FLATMATES"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]
    draft = client.put(
        f"/api/v1/group/shared-living/moments/{moment_id}/setup/draft",
        json={"living_type": "FLATMATES", "living_name": "Indiranagar Flat"},
        headers=AUTH,
    )
    assert draft.status_code == 200, draft.text
    activate = client.post(
        f"/api/v1/group/shared-living/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["lifecycle_status"] == "active"
    return moment_id


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_active_projections_after_activate(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    pulse = client.get(f"/api/v1/group/shared-living/moments/{moment_id}/pulse", headers=AUTH)
    assert pulse.status_code == 200, pulse.text
    body = pulse.json()
    assert body["moment_name"] == "Indiranagar Flat"
    assert "residents_joined" in body["stats"]

    active_pulse = client.get(f"/api/v1/group/active/pulse/{moment_id}", headers=AUTH)
    assert active_pulse.status_code == 200, active_pulse.text
    assert active_pulse.json()["moment_type"] == "SHARED_LIVING"

    moments = client.get(f"/api/v1/group/active/moments/{moment_id}", headers=AUTH)
    assert moments.status_code == 200, moments.text
    assert moments.json()["moment_type"] == "SHARED_LIVING"

    memory = client.get(f"/api/v1/group/active/memory/{moment_id}", headers=AUTH)
    assert memory.status_code == 200, memory.text

    life = client.get("/api/v1/group/active/life", headers=AUTH)
    assert life.status_code == 200, life.text
    assert life.json().get("active_moment_count", 0) >= 1


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_resident_persists(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    created = client.post(
        f"/api/v1/group/shared-living/moments/{moment_id}/quick-add/residents",
        json={"full_name": "Alex", "relationship_type": "roommate", "status": "active"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    assert created.json().get("id")

    pulse = client.get(f"/api/v1/group/shared-living/moments/{moment_id}/pulse", headers=AUTH)
    assert pulse.status_code == 200
    assert pulse.json()["stats"]["residents_joined"] >= 1
    assert pulse.json()["resident_count"] >= 1


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_resident_invite_status_preserved(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    created = client.post(
        f"/api/v1/group/shared-living/moments/{moment_id}/quick-add/residents",
        json={"full_name": "Invited Sam", "relationship_type": "roommate", "status": "invited"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    resident_id = created.json().get("id")
    assert resident_id

    ctx = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/quick-add/residents/context",
        headers=AUTH,
    )
    assert ctx.status_code == 200, ctx.text
    guests = ctx.json().get("guests") or []
    match = next((g for g in guests if str(g.get("id") or "") == str(resident_id)), None)
    if match is None:
        match = next((g for g in guests if "Invited Sam" in str(g.get("full_name") or g.get("name") or "")), None)
    assert match is not None, f"resident not found in context guests: {ctx.json()}"
    assert str(match.get("status") or "").lower() == "invited"


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_expense_context_includes_creator_after_activate(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    ctx = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/quick-add/expenses/context",
        headers=AUTH,
    )
    assert ctx.status_code == 200, ctx.text
    data = ctx.json()
    payers = data.get("payers") or []
    members = data.get("members") or data.get("participants") or []
    assert payers or members, "creator must appear in living expense context after activate"
    uid = str(sample_user.id)
    roster = payers or members
    assert any(str(p.get("id") or p.get("user_id") or "") == uid for p in roster)
    assert data.get("default_paid_by_participant_id") == uid


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_expense_quick_add(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    created = client.post(
        f"/api/v1/group/shared-living/moments/{moment_id}/quick-add/expenses",
        json={"description": "Rent", "amount_major": "12000", "currency_code": "INR", "split_type": "equal"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    pulse = client.get(f"/api/v1/group/shared-living/moments/{moment_id}/pulse", headers=AUTH)
    assert pulse.status_code == 200
    assert pulse.json()["stats"]["total_expenses_minor"] == 1200000


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_quick_add_config(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    cfg = client.get(f"/api/v1/group/quickadd/{moment_id}", headers=AUTH)
    assert cfg.status_code == 200, cfg.text
    assert cfg.json()["moment_type"] == "SHARED_LIVING"
    assert len(cfg.json().get("categories") or []) > 0


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_pulse_enriched_with_runtime(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    from app.domains.group import moment_store as store

    moment = mock_db._get_from_store("moments", moment_id)
    store.append_item(
        moment,
        "guests",
        {"id": "r1", "full_name": "Alex", "status": "active", "assigned_role": "Owner", "created_at": store.now_iso()},
    )
    store.append_item(
        moment,
        "expenses",
        {"id": "e1", "description": "Rent", "amount_minor": 1200000, "created_at": store.now_iso()},
    )
    store.append_item(
        moment,
        "tasks",
        {"id": "t1", "title": "Clean kitchen", "status": "open", "created_at": store.now_iso()},
    )
    store.append_activity(
        moment,
        {"id": "a1", "title": "Expense logged", "activity_type": "expense", "occurred_at": store.now_iso()},
    )

    pulse = client.get(f"/api/v1/group/shared-living/moments/{moment_id}/pulse", headers=AUTH)
    assert pulse.status_code == 200, pulse.text
    body = pulse.json()
    assert body["resident_count"] >= 1
    assert body["expenses_total_minor"] >= 1200000
    assert body["health_dimensions"]
    assert body["attention_items"] is not None
    assert body["next_best_action"]
    assert body["metric_tiles"]
    assert body["recent_activity"] is not None


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_moments_operations_hub(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    from app.domains.group import moment_store as store

    moment = mock_db._get_from_store("moments", moment_id)
    store.append_item(moment, "guests", {"id": "r1", "full_name": "Sam", "status": "active", "assigned_role": "Owner"})
    store.append_item(moment, "expenses", {"id": "e1", "description": "Utilities", "amount_minor": 50000})
    store.append_item(moment, "contributions", {"id": "c1", "title": "Share", "amount_minor": 25000})
    store.append_item(moment, "tasks", {"id": "t1", "title": "Trash", "status": "open"})
    store.append_item(moment, "polls", {"id": "p1", "question": "New Wi-Fi plan?", "status": "open"})
    store.append_item(moment, "memories", {"id": "m1", "title": "Housewarming"})

    resp = client.get(f"/api/v1/group/shared-living/moments/{moment_id}/moments-view", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    hub = data["operations_hub"]
    assert hub["core_summary"]["moment_name"] == "Indiranagar Flat"
    assert hub["core_summary"]["stat_tiles"]
    assert hub["money_status"]["columns"]
    assert hub["activity_ops"]
    assert hub["assets"]
    mem = data["memory_hub"]
    assert mem["hero"]["moment_name"] == "Indiranagar Flat"
    assert mem["timeline"] or mem["milestone_wall"] or mem["gallery"] is not None


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_activity_list_patch_delete(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    created = client.post(
        f"/api/v1/group/shared-living/moments/{moment_id}/quick-add/updates",
        json={"body": "Wi-Fi is down", "title": "Wi-Fi is down"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text

    listed = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/activity",
        headers=AUTH,
    )
    assert listed.status_code == 200, listed.text
    items = listed.json().get("items") or []
    assert len(items) >= 1
    event = next((i for i in items if "Wi-Fi" in str(i.get("title") or "")), items[0])
    event_id = event["id"]
    assert event.get("can_edit") is True
    assert event.get("can_delete") is True

    detail = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/activity/{event_id}",
        headers=AUTH,
    )
    assert detail.status_code == 200, detail.text
    assert detail.json()["id"] == event_id

    patched = client.patch(
        f"/api/v1/group/shared-living/moments/{moment_id}/activity/{event_id}",
        json={"title": "Wi-Fi restored", "subtitle": "Fixed tonight"},
        headers=AUTH,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["title"] == "Wi-Fi restored"
    assert patched.json()["subtitle"] == "Fixed tonight"

    listed2 = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/activity",
        headers=AUTH,
    )
    assert any(i.get("id") == event_id and i.get("title") == "Wi-Fi restored" for i in listed2.json()["items"])

    deleted = client.delete(
        f"/api/v1/group/shared-living/moments/{moment_id}/activity/{event_id}",
        headers=AUTH,
    )
    assert deleted.status_code == 200, deleted.text
    assert deleted.json().get("status") == "deleted"

    listed3 = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/activity",
        headers=AUTH,
    )
    assert all(i.get("id") != event_id for i in listed3.json().get("items") or [])


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_pulse_recent_activity_ids_are_fetchable(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Pulse recent_activity ids must resolve via GET /activity/{id} (no ephemeral ids)."""
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    created = client.post(
        f"/api/v1/group/shared-living/moments/{moment_id}/quick-add/polls",
        json={"question": "fuck off", "title": "fuck off"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    poll_id = created.json().get("id")

    pulse = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/pulse",
        headers=AUTH,
    )
    assert pulse.status_code == 200, pulse.text
    recent = pulse.json().get("recent_activity") or []
    assert recent, "expected recent_activity after creating a poll"
    event_id = recent[0]["id"]
    assert event_id, "recent_activity items must expose a persisted id"
    assert event_id != "None"

    detail = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/activity/{event_id}",
        headers=AUTH,
    )
    assert detail.status_code == 200, detail.text
    assert detail.json()["id"] == event_id

    if poll_id:
        by_ref = client.get(
            f"/api/v1/group/shared-living/moments/{moment_id}/activity/{poll_id}",
            headers=AUTH,
        )
        assert by_ref.status_code == 200, by_ref.text


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_activity_backfills_missing_ids(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Legacy timeline rows without id must be backfilled and become editable."""
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_living(client)

    from app.domains.group import moment_store as store

    moment = mock_db._get_from_store("moments", moment_id)
    store.append_activity(
        moment,
        {
            "activity_type": "POLL",
            "ref_id": "poll-legacy",
            "title": "legacy poll",
            "subtitle": "Poll",
            "icon": "poll",
            "occurred_at": store.now_iso(),
            "deleted": False,
        },
    )

    pulse = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/pulse",
        headers=AUTH,
    )
    assert pulse.status_code == 200, pulse.text
    recent = pulse.json().get("recent_activity") or []
    assert recent
    event_id = recent[0]["id"]
    assert event_id

    detail = client.get(
        f"/api/v1/group/shared-living/moments/{moment_id}/activity/{event_id}",
        headers=AUTH,
    )
    assert detail.status_code == 200, detail.text
