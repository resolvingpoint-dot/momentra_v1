"""End-to-end smoke tests mirroring Android Group flows (setup → activate → reads → writes)."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _setup_flow(client: TestClient, category: str, profile_key: str, profile_code: str, name: str) -> str:
    created = client.post(
        f"/api/v1/group/{category}/moments",
        json={profile_key: profile_code},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    mid = created.json()["moment_id"]

    draft_key = {
        "shared-experience": "experience_profile",
        "shared-purchase": "purchase_profile",
        "shared-living": "living_type",
    }[category]
    client.put(
        f"/api/v1/group/{category}/moments/{mid}/setup/draft",
        json={draft_key: profile_code, "moment_name": name},
        headers=AUTH,
    )
    activated = client.post(f"/api/v1/group/{category}/moments/{mid}/setup/activate", headers=AUTH)
    assert activated.status_code == 200, activated.text
    return mid


def _assert_ops_hub(data: dict) -> None:
    hub = data["operations_hub"]
    assert hub["core_summary"]["moment_name"]
    assert hub["money_status"]["progress_label"]
    assert isinstance(hub["activity_ops"], list)
    assert isinstance(hub["assets"], list)
    assert isinstance(hub["decisions"], list)
    assert isinstance(hub["current_state"]["focus_items"], list)


@pytest.mark.parametrize(
    "category,profile_key,profile_code,name,read_prefix",
    [
        ("shared-experience", "experience_profile", "TRIP_VACATION", "Goa 2026", "trips"),
        ("shared-purchase", "purchase_profile", "GIFT_POOL", "Birthday Gift", "shared-purchase"),
        ("shared-living", "living_type", "FLATMATES", "Our Flat", "shared-living"),
    ],
)
@patch("app.dependencies.auth.verify_firebase_token")
def test_full_group_flow_smoke(
    mock_verify,
    client: TestClient,
    mock_db,
    sample_user: UserModel,
    category,
    profile_key,
    profile_code,
    name,
    read_prefix,
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _setup_flow(client, category, profile_key, profile_code, name)

    if read_prefix == "trips":
        live = client.get(f"/api/v1/group/trips/{mid}/live-hub", headers=AUTH)
        assert live.status_code == 200, live.text
        assert live.json()["header"]["moment_name"] == name
        assert live.json()["experience_profile"]["title"]

        pulse = client.get(f"/api/v1/group/trips/{mid}/pulse", headers=AUTH)
        assert pulse.status_code == 200
        assert pulse.json()["trip_name"] == name

        mv = client.get(f"/api/v1/group/trips/{mid}/moments-view", headers=AUTH)
        assert mv.status_code == 200
        _assert_ops_hub(mv.json())

        ws = client.get(f"/api/v1/group/trips/{mid}/live-workspace", headers=AUTH)
        assert ws.status_code == 200
        assert ws.json()["header"]["moment_name"] == name
    else:
        live = client.get(f"/api/v1/group/{read_prefix}/moments/{mid}/live-hub", headers=AUTH)
        assert live.status_code == 200, live.text
        assert live.json()["header"]["moment_name"] == name

        pulse = client.get(f"/api/v1/group/{read_prefix}/moments/{mid}/pulse", headers=AUTH)
        assert pulse.status_code == 200
        assert pulse.json()["moment_name"] == name

        mv = client.get(f"/api/v1/group/{read_prefix}/moments/{mid}/moments-view", headers=AUTH)
        assert mv.status_code == 200
        _assert_ops_hub(mv.json())


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_guest_expense_persist_roundtrip(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _setup_flow(client, "shared-experience", "experience_profile", "TRIP_VACATION", "Persist Trip")

    guest = client.post(
        f"/api/v1/group/trips/{mid}/guests",
        json={"full_name": "Sam Guest", "relationship_type": "friend"},
        headers=AUTH,
    )
    assert guest.status_code == 201, guest.text

    expense = client.post(
        f"/api/v1/group/trips/{mid}/expenses",
        json={
            "paid_by_user_id": str(sample_user.id),
            "amount_minor": 12500,
            "description": "Dinner",
            "currency_code": "INR",
        },
        headers=AUTH,
    )
    assert expense.status_code == 201, expense.text

    listed = client.get(f"/api/v1/group/trips/{mid}/expenses", headers=AUTH)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["amount_minor"] == 12500

    pulse = client.get(f"/api/v1/group/trips/{mid}/pulse", headers=AUTH)
    assert pulse.status_code == 200
    assert pulse.json()["stats"]["total_expenses_minor"] == 12500

    ctx = client.get(f"/api/v1/group/trips/{mid}/quick-add/participant/context", headers=AUTH)
    assert ctx.status_code == 200
    guests = ctx.json()["guests"]
    assert any(g.get("full_name") == "Sam Guest" for g in guests)


@patch("app.dependencies.auth.verify_firebase_token")
def test_living_resident_expense_persist(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _setup_flow(client, "shared-living", "living_type", "FLATMATES", "Persist Home")

    resident = client.post(
        f"/api/v1/group/shared-living/moments/{mid}/quick-add/residents",
        json={"full_name": "Alex", "relationship_type": "roommate", "status": "active"},
        headers=AUTH,
    )
    assert resident.status_code == 201, resident.text

    expense = client.post(
        f"/api/v1/group/shared-living/moments/{mid}/quick-add/expenses",
        json={"description": "Rent", "amount_major": "12000", "currency_code": "INR", "split_type": "equal"},
        headers=AUTH,
    )
    assert expense.status_code == 201, expense.text

    pulse = client.get(f"/api/v1/group/shared-living/moments/{mid}/pulse", headers=AUTH)
    assert pulse.status_code == 200
    # Creator from activate + Alex from quick-add.
    assert pulse.json()["stats"]["residents_joined"] >= 1
    assert pulse.json()["stats"]["total_expenses_minor"] == 1200000
