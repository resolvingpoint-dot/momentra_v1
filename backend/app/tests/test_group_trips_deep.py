from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _trip(client: TestClient) -> str:
    created = client.post(
        "/api/v1/group/shared-experience/moments",
        json={"experience_profile": "TRIP_VACATION"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    return created.json()["moment_id"]


def _trip_activated(client: TestClient) -> str:
    mid = _trip(client)
    client.put(
        f"/api/v1/group/shared-experience/moments/{mid}/setup/draft",
        json={"experience_profile": "TRIP_VACATION", "moment_name": "Settlement Trip"},
        headers=AUTH,
    )
    activated = client.post(
        f"/api/v1/group/shared-experience/moments/{mid}/setup/activate",
        headers=AUTH,
    )
    assert activated.status_code == 200, activated.text
    return mid


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_settlements_context_uses_engine_preview(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    """Projection correctness: empty trip must not invent fake debts; status is honest."""
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    resp = client.get(f"/api/v1/group/trips/{mid}/settlements/context", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["moment_id"] == mid
    assert "harmony_label" in data
    assert "balance_insight" in data
    assert isinstance(data.get("pending_balances"), list)
    # No expenses → no invented settlement suggestions
    assert data["pending_balances"] == []
    assert data["balance_sync_percent"] == 100.0
    assert data.get("member_contributions") == []
    assert data.get("suggested_transfer") is None
    assert (data.get("settlement_widget") or {}).get("members_needing_settlement", 0) == 0


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_settlements_with_expense_and_mark_paid(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    from app.domains.group import moment_store as store

    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip_activated(client)
    moment = mock_db._stores["moments"][mid]
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
            "participant_ids": [member_a, member_b],
            "split_type": "equal",
            "created_at": store.now_iso(),
            "deleted": False,
        }
    ]
    store.write_state(moment, state)

    pulse = client.get(f"/api/v1/group/trips/{mid}/pulse", headers=AUTH)
    assert pulse.status_code == 200, pulse.text
    widget = pulse.json().get("settlement_widget") or {}
    assert widget.get("total_paid_minor", 0) > 0
    assert widget.get("members_needing_settlement", 0) >= 1

    ctx = client.get(f"/api/v1/group/trips/{mid}/settlements/context", headers=AUTH)
    assert ctx.status_code == 200, ctx.text
    data = ctx.json()
    assert data["pending_balances"]
    assert data["suggested_transfer"]
    assert data["suggested_transfer"]["from_user_id"]
    assert data["suggested_transfer"]["to_user_id"]
    assert data["member_contributions"]
    assert data["balance_sync_percent"] < 100.0

    sug = data["suggested_transfer"]
    paid = client.post(
        f"/api/v1/group/trips/{mid}/settlements/mark-paid",
        json={
            "from_user_id": sug["from_user_id"],
            "to_user_id": sug["to_user_id"],
            "amount_minor": sug["amount_minor"],
            "currency_code": sug.get("currency_code") or "INR",
            "client_request_id": f"test-mark-{mid}",
        },
        headers=AUTH,
    )
    assert paid.status_code == 200, paid.text
    after = paid.json()
    assert after.get("suggested_transfer") is None or after.get("pending_balances") == []
    assert after["balance_sync_percent"] == 100.0


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_creation_options(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/group/trip-creation-options", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["vibes"] and data["budget_moods"]
    assert all(v["icon"] for v in data["vibes"])


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_live_workspace_and_reads(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    ws = client.get(f"/api/v1/group/trips/{mid}/live-workspace", headers=AUTH)
    assert ws.status_code == 200, ws.text
    assert ws.json()["header"]["moment_name"]

    for path in ("corpus", "settlements/context", "approvals/context"):
        resp = client.get(f"/api/v1/group/trips/{mid}/{path}", headers=AUTH)
        assert resp.status_code == 200, f"{path}: {resp.text}"
        assert resp.json()["moment_id"] == mid


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_expenses_and_contributions(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    assert client.get(f"/api/v1/group/trips/{mid}/expenses", headers=AUTH).json() == []

    exp = client.post(
        f"/api/v1/group/trips/{mid}/expenses",
        json={"paid_by_user_id": str(sample_user.id), "amount_minor": 5000, "description": "Dinner"},
        headers=AUTH,
    )
    assert exp.status_code == 201, exp.text
    assert exp.json()["amount_minor"] == 5000 and exp.json()["description"] == "Dinner"

    con = client.post(
        f"/api/v1/group/trips/{mid}/contributions",
        json={"contributor_user_id": "u1", "amount_minor": 10000, "allocation_category": "stay"},
        headers=AUTH,
    )
    assert con.status_code == 201, con.text
    assert con.json()["amount_minor"] == 10000


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_plans_and_approvals(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    ctx = client.get(f"/api/v1/group/trips/{mid}/plans/context", headers=AUTH)
    assert ctx.status_code == 200
    assert ctx.json()["categories"]

    plan = client.post(
        f"/api/v1/group/trips/{mid}/plans",
        json={"category": "stay", "title": "Hotel", "details": {"nights": 3}, "participant_user_ids": ["u1"]},
        headers=AUTH,
    )
    assert plan.status_code == 201, plan.text
    assert plan.json()["title"] == "Hotel"

    poll = client.post(
        f"/api/v1/group/trips/{mid}/approvals/polls",
        json={"question": "Where to?", "options": ["Goa", "Manali"]},
        headers=AUTH,
    )
    assert poll.status_code == 201, poll.text
    assert len(poll.json()["options"]) == 2


@pytest.mark.parametrize(
    "module", ["participant", "booking", "planning-item", "expense", "memory", "poll", "attendance", "budget", "vendor", "update"]
)
@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_quick_add_contexts(mock_verify, client: TestClient, mock_db, sample_user: UserModel, module):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    resp = client.get(f"/api/v1/group/trips/{mid}/quick-add/{module}/context", headers=AUTH)
    assert resp.status_code == 200, f"{module}: {resp.text}"
    assert resp.json()["moment_id"] == mid


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_guest_and_attachments(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    guest = client.post(
        f"/api/v1/group/trips/{mid}/guests",
        json={"full_name": "Sam", "relationship_type": "friend"},
        headers=AUTH,
    )
    assert guest.status_code == 201, guest.text
    assert guest.json()["full_name"] == "Sam"

    upload = client.post(
        f"/api/v1/group/trips/{mid}/attachments/upload-url",
        json={"content_type": "image/jpeg", "byte_size": 1024, "purpose": "receipt"},
        headers=AUTH,
    )
    assert upload.status_code == 201, upload.text
    assert upload.json()["storage_path"] and upload.json()["upload_url"]

    confirm = client.post(
        f"/api/v1/group/trips/{mid}/attachments/confirm",
        json={"storage_path": upload.json()["storage_path"], "purpose": "receipt"},
        headers=AUTH,
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["storage_path"] == upload.json()["storage_path"]

    too_big = client.post(
        f"/api/v1/group/trips/{mid}/attachments/upload-url",
        json={
            "content_type": "video/mp4",
            "byte_size": 11 * 1024 * 1024,
            "purpose": "memory",
        },
        headers=AUTH,
    )
    assert too_big.status_code == 400, too_big.text

    bad_type = client.post(
        f"/api/v1/group/trips/{mid}/attachments/upload-url",
        json={"content_type": "application/zip", "byte_size": 1024, "purpose": "memory"},
        headers=AUTH,
    )
    assert bad_type.status_code == 400, bad_type.text

    memory_ok = client.post(
        f"/api/v1/group/trips/{mid}/attachments/upload-url",
        json={"content_type": "application/pdf", "byte_size": 2048, "purpose": "memory"},
        headers=AUTH,
    )
    assert memory_ok.status_code == 201, memory_ok.text

    ctx = client.get(
        f"/api/v1/group/trips/{mid}/quick-add/memory/context",
        headers=AUTH,
    )
    assert ctx.status_code == 200, ctx.text
    formats = {item["id"] for item in ctx.json().get("memory_formats", [])}
    assert formats == {"photo", "video", "pdf", "note"}


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_quick_add_creates(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    booking = client.post(
        f"/api/v1/group/trips/{mid}/quick-add/booking",
        json={"booking_type": "stay", "provider": "Beach Hotel"},
        headers=AUTH,
    )
    assert booking.status_code == 201, booking.text
    assert booking.json()["provider"] == "Beach Hotel"

    vendor = client.post(
        f"/api/v1/group/trips/{mid}/quick-add/vendor",
        json={"vendor_name": "Local Tours", "vendor_type": "service"},
        headers=AUTH,
    )
    assert vendor.status_code == 201, vendor.text
    assert vendor.json()["vendor_name"] == "Local Tours"

    update = client.post(
        f"/api/v1/group/trips/{mid}/quick-add/update",
        json={"title": "Flight booked", "body": "Tickets confirmed for everyone"},
        headers=AUTH,
    )
    assert update.status_code == 201, update.text
    assert update.json()["title"] == "Flight booked"

    poll = client.post(
        f"/api/v1/group/trips/{mid}/quick-add/poll",
        json={"question": "Beach or mountains?", "options": ["Beach", "Mountains"]},
        headers=AUTH,
    )
    assert poll.status_code == 201, poll.text
    assert poll.json()["question"] == "Beach or mountains?"


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_quick_add_hub_config_sectioned(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    resp = client.get(f"/api/v1/group/quickadd/{mid}", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["moment_type"] == "SHARED_EXPERIENCE"
    categories = data["categories"]
    assert len(categories) >= 4
    first_module = categories[0]["modules"][0]
    assert "module_code" in first_module
    assert "label" in first_module
    assert "icon" in first_module
    money = next(c for c in categories if c["id"] == "money")
    money_codes = {m["module_code"] for m in money["modules"]}
    assert "BUDGET" in money_codes
    assert "EXPENSE" in money_codes
    assert "CONTRIBUTION" in money_codes


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_deep_unknown_moment_404(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/group/trips/00000000-0000-0000-0000-000000000000/corpus",
        headers=AUTH,
    )
    assert resp.status_code == 404


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_budget_plan_persists(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _trip(client)

    ctx = client.get(f"/api/v1/group/trips/{mid}/quick-add/budget/context", headers=AUTH)
    assert ctx.status_code == 200
    assert len(ctx.json()["templates"]) >= 1
    assert len(ctx.json()["categories"]) >= 4

    create = client.post(
        f"/api/v1/group/trips/{mid}/quick-add/budget/plans",
        headers=AUTH,
        json={
            "template_id": "weekend",
            "total_amount_major": 10000,
            "currency_code": "INR",
            "split_method": "EQUAL",
            "participant_count": 4,
            "allocations": [
                {"category_code": "stay", "amount_major": 4000, "percent": 40},
                {"category_code": "travel", "amount_major": 3000, "percent": 30},
                {"category_code": "food", "amount_major": 2000, "percent": 20},
                {"category_code": "activities", "amount_major": 1000, "percent": 10},
            ],
            "notes": "Planning ceiling",
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["id"]
    assert body["total_amount_minor"] == 1_000_000
    assert body["split_method"] == "EQUAL"
    assert body["contribution_per_person_minor"] == 250_000
    assert len(body["allocations"]) == 4

    again = client.get(f"/api/v1/group/trips/{mid}/quick-add/budget/context", headers=AUTH)
    assert again.status_code == 200
    assert again.json()["existing_plan_id"] == body["id"]
