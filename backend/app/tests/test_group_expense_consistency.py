"""Group expense consistency — creator membership, currency, shares, edit/delete."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

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
    return created.json()["moment_id"]


def _activate(client: TestClient, moment_id: str, *, currency: str = "INR", allow_multi: bool = True) -> None:
    draft = client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={
            "answers": {
                "moment_name": "Goa Trip",
                "currency_code": currency,
                "allow_multi_currency": allow_multi,
                "money_tracking_mode": "EQUAL_SPLIT",
            }
        },
        headers=AUTH,
    )
    assert draft.status_code == 200, draft.text
    activate = client.post(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert activate.status_code == 200, activate.text


@patch("app.dependencies.auth.verify_firebase_token")
def test_activate_upserts_creator_organizer_in_expense_context(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create_experience(client)
    _activate(client, mid)

    ctx = client.get(f"/api/v1/group/trips/{mid}/quick-add/expense/context", headers=AUTH)
    assert ctx.status_code == 200, ctx.text
    data = ctx.json()
    payers = data.get("payers") or []
    assert payers, "creator must appear as payer after activate"
    assert any(p.get("id") == str(sample_user.id) for p in payers)
    assert data.get("default_paid_by_participant_id") == str(sample_user.id)
    assert data.get("default_currency_code") == "INR"
    assert data.get("allow_multi_currency") is True
    codes = {c.get("id") for c in data.get("currencies") or []}
    assert "INR" in codes and "JPY" in codes and "KWD" in codes
    assert len(codes) > 3


@patch("app.dependencies.auth.verify_firebase_token")
def test_expense_create_equal_shares_and_idempotent(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create_experience(client)
    _activate(client, mid, currency="USD")
    uid = str(sample_user.id)

    body = {
        "title": "Dinner",
        "amount_minor": 3000,
        "currency_code": "USD",
        "paid_by_participant_id": uid,
        "participant_ids": [uid],
        "split_style": "EQUAL",
        "client_request_id": "req-dinner-1",
        "category_code": "food",
        "notes": "beach shack",
    }
    exp = client.post(f"/api/v1/group/trips/{mid}/expenses", json=body, headers=AUTH)
    assert exp.status_code == 201, exp.text
    data = exp.json()
    assert data["title"] == "Dinner"
    assert data["amount_minor"] == 3000
    assert data["currency_code"] == "USD"
    assert data["shares"] == [{"member_id": uid, "amount_minor": 3000}]
    assert data["paid_by_participant_id"] == uid
    eid = data["id"]

    replay = client.post(f"/api/v1/group/trips/{mid}/expenses", json=body, headers=AUTH)
    assert replay.status_code == 201, replay.text
    assert replay.json()["id"] == eid


@patch("app.dependencies.auth.verify_firebase_token")
def test_expense_rejects_currency_when_multi_disabled(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create_experience(client)
    _activate(client, mid, currency="INR", allow_multi=False)
    uid = str(sample_user.id)

    bad = client.post(
        f"/api/v1/group/trips/{mid}/expenses",
        json={
            "title": "Sushi",
            "amount_minor": 1000,
            "currency_code": "JPY",
            "paid_by_participant_id": uid,
            "participant_ids": [uid],
        },
        headers=AUTH,
    )
    assert bad.status_code == 422, bad.text

    ok = client.post(
        f"/api/v1/group/trips/{mid}/expenses",
        json={
            "title": "Chai",
            "amount_minor": 5000,
            "currency_code": "INR",
            "paid_by_participant_id": uid,
            "participant_ids": [uid],
        },
        headers=AUTH,
    )
    assert ok.status_code == 201, ok.text


@patch("app.dependencies.auth.verify_firebase_token")
def test_expense_exact_percentage_shares_and_edit_delete(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create_experience(client)
    _activate(client, mid)
    uid = str(sample_user.id)
    # Simulate a second accepted member in runtime via guest+member dual path:
    # add guest then expense with only creator is still valid; for multi-participant
    # we inject via a second expense participant by posting a guest first.
    guest = client.post(
        f"/api/v1/group/trips/{mid}/guests",
        json={"full_name": "Alex", "relationship_type": "friend", "status": "active"},
        headers=AUTH,
    )
    # guests endpoint may or may not exist — if missing, test EQUAL with one member only
    alex_id = None
    if guest.status_code in (200, 201):
        alex_id = guest.json().get("id")

    exact = client.post(
        f"/api/v1/group/trips/{mid}/expenses",
        json={
            "title": "Cab",
            "amount_minor": 1000,
            "currency_code": "INR",
            "paid_by_participant_id": uid,
            "participant_ids": [uid],
            "split_style": "EXACT",
            "split_details": {uid: 1000},
        },
        headers=AUTH,
    )
    assert exact.status_code == 201, exact.text
    assert sum(s["amount_minor"] for s in exact.json()["shares"]) == 1000

    pct = client.post(
        f"/api/v1/group/trips/{mid}/expenses",
        json={
            "title": "Snacks",
            "amount_minor": 200,
            "currency_code": "INR",
            "paid_by_participant_id": uid,
            "participant_ids": [uid],
            "split_style": "PERCENTAGE",
            "split_details": {uid: 100},
        },
        headers=AUTH,
    )
    assert pct.status_code == 201, pct.text
    assert pct.json()["shares"][0]["amount_minor"] == 200

    shares_exp = client.post(
        f"/api/v1/group/trips/{mid}/expenses",
        json={
            "title": "Gear",
            "amount_minor": 900,
            "currency_code": "INR",
            "paid_by_participant_id": uid,
            "participant_ids": [uid],
            "split_style": "SHARES",
            "split_details": {uid: 3},
        },
        headers=AUTH,
    )
    assert shares_exp.status_code == 201, shares_exp.text
    assert shares_exp.json()["shares"][0]["amount_minor"] == 900

    eid = exact.json()["id"]
    patched = client.patch(
        f"/api/v1/group/trips/{mid}/expenses/{eid}",
        json={
            "title": "Airport Cab",
            "amount_minor": 1500,
            "currency_code": "INR",
            "paid_by_participant_id": uid,
            "participant_ids": [uid],
            "split_style": "EQUAL",
        },
        headers=AUTH,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["title"] == "Airport Cab"
    assert patched.json()["amount_minor"] == 1500
    assert patched.json()["shares"][0]["amount_minor"] == 1500

    deleted = client.delete(f"/api/v1/group/trips/{mid}/expenses/{eid}", headers=AUTH)
    assert deleted.status_code == 200, deleted.text
    listed = client.get(f"/api/v1/group/trips/{mid}/expenses", headers=AUTH)
    assert listed.status_code == 200
    assert all(row["id"] != eid for row in listed.json())
    _ = alex_id  # reserved for multi-member extension


@patch("app.dependencies.auth.verify_firebase_token")
def test_jpy_zero_decimal_amount(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create_experience(client)
    _activate(client, mid, currency="JPY", allow_multi=True)
    uid = str(sample_user.id)
    exp = client.post(
        f"/api/v1/group/trips/{mid}/expenses",
        json={
            "title": "Ramen",
            "amount_minor": 1200,
            "currency_code": "JPY",
            "paid_by_participant_id": uid,
            "participant_ids": [uid],
            "split_style": "EQUAL",
        },
        headers=AUTH,
    )
    assert exp.status_code == 201, exp.text
    assert exp.json()["currency_code"] == "JPY"
    assert exp.json()["amount_minor"] == 1200
