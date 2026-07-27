from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel
from app.tests.conftest import MOCK_USER_ID


@patch("app.dependencies.auth.verify_firebase_token")
def test_bootstrap_returns_module_states(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/app/bootstrap",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["email"] == "test@example.com"
    assert data["preferences"]["selected_context"] == "MY_MONEY"
    assert data["reference_data_version"] == 18
    assert len(data["contexts"]) == 4
    for ctx in data["contexts"]:
        assert ctx["state"] == "EMPTY"
        # Bootstrap is state-only: static empty-state content ships in the app.
        assert "empty_state" not in ctx
    assert data["modules"]["pulse"]["state"] == "EMPTY"
    assert data["modules"]["moments"]["state"] == "EMPTY"
    assert data["summary_counts"]["my_money_moments"] == 0
    assert "server_time" in data


@patch("app.dependencies.auth.verify_firebase_token")
def test_bootstrap_requires_auth(mock_verify, client: TestClient):
    resp = client.get("/api/v1/app/bootstrap")
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
def test_update_preferences(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    from app.domains.preferences.models import UserPreferencesModel
    from datetime import datetime, timezone

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

    resp = client.patch(
        "/api/v1/app/preferences",
        json={"selected_context": "GROUP"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["selected_context"] == "GROUP"


@patch("app.dependencies.auth.verify_firebase_token")
def test_update_preferences_invalid_context(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.patch(
        "/api/v1/app/preferences",
        json={"selected_context": "INVALID"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 422
