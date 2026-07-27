from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH_HEADERS = {"Authorization": "Bearer fake-token"}
AUTH_USER = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _setup_auth(mock_verify, mock_db, sample_user: UserModel) -> None:
    mock_verify.return_value = AUTH_USER
    mock_db.add(sample_user)


def _create_shared_moment(
    client: TestClient,
    *,
    context_type: str = "MY_MONEY",
    title: str = "Test Moment",
) -> dict:
    resp = client.post(
        "/api/v1/moments",
        json={"context_type": context_type, "title": title},
        headers=AUTH_HEADERS,
    )
    assert resp.status_code == 200
    return resp.json()


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_moment_my_money(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _setup_auth(mock_verify, mock_db, sample_user)

    resp = client.post(
        "/api/v1/moments",
        json={"context_type": "MY_MONEY", "title": "First Money Moment"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["context_type"] == "MY_MONEY"
    assert data["title"] == "First Money Moment"
    assert data["status"] == "DRAFT"
    assert data["setup_state"] == "ACTIVE"


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_moment_group(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/moments",
        json={"context_type": "GROUP", "title": "Group Moment"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["context_type"] == "GROUP"


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_moment_business(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/moments",
        json={"context_type": "BUSINESS", "title": "Biz Moment"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["context_type"] == "BUSINESS"


@patch("app.dependencies.auth.verify_firebase_token")
def test_cannot_create_circle_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/moments",
        json={"context_type": "CIRCLE", "title": "Circle Moment"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 422


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_moment_without_title_sets_setup(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/moments",
        json={"context_type": "MY_MONEY"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["setup_state"] == "SETUP"


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_moment_updates_module_state(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/moments",
        json={"context_type": "MY_MONEY", "title": "Test"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    assert any(
        ms.state == "ACTIVE" and "MY_MONEY" in key
        for key, ms in mock_db._stores["module_states"].items()
    )


@patch("app.dependencies.auth.verify_firebase_token")
def test_moments_home_empty(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/moments/home",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert data["total_pages"] == 1
    assert data["items"] == []


@patch("app.dependencies.auth.verify_firebase_token")
def test_moments_home_pagination(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/moments/home?page=1&per_page=5",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["per_page"] == 5


@patch("app.dependencies.auth.verify_firebase_token")
def test_my_money_home(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/my-money/home",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["context"] == "MY_MONEY"
    assert "primary_cta" in data


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_home(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/group/home",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["context"] == "GROUP"


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_home(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/business/home",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["context"] == "BUSINESS"


@patch("app.dependencies.auth.verify_firebase_token")
def test_circle_home(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/circle/home",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["context"] == "CIRCLE"


@patch("app.dependencies.auth.verify_firebase_token")
def test_life360_home(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/life360/home",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["module"] == "LIFE360"


@patch("app.dependencies.auth.verify_firebase_token")
def test_memory_home(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/memory/home",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["module"] == "MEMORY"


@patch("app.dependencies.auth.verify_firebase_token")
def test_patch_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _setup_auth(mock_verify, mock_db, sample_user)
    created = _create_shared_moment(client)
    moment_id = created["id"]

    resp = client.patch(
        f"/api/v1/moments/{moment_id}",
        json={"title": "Updated Title", "description": "New description"},
        headers=AUTH_HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "New description"


@patch("app.dependencies.auth.verify_firebase_token")
def test_delete_moment_draft(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _setup_auth(mock_verify, mock_db, sample_user)
    created = _create_shared_moment(client)
    moment_id = created["id"]

    resp = client.delete(f"/api/v1/moments/{moment_id}", headers=AUTH_HEADERS)
    assert resp.status_code == 204

    get_resp = client.get(f"/api/v1/moments/{moment_id}", headers=AUTH_HEADERS)
    assert get_resp.status_code == 404


@patch("app.dependencies.auth.verify_firebase_token")
def test_cannot_delete_active_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _setup_auth(mock_verify, mock_db, sample_user)
    created = _create_shared_moment(client)
    moment_id = created["id"]

    activate_resp = client.post(
        f"/api/v1/moments/{moment_id}/activate",
        headers=AUTH_HEADERS,
    )
    assert activate_resp.status_code == 200

    delete_resp = client.delete(f"/api/v1/moments/{moment_id}", headers=AUTH_HEADERS)
    assert delete_resp.status_code == 409


@patch("app.dependencies.auth.verify_firebase_token")
def test_activate_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _setup_auth(mock_verify, mock_db, sample_user)
    created = _create_shared_moment(client)
    moment_id = created["id"]
    assert created["status"] == "DRAFT"

    resp = client.post(f"/api/v1/moments/{moment_id}/activate", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACTIVE"


@patch("app.dependencies.auth.verify_firebase_token")
def test_complete_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _setup_auth(mock_verify, mock_db, sample_user)
    created = _create_shared_moment(client)
    moment_id = created["id"]

    client.post(f"/api/v1/moments/{moment_id}/activate", headers=AUTH_HEADERS)

    resp = client.post(f"/api/v1/moments/{moment_id}/complete", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"


@patch("app.dependencies.auth.verify_firebase_token")
def test_archive_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _setup_auth(mock_verify, mock_db, sample_user)
    created = _create_shared_moment(client)
    moment_id = created["id"]

    resp = client.post(f"/api/v1/moments/{moment_id}/archive", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ARCHIVED"
