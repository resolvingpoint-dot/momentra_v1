from __future__ import annotations

import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domains.group.experience_types.registry import ExperienceTypeRegistry
from app.domains.group.projection_cache import (
    get_cached_envelope,
    get_cached_slice,
    invalidate_group_projections,
)
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create_experience(client: TestClient) -> str:
    created = client.post(
        "/api/v1/group/shared-experience/moments",
        json={"experience_profile": "TRIP_VACATION"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]
    client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={"experience_profile": "TRIP_VACATION", "moment_name": "Goa 2026"},
        headers=AUTH,
    )
    return moment_id


@patch("app.dependencies.auth.verify_firebase_token")
def test_experience_type_changes_pulse_copy(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)
    client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={"experience_profile": "WEDDING", "moment_name": "Our Wedding"},
        headers=AUTH,
    )
    resp = client.get(f"/api/v1/group/trips/{moment_id}/pulse", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    wedding = ExperienceTypeRegistry.get("WEDDING")
    assert data["readiness_title"] == wedding.pulse_readiness_title
    assert data["readiness_narrative"] == wedding.pulse_readiness_narrative


@patch("app.dependencies.auth.verify_firebase_token")
def test_activity_expense_updates_pulse_stats(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)
    before = client.get(f"/api/v1/group/trips/{moment_id}/pulse", headers=AUTH).json()
    assert before["stats"]["total_expenses_minor"] == 0

    created = client.post(
        f"/api/v1/group/trips/{moment_id}/expenses",
        json={"description": "Dinner", "amount_minor": 250000, "currency_code": "INR"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text

    after = client.get(
        f"/api/v1/group/trips/{moment_id}/pulse",
        headers=AUTH,
    ).json()
    assert after["stats"]["total_expenses_minor"] == 250000


@patch("app.dependencies.auth.verify_firebase_token")
def test_quick_add_booking_updates_pulse_bookings_and_spent(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Bookings write `booking_status` (not `status`); hero KPIs must still update."""
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)

    created = client.post(
        f"/api/v1/group/trips/{moment_id}/quick-add/booking",
        json={
            "booking_type": "flight",
            "provider": "Air India",
            "title": "Air India",
            "booking_status": "confirmed",
            "amount_minor": 1500000,
        },
        headers=AUTH,
    )
    assert created.status_code in {200, 201}, created.text

    pulse = client.get(
        f"/api/v1/group/trips/{moment_id}/pulse?force_refresh=true",
        headers=AUTH,
    ).json()
    assert pulse["stats"]["confirmed_bookings"] >= 1
    assert pulse["stats"]["total_expenses_minor"] >= 1500000
    recent = pulse.get("dashboard_card", {}).get("recent_items") or []
    assert any("air india" in str(item.get("title", "")).lower() for item in recent)


@patch("app.dependencies.auth.verify_firebase_token")
def test_booking_status_only_counts_in_pulse(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Legacy rows with only booking_status (no status) must count as bookings."""
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)
    from app.domains.group import moment_store as store

    moment = mock_db._get_from_store("moments", moment_id)
    store.append_item(
        moment,
        "bookings",
        {
            "id": "b-legacy",
            "title": "Hotel Taj",
            "booking_status": "planned",
            "amount_minor": 500000,
            "created_at": store.now_iso(),
        },
    )

    pulse = client.get(
        f"/api/v1/group/trips/{moment_id}/pulse?force_refresh=true",
        headers=AUTH,
    ).json()
    assert pulse["stats"]["confirmed_bookings"] >= 1
    assert pulse["stats"]["total_expenses_minor"] >= 500000


@patch("app.dependencies.auth.verify_firebase_token")
def test_memory_create_appears_in_memory_projection(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)
    client.post(
        f"/api/v1/group/trips/{moment_id}/memories",
        json={"title": "Sunset", "note": "Beach"},
        headers=AUTH,
    )
    listed = client.get(f"/api/v1/group/trips/{moment_id}/memories", headers=AUTH)
    assert len(listed.json()) == 1
    assert listed.json()[0]["title"] == "Sunset"


@patch("app.dependencies.auth.verify_firebase_token")
@pytest.mark.asyncio
async def test_redis_invalidate_on_write(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)
    user_id = sample_user.id
    mid = uuid.UUID(moment_id)
    pulse = client.get(f"/api/v1/group/trips/{moment_id}/pulse", headers=AUTH).json()
    cached = await get_cached_slice(user_id, mid, "pulse")
    assert cached is not None
    assert cached["readiness_title"] == pulse["readiness_title"]

    await invalidate_group_projections(user_id, mid, reason="test")
    # Invalidate marks stale (SWR); payload may still be readable until rebuild.
    envelope = await get_cached_envelope(user_id, mid, "pulse")
    assert envelope is not None
    assert envelope.stale is True


@patch("app.dependencies.auth.verify_firebase_token")
def test_legacy_trip_routes_still_work(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_experience(client)
    hub = client.get(f"/api/v1/group/trips/{moment_id}/live-hub", headers=AUTH)
    assert hub.status_code == 200
    assert hub.json()["quick_add_modules"]
