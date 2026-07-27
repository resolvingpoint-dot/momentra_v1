"""Team Operations setup activate / preview / members (Run 3)."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _complete_answers(owner_hint: str | None = None) -> dict:
    return {
        "moment_name": "Alpha Ops",
        "team_name": "Alpha Team",
        "team_purpose": "Ship reliable ops",
        "team_size": "SMALL",
        "work_style": "HYBRID",
        "operating_currency_code": "USD",
        "timezone": "America/New_York",
        "locale": "en-US",
        "country_code": "US",
        "coordination_style": "SHARED_OWNERSHIP",
        "monitoring_level": "STANDARD",
        "review_cycle": "MONTHLY",
        "visibility": "TEAM",
        "supported_roles": ["OWNER", "MEMBER", "APPROVER"],
        "approval_required_for_spend": False,
        "invite_on_activation": True,
        "members": [
            {
                "local_id": "m-alex",
                "name": "Alex",
                "email": "alex@example.com",
                "role": "MEMBER",
                "permission_profile": "TEAM_MEMBER_V1",
                "permission_version": 1,
                "invite_method": "EMAIL",
                "invite_status": "DRAFT",
                "is_approver": False,
                "is_budget_owner": False,
            },
            {
                "local_id": "m-sam",
                "name": "Sam",
                "email": "sam@example.com",
                "role": "APPROVER",
                "permission_profile": "APPROVER_V1",
                "permission_version": 1,
                "invite_method": "EMAIL",
                "invite_status": "DRAFT",
                "is_approver": True,
                "is_budget_owner": False,
            },
        ],
    }


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_injects_locked_owner(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "TEAM_OPERATIONS", "title": "T1"},
        headers=AUTH,
    )
    assert created.status_code == 201
    body = created.json()
    # Create seeds answers/progress so clients can skip GET /setup.
    assert "answers" in body
    assert "progress" in body
    assert body["progress"]["current_step"] == 1
    members = body["answers"]["members"]
    assert members
    assert members[0]["role"] == "OWNER"
    assert members[0]["user_id"] == str(sample_user.id)
    assert members[0]["permission_profile"] == "OWNER_V1"
    moment_id = body["moment_id"]
    state = client.get(f"/api/v1/business/moments/{moment_id}/setup", headers=AUTH).json()
    assert state["answers"]["members"][0]["user_id"] == str(sample_user.id)


@patch("app.dependencies.auth.verify_firebase_token")
def test_team_ops_preview_server_readiness(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "TEAM_OPERATIONS"},
        headers=AUTH,
    ).json()["moment_id"]

    incomplete = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/preview",
        json={"answers": {}},
        headers=AUTH,
    ).json()
    assert incomplete["activation_ready"] is False
    assert incomplete["blocking_errors"]

    client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={"answers": _complete_answers(), "progress": {"current_step": 4, "completed_steps": [1, 2, 3]}},
        headers=AUTH,
    )
    ready = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/preview",
        json={},
        headers=AUTH,
    ).json()
    assert ready["activation_ready"] is True
    assert ready["blocking_errors"] == []
    assert any(b["block_id"] == "team_identity" for b in ready["summary_blocks"])


@patch("app.dependencies.auth.verify_firebase_token")
def test_team_ops_activate_sql_bridge_and_retry(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "TEAM_OPERATIONS", "title": "Alpha"},
        headers=AUTH,
    ).json()["moment_id"]

    saved = client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={"answers": _complete_answers()},
        headers=AUTH,
    )
    assert saved.status_code == 200
    members = saved.json()["answers"]["members"]
    assert any(m["role"] == "OWNER" for m in members)
    assert sum(1 for m in members if m.get("email") == "alex@example.com") == 1

    with patch(
        "app.domains.business.setup.invites.send_group_invite_email",
        new_callable=AsyncMock,
        return_value={"sent": False, "error": "resend_not_configured"},
    ):
        activated = client.post(
            f"/api/v1/business/moments/{moment_id}/setup/activate",
            headers=AUTH,
        )
    assert activated.status_code == 200, activated.text
    body = activated.json()
    assert body["status"] == "ACTIVE"

    # Shared moment UUID is used for business_moments bridge.
    assert moment_id in mock_db._stores["business_moments"]
    biz = mock_db._stores["business_moments"][moment_id]
    assert biz.status == "active", f"expected SQL root active after activate, got {biz.status!r}"
    assert biz.activated_at is not None
    assert mock_db._stores["business_moment_setup"]
    assert mock_db._stores["business_moment_members"]
    assert mock_db._stores["business_workspaces"]

    # Simulate split-brain: shared ACTIVE but legacy left configured (pre-fix rows).
    biz.status = "configured"
    biz.activated_at = None

    # Retry heals SQL root and does not duplicate owner membership envelope.
    again = client.post(
        f"/api/v1/business/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert again.status_code == 200
    assert again.json()["status"] == "ACTIVE"
    assert len(again.json()["membership"]) == 1
    healed = mock_db._stores["business_moments"][moment_id]
    assert healed.status == "active"
    assert healed.activated_at is not None


@patch("app.dependencies.auth.verify_firebase_token")
def test_negative_budget_rejected_on_activate(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = client.post(
        "/api/v1/business/moments",
        json={"moment_type_code": "TEAM_OPERATIONS"},
        headers=AUTH,
    ).json()["moment_id"]
    answers = _complete_answers()
    answers["monthly_team_budget_minor"] = -5
    client.put(
        f"/api/v1/business/moments/{moment_id}/setup/draft",
        json={"answers": answers},
        headers=AUTH,
    )
    resp = client.post(f"/api/v1/business/moments/{moment_id}/setup/activate", headers=AUTH)
    assert resp.status_code == 400
