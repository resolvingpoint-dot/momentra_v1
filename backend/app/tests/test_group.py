from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.group.catalog import GROUP_MOMENT_TYPES
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_pulse_empty_state(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/group/pulse", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_empty"] is True
    assert data["active_moment_count"] == 0
    assert len(data["type_cards"]) == len(GROUP_MOMENT_TYPES)
    assert data["why_groups"] and data["magic_steps"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_session_bootstrap_shape(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/group/session/bootstrap", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    # Android nested shape + iOS flat shape both present.
    assert "pulse" in data and "live_overview" in data
    assert data["pulse"]["is_empty"] is True
    assert data["is_empty"] is True
    assert data["active_moment_count"] == 0


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_create_options_lists_all_types(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/group/create/options", headers=AUTH)
    assert resp.status_code == 200
    codes = {c["moment_type_code"] for c in resp.json()["cards"]}
    assert codes == {mt.code for mt in GROUP_MOMENT_TYPES}


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_moment_templates(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/group/moment-templates", headers=AUTH)
    assert resp.status_code == 200
    templates = resp.json()
    assert len(templates) == len(GROUP_MOMENT_TYPES)
    assert all(t["default_name"] for t in templates)


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_setup_profiles(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/group/setup/TRIP/profiles", headers=AUTH)
    assert resp.status_code == 200
    profiles = resp.json()
    assert profiles
    assert all(p["moment_type"] == "TRIP" for p in profiles)


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_home_memory_life_empty(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    for path in ("/api/v1/group/moments/home", "/api/v1/group/memory", "/api/v1/group/life", "/api/v1/group/live"):
        resp = client.get(path, headers=AUTH)
        assert resp.status_code == 200, path
        assert resp.json()["is_empty"] is True, path


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_create_and_activate_flow(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/group/moments",
        json={"moment_type_code": "TRIP", "moment_name": "Goa 2026"},
        headers=AUTH,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["moment_type_code"] == "TRIP"
    assert body["moment_name"] == "Goa 2026"
    moment_id = body["moment_id"]

    # Android review path resolves the created moment
    review = client.get(f"/api/v1/group/setup/moments/{moment_id}/review", headers=AUTH)
    assert review.status_code == 200
    assert review.json()["moment_id"] == moment_id

    # iOS review path variant resolves the same moment
    review_ios = client.get(f"/api/v1/group/setup/review/{moment_id}", headers=AUTH)
    assert review_ios.status_code == 200
    assert review_ios.json()["moment_id"] == moment_id

    activate = client.post(f"/api/v1/group/setup/moments/{moment_id}/activate", headers=AUTH)
    assert activate.status_code == 200
    assert activate.json()["lifecycle_status"] == "ACTIVE"


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_setup_basics_then_ios_people(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    basics = client.post(
        "/api/v1/group/setup/TRIP/basics",
        json={"moment_name": "Euro Trip", "currency_code": "EUR", "detail_fields": {}},
        headers=AUTH,
    )
    assert basics.status_code == 200
    assert basics.json()["moment_type_code"] == "TRIP"
    assert basics.json()["lifecycle_status"] == "SETUP"

    # iOS people path has no moment id — resolves the latest TRIP draft.
    people = client.post(
        "/api/v1/group/setup/TRIP/people",
        json={"members": [{"name": "A", "email": "a@x.com"}]},
        headers=AUTH,
    )
    assert people.status_code == 200
    assert people.json()["moment_id"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_patch_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/group/moments",
        json={"moment_type_code": "CELEBRATION"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]

    patched = client.patch(
        f"/api/v1/group/moments/{moment_id}",
        json={"moment_name": "Wedding", "status": "ACTIVE"},
        headers=AUTH,
    )
    assert patched.status_code == 200
    data = patched.json()
    assert data["moment_name"] == "Wedding"
    assert data["status"] == "ACTIVE"


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_active_pulse_after_create(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/group/moments",
        json={"moment_type_code": "TRIP", "moment_name": "Trip"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]

    pulse = client.get(f"/api/v1/group/active/pulse/{moment_id}", headers=AUTH)
    assert pulse.status_code == 200
    assert pulse.json()["moment_id"] == moment_id
    assert pulse.json()["moment_type"] == "TRIP"


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_requires_auth(mock_verify, client: TestClient, mock_db):
    resp = client.get("/api/v1/group/pulse")
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
def test_member_archive_returns_403_not_owned(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Members who can see a moment get 403 moment_not_owned on archive, not 404."""
    from datetime import datetime, timezone
    from uuid import uuid4

    from app.domains.group.models import GroupMomentMembers
    from app.domains.moments.models import MomentModel

    _auth(mock_verify)
    mock_db.add(sample_user)

    owner_id = uuid4()
    moment_id = uuid4()
    mock_db.add(
        MomentModel(
            id=moment_id,
            user_id=owner_id,
            context_type="GROUP",
            moment_type="SHARED_EXPERIENCE",
            title="Wedding",
            status="ACTIVE",
            setup_state="COMPLETE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    mock_db.add(
        GroupMomentMembers(
            member_id=uuid4(),
            moment_id=moment_id,
            display_name="Guest",
            role_code="PARTICIPANT",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
            user_id=sample_user.id,
        )
    )

    resp = client.post(
        f"/api/v1/group/moments/{moment_id}/archive",
        headers=AUTH,
    )
    assert resp.status_code == 403
    body = resp.json()
    err = body.get("error") or {}
    code = err.get("code") or body.get("detail") or ""
    assert "moment_not_owned" in str(code) or "owner" in str(err.get("message", "")).lower()
