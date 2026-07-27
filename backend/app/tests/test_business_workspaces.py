"""Tests for multi-company Business workspaces."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.domains.business.workspace_service import MODULE_TILES, BusinessWorkspaceService
from app.domains.preferences.models import UserPreferencesModel
from app.domains.users.models import UserModel
from app.tests.conftest import MOCK_USER_ID

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


@pytest.mark.asyncio
async def test_create_workspace_makes_owner_member(mock_db):
    svc = BusinessWorkspaceService(mock_db)
    created = await svc.create_workspace(MOCK_USER_ID, name="Pureborn")
    assert created["name"] == "Pureborn"
    assert created["role"] == "OWNER"
    assert created["currency"] == "INR"

    memberships = await svc.list_memberships(MOCK_USER_ID)
    assert len(memberships) == 1
    assert memberships[0][0].name == "Pureborn"
    assert memberships[0][1].role == "OWNER"


@pytest.mark.asyncio
async def test_second_workspace_allowed(mock_db):
    svc = BusinessWorkspaceService(mock_db)
    a = await svc.create_workspace(MOCK_USER_ID, name="Pureborn")
    b = await svc.create_workspace(MOCK_USER_ID, name="Monytix")
    assert a["id"] != b["id"]
    memberships = await svc.list_memberships(MOCK_USER_ID)
    assert len(memberships) == 2
    names = {m[0].name for m in memberships}
    assert names == {"Pureborn", "Monytix"}


@pytest.mark.asyncio
async def test_select_and_resolve_workspace(mock_db):
    pref = UserPreferencesModel(
        id=uuid4(),
        user_id=MOCK_USER_ID,
        selected_context="BUSINESS",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.add(pref)

    svc = BusinessWorkspaceService(mock_db)
    first = await svc.create_workspace(MOCK_USER_ID, name="Pureborn")
    second = await svc.create_workspace(MOCK_USER_ID, name="Monytix")
    selected = await svc.select_workspace(MOCK_USER_ID, UUID(second["id"]))
    assert selected["name"] == "Monytix"

    resolved = await svc.resolve_selected(MOCK_USER_ID)
    assert resolved is not None
    assert str(resolved[0].workspace_id) == second["id"]

    resolved2 = await svc.resolve_selected(MOCK_USER_ID, workspace_id=UUID(first["id"]))
    assert resolved2 is not None
    assert str(resolved2[0].workspace_id) == first["id"]


@pytest.mark.asyncio
async def test_invite_and_accept(mock_db):
    svc = BusinessWorkspaceService(mock_db)
    created = await svc.create_workspace(MOCK_USER_ID, name="Pureborn")
    ws_id = UUID(created["id"])
    invite = await svc.invite_member(MOCK_USER_ID, ws_id, email="ca@example.com", role="MEMBER")
    assert invite["token"]
    assert invite["status"] == "PENDING"
    assert invite["invite_link"].endswith(f"/company-invite/{invite['token']}")
    assert invite["qr_payload"] == invite["invite_link"]

    other = uuid4()
    joined = await svc.accept_invite(other, invite["token"])
    assert joined["name"] == "Pureborn"
    assert joined["role"] == "MEMBER"

    members = await svc.list_members(MOCK_USER_ID, ws_id)
    user_ids = {m["user_id"] for m in members}
    assert str(MOCK_USER_ID) in user_ids
    assert str(other) in user_ids


@pytest.mark.asyncio
async def test_module_tiles_coming_soon():
    assert all(t["status"] == "coming_soon" for t in MODULE_TILES)
    keys = {t["key"] for t in MODULE_TILES}
    assert {"finance", "inventory", "sales", "gst"} <= keys


@patch("app.dependencies.auth.verify_firebase_token")
def test_workspace_api_create_and_bootstrap(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    r = client.post(
        "/api/v1/business/workspaces",
        json={"name": "Pureborn", "currency_code": "INR"},
        headers=AUTH,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["name"] == "Pureborn"
    assert body["role"] == "OWNER"
    ws_id = body["id"]

    boot = client.get("/api/v1/business/session/bootstrap", headers=AUTH)
    assert boot.status_code == 200, boot.text
    data = boot.json()
    assert data["selected_workspace"] is not None
    assert data["selected_workspace"]["id"] == ws_id
    assert data["selected_workspace"]["name"] == "Pureborn"
    assert len(data["workspaces"]) >= 1
    assert data["module_tiles"]
    assert data["dashboard"]["member_count"] >= 1

    created = client.post(
        "/api/v1/business/moments",
        json={
            "moment_type_code": "TEAM_OPERATIONS",
            "title": "Ops",
            "workspace_id": ws_id,
        },
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]
    assert moment_id

    boot2 = client.get(
        f"/api/v1/business/session/bootstrap?workspace_id={ws_id}",
        headers=AUTH,
    )
    assert boot2.status_code == 200
    moments = boot2.json().get("moments") or []
    assert any(m["moment_id"] == moment_id for m in moments)


@patch("app.dependencies.auth.verify_firebase_token")
def test_owner_can_update_workspace(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    r = client.post(
        "/api/v1/business/workspaces",
        json={"name": "Cafe"},
        headers=AUTH,
    )
    assert r.status_code == 201
    ws_id = r.json()["id"]

    patch_resp = client.patch(
        f"/api/v1/business/workspaces/{ws_id}",
        json={"name": "Cafe Renamed"},
        headers=AUTH,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Cafe Renamed"
