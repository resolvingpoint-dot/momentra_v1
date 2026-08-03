"""Contract tests for me preferences, account deletion, preference sync."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.preferences.models import UserPreferencesModel
from app.domains.users.models import UserModel
from app.tests.conftest import MOCK_USER_ID


def _auth(mock_verify):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }


def _seed_prefs(mock_db, sample_user: UserModel):
    mock_db.add(sample_user)
    pref = UserPreferencesModel(
        id=MOCK_USER_ID,
        user_id=MOCK_USER_ID,
        selected_context="MY_MONEY",
        default_currency_code="INR",
        locale="en-IN",
        country_code="IN",
        timezone="Asia/Kolkata",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.add(pref)
    return pref


@patch("app.dependencies.auth.verify_firebase_token")
def test_get_me_preferences_creates_defaults(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    _seed_prefs(mock_db, sample_user)

    resp = client.get(
        "/api/v1/me/preferences",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["week_start_day"] == "MONDAY"
    assert data["notification_enabled"] is True
    assert data["privacy_mode_enabled"] is False
    assert data["user_id"] == str(MOCK_USER_ID)


@patch("app.dependencies.auth.verify_firebase_token")
def test_patch_me_preferences(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    _seed_prefs(mock_db, sample_user)

    resp = client.patch(
        "/api/v1/me/preferences",
        json={
            "week_start_day": "SUNDAY",
            "privacy_mode_enabled": True,
            "notification_enabled": False,
            "daily_summary_enabled": True,
        },
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["week_start_day"] == "SUNDAY"
    assert data["privacy_mode_enabled"] is True
    assert data["notification_enabled"] is False
    assert data["daily_summary_enabled"] is True


@patch("app.dependencies.auth.verify_firebase_token")
def test_patch_me_preferences_invalid_week_start(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    _seed_prefs(mock_db, sample_user)

    resp = client.patch(
        "/api/v1/me/preferences",
        json={"week_start_day": "WEDNESDAY"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 400


@patch("app.dependencies.auth.verify_firebase_token")
def test_bootstrap_includes_personal_preferences(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    _seed_prefs(mock_db, sample_user)

    resp = client.get(
        "/api/v1/app/bootstrap",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "personal_preferences" in data
    assert data["personal_preferences"]["week_start_day"] == "MONDAY"
    assert data["personal_preferences"]["privacy_mode_enabled"] is False


@patch("app.dependencies.auth.verify_firebase_token")
def test_app_preferences_syncs_personal_currency_timezone(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    _seed_prefs(mock_db, sample_user)

    # Ensure personal row exists first
    client.get(
        "/api/v1/me/preferences",
        headers={"Authorization": "Bearer fake-token"},
    )

    resp = client.patch(
        "/api/v1/app/preferences",
        json={"default_currency_code": "USD", "timezone": "America/New_York"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    assert resp.json()["default_currency_code"] == "USD"
    assert resp.json()["timezone"] == "America/New_York"

    personal = client.get(
        "/api/v1/me/preferences",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert personal.status_code == 200
    pdata = personal.json()
    assert pdata["default_currency_code"] == "USD"
    assert pdata["timezone_name"] == "America/New_York"


@patch("app.core.firebase.disable_or_delete_firebase_user")
@patch("app.dependencies.auth.verify_firebase_token")
def test_delete_me(
    mock_verify,
    mock_disable,
    client: TestClient,
    mock_db,
    sample_user: UserModel,
):
    _auth(mock_verify)
    _seed_prefs(mock_db, sample_user)

    resp = client.delete(
        "/api/v1/me",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 204
    mock_disable.assert_called_once_with("test123")
    assert sample_user.deleted_at is not None
    assert sample_user.display_name == "Deleted User"
    assert sample_user.email is None


@patch("app.dependencies.auth.verify_firebase_token")
def test_delete_me_requires_auth(mock_verify, client: TestClient):
    resp = client.delete("/api/v1/me")
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
def test_me_preferences_requires_auth(mock_verify, client: TestClient):
    resp = client.get("/api/v1/me/preferences")
    assert resp.status_code == 401
