"""Reference Vertical — template projection routes (Life Operations)."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.domains.personal.templates.registry import get_template_projection_registry
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


@patch("app.dependencies.auth.verify_firebase_token")
def test_unregistered_template_returns_501(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.get("/api/v1/personal/templates/UNKNOWN_TEMPLATE/moments", headers=AUTH)
    assert resp.status_code == 501
    assert resp.json()["error"]["code"] == "template_not_registered"


@patch("app.dependencies.auth.verify_firebase_token")
def test_life_operations_registered(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    assert get_template_projection_registry().is_registered("LIFE_OPERATIONS")


@patch("app.dependencies.auth.verify_firebase_token")
def test_template_moments_empty_state(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/moments", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["moment_type_code"] == "LIFE_OPERATIONS"
    assert data["status"] == "EMPTY"
    assert data["moment"] is None
    assert data["recent_events"] == []
    assert "projection_version" in data
    assert data["moment_projection"] is None


@patch("app.dependencies.auth.verify_firebase_token")
def test_template_moments_active_after_setup(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "LIFE_OPERATIONS", "moment_name": "My Ops"},
        headers=AUTH,
    )
    assert created.status_code == 201
    moment_id = created.json()["moment_id"]
    commit = client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={"answers": {"moment_name": "My Ops"}},
        headers=AUTH,
    )
    assert commit.status_code == 200

    resp = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/moments", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ACTIVE"
    assert data["moment"]["moment_id"] == moment_id
    assert "setup_summary" in data
    assert "progress" in data
    assert "projection_version" in data
    mp = data.get("moment_projection")
    assert mp is not None
    assert "journey_hero" in mp
    assert "journey_timeline" in mp
    assert "money_journey" in mp
    assert "best_moments" in mp
    assert "turning_points" in mp


@patch("app.dependencies.auth.verify_firebase_token")
def test_template_life_operating_view_shape(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/life", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["moment_type_code"] == "LIFE_OPERATIONS"
    assert "headline" in data
    assert "dimensions" in data
    dims = data["dimensions"]
    for key in (
        "financial_health",
        "recovery",
        "attention",
        "rhythm",
        "workload",
        "momentum",
    ):
        assert key in dims
        assert "score" in dims[key]


@patch("app.dependencies.auth.verify_firebase_token")
def test_template_memory_shape(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/memory", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["moment_type_code"] == "LIFE_OPERATIONS"
    assert data["status"] == "EMPTY"
    assert "projection_version" in data
    assert data.get("memory_projection") is None


@patch("app.dependencies.auth.verify_firebase_token")
def test_template_memory_projection_when_active(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "LIFE_OPERATIONS", "moment_name": "Mem Ops"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={"answers": {}},
        headers=AUTH,
    )
    resp = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/memory", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ACTIVE"
    mp = data.get("memory_projection")
    assert mp is not None
    for key in (
        "identity_snapshot",
        "core_pattern",
        "best_drivers",
        "emotional_dna",
        "ai_interpretation",
        "next_growth_edge",
    ):
        assert key in mp


@patch("app.dependencies.auth.verify_firebase_token")
def test_personal_life_projection(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.get("/api/v1/personal/life", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_empty"] is True
    assert "projection_version" in data

    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "LIFE_OPERATIONS", "moment_name": "Life"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={"answers": {}},
        headers=AUTH,
    )
    active = client.get("/api/v1/personal/life", headers=AUTH)
    assert active.status_code == 200
    body = active.json()
    assert body["is_empty"] is False
    assert body.get("life_projection") is not None
    assert "life_health" in body["life_projection"]
    assert body.get("metrics") is not None


@patch("app.dependencies.auth.verify_firebase_token")
def test_template_archive_moment(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "LIFE_OPERATIONS", "moment_name": "Archive Me"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={"answers": {}},
        headers=AUTH,
    )
    resp = client.post(
        f"/api/v1/personal/templates/LIFE_OPERATIONS/moments/{moment_id}/archive",
        headers=AUTH,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ARCHIVED"

    moments = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/moments", headers=AUTH)
    assert moments.json()["status"] in {"EMPTY", "SETUP"}


@patch("app.dependencies.auth.verify_firebase_token")
def test_template_complete_moment(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "LIFE_OPERATIONS", "moment_name": "Complete Me"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={"answers": {}},
        headers=AUTH,
    )
    resp = client.post(
        f"/api/v1/personal/templates/LIFE_OPERATIONS/moments/{moment_id}/complete",
        headers=AUTH,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"


@patch("app.dependencies.auth.verify_firebase_token")
def test_shared_template_life_and_memory(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    for code in ("FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS"):
        life = client.get(f"/api/v1/personal/templates/{code}/life", headers=AUTH)
        assert life.status_code == 200
        data = life.json()
        assert data["moment_type_code"] == code
        assert "dimensions" in data
        memory = client.get(f"/api/v1/personal/templates/{code}/memory", headers=AUTH)
        assert memory.status_code == 200
        mem = memory.json()
        assert mem["moment_type_code"] == code
        assert "memory_projection" in mem
        assert "projection_version" in mem
        if code == "RELATIONSHIPS":
            moments = client.get(f"/api/v1/personal/templates/{code}/moments", headers=AUTH)
            assert moments.status_code == 200
            assert moments.json()["status"] == "EMPTY"
        if code == "LIFESTYLE":
            moments = client.get(f"/api/v1/personal/templates/{code}/moments", headers=AUTH)
            assert moments.status_code == 200
            assert moments.json()["status"] == "EMPTY"


@patch("app.dependencies.auth.verify_firebase_token")
@patch("app.workers.procedures.refresh_personal_orchestration", new_callable=AsyncMock)
def test_future_building_registered_and_moments_shape(
    _mock_orch, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    assert get_template_projection_registry().is_registered("FUTURE_BUILDING")

    empty = client.get("/api/v1/personal/templates/FUTURE_BUILDING/moments", headers=AUTH)
    assert empty.status_code == 200
    assert empty.json()["status"] == "EMPTY"

    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "FUTURE_BUILDING", "moment_name": "FB"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={
            "answers": {
                "building_focus": "LEARNING_SKILLS",
                "current_state": "MAKING_PROGRESS",
                "values": ["GROWTH"],
                "friction_sources": ["DISTRACTIONS"],
                "momentum_drivers": ["FOCUS_TIME"],
                "future_feeling": "EXCITING",
            }
        },
        headers=AUTH,
    )

    moments = client.get("/api/v1/personal/templates/FUTURE_BUILDING/moments", headers=AUTH)
    assert moments.status_code == 200
    data = moments.json()
    assert data["status"] == "ACTIVE"
    mp = data.get("moment_projection")
    assert mp is not None
    assert "journey_hero" in mp

    pulse = client.get("/api/v1/personal/templates/FUTURE_BUILDING/pulse", headers=AUTH)
    assert pulse.status_code == 200
    pulse_body = pulse.json()
    assert pulse_body["status"] == "ACTIVE"
    assert pulse_body["pulse"]["hero_title"] == "Future Momentum"

    memory = client.get("/api/v1/personal/templates/FUTURE_BUILDING/memory", headers=AUTH)
    assert memory.status_code == 200
    assert memory.json()["memory_projection"] is not None
