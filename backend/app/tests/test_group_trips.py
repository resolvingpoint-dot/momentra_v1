from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create_experience(client: TestClient) -> str:
    created = client.post(
        "/api/v1/group/shared-experience/moments",
        json={"experience_profile": "TRIP_VACATION"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]
    client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={"experience_profile": "TRIP_VACATION", "moment_name": "Goa 2026"},
        headers=AUTH,
    )
    return moment_id


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_live_hub(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)

    resp = client.get(f"/api/v1/group/trips/{moment_id}/live-hub", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["moment_id"] == moment_id
    assert data["header"]["moment_name"] == "Goa 2026"
    assert data["hero"]["title"] and data["insight"]["title"]
    assert data["experience_profile"]["title"] and data["creation_event"]["title"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_pulse(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)

    resp = client.get(f"/api/v1/group/trips/{moment_id}/pulse", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["trip_name"] == "Goa 2026"
    assert data["readiness_title"]
    assert "participants_joined" in data["stats"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_moments_view(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)

    resp = client.get(f"/api/v1/group/trips/{moment_id}/moments-view", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["memory_hero"]["title"] == "Goa 2026"
    assert data["operations_hub"]["core_summary"]["moment_name"] == "Goa 2026"
    assert data["memory_hub"]["hero"]["moment_name"] == "Goa 2026"


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_memories_list_and_create(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)

    listed = client.get(f"/api/v1/group/trips/{moment_id}/memories", headers=AUTH)
    assert listed.status_code == 200
    assert listed.json() == []

    created = client.post(
        f"/api/v1/group/trips/{moment_id}/memories",
        json={"title": "Sunset at the beach", "note": "Everyone was there"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    data = created.json()
    assert data["title"] == "Sunset at the beach"
    assert data["moment_id"] == moment_id
    assert data["id"] and data["created_at"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_unknown_moment_404(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/group/trips/00000000-0000-0000-0000-000000000000/pulse",
        headers=AUTH,
    )
    assert resp.status_code == 404


def test_trip_requires_auth(client: TestClient, mock_db):
    resp = client.get("/api/v1/group/trips/00000000-0000-0000-0000-000000000000/pulse")
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_pulse_enriched_with_runtime(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)
    from app.domains.group import moment_store as store

    client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={
            "experience_profile": "TRIP_VACATION",
            "moment_name": "Goa 2026",
            "target_amount_major": "150000",
            "end_date": "2026-12-31",
        },
        headers=AUTH,
    )

    moment = mock_db._get_from_store("moments", moment_id)
    assert moment is not None
    store.append_item(
        moment,
        "guests",
        {"id": "g1", "full_name": "Priya", "status": "active", "created_at": store.now_iso()},
    )
    store.append_item(
        moment,
        "bookings",
        {"id": "b1", "title": "Hotel", "status": "confirmed", "created_at": store.now_iso()},
    )
    store.append_item(
        moment,
        "expenses",
        {"id": "e1", "title": "Dinner", "amount_minor": 8200000, "created_at": store.now_iso()},
    )
    store.append_activity(
        moment,
        {
            "id": "a1",
            "activity_type": "EXPENSE",
            "title": "Budget Plan Created",
            "subtitle": "10:30 AM",
            "occurred_at": store.now_iso(),
        },
    )

    resp = client.get(f"/api/v1/group/trips/{moment_id}/pulse", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["stats"]["guests_joined"] >= 1
    assert data["stats"]["confirmed_bookings"] >= 1
    assert data["next_best_action"]["title"]
    assert data["dashboard_card"]["recent_items"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_moments_operations_hub(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)
    from app.domains.group import moment_store as store

    moment = mock_db._get_from_store("moments", moment_id)
    store.append_item(moment, "guests", {"id": "g1", "full_name": "Sarah", "status": "active"})
    store.append_item(
        moment,
        "members",
        {
            "id": "m1",
            "user_id": "m1",
            "display_name": "Sarah Jenkins",
            "role_code": "ORGANIZER",
            "status": "ACTIVE",
        },
    )
    store.append_item(moment, "bookings", {"id": "b1", "status": "confirmed"})
    store.append_item(moment, "polls", {"id": "p1", "question": "Sunset Trek vs Kayaking", "status": "open"})

    resp = client.get(f"/api/v1/group/trips/{moment_id}/moments-view", headers=AUTH)
    assert resp.status_code == 200, resp.text
    hub = resp.json()["operations_hub"]
    assert hub["core_summary"]["stat_tiles"]
    assert hub["people_roles"]["primary"]
    assert hub["money_status"]["columns"]
    assert hub["activity_ops"]
    assert hub["decisions"]
    assert hub["current_state"]["focus_items"]
    memory = resp.json()["memory_hub"]
    assert memory["hero"]["chips"]
    assert "timeline" in memory
