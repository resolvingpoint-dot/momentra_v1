"""Business Runway setup activate / preview (Run 4)."""
from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _complete_answers() -> dict:
    return {
        "moment_name": "Cash Runway",
        "runway_name": "Q3 Runway",
        "business_stage": "EARLY_REVENUE",
        "operating_currency_code": "USD",
        "timezone": "America/New_York",
        "locale": "en-US",
        "country_code": "US",
        "runway_goal_months": 12,
        "current_cash_minor": 5000000,
        "monthly_burn_minor": 400000,
        "revenue_status": "EARLY_REVENUE",
        "estimated_monthly_revenue_minor": 100000,
        "runway_alert_threshold_months": 3,
        "burn_categories": ["payroll", "saas"],
        "revenue_model": "SUBSCRIPTION",
        "funding_sources": ["BOOTSTRAPPED"],
        "visibility": "TEAM",
        "invite_on_activation": True,
        "members": [
            {
                "local_id": "m-fin",
                "name": "Fin",
                "email": "fin@example.com",
                "role": "FINANCE_LEAD",
                "permission_profile": "FINANCE_LEAD_V1",
                "permission_version": 1,
                "invite_method": "EMAIL",
                "invite_status": "DRAFT",
                "is_finance_lead": True,
            }
        ],
    }


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_runway_injects_owner(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_RUNWAY", "title": "R1", "template_id": "runway"},
        headers=AUTH,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["moment_type_code"] == "BUSINESS_RUNWAY"
    assert body["template_id"] == "business_runway"
    moment_id = body["moment_id"]
    state = client.get(f"/api/v1/business/moments/{moment_id}/setup", headers=AUTH).json()
    members = state["answers"]["members"]
    assert members[0]["role"] == "OWNER"
    assert members[0]["user_id"] == str(sample_user.id)


@patch("app.dependencies.auth.verify_firebase_token")
def test_save_partial_and_resume(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_RUNWAY"},
        headers=AUTH,
    ).json()["moment_id"]
    saved = client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={
            "answers": {"runway_name": "Partial", "current_cash_minor": 100},
            "progress": {"current_step": 2, "completed_steps": [1]},
        },
        headers=AUTH,
    )
    assert saved.status_code == 200
    state = client.get(f"/api/v1/business/moments/{moment_id}/setup", headers=AUTH).json()
    assert state["answers"]["runway_name"] == "Partial"
    assert state["answers"]["current_cash_minor"] == 100
    assert state["progress"]["current_step"] == 2


@patch("app.dependencies.auth.verify_firebase_token")
def test_preview_and_activate(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_RUNWAY", "title": "Activate Me"},
        headers=AUTH,
    ).json()["moment_id"]
    client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={"answers": _complete_answers(), "progress": {"current_step": 4, "completed_steps": [1, 2, 3]}},
        headers=AUTH,
    )
    preview = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/preview",
        json={},
        headers=AUTH,
    )
    assert preview.status_code == 200
    pdata = preview.json()
    assert pdata["activation_ready"] is True
    assert pdata["derived_preview"]["estimated_runway_months"] == 12
    assert pdata["template_id"] == "business_runway"

    activated = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/activate",
        json={},
        headers=AUTH,
    )
    assert activated.status_code == 200
    assert activated.json()["status"] == "ACTIVE"
    biz = mock_db._stores["business_moments"][moment_id]
    assert biz.status == "active"
    assert biz.activated_at is not None

    # Idempotent retry
    again = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/activate",
        json={},
        headers=AUTH,
    )
    assert again.status_code == 200
    assert mock_db._stores["business_moments"][moment_id].status == "active"

    runway_rows = mock_db._get_store_values("business_runway_setup")
    assert runway_rows
    assert str(runway_rows[0].moment_id) == moment_id
    assert runway_rows[0].current_cash_minor == 5000000


@patch("app.dependencies.auth.verify_firebase_token")
def test_activation_rejects_negative_cash(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_RUNWAY"},
        headers=AUTH,
    ).json()["moment_id"]
    bad = _complete_answers()
    bad["current_cash_minor"] = -1
    client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={"answers": bad},
        headers=AUTH,
    )
    preview = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/preview",
        json={},
        headers=AUTH,
    ).json()
    assert preview["activation_ready"] is False
    assert any("cash" in e.lower() for e in preview["blocking_errors"])


@patch("app.dependencies.auth.verify_firebase_token")
def test_jpy_activate(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_RUNWAY"},
        headers=AUTH,
    ).json()["moment_id"]
    answers = _complete_answers()
    answers["operating_currency_code"] = "JPY"
    answers["current_cash_minor"] = 1_000_000
    answers["monthly_burn_minor"] = 100_000
    client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={"answers": answers},
        headers=AUTH,
    )
    activated = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/activate",
        json={},
        headers=AUTH,
    )
    assert activated.status_code == 200
