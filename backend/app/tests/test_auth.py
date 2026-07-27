from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel


def test_health(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_auth_sync_no_token(client: TestClient):
    resp = client.post("/api/v1/auth/sync")
    assert resp.status_code == 401


def test_auth_exchange_no_token(client: TestClient):
    resp = client.post("/api/v1/auth/exchange")
    assert resp.status_code == 401


def test_me_no_token(client: TestClient):
    resp = client.get("/api/v1/me")
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
def test_auth_sync_valid_token(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/auth/sync",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["user"]["firebase_uid"] == "test123"
    assert data["user"]["email"] == "test@example.com"
    assert "preferences" in data


@patch("app.dependencies.auth.verify_firebase_token")
def test_auth_sync_creates_preferences(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/auth/sync",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["preferences"]["selected_context"] == "MY_MONEY"


@patch("app.dependencies.auth.verify_firebase_token")
def test_auth_sync_creates_module_states(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/auth/sync",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    assert mock_db._stores["module_states"] != {}


@patch("app.dependencies.auth.verify_firebase_token")
def test_auth_exchange_valid_token(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/auth/exchange",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["app_session_token"] is not None
    assert data["token_type"] == "bearer"
    assert "expires_at" in data
    assert data["user"]["firebase_uid"] == "test123"


@patch("app.dependencies.auth.verify_firebase_token")
def test_auth_sync_idempotent(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp1 = client.post(
        "/api/v1/auth/sync",
        headers={"Authorization": "Bearer fake-token"},
    )
    resp2 = client.post(
        "/api/v1/auth/sync",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["user"]["id"] == resp2.json()["user"]["id"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_invalid_token_returns_401(mock_verify, client: TestClient):
    mock_verify.side_effect = Exception("Invalid token")

    resp = client.post(
        "/api/v1/auth/sync",
        headers={"Authorization": "Bearer bad-token"},
    )
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
def test_exchange_returns_app_session_token_format(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/auth/exchange",
        headers={"Authorization": "Bearer fake-token"},
    )
    data = resp.json()
    assert "app_session_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_at" in data
