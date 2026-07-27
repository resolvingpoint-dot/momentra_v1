from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create(client: TestClient, category: str, profile_key: str, profile_code: str) -> str:
    created = client.post(
        f"/api/v1/group/{category}/moments",
        json={profile_key: profile_code},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    return created.json()["moment_id"]


# ----- shared-purchase ---------------------------------------------------- #
@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_read_surfaces(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create(client, "shared-purchase", "purchase_profile", "GIFT_POOL")

    live = client.get(f"/api/v1/group/shared-purchase/moments/{mid}/live-hub", headers=AUTH)
    assert live.status_code == 200, live.text
    assert live.json()["selector"]["moment_id"] == mid
    assert live.json()["header"]["moment_name"] and live.json()["insight"]["title"]

    pulse = client.get(f"/api/v1/group/shared-purchase/moments/{mid}/pulse", headers=AUTH)
    assert pulse.status_code == 200
    assert "contributors_joined" in pulse.json()["stats"]

    mv = client.get(f"/api/v1/group/shared-purchase/moments/{mid}/moments-view", headers=AUTH)
    assert mv.status_code == 200
    assert mv.json()["operations_hub"]["core_summary"]["moment_name"]
    assert mv.json()["memory_hub"]["hero"]["moment_name"]
    assert mv.json()["next_best_action"]["title"]


@pytest.mark.parametrize(
    "module",
    [
        "vendors",
        "updates",
        "ownership",
        "delivery",
        "contributors",
        "participants",
        "purchase-items",
        "expenses",
        "polls",
        "memories",
    ],
)
@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_quick_add(mock_verify, client: TestClient, mock_db, sample_user: UserModel, module):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create(client, "shared-purchase", "purchase_profile", "GIFT_POOL")

    ctx = client.get(f"/api/v1/group/shared-purchase/moments/{mid}/quick-add/{module}/context", headers=AUTH)
    assert ctx.status_code == 200, ctx.text
    assert ctx.json()["moment_id"] == mid

    created = client.post(f"/api/v1/group/shared-purchase/moments/{mid}/quick-add/{module}", json={}, headers=AUTH)
    assert created.status_code == 201, created.text


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_quick_add_hub_has_sections(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create(client, "shared-purchase", "purchase_profile", "GIFT_POOL")
    hub = client.get(f"/api/v1/group/shared-purchase/moments/{mid}/quick-add/hub", headers=AUTH)
    assert hub.status_code == 200, hub.text
    assert len(hub.json().get("sections") or []) >= 1
    cfg = client.get(f"/api/v1/group/quickadd/{mid}", headers=AUTH)
    assert cfg.status_code == 200
    cats = cfg.json().get("categories") or []
    assert len(cats) >= 1
    assert any(m.get("module_code") for c in cats for m in c.get("modules") or [])


# ----- shared-living ------------------------------------------------------ #
@patch("app.dependencies.auth.verify_firebase_token")
def test_living_read_surfaces(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create(client, "shared-living", "living_type", "FLATMATES")

    live = client.get(f"/api/v1/group/shared-living/moments/{mid}/live-hub", headers=AUTH)
    assert live.status_code == 200, live.text
    assert live.json()["selector"]["moment_id"] == mid

    pulse = client.get(f"/api/v1/group/shared-living/moments/{mid}/pulse", headers=AUTH)
    assert pulse.status_code == 200
    assert "residents_joined" in pulse.json()["stats"]

    mv = client.get(f"/api/v1/group/shared-living/moments/{mid}/moments-view", headers=AUTH)
    assert mv.status_code == 200
    assert mv.json()["operations_hub"]["core_summary"]["moment_name"]


@pytest.mark.parametrize(
    "module",
    ["residents", "expenses", "contributions", "tasks", "rules", "assets", "maintenance", "updates", "polls", "memories"],
)
@patch("app.dependencies.auth.verify_firebase_token")
def test_living_quick_add(mock_verify, client: TestClient, mock_db, sample_user: UserModel, module):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create(client, "shared-living", "living_type", "FLATMATES")

    ctx = client.get(f"/api/v1/group/shared-living/moments/{mid}/quick-add/{module}/context", headers=AUTH)
    assert ctx.status_code == 200, ctx.text
    assert ctx.json()["moment_id"] == mid
    assert ctx.json()["living_name"]

    created = client.post(f"/api/v1/group/shared-living/moments/{mid}/quick-add/{module}", json={}, headers=AUTH)
    assert created.status_code == 201, created.text


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_resident_context_has_invite(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create(client, "shared-living", "living_type", "FLATMATES")

    ctx = client.get(f"/api/v1/group/shared-living/moments/{mid}/quick-add/residents/context", headers=AUTH)
    assert ctx.status_code == 200
    assert ctx.json()["invite"]["share_message"]
