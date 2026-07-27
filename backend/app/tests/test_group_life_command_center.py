"""Tests for Group Life Command Center (GET /group/life)."""
from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.group import moment_store as store
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create_and_activate_experience(client: TestClient) -> str:
    created = client.post(
        "/api/v1/group/shared-experience/moments",
        json={"experience_profile": "TRIP_VACATION"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]
    client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={"experience_profile": "TRIP_VACATION", "moment_name": "Goa Trip"},
        headers=AUTH,
    )
    activated = client.post(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert activated.status_code == 200, activated.text
    return moment_id


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_life_empty(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.get("/api/v1/group/life", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_empty"] is True
    assert body["metrics"] is None


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_life_active_has_metrics(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_experience(client)
    resp = client.get("/api/v1/group/life", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_empty"] is False
    assert body["active_moment_count"] == 1
    metrics = body["metrics"]
    assert metrics is not None
    assert metrics["life_health"]["life_score"] > 0
    assert len(metrics["balance_model"]["dimensions"]) == 5
    assert metrics["intelligence"]["insight_text"]
    assert "SHARED_EXPERIENCE" in {s["moment_type_code"] for s in metrics["life_health"]["satellite_scores"] if s["score"] is not None}


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_life_score_changes_with_moment_data(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate_experience(client)
    before = client.get("/api/v1/group/life", headers=AUTH).json()["metrics"]["life_health"]["life_score"]

    moment = mock_db._stores["moments"][moment_id]
    state = store.read_state(moment)
    state["runtime"]["guests"] = [
        {"id": store.new_id(), "full_name": "Alice", "status": "confirmed"},
        {"id": store.new_id(), "full_name": "Bob", "status": "confirmed"},
        {"id": store.new_id(), "full_name": "Carol", "status": "confirmed"},
    ]
    state["runtime"]["plans"] = [{"id": store.new_id(), "title": "Day 1", "deleted": False}]
    store.write_state(moment, state)

    after = client.get("/api/v1/group/life", headers=AUTH).json()["metrics"]["life_health"]["life_score"]
    assert after != before
    assert after > before


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_active_life_matches_life_metrics(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    _create_and_activate_experience(client)
    life = client.get("/api/v1/group/life", headers=AUTH).json()
    active_life = client.get("/api/v1/group/active/life", headers=AUTH).json()
    assert active_life["is_empty"] is False
    assert active_life["metrics"]["life_health"]["life_score"] == life["metrics"]["life_health"]["life_score"]
