"""Sprint B.6 — recent activity + account management tests."""
from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
)
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


class _TimelineStub:
    timeline_id = uuid4()
    quick_add_event_id = uuid4()
    event_type = "EXPENSE"
    display_title = "Coffee"
    display_subtitle = "Food · Essential"
    display_amount = None
    impact_labels_json = {"pressure_impact": "Essential"}
    event_occurred_at = __import__("datetime").datetime(2026, 7, 6, 12, 0, 0)
    is_editable = True


def test_map_timeline_to_recent_item_client_shape():
    item = map_timeline_to_recent_item(_TimelineStub())
    assert item["activity_type"] == "EXPENSE"
    assert item["subtitle"] == "Food · Essential"
    assert item["title"] == "Coffee"
    assert "occurred_at" in item
    assert item["impact_label"] == "Essential"


@patch("app.dependencies.auth.verify_firebase_token")
def test_list_accounts_excludes_archived_by_default(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.get("/api/v1/personal/accounts", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json() == []


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_account_rejects_invalid_type(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.post(
        "/api/v1/personal/accounts",
        json={
            "account_name": "Test",
            "account_type": "NOT_A_TYPE",
            "currency_code": "INR",
        },
        headers=AUTH,
    )
    assert resp.status_code in (400, 422)


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_account_rejects_invalid_currency(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.post(
        "/api/v1/personal/accounts",
        json={
            "account_name": "Test",
            "account_type": "SAVINGS",
            "currency_code": "XXX",
        },
        headers=AUTH,
    )
    assert resp.status_code in (400, 422)


@patch("app.dependencies.auth.verify_firebase_token")
def test_quick_add_expense_requires_amount_minor(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.post(
        "/api/v1/personal/live/quick-add",
        json={
            "moment_id": "abc",
            "event_type": "EXPENSE",
            "event_title": "Coffee",
            "expense": {"currency_code": "INR", "account_id": "x"},
        },
        headers=AUTH,
    )
    assert resp.status_code in (400, 422)
