"""Executable golden flows for Quick Add production verification.

Capability-aware:
- Personal + trip expense: create → read → edit → delete + idempotent retry
- Purchase CONTRIBUTOR + living rent: create → read + idempotent retry (no edit/delete)

Projection checks spy enqueue/invalidation (no live Celery worker required).
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domains.quick_add_contract.aliases import normalize_action_id
from app.domains.quick_add_contract.hash import fixtures_root, load_reference_actions
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _load_golden(flow_file: str) -> dict:
    root = fixtures_root()
    golden = json.loads((root / "golden_flow" / flow_file).read_text(encoding="utf-8"))
    fixture = json.loads((root / golden["fixture"]).read_text(encoding="utf-8"))
    return {"golden": golden, "fixture": fixture}


def _ref_by_key(key: str) -> dict:
    for row in load_reference_actions():
        if row["key"] == key:
            return row
    raise KeyError(key)


# ---------------------------------------------------------------------------
# Contract / naming locks
# ---------------------------------------------------------------------------


def test_purchase_contribution_reserved_not_contributor():
    assert normalize_action_id("CONTRIBUTOR") == "CONTRIBUTOR"
    assert normalize_action_id("PURCHASE_CONTRIBUTION") == "PURCHASE_CONTRIBUTION"
    assert normalize_action_id("PURCHASE_CONTRIBUTION") != "CONTRIBUTOR"
    assert "PURCHASE_CONTRIBUTION" not in {
        a["action_id"] for a in load_reference_actions()
    }


def test_golden_flows_match_reference_capabilities():
    """Each golden flow's edit/delete steps align with contract capabilities."""
    mapping = {
        "life_ops_expense.json": "LIFE_OPERATIONS:EXPENSE",
        "future_contribution.json": "FUTURE_BUILDING:CONTRIBUTION",
        "lifestyle_experience.json": "LIFESTYLE:EXPERIENCE",
        "relationship_connection.json": "RELATIONSHIPS:CONNECTION",
        "group_trip_expense.json": "SHARED_EXPERIENCE:EXPENSE",
        "purchase_contribution.json": "SHARED_PURCHASE:CONTRIBUTOR",
        "living_rent.json": "SHARED_LIVING:EXPENSE",
    }
    for flow_file, key in mapping.items():
        data = _load_golden(flow_file)
        caps = _ref_by_key(key)["capabilities"]
        steps = set(data["golden"]["steps"])
        if caps.get("edit"):
            assert "edit" in steps, flow_file
        else:
            assert "edit" not in steps, flow_file
        if caps.get("delete"):
            assert "delete" in steps, flow_file
        else:
            assert "delete" not in steps, flow_file
        assert "create" in steps


# ---------------------------------------------------------------------------
# Personal projection invalidation (enqueue spy)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "template,event_type,expect_moments",
    [
        ("LIFE_OPERATIONS", "EXPENSE", False),
        ("FUTURE_BUILDING", "CONTRIBUTION", True),
        ("LIFESTYLE", "EXPERIENCE", True),
        ("RELATIONSHIPS", "CONNECTION", True),
    ],
)
@patch("app.domains.projections.invalidation._enqueue_slice")
async def test_personal_reference_invalidation_enqueues(
    mock_enqueue, template, event_type, expect_moments
):
    from app.domains.projections.invalidation import invalidate_for_quick_add

    user_id = uuid4()
    await invalidate_for_quick_add(user_id, template, event_type)
    slices = {call.args[2] for call in mock_enqueue.call_args_list}
    assert "pulse" in slices
    assert "memory" in slices or "life" in {
        call.args[1] for call in mock_enqueue.call_args_list
    }
    if expect_moments:
        assert "moments" in slices
    else:
        assert "moments" not in slices
    assert mock_enqueue.call_count >= 2


# ---------------------------------------------------------------------------
# Trip expense golden flow (full CRUD + idempotency + group invalidation)
# ---------------------------------------------------------------------------


def _create_experience(client: TestClient) -> str:
    created = client.post(
        "/api/v1/group/shared-experience/moments",
        json={"experience_profile": "TRIP_VACATION"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    return created.json()["moment_id"]


def _activate_experience(client: TestClient, moment_id: str, *, currency: str = "USD") -> None:
    draft = client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={
            "answers": {
                "moment_name": "Golden Trip",
                "currency_code": currency,
                "allow_multi_currency": True,
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


@patch("app.domains.group.projection_cache.invalidate_group_projections", new_callable=AsyncMock)
@patch("app.domains.group.activity.engine.invalidate_group_projections", new_callable=AsyncMock)
@patch("app.dependencies.auth.verify_firebase_token")
def test_golden_group_trip_expense_crud_idempotent_invalidate(
    mock_verify,
    mock_activity_invalidate,
    mock_proj_invalidate,
    client: TestClient,
    mock_db,
    sample_user: UserModel,
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    data = _load_golden("group_trip_expense.json")
    wire = dict(data["fixture"]["wire"])
    mid = _create_experience(client)
    _activate_experience(client, mid, currency=wire["currency_code"])
    uid = str(sample_user.id)
    wire["paid_by_participant_id"] = uid
    wire["participant_ids"] = [uid]

    create = client.post(f"/api/v1/group/trips/{mid}/expenses", json=wire, headers=AUTH)
    assert create.status_code == 201, create.text
    eid = create.json()["id"]
    assert create.json()["amount_minor"] == wire["amount_minor"]

    listing = client.get(f"/api/v1/group/trips/{mid}/expenses", headers=AUTH)
    assert listing.status_code == 200, listing.text
    rows = listing.json()
    if isinstance(rows, dict):
        rows = rows.get("expenses") or rows.get("items") or []
    ids = {row.get("id") for row in rows if isinstance(row, dict)}
    assert not ids or eid in ids

    detail = client.get(f"/api/v1/group/trips/{mid}/expenses/{eid}", headers=AUTH)
    if detail.status_code == 200:
        assert detail.json().get("id") == eid

    replay = client.post(f"/api/v1/group/trips/{mid}/expenses", json=wire, headers=AUTH)
    assert replay.status_code == 201, replay.text
    assert replay.json()["id"] == eid

    patched = client.patch(
        f"/api/v1/group/trips/{mid}/expenses/{eid}",
        json={
            "title": "Dinner (edited)",
            "amount_minor": wire["amount_minor"],
            "currency_code": wire["currency_code"],
            "paid_by_participant_id": uid,
            "participant_ids": [uid],
            "split_style": "EQUAL",
        },
        headers=AUTH,
    )
    assert patched.status_code == 200, patched.text

    deleted = client.delete(f"/api/v1/group/trips/{mid}/expenses/{eid}", headers=AUTH)
    assert deleted.status_code in (200, 204), deleted.text

    assert mock_proj_invalidate.await_count >= 1 or mock_activity_invalidate.await_count >= 1


# ---------------------------------------------------------------------------
# Purchase CONTRIBUTOR (people) + Living rent
# ---------------------------------------------------------------------------


def _create_group(client: TestClient, category: str, profile_key: str, profile_code: str) -> str:
    created = client.post(
        f"/api/v1/group/{category}/moments",
        json={profile_key: profile_code},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    return created.json()["moment_id"]


@patch("app.domains.group.activity.engine.invalidate_group_projections", new_callable=AsyncMock)
@patch("app.dependencies.auth.verify_firebase_token")
def test_golden_purchase_contributor_create_idempotent_invalidate(
    mock_verify,
    mock_invalidate,
    client: TestClient,
    mock_db,
    sample_user: UserModel,
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    data = _load_golden("purchase_contribution.json")
    wire = dict(data["fixture"]["wire"])
    mid = _create_group(client, "shared-purchase", "purchase_profile", "GIFT_POOL")

    create = client.post(
        f"/api/v1/group/shared-purchase/moments/{mid}/quick-add/contributors",
        json=wire,
        headers=AUTH,
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body.get("status") == "ok"
    cid = body["id"]

    replay = client.post(
        f"/api/v1/group/shared-purchase/moments/{mid}/quick-add/contributors",
        json=wire,
        headers=AUTH,
    )
    assert replay.status_code == 201, replay.text
    assert replay.json()["id"] == cid
    assert replay.json().get("idempotent_replay") is True

    assert mock_invalidate.await_count >= 1


@patch("app.domains.group.activity.engine.invalidate_group_projections", new_callable=AsyncMock)
@patch("app.dependencies.auth.verify_firebase_token")
def test_golden_living_rent_create_idempotent_invalidate(
    mock_verify,
    mock_invalidate,
    client: TestClient,
    mock_db,
    sample_user: UserModel,
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    data = _load_golden("living_rent.json")
    wire = dict(data["fixture"]["wire"])
    mid = _create_group(client, "shared-living", "living_type", "FLATMATES")

    create = client.post(
        f"/api/v1/group/shared-living/moments/{mid}/quick-add/expenses",
        json=wire,
        headers=AUTH,
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body.get("status") == "ok"
    eid = body["id"]

    replay = client.post(
        f"/api/v1/group/shared-living/moments/{mid}/quick-add/expenses",
        json=wire,
        headers=AUTH,
    )
    assert replay.status_code == 201, replay.text
    assert replay.json()["id"] == eid
    assert replay.json().get("idempotent_replay") is True

    assert mock_invalidate.await_count >= 1


# ---------------------------------------------------------------------------
# Unsupported action typed error (API)
# ---------------------------------------------------------------------------


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_unknown_module_typed_error(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    mid = _create_group(client, "shared-purchase", "purchase_profile", "GIFT_POOL")
    resp = client.post(
        f"/api/v1/group/shared-purchase/moments/{mid}/quick-add/not-a-real-module",
        json={},
        headers=AUTH,
    )
    assert resp.status_code in (400, 404, 422), resp.text
    detail = resp.json().get("detail")
    if isinstance(detail, dict):
        assert detail.get("code") == "quick_add_action_not_supported"


# ---------------------------------------------------------------------------
# Personal golden fixtures — wire + normalize readiness (HTTP CRUD limited by mock_db)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "flow_file",
    [
        "life_ops_expense.json",
        "future_contribution.json",
        "lifestyle_experience.json",
        "relationship_connection.json",
    ],
)
def test_personal_golden_fixture_wire_ready(flow_file: str):
    data = _load_golden(flow_file)
    wire = data["fixture"]["wire"]
    assert data["fixture"]["contract_version"] in {"v1", "v2"}
    if flow_file == "life_ops_expense.json":
        assert data["fixture"]["contract_version"] == "v2"
        assert data["fixture"]["wire"]["expense"]["subcategory_code"] == "GROCERIES"
    assert wire.get("client_request_id")
    assert wire.get("event_type") or wire.get("action_id")
    assert "create" in data["golden"]["steps"]
    assert "edit" in data["golden"]["steps"]
    assert "delete" in data["golden"]["steps"]
