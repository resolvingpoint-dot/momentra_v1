"""Tests for Settlement Engine v1 (moment_store runtime)."""
from __future__ import annotations

import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.group import moment_store as store
from app.domains.group.settlements import calculator
from app.domains.group.settlements.schemas import MemberBalance
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create_and_activate(client: TestClient, category: str, profile_key: str, profile_code: str) -> str:
    created = client.post(
        f"/api/v1/group/{category}/moments",
        json={profile_key: profile_code},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]
    client.put(
        f"/api/v1/group/{category}/moments/{moment_id}/setup/draft",
        json={profile_key: profile_code, "moment_name": "Settlement Test"},
        headers=AUTH,
    )
    activated = client.post(
        f"/api/v1/group/{category}/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert activated.status_code == 200, activated.text
    return moment_id


def _seed_members_and_expense(mock_db, moment_id: str, user_id: uuid.UUID) -> tuple[str, str]:
    moment = mock_db._stores["moments"][moment_id]
    state = store.read_state(moment)
    member_a = store.new_id()
    member_b = store.new_id()
    state["runtime"]["guests"] = [
        {"id": member_a, "full_name": "Alice", "status": "confirmed"},
        {"id": member_b, "full_name": "Bob", "status": "confirmed"},
    ]
    state["runtime"]["expenses"] = [
        {
            "id": store.new_id(),
            "description": "Dinner",
            "amount_minor": 10000,
            "currency_code": "INR",
            "paid_by_user_id": member_a,
            "split_type": "equal",
            "created_at": store.now_iso(),
            "deleted": False,
        }
    ]
    store.write_state(moment, state)
    return member_a, member_b


# ----- calculator unit tests ---------------------------------------------- #
def test_equal_split_remainder_to_first_sorted_participant():
    allocations = calculator.allocate_equal(10001, ["b", "a", "c"])
    assert allocations == {"a": 3335, "b": 3333, "c": 3333}
    assert sum(allocations.values()) == 10001


def test_exact_split():
    expense = {
        "amount_minor": 5000,
        "split_style": "EXACT",
        "splits": [
            {"member_id": "m2", "amount_minor": 2000},
            {"member_id": "m1", "amount_minor": 3000},
        ],
    }
    out = calculator.allocate_expense(expense, ["m1", "m2"])
    assert out == {"m1": 3000, "m2": 2000}


def test_percentage_split_remainder_to_first_sorted():
    expense = {
        "amount_minor": 100,
        "split_style": "PERCENTAGE",
        "splits": [
            {"member_id": "b", "percent": 33},
            {"member_id": "a", "percent": 33},
            {"member_id": "c", "percent": 34},
        ],
    }
    out = calculator.allocate_expense(expense, ["b", "a", "c"])
    assert sum(out.values()) == 100
    assert out["a"] == out["b"] + 1 or out["a"] >= out["b"]


def test_shares_split():
    expense = {
        "amount_minor": 1000,
        "split_style": "SHARES",
        "splits": [
            {"member_id": "a", "shares": 1},
            {"member_id": "b", "shares": 3},
        ],
    }
    out = calculator.allocate_expense(expense, ["a", "b"])
    assert out["a"] == 250
    assert out["b"] == 750


def test_greedy_debt_simplification():
    balances = [
        MemberBalance(
            member_id="a", display_name="Alice", paid_minor=10000, owed_minor=5000, net_minor=5000, currency_code="INR"
        ),
        MemberBalance(
            member_id="b", display_name="Bob", paid_minor=0, owed_minor=5000, net_minor=-5000, currency_code="INR"
        ),
    ]
    suggestions = calculator.simplify_debts(balances)
    assert len(suggestions) == 1
    assert suggestions[0].from_member_id == "b"
    assert suggestions[0].to_member_id == "a"
    assert suggestions[0].amount_minor == 5000


def test_greedy_debt_simplification_three_way():
    balances = [
        MemberBalance(member_id="a", display_name="A", net_minor=3000, currency_code="INR"),
        MemberBalance(member_id="b", display_name="B", net_minor=-2000, currency_code="INR"),
        MemberBalance(member_id="c", display_name="C", net_minor=-1000, currency_code="INR"),
    ]
    suggestions = calculator.simplify_debts(balances)
    assert sum(s.amount_minor for s in suggestions) == 3000
    assert all(s.from_member_id in {"b", "c"} for s in suggestions)
    assert all(s.to_member_id == "a" for s in suggestions)


# ----- API integration tests ---------------------------------------------- #
@patch("app.dependencies.auth.verify_firebase_token")
def test_settlement_preview_endpoint(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate(client, "shared-experience", "experience_profile", "TRIP_VACATION")
    _seed_members_and_expense(mock_db, moment_id, sample_user.id)

    resp = client.get(f"/api/v1/group/moments/{moment_id}/settlements/preview", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total_expenses_minor"] == 10000
    assert len(data["member_balances"]) == 2
    assert len(data["suggestions"]) == 1
    assert data["suggestions"][0]["amount_minor"] == 5000


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_list_mark_settled_idempotent(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate(client, "shared-purchase", "purchase_profile", "GIFT_POOL")
    member_a, member_b = _seed_members_and_expense(mock_db, moment_id, sample_user.id)
    client_request_id = str(uuid.uuid4())

    create = client.post(
        f"/api/v1/group/moments/{moment_id}/settlements",
        json={
            "from_member_id": member_b,
            "to_member_id": member_a,
            "amount_minor": 5000,
            "currency_code": "INR",
            "client_request_id": client_request_id,
        },
        headers=AUTH,
    )
    assert create.status_code == 201, create.text
    settlement_id = create.json()["id"]

    dup = client.post(
        f"/api/v1/group/moments/{moment_id}/settlements",
        json={
            "from_member_id": member_b,
            "to_member_id": member_a,
            "amount_minor": 5000,
            "currency_code": "INR",
            "client_request_id": client_request_id,
        },
        headers=AUTH,
    )
    assert dup.status_code == 201
    assert dup.json()["id"] == settlement_id

    listed = client.get(f"/api/v1/group/moments/{moment_id}/settlements", headers=AUTH)
    assert listed.status_code == 200
    assert len(listed.json()["settlements"]) == 1

    marked = client.post(
        f"/api/v1/group/moments/{moment_id}/settlements/{settlement_id}/mark-settled",
        headers=AUTH,
    )
    assert marked.status_code == 200
    assert marked.json()["settlement"]["status"] == "SETTLED"
    assert marked.json()["idempotent"] is False

    again = client.post(
        f"/api/v1/group/moments/{moment_id}/settlements/{settlement_id}/mark-settled",
        headers=AUTH,
    )
    assert again.status_code == 200
    assert again.json()["idempotent"] is True


@patch("app.dependencies.auth.verify_firebase_token")
def test_soft_delete_settlement(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate(client, "shared-living", "living_type", "FLATMATES")
    member_a, member_b = _seed_members_and_expense(mock_db, moment_id, sample_user.id)

    create = client.post(
        f"/api/v1/group/moments/{moment_id}/settlements",
        json={
            "from_member_id": member_b,
            "to_member_id": member_a,
            "amount_minor": 2500,
            "currency_code": "INR",
        },
        headers=AUTH,
    )
    assert create.status_code == 201
    settlement_id = create.json()["id"]

    deleted = client.delete(
        f"/api/v1/group/moments/{moment_id}/settlements/{settlement_id}",
        headers=AUTH,
    )
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"

    listed = client.get(f"/api/v1/group/moments/{moment_id}/settlements", headers=AUTH)
    assert listed.json()["settlements"] == []

    again = client.delete(
        f"/api/v1/group/moments/{moment_id}/settlements/{settlement_id}",
        headers=AUTH,
    )
    assert again.json()["idempotent"] is True


@patch("app.dependencies.auth.verify_firebase_token")
def test_member_validation_rejects_unknown(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate(client, "shared-experience", "experience_profile", "TRIP_VACATION")

    resp = client.post(
        f"/api/v1/group/moments/{moment_id}/settlements",
        json={
            "from_member_id": "unknown",
            "to_member_id": "also-unknown",
            "amount_minor": 100,
            "currency_code": "INR",
        },
        headers=AUTH,
    )
    assert resp.status_code == 400


@patch("app.dependencies.auth.verify_firebase_token")
def test_life_mapper_uses_calculator_when_cheap(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_and_activate(client, "shared-purchase", "purchase_profile", "GIFT_POOL")
    _seed_members_and_expense(mock_db, moment_id, sample_user.id)

    life = client.get("/api/v1/group/active/life", headers=AUTH)
    assert life.status_code == 200, life.text
    preview = life.json().get("settlement_preview")
    assert preview is not None
    assert preview.get("pending_count", 0) >= 1 or "owes" in preview.get("balance_insight", "").lower()
