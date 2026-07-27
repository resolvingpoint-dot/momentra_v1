"""Template coexistence — LO, Future Building, Lifestyle, and Relationships."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}

FB_SETUP = {
    "building_focus": "CAREER_GROWTH",
    "current_state": "JUST_STARTING",
    "values": ["GROWTH"],
    "friction_sources": ["LACK_OF_TIME"],
    "momentum_drivers": ["LEARNING"],
    "future_feeling": "HOPEFUL",
}

LS_SETUP = {
    "moment_name": "My Lifestyle",
    "lifestyle_vision": "BALANCED",
    "current_lifestyle": "STEADY",
    "health_energy": "STEADY",
    "daily_habits": ["MORNING_ROUTINE", "MOVEMENT"],
    "work_life_balance": ["BOUNDARIES"],
    "relationships_social": ["QUALITY_TIME"],
    "home_environment": ["CALM_SPACE"],
    "personal_priorities": ["JOY", "HEALTH"],
    "neglected": ["REST"],
    "future_lifestyle_goals": ["VIBRANT_HEALTH", "BALANCED_RHYTHM"],
}

RS_SETUP = {
    "moment_name": "My Relationships",
    "relationship_focus": "FAMILY",
    "current_state": "CONNECTED",
    "want_more": ["QUALITY_TIME", "TRUST"],
    "neglected": ["CHECK_INS"],
    "strength_drivers": ["CONSISTENCY", "HONESTY"],
    "investment_areas": ["LISTENING", "PLANNING"],
}

ORCH_PATCH = patch(
    "app.workers.procedures.refresh_personal_orchestration",
    new_callable=AsyncMock,
)


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create_and_activate(client: TestClient, type_code: str, name: str, answers: dict | None = None):
    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": type_code, "moment_name": name},
        headers=AUTH,
    )
    assert created.status_code == 201
    moment_id = created.json()["moment_id"]
    commit = client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={"answers": answers or {}},
        headers=AUTH,
    )
    assert commit.status_code == 200
    return moment_id


@patch("app.dependencies.auth.verify_firebase_token")
@ORCH_PATCH
def test_lo_and_future_building_coexist(
    _mock_orch, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Behavioral gate: both templates ACTIVE; isolated pulse/memory; shared Life."""
    _auth(mock_verify)
    mock_db.add(sample_user)

    lo_id = _create_and_activate(client, "LIFE_OPERATIONS", "Ops")
    fb_id = _create_and_activate(client, "FUTURE_BUILDING", "Future", FB_SETUP)
    assert lo_id != fb_id

    lo_moments = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/moments", headers=AUTH)
    fb_moments = client.get("/api/v1/personal/templates/FUTURE_BUILDING/moments", headers=AUTH)
    assert lo_moments.status_code == 200
    assert fb_moments.status_code == 200
    assert lo_moments.json()["status"] == "ACTIVE"
    assert fb_moments.json()["status"] == "ACTIVE"
    assert lo_moments.json()["moment"]["moment_id"] == lo_id
    assert fb_moments.json()["moment"]["moment_id"] == fb_id

    aggregate_pulse = client.get("/api/v1/personal/pulse", headers=AUTH)
    assert aggregate_pulse.status_code == 200
    pulse = aggregate_pulse.json()
    assert pulse["life_operations"] is not None
    assert pulse["future_building"] is not None

    lo_pulse = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/pulse", headers=AUTH)
    fb_pulse = client.get("/api/v1/personal/templates/FUTURE_BUILDING/pulse", headers=AUTH)
    assert lo_pulse.status_code == 200
    assert fb_pulse.status_code == 200
    assert lo_pulse.json()["moment_type_code"] == "LIFE_OPERATIONS"
    assert fb_pulse.json()["moment_type_code"] == "FUTURE_BUILDING"

    lo_mem = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/memory", headers=AUTH)
    fb_mem = client.get("/api/v1/personal/templates/FUTURE_BUILDING/memory", headers=AUTH)
    assert lo_mem.json()["status"] == "ACTIVE"
    assert fb_mem.json()["status"] == "ACTIVE"
    assert lo_mem.json()["memory_projection"] is not None
    assert fb_mem.json()["memory_projection"] is not None

    life = client.get("/api/v1/personal/life", headers=AUTH)
    assert life.status_code == 200
    life_body = life.json()
    assert life_body["is_empty"] is False
    projection = life_body.get("life_projection") or {}
    assert projection.get("future_signals") is not None

    archive = client.post(
        f"/api/v1/personal/templates/FUTURE_BUILDING/moments/{fb_id}/archive",
        headers=AUTH,
    )
    assert archive.status_code == 200
    assert archive.json()["status"] == "ARCHIVED"

    lo_after = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/moments", headers=AUTH)
    assert lo_after.json()["status"] == "ACTIVE"

    life_after_fb_archive = client.get("/api/v1/personal/life", headers=AUTH)
    after_projection = life_after_fb_archive.json().get("life_projection") or {}
    assert after_projection.get("future_signals") is None

    complete = client.post(
        f"/api/v1/personal/templates/LIFE_OPERATIONS/moments/{lo_id}/complete",
        headers=AUTH,
    )
    assert complete.status_code == 200
    fb_still = client.get("/api/v1/personal/templates/FUTURE_BUILDING/moments", headers=AUTH)
    assert fb_still.json()["status"] in {"EMPTY", "SETUP", "ARCHIVED"}


@patch("app.dependencies.auth.verify_firebase_token")
@ORCH_PATCH
def test_lo_future_building_and_lifestyle_coexist(
    _mock_orch, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Behavioral gate: all three reference templates ACTIVE with isolated projections."""
    _auth(mock_verify)
    mock_db.add(sample_user)

    lo_id = _create_and_activate(client, "LIFE_OPERATIONS", "Ops")
    fb_id = _create_and_activate(client, "FUTURE_BUILDING", "Future", FB_SETUP)
    ls_id = _create_and_activate(client, "LIFESTYLE", "Lifestyle", LS_SETUP)
    assert len({lo_id, fb_id, ls_id}) == 3

    for code, moment_id in (
        ("LIFE_OPERATIONS", lo_id),
        ("FUTURE_BUILDING", fb_id),
        ("LIFESTYLE", ls_id),
    ):
        moments = client.get(f"/api/v1/personal/templates/{code}/moments", headers=AUTH)
        assert moments.status_code == 200
        body = moments.json()
        assert body["status"] == "ACTIVE"
        assert body["moment"]["moment_id"] == moment_id
        assert body.get("moment_projection") is not None

    aggregate_pulse = client.get("/api/v1/personal/pulse", headers=AUTH)
    assert aggregate_pulse.status_code == 200
    pulse = aggregate_pulse.json()
    assert pulse["life_operations"] is not None
    assert pulse["future_building"] is not None
    assert pulse["lifestyle"] is not None

    for code in ("LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE"):
        template_pulse = client.get(f"/api/v1/personal/templates/{code}/pulse", headers=AUTH)
        assert template_pulse.status_code == 200
        assert template_pulse.json()["moment_type_code"] == code

        memory = client.get(f"/api/v1/personal/templates/{code}/memory", headers=AUTH)
        assert memory.status_code == 200
        assert memory.json()["status"] == "ACTIVE"
        assert memory.json()["memory_projection"] is not None

    life = client.get("/api/v1/personal/life", headers=AUTH)
    assert life.status_code == 200
    projection = life.json().get("life_projection") or {}
    assert projection.get("future_signals") is not None
    assert projection.get("lifestyle_signals") is not None

    archive_ls = client.post(
        f"/api/v1/personal/templates/LIFESTYLE/moments/{ls_id}/archive",
        headers=AUTH,
    )
    assert archive_ls.status_code == 200
    assert archive_ls.json()["status"] == "ARCHIVED"

    lo_after = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/moments", headers=AUTH)
    fb_after = client.get("/api/v1/personal/templates/FUTURE_BUILDING/moments", headers=AUTH)
    assert lo_after.json()["status"] == "ACTIVE"
    assert fb_after.json()["status"] == "ACTIVE"

    life_after_ls = client.get("/api/v1/personal/life", headers=AUTH)
    after_projection = life_after_ls.json().get("life_projection") or {}
    assert after_projection.get("lifestyle_signals") is None
    assert after_projection.get("future_signals") is not None


@patch("app.dependencies.auth.verify_firebase_token")
@ORCH_PATCH
def test_all_four_reference_templates_coexist(
    _mock_orch, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Behavioral gate: LO, FB, LS, RS all ACTIVE with isolated projections and shared Life."""
    _auth(mock_verify)
    mock_db.add(sample_user)

    lo_id = _create_and_activate(client, "LIFE_OPERATIONS", "Ops")
    fb_id = _create_and_activate(client, "FUTURE_BUILDING", "Future", FB_SETUP)
    ls_id = _create_and_activate(client, "LIFESTYLE", "Lifestyle", LS_SETUP)
    rs_id = _create_and_activate(client, "RELATIONSHIPS", "Relationships", RS_SETUP)
    assert len({lo_id, fb_id, ls_id, rs_id}) == 4

    for code, moment_id in (
        ("LIFE_OPERATIONS", lo_id),
        ("FUTURE_BUILDING", fb_id),
        ("LIFESTYLE", ls_id),
        ("RELATIONSHIPS", rs_id),
    ):
        moments = client.get(f"/api/v1/personal/templates/{code}/moments", headers=AUTH)
        assert moments.status_code == 200
        body = moments.json()
        assert body["status"] == "ACTIVE"
        assert body["moment"]["moment_id"] == moment_id
        assert body.get("moment_projection") is not None

    aggregate_pulse = client.get("/api/v1/personal/pulse", headers=AUTH)
    assert aggregate_pulse.status_code == 200
    pulse = aggregate_pulse.json()
    assert pulse["life_operations"] is not None
    assert pulse["future_building"] is not None
    assert pulse["lifestyle"] is not None
    assert pulse["emotional_security"] is not None

    for code in ("LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS"):
        template_pulse = client.get(f"/api/v1/personal/templates/{code}/pulse", headers=AUTH)
        assert template_pulse.status_code == 200
        assert template_pulse.json()["moment_type_code"] == code

        memory = client.get(f"/api/v1/personal/templates/{code}/memory", headers=AUTH)
        assert memory.status_code == 200
        assert memory.json()["status"] == "ACTIVE"
        assert memory.json()["memory_projection"] is not None

    life = client.get("/api/v1/personal/life", headers=AUTH)
    assert life.status_code == 200
    projection = life.json().get("life_projection") or {}
    assert projection.get("future_signals") is not None
    assert projection.get("lifestyle_signals") is not None
    balance_dims = (projection.get("balance_model") or {}).get("dimensions") or []
    assert len(balance_dims) == 4

    archive_rs = client.post(
        f"/api/v1/personal/templates/RELATIONSHIPS/moments/{rs_id}/archive",
        headers=AUTH,
    )
    assert archive_rs.status_code == 200
    assert archive_rs.json()["status"] == "ARCHIVED"

    lo_after = client.get("/api/v1/personal/templates/LIFE_OPERATIONS/moments", headers=AUTH)
    ls_after = client.get("/api/v1/personal/templates/LIFESTYLE/moments", headers=AUTH)
    assert lo_after.json()["status"] == "ACTIVE"
    assert ls_after.json()["status"] == "ACTIVE"
