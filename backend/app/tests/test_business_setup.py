from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.business.catalog import V1_CREATABLE_CODES, business_type_id
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_draft_each_canonical_template(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    for code in sorted(V1_CREATABLE_CODES):
        resp = client.post(
            "/api/v1/business/moments",
            json={"moment_type_code": code, "title": f"Draft {code}"},
            headers=AUTH,
        )
        assert resp.status_code == 201, code
        body = resp.json()
        assert body["moment_type_code"] == code
        assert body["status"] == "DRAFT"
        assert body["moment_type_id"] == business_type_id(code)
        assert isinstance(body.get("answers"), dict)
        assert body.get("progress", {}).get("current_step") == 1
        assert body.get("template_id")
        assert body.get("setup_version")


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_rejects_unsupported(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "PROJECT_OPERATIONS"},
        headers=AUTH,
    )
    assert resp.status_code == 400


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_alias_normalizes(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "team_operations", "template_id": "team_operations"},
        headers=AUTH,
    )
    assert resp.status_code == 201
    assert resp.json()["moment_type_code"] == "TEAM_OPERATIONS"


@patch("app.dependencies.auth.verify_firebase_token")
def test_setup_state_and_draft_round_trip(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "TEAM_OPERATIONS", "title": "Ops"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]

    state = client.get(f"/api/v1/business/moments/{moment_id}/setup", headers=AUTH)
    assert state.status_code == 200
    data = state.json()
    assert data["moment_id"] == moment_id
    assert data["template_id"] == "team_ops"
    assert data["status"] == "DRAFT"

    saved = client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={
            "answers": {
                "team_purpose": "Ship faster",
                "default_currency_code": "JPY",
                "custom_future_field": {"nested": True},
            },
            "progress": {"current_step": 2, "completed_steps": [1]},
            "template_id": "team_ops",
            "setup_version": "1",
        },
        headers=AUTH,
    )
    assert saved.status_code == 200
    answers = saved.json()["answers"]
    assert answers["team_purpose"] == "Ship faster"
    assert answers["default_currency_code"] == "JPY"
    assert answers["custom_future_field"] == {"nested": True}
    assert saved.json()["progress"]["current_step"] == 2

    resumed = client.get(f"/api/v1/business/moments/{moment_id}/setup", headers=AUTH)
    assert resumed.json()["answers"]["custom_future_field"] == {"nested": True}


def _runway_complete_answers() -> dict:
    """Minimal Runway answers that clear activation blockers (Run 4 contract)."""
    return {
        "moment_name": "Cash Runway",
        "runway_name": "Q3 Runway",
        "business_stage": "EARLY_REVENUE",
        "operating_currency_code": "KWD",
        "timezone": "Asia/Kuwait",
        "runway_goal_months": 12,
        "current_cash_minor": 0,
        "monthly_burn_minor": 0,
        "revenue_status": "NO_REVENUE",
        "runway_alert_threshold_months": 3,
    }


def _ops_complete_answers() -> dict:
    """Minimal Ops answers that clear activation blockers (Run 5 contract)."""
    return {
        "moment_name": "Ops Co",
        "operations_name": "Core Operations",
        "operations_scope": "GENERAL_OPERATIONS",
        "operating_model": "HYBRID",
        "operating_currency_code": "USD",
        "timezone": "America/New_York",
        "review_cycle": "MONTHLY",
        "monthly_budget_minor": 0,
        "confirm_budget": True,
        "confirm_governance": True,
        "confirm_members": True,
    }


@patch("app.dependencies.auth.verify_firebase_token")
def test_preview_incomplete_runway_blocks_activation(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Sparse preview stays 200 but activation_ready is False (no Run 2 placeholder)."""
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_RUNWAY"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    preview = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/preview",
        json={"answers": {"default_currency_code": "KWD"}},
        headers=AUTH,
    )
    assert preview.status_code == 200
    body = preview.json()
    assert "summary_blocks" in body
    assert "warnings" in body
    assert body["activation_ready"] is False
    assert body.get("blocking_errors")


@patch("app.dependencies.auth.verify_firebase_token")
def test_preview_complete_runway_ready(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_RUNWAY", "title": "Cash Runway"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    preview = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/preview",
        json={"answers": _runway_complete_answers()},
        headers=AUTH,
    )
    assert preview.status_code == 200
    body = preview.json()
    assert body["activation_ready"] is True
    assert not body.get("blocking_errors")


@patch("app.dependencies.auth.verify_firebase_token")
def test_activate_owner_and_status(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    """Activate requires complete Ops answers; then OWNER membership is ACTIVE."""
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_OPERATIONS", "title": "Ops Co"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]

    # Incomplete activate must fail (readiness enforced).
    blocked = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert blocked.status_code == 400

    saved = client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={
            "answers": _ops_complete_answers(),
            "progress": {"current_step": 4, "completed_steps": [1, 2, 3]},
            "template_id": "business_operations",
            "setup_version": "1",
        },
        headers=AUTH,
    )
    assert saved.status_code == 200

    activated = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert activated.status_code == 200, activated.text
    body = activated.json()
    assert body["status"] == "ACTIVE"
    assert body["moment_type_code"] == "BUSINESS_OPERATIONS"
    assert body["membership"]
    assert body["membership"][0]["role"] == "OWNER"
    assert body["membership"][0]["status"] == "ACTIVE"
    assert body["membership"][0]["invitation_status"] == "ACCEPTED"
    assert body["activated_at"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_save_does_not_block_after_patterns(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "TEAM_OPERATIONS"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    # Multiple autosaves should succeed (idempotent).
    for i in range(3):
        resp = client.put(
            f"/api/v1/business/moments/{moment_id}/setup/draft",
            json={"answers": {"note": f"n{i}"}},
            headers=AUTH,
        )
        assert resp.status_code == 200
    assert client.get(f"/api/v1/business/moments/{moment_id}/setup", headers=AUTH).json()["answers"]["note"] == "n2"
