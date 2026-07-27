from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.business.catalog import (
    BUSINESS_CREATE_CATALOG,
    BUSINESS_DIMENSIONS,
    BUSINESS_UNSUPPORTED_DIMENSIONS,
    V1_CREATABLE_CODES,
    business_type_id,
    normalize_moment_type_code,
)
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_pulse_empty_state(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/business/pulse", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_empty"] is True
    assert data["active_moment_count"] == 0
    # Required nested objects must always be present.
    assert "avatar_requirements" in data and "cover_requirements" in data
    assert data["avatar_requirements"]["allowed_content_types"]
    assert data["benefits"]
    assert len(data["dimension_cards"]) == len(BUSINESS_DIMENSIONS)
    codes = {c["moment_type_code"] for c in data["dimension_cards"]}
    assert codes == V1_CREATABLE_CODES
    assert "REVENUE" not in codes
    assert "Department Operations" not in {c["moment_type_name"] for c in data["dimension_cards"]}


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_session_bootstrap_shape(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/business/session/bootstrap", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert "pulse" in data and "moments_home" in data
    assert data["moments_home"]["is_empty"] is True


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_screens_have_requirements(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    for path in (
        "/api/v1/business/moments/home",
        "/api/v1/business/live",
        "/api/v1/business/create/options",
    ):
        resp = client.get(path, headers=AUTH)
        assert resp.status_code == 200, path
        data = resp.json()
        assert data["is_empty"] is True, path
        assert data["avatar_requirements"]["target_width"] > 0, path
        assert data["cover_requirements"]["aspect_ratio"], path

    mem = client.get("/api/v1/business/memory", headers=AUTH)
    assert mem.status_code == 200
    mem_data = mem.json()
    assert mem_data["active_moment_count"] == 0
    assert "buckets" in mem_data
    assert "events" in mem_data


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_create_options_lists_v1_and_gated(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/business/create/options", headers=AUTH)
    assert resp.status_code == 200
    cards = resp.json()["cards"]
    codes = {c["moment_type_code"] for c in cards}
    assert codes == {d.code for d in BUSINESS_CREATE_CATALOG}
    assert codes == V1_CREATABLE_CODES | {d.code for d in BUSINESS_UNSUPPORTED_DIMENSIONS}
    assert "REVENUE" not in codes
    assert "OPERATIONS" not in codes
    assert "FINANCE" not in codes
    assert "PEOPLE" not in codes

    by_code = {c["moment_type_code"]: c for c in cards}
    assert by_code["TEAM_OPERATIONS"]["is_available"] is True
    assert by_code["BUSINESS_RUNWAY"]["is_available"] is True
    assert by_code["BUSINESS_OPERATIONS"]["is_available"] is True
    assert by_code["BUSINESS_OPERATIONS"]["moment_type_name"] == "Business Operations"
    assert by_code["PROJECT_OPERATIONS"]["is_available"] is False
    assert by_code["PROJECT_OPERATIONS"]["implementation_status"] == "coming_soon"


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_create_and_patch_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "TEAM_OPERATIONS", "moment_name": "Marketing Team"},
        headers=AUTH,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["moment_type_code"] == "TEAM_OPERATIONS"
    assert body["moment_name"] == "Marketing Team"
    assert body["moment_type_id"] == business_type_id("TEAM_OPERATIONS")
    assert body["status"] == "DRAFT"
    moment_id = body["moment_id"]

    patched = client.patch(
        f"/api/v1/business/moments/{moment_id}",
        json={"status": "ACTIVE"},
        headers=AUTH,
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "ACTIVE"


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_create_accepts_snake_alias(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "business_runway", "moment_name": "Runway"},
        headers=AUTH,
    )
    assert created.status_code == 201
    assert created.json()["moment_type_code"] == "BUSINESS_RUNWAY"


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_create_rejects_unsupported_and_legacy(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    unsupported = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "PROJECT_OPERATIONS"},
        headers=AUTH,
    )
    assert unsupported.status_code == 400

    legacy = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "REVENUE"},
        headers=AUTH,
    )
    assert legacy.status_code == 400


def test_normalize_department_alias():
    assert normalize_moment_type_code("department_operations") == "BUSINESS_OPERATIONS"
    assert normalize_moment_type_code("team_operations") == "TEAM_OPERATIONS"


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_cover_upload_and_confirm(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_RUNWAY"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]

    upload = client.post(
        f"/api/v1/business/moments/{moment_id}/cover/upload-url",
        json={"filename": "cover.png", "content_type": "image/png", "byte_size": 1024},
        headers=AUTH,
    )
    assert upload.status_code == 200
    assert upload.json()["storage_path"]

    confirm = client.patch(
        f"/api/v1/business/moments/{moment_id}/cover",
        json={"storage_path": upload.json()["storage_path"]},
        headers=AUTH,
    )
    assert confirm.status_code == 200
    assert confirm.json()["moment_id"] == moment_id


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_requires_auth(mock_verify, client: TestClient, mock_db):
    resp = client.get("/api/v1/business/pulse")
    assert resp.status_code == 401
