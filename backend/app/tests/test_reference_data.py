"""Tests for Reference Data Engine and preferences."""
from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel
from app.tests.conftest import MOCK_USER_ID


def _auth(mock_verify):
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }


AUTH = {"Authorization": "Bearer fake-token"}


def test_reference_data_bootstrap_shape(client: TestClient):
    resp = client.get("/api/v1/reference-data/bootstrap")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reference_data_version"] == 18
    assert len(data["currencies"]) >= 2
    inr = next(c for c in data["currencies"] if c["code"] == "INR")
    assert inr["symbol"] == "₹"
    assert inr["minor_unit"] == 2
    assert inr["icon"]
    assert "sort_order" in inr
    food = next(c for c in data["categories"]["expense"] if c["code"] == "FOOD")
    assert food["label"] == "Food"
    assert food["icon"] == "restaurant"


def test_metadata_bootstrap_alias(client: TestClient):
    resp = client.get("/api/v1/metadata/bootstrap")
    assert resp.status_code == 200
    data = resp.json()
    assert data["metadata_version"] == 18
    assert data["reference_data_version"] == 18
    assert any(c["code"] == "KWD" for c in data["currencies"])


def test_reference_catalog_get_active_sorted(client: TestClient):
    from app.domains.reference_data.catalog import get_reference_catalog

    catalog = get_reference_catalog()
    assert catalog.version() == 18
    categories = catalog.get("expense_categories", active_only=True)
    assert categories[0]["code"] == "FOOD"
    assert all(c.get("is_active", True) for c in categories)


def test_reference_data_options_filter(client: TestClient):
    resp = client.get(
        "/api/v1/reference-data/options?keys=currencies,expense_categories"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reference_data_version"] == 18
    assert "currencies" in body["data"]
    assert "expense_categories" in body["data"]


def test_metadata_options_alias(client: TestClient):
    resp = client.get("/api/v1/metadata/options?keys=currencies")
    assert resp.status_code == 200
    body = resp.json()
    assert body["metadata_version"] == 18


def test_reference_data_options_invalid_key(client: TestClient):
    resp = client.get("/api/v1/reference-data/options?keys=not_a_real_key")
    assert resp.status_code == 400


@patch("app.dependencies.auth.verify_firebase_token")
def test_bootstrap_includes_metadata_version_and_prefs(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/app/bootstrap", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["reference_data_version"] == 18
    assert data["metadata_version"] == 18
    prefs = data["preferences"]
    assert prefs["default_currency_code"] == "INR"


@patch("app.dependencies.auth.verify_firebase_token")
def test_patch_preferences_valid_currency(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    from app.domains.preferences.models import UserPreferencesModel
    from datetime import datetime, timezone

    pref = UserPreferencesModel(
        id=MOCK_USER_ID,
        user_id=MOCK_USER_ID,
        selected_context="MY_MONEY",
        default_currency_code="INR",
        locale="en-IN",
        country_code="IN",
        timezone="Asia/Kolkata",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.add(pref)

    resp = client.patch(
        "/api/v1/app/preferences",
        json={"default_currency_code": "USD"},
        headers=AUTH,
    )
    assert resp.status_code == 200
    assert resp.json()["default_currency_code"] == "USD"


@patch("app.dependencies.auth.verify_firebase_token")
def test_patch_preferences_invalid_currency(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    from app.domains.preferences.models import UserPreferencesModel
    from datetime import datetime, timezone

    pref = UserPreferencesModel(
        id=MOCK_USER_ID,
        user_id=MOCK_USER_ID,
        selected_context="MY_MONEY",
        default_currency_code="INR",
        locale="en-IN",
        country_code="IN",
        timezone="Asia/Kolkata",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.add(pref)

    resp = client.patch(
        "/api/v1/app/preferences",
        json={"default_currency_code": "XXX"},
        headers=AUTH,
    )
    assert resp.status_code == 422


@patch("app.dependencies.auth.verify_firebase_token")
def test_quick_add_options_include_reference_collections(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/personal/live/quick-add/options", headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["default_currency_code"] == "INR"
    assert len(body["currencies"]) >= 7
    assert body["currencies"][0]["icon"]
    assert len(body["expense_categories"]) >= 1
    assert body["expense_categories"][0]["code"] == "FOOD"
    assert len(body["account_types"]) >= 1
    assert "expense_category_names" in (body.get("metadata") or {})


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


@patch("app.dependencies.auth.verify_firebase_token")
def test_quick_add_expense_rejects_invalid_currency(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/personal/live/quick-add",
        json={
            "moment_id": "abc",
            "event_type": "EXPENSE",
            "expense": {
                "amount_minor": 100,
                "currency_code": "XXX",
                "category_code": "FOOD",
                "account_id": "x",
            },
        },
        headers=AUTH,
    )
    assert resp.status_code in (400, 422)


def test_supported_currencies_include_sprint_set(client: TestClient):
    resp = client.get("/api/v1/metadata/bootstrap")
    codes = {c["code"] for c in resp.json()["currencies"]}
    assert {"INR", "USD", "EUR", "GBP", "AED", "SGD", "JPY", "KWD"}.issubset(codes)


def test_minor_unit_jpy_and_kwd():
    from app.domains.reference_data.catalog import get_reference_catalog

    catalog = get_reference_catalog()
    assert catalog.minor_from_major_string("4500", "JPY") == 4500
    assert catalog.minor_from_major_string("4.123", "KWD") == 4123
    assert catalog.minor_from_major_string("4500", "INR") == 450000
