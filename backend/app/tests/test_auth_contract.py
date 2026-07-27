from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}
AUTH = {"Authorization": "Bearer fake-token"}


@patch("app.api.v1.auth.verify_firebase_token")
def test_firebase_exchange_returns_user_and_tokens(mock_verify, client: TestClient, mock_db):
    mock_verify.return_value = FIREBASE_CLAIMS

    resp = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["display_name"] == "Test User"
    tokens = data["tokens"]
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"
    assert tokens["expires_in"] > 0


@patch("app.api.v1.auth.verify_firebase_token")
def test_firebase_exchange_missing_token(mock_verify, client: TestClient, mock_db):
    resp = client.post("/api/v1/auth/firebase/exchange", json={})
    assert resp.status_code == 401


@patch("app.api.v1.auth.verify_firebase_token")
def test_refresh_rotates_and_rejects_reuse(mock_verify, client: TestClient, mock_db):
    mock_verify.return_value = FIREBASE_CLAIMS

    exchange = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    assert exchange.status_code == 200
    old_refresh = exchange.json()["tokens"]["refresh_token"]

    first = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert first.status_code == 200
    new_refresh = first.json()["refresh_token"]
    assert new_refresh != old_refresh

    reuse = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse.status_code == 401

    # Family revoke: even the rotated token should fail after reuse detection.
    after_reuse = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": new_refresh}
    )
    assert after_reuse.status_code == 401


@patch("app.api.v1.auth.verify_firebase_token")
def test_logout_revokes_refresh(mock_verify, client: TestClient, mock_db):
    mock_verify.return_value = FIREBASE_CLAIMS

    exchange = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    refresh_token = exchange.json()["tokens"]["refresh_token"]

    logout = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout.status_code == 200

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 401


@patch("app.api.v1.auth.verify_firebase_token")
def test_logout_all_revokes_other_sessions(mock_verify, client: TestClient, mock_db):
    mock_verify.return_value = FIREBASE_CLAIMS

    first = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    second = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    access = first.json()["tokens"]["access_token"]
    other_refresh = second.json()["tokens"]["refresh_token"]

    resp = client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert resp.status_code == 200
    assert resp.json()["revoked"] >= 1

    denied = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": other_refresh}
    )
    assert denied.status_code == 401


def test_validate_production_security_rejects_unsafe_flags():
    from app.core.config import Settings, validate_production_security

    unsafe = Settings.model_construct(
        debug=False,
        momentra_env="production",
        allow_test_auth=False,
        app_session_secret="x" * 32,
        session_secret_key="",
        cors_origins_str="*",
        storage_public_base_url="",
    )
    try:
        validate_production_security(unsafe)
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        msg = str(exc)
        assert "64" in msg or "APP_SESSION_SECRET" in msg
        assert "STORAGE_PUBLIC_BASE_URL" in msg or "https" in msg


def test_refresh_rejects_garbage(client: TestClient, mock_db):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-jwt"})
    assert resp.status_code == 401


@patch("app.api.v1.auth.verify_firebase_token")
def test_refresh_rejects_access_token(mock_verify, client: TestClient, mock_db):
    mock_verify.return_value = FIREBASE_CLAIMS
    exchange = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    access_token = exchange.json()["tokens"]["access_token"]

    # An access (session) token is not a refresh token.
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
def test_me_returns_bare_user_response(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = FIREBASE_CLAIMS
    mock_db.add(sample_user)

    resp = client.get("/api/v1/me", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    # Bare UserResponse — no {"ok": ..., "user": ...} envelope.
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert "is_active" in data
    assert "ok" not in data


@patch("app.dependencies.auth.verify_firebase_token")
def test_patch_me_updates_display_name(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = FIREBASE_CLAIMS
    mock_db.add(sample_user)

    resp = client.patch(
        "/api/v1/me",
        json={"display_name": "Renamed User"},
        headers=AUTH,
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Renamed User"


@patch("app.dependencies.auth.verify_firebase_token")
def test_avatar_upload_url_and_confirm(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = FIREBASE_CLAIMS
    mock_db.add(sample_user)

    upload = client.post(
        "/api/v1/me/avatar/upload-url",
        json={"content_type": "image/jpeg", "byte_size": 12345},
        headers=AUTH,
    )
    assert upload.status_code == 200
    storage_path = upload.json()["storage_path"]
    assert storage_path

    confirm = client.patch(
        "/api/v1/me/avatar",
        json={"storage_path": storage_path},
        headers=AUTH,
    )
    assert confirm.status_code == 200
    assert confirm.json()["photo_url"].endswith(storage_path)
