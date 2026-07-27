"""Business Operations setup activate / preview (Run 5)."""
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
        "moment_name": "Ops HQ",
        "operations_name": "Core Operations",
        "operations_scope": "GENERAL_OPERATIONS",
        "operating_model": "HYBRID",
        "operating_currency_code": "USD",
        "timezone": "America/New_York",
        "locale": "en-US",
        "country_code": "US",
        "review_cycle": "MONTHLY",
        "monthly_budget_minor": 1_000_000,
        "allocation_mode": "FIXED_AMOUNT",
        "budget_allocations": [
            {
                "allocation_id": "alloc-1",
                "category_code": "payroll",
                "label": "Payroll",
                "amount_minor": 600_000,
            },
            {
                "allocation_id": "alloc-2",
                "category_code": "vendors",
                "label": "Vendors",
                "amount_minor": 200_000,
            },
        ],
        "vendor_dependency_level": "MODERATE",
        "approval_model": "OWNER_ONLY",
        "issue_sensitivity": "NORMAL",
        "monitoring_level": "STANDARD",
        "operational_visibility": "TEAM",
        "confirm_budget": True,
        "confirm_allocations": True,
        "confirm_governance": True,
        "confirm_members": True,
        "confirm_alerts": True,
        "invite_on_activation": True,
        "members": [
            {
                "local_id": "m-ops",
                "name": "Ops Lead",
                "email": "ops@example.com",
                "role": "OPERATIONS_LEAD",
                "permission_profile": "OPERATIONS_LEAD_V1",
                "permission_version": 1,
                "invite_method": "EMAIL",
                "invite_status": "DRAFT",
                "is_operations_lead": True,
            }
        ],
    }


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_ops_injects_owner(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/business/moments",
        json={
            "moment_type_code": "department_operations",
            "title": "Ops",
            "template_id": "operations",
        },
        headers=AUTH,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["moment_type_code"] == "BUSINESS_OPERATIONS"
    assert body["template_id"] == "business_operations"
    state = client.get(
        f"/api/v1/business/moments/{body['moment_id']}/setup", headers=AUTH
    ).json()
    assert state["answers"]["members"][0]["role"] == "OWNER"


@patch("app.dependencies.auth.verify_firebase_token")
def test_partial_save_resume_and_activate(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_OPERATIONS"},
        headers=AUTH,
    ).json()["moment_id"]
    saved = client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={
            "answers": {"operations_name": "Partial Ops", "monthly_budget_minor": 500},
            "progress": {"current_step": 2, "completed_steps": [1]},
        },
        headers=AUTH,
    )
    assert saved.status_code == 200
    state = client.get(f"/api/v1/business/moments/{moment_id}/setup", headers=AUTH).json()
    assert state["answers"]["operations_name"] == "Partial Ops"
    assert state["progress"]["current_step"] == 2

    client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={"answers": _complete_answers(), "progress": {"current_step": 4, "completed_steps": [1, 2, 3]}},
        headers=AUTH,
    )
    preview = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/preview",
        json={},
        headers=AUTH,
    ).json()
    assert preview["activation_ready"] is True, preview.get("blocking_errors")
    assert preview["derived_preview"]["allocated_budget_minor"] == 800_000
    assert preview["template_id"] == "business_operations"

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
    again = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/activate",
        json={},
        headers=AUTH,
    )
    assert again.status_code == 200
    assert mock_db._stores["business_moments"][moment_id].status == "active"
    rows = mock_db._get_store_values("business_operations_setup")
    assert rows
    assert str(rows[0].moment_id) == moment_id


@patch("app.dependencies.auth.verify_firebase_token")
def test_overallocation_blocks(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "BUSINESS_OPERATIONS"},
        headers=AUTH,
    ).json()["moment_id"]
    bad = _complete_answers()
    bad["budget_allocations"] = [
        {
            "allocation_id": "x",
            "category_code": "payroll",
            "label": "P",
            "amount_minor": 2_000_000,
        }
    ]
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
    assert any("allocation" in e.lower() or "budget" in e.lower() for e in preview["blocking_errors"])
