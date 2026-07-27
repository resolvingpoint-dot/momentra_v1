"""Master Expense Orchestrator tests."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

from app.domains.personal.master_expense.mapper import (
    build_life_operations_body,
    build_lifestyle_body,
    build_relationships_body,
    normalize_legacy_body,
    parse_occurred_at,
)
from app.domains.personal.master_expense.schemas import (
    MasterExpenseCreateRequest,
    MasterExpenseSharedInput,
)


def test_normalize_legacy_nested_payload():
    body = {
        "client_request_id": str(uuid4()),
        "expense": {
            "title": "Dinner",
            "amount": "4500",
            "account_id": str(uuid4()),
            "category_name": "Dining Out",
            "currency_code": "INR",
        },
        "experience": {"feeling": "GREAT", "meaningfulness": "HIGH"},
        "shared_experience": {
            "enabled": True,
            "shared_with": ["SPOUSE"],
            "relationship_impact": "STRENGTHENED_CONNECTION",
        },
        "context": {"reason": "CELEBRATION"},
        "notes": "Lovely evening",
    }
    normalized = normalize_legacy_body(body)
    assert normalized["title"] == "Dinner"
    assert normalized["amount"] == "4500"
    assert normalized["shared"]["is_shared"] is True
    assert normalized["shared"]["shared_with"] == ["SPOUSE"]


def test_normalize_flat_payload_passthrough():
    body = {
        "title": "Dinner Celebration",
        "amount_minor": 450000,
        "currency_code": "INR",
        "account_id": str(uuid4()),
        "category_code": "DINING_OUT",
    }
    normalized = normalize_legacy_body(body)
    assert normalized["title"] == "Dinner Celebration"
    assert normalized["amount_minor"] == 450000


def test_build_life_operations_body_includes_source():
    master_id = uuid4()
    req = MasterExpenseCreateRequest(
        title="Dinner",
        amount_minor=450000,
        currency_code="INR",
        account_id=str(uuid4()),
        category_code="DINING_OUT",
    )
    validated = {
        "amount_minor": 450000,
        "currency_code": "INR",
        "account_id": str(uuid4()),
        "category_code": "DINING_OUT",
        "transaction_type": "EXPENSE",
    }
    body = build_life_operations_body(req, master_expense_id=master_id, validated_expense=validated)
    assert body["event_type"] == "EXPENSE"
    assert body["source"] == "MASTER_EXPENSE"
    assert body["expense"]["source"] == "MASTER_EXPENSE"


def test_build_relationships_body_only_when_shared():
    master_id = uuid4()
    req = MasterExpenseCreateRequest(
        title="Dinner",
        amount_minor=10000,
        currency_code="INR",
        account_id=str(uuid4()),
        category_code="DINING_OUT",
        shared=MasterExpenseSharedInput(
            is_shared=True,
            shared_with=["SPOUSE"],
            relationship_impact=["STRENGTHENED_CONNECTION"],
        ),
    )
    validated = {
        "amount_minor": 10000,
        "currency_code": "INR",
        "account_id": str(uuid4()),
        "category_code": "DINING_OUT",
    }
    body = build_relationships_body(
        req,
        master_expense_id=master_id,
        validated_expense=validated,
        shared=req.shared,
    )
    assert body["event_type"] == "SHARED_EXPERIENCE"
    assert body["relationships"]["relationship_type"] == "Partner"


def test_lifestyle_body_maps_feeling_to_energy():
    master_id = uuid4()
    req = MasterExpenseCreateRequest(
        title="Trip",
        amount_minor=50000,
        currency_code="INR",
        account_id=str(uuid4()),
        category_code="TRAVEL",
        experience=__import__(
            "app.domains.personal.master_expense.schemas", fromlist=["MasterExpenseExperienceInput"]
        ).MasterExpenseExperienceInput(feeling="GREAT", meaningfulness="HIGH"),
        context=__import__(
            "app.domains.personal.master_expense.schemas", fromlist=["MasterExpenseContextInput"]
        ).MasterExpenseContextInput(reason="TRAVEL"),
    )
    validated = {
        "amount_minor": 50000,
        "currency_code": "INR",
        "account_id": str(uuid4()),
        "category_code": "TRAVEL",
    }
    body = build_lifestyle_body(req, master_expense_id=master_id, validated_expense=validated)
    assert body["lifestyle"]["energy_impact"] == "Energized"
    assert body["lifestyle"]["experience_type"] == "Travel"


def test_parse_occurred_at_fallback():
    fallback = datetime(2026, 7, 8, 12, 0, 0)
    assert parse_occurred_at(None, fallback=fallback) == fallback


@pytest.mark.asyncio
@patch("app.domains.projections.invalidation._enqueue_slice")
async def test_invalidate_for_master_expense_shared(mock_enqueue):
    from app.domains.projections.invalidation import invalidate_for_master_expense

    user_id = uuid4()
    await invalidate_for_master_expense(user_id, include_relationships=True)

    templates = {
        call.args[1]
        for call in mock_enqueue.call_args_list
        if call.args[1] != "personal"
    }
    assert templates == {"LIFE_OPERATIONS", "LIFESTYLE", "RELATIONSHIPS"}


@pytest.mark.asyncio
@patch("app.domains.projections.invalidation._enqueue_slice")
async def test_invalidate_for_master_expense_not_shared_skips_relationships(mock_enqueue):
    from app.domains.projections.invalidation import invalidate_for_master_expense

    user_id = uuid4()
    await invalidate_for_master_expense(user_id, include_relationships=False)

    templates = {
        call.args[1]
        for call in mock_enqueue.call_args_list
        if call.args[1] != "personal"
    }
    assert templates == {"LIFE_OPERATIONS", "LIFESTYLE"}
    assert "RELATIONSHIPS" not in templates


@pytest.mark.asyncio
@patch("app.domains.projections.invalidation._enqueue_slice")
async def test_invalidate_for_master_expense_lifestyle_includes_moments(mock_enqueue):
    from app.domains.projections.invalidation import invalidate_for_master_expense

    user_id = uuid4()
    await invalidate_for_master_expense(user_id, include_relationships=False)

    lifestyle_slices = {
        call.args[2]
        for call in mock_enqueue.call_args_list
        if call.args[1] == "LIFESTYLE"
    }
    assert "moments" in lifestyle_slices
    assert "pulse" in lifestyle_slices
    assert "memory" in lifestyle_slices


@pytest.mark.asyncio
@patch("app.domains.projections.invalidation._enqueue_slice")
async def test_invalidate_for_master_expense_lo_includes_moments(mock_enqueue):
    from app.domains.projections.invalidation import invalidate_for_master_expense

    user_id = uuid4()
    await invalidate_for_master_expense(user_id, include_relationships=False)

    lo_slices = {
        call.args[2]
        for call in mock_enqueue.call_args_list
        if call.args[1] == "LIFE_OPERATIONS"
    }
    assert lo_slices == {"pulse", "moments", "memory"}


def test_build_impact_preview_honest_fanout():
    from app.domains.personal.master_expense.schemas import build_impact_preview

    preview = build_impact_preview(
        life_operations=True, lifestyle=True, relationships=False
    )
    assert "refresh" in preview["life_operations"].lower()
    assert "refresh" in preview["lifestyle"].lower()
    assert "skipped" in preview["relationships"].lower()
    assert preview["templates_touched"] == "2"
    assert "₹" not in preview["life_operations"]
    assert "budget" not in preview["life_operations"].lower()


def test_build_impact_preview_shared_relationships():
    from app.domains.personal.master_expense.schemas import build_impact_preview

    preview = build_impact_preview(
        life_operations=True, lifestyle=True, relationships=True
    )
    assert preview["templates_touched"] == "3"
    assert "refresh" in preview["relationships"].lower()


@patch("app.dependencies.auth.verify_firebase_token")
def test_master_expense_rejects_invalid_currency(
    mock_verify, client, mock_db, sample_user
):
    from app.tests.test_personal import AUTH, _auth

    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.post(
        "/api/v1/personal/master-expense",
        json={
            "title": "Test",
            "amount_minor": 100,
            "currency_code": "XXX",
            "account_id": str(uuid4()),
            "category_code": "FOOD",
        },
        headers=AUTH,
    )
    assert resp.status_code in (400, 422)


@patch("app.dependencies.auth.verify_firebase_token")
def test_master_expense_rejects_invalid_account(
    mock_verify, client, mock_db, sample_user
):
    from app.tests.test_personal import AUTH, _auth

    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.post(
        "/api/v1/personal/master-expense",
        json={
            "title": "Test",
            "amount_minor": 100,
            "currency_code": "INR",
            "account_id": str(uuid4()),
            "category_code": "FOOD",
        },
        headers=AUTH,
    )
    assert resp.status_code in (400, 422, 409)


@patch("app.dependencies.auth.verify_firebase_token")
@patch(
    "app.domains.personal.app_service.PersonalAppService.master_expense_submit",
    new_callable=AsyncMock,
)
def test_master_expense_create_success(
    mock_submit,
    mock_verify,
    client: TestClient,
    mock_db,
    sample_user: UserModel,
):
    from app.tests.test_personal import AUTH, _auth

    _auth(mock_verify)
    mock_db.add(sample_user)
    master_id = str(uuid4())
    mock_submit.return_value = {
        "id": master_id,
        "master_expense_id": master_id,
        "created_events": {
            "life_operations": str(uuid4()),
            "lifestyle": str(uuid4()),
            "relationships": None,
        },
        "impact_preview": {
            "life_operations": "Expense logged",
            "lifestyle": "Experience captured",
            "relationships": "Skipped",
        },
        "idempotent_replay": False,
        "master_expense_group_id": master_id,
        "transaction_id": str(uuid4()),
        "account_id": str(uuid4()),
        "amount_minor": 450000,
        "events": [
            {
                "quick_add_event_id": str(uuid4()),
                "moment_id": str(uuid4()),
                "moment_type_code": "LIFE_OPERATIONS",
                "event_type": "EXPENSE",
            },
            {
                "quick_add_event_id": str(uuid4()),
                "moment_id": str(uuid4()),
                "moment_type_code": "LIFESTYLE",
                "event_type": "EXPERIENCE",
            },
        ],
    }

    client_request_id = str(uuid4())
    resp = client.post(
        "/api/v1/personal/master-expense",
        json={
            "client_request_id": client_request_id,
            "title": "Dinner Celebration",
            "amount_minor": 450000,
            "currency_code": "INR",
            "account_id": str(uuid4()),
            "category_code": "DINING_OUT",
            "shared": {"is_shared": False, "shared_with": [], "relationship_impact": []},
        },
        headers=AUTH,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["master_expense_id"] == master_id
    assert len(body["events"]) == 2
    mock_submit.assert_awaited_once()
    assert mock_submit.await_args.args[1]["client_request_id"] == client_request_id


@patch("app.dependencies.auth.verify_firebase_token")
@patch(
    "app.domains.personal.app_service.PersonalAppService.master_expense_submit",
    new_callable=AsyncMock,
)
def test_master_expense_idempotent_replay_flag(
    mock_submit,
    mock_verify,
    client: TestClient,
    mock_db,
    sample_user: UserModel,
):
    from app.tests.test_personal import AUTH, _auth

    _auth(mock_verify)
    mock_db.add(sample_user)
    master_id = str(uuid4())
    mock_submit.return_value = {
        "id": master_id,
        "master_expense_id": master_id,
        "created_events": {"life_operations": str(uuid4()), "lifestyle": str(uuid4())},
        "impact_preview": {},
        "idempotent_replay": True,
        "master_expense_group_id": master_id,
        "transaction_id": str(uuid4()),
        "account_id": str(uuid4()),
        "amount_minor": 10000,
        "events": [],
    }

    resp = client.post(
        "/api/v1/personal/master-expense",
        json={
            "client_request_id": str(uuid4()),
            "title": "Coffee",
            "amount_minor": 10000,
            "currency_code": "INR",
            "account_id": str(uuid4()),
            "category_code": "FOOD",
        },
        headers=AUTH,
    )
    assert resp.status_code == 201
    assert resp.json()["idempotent_replay"] is True
