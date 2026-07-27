from unittest.mock import patch

from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _create_group_moment(client: TestClient) -> str:
    created = client.post(
        "/api/v1/group/moments",
        json={"moment_type_code": "TRIP", "moment_name": "Goa 2026"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    return created.json()["moment_id"]


@patch("app.dependencies.auth.verify_firebase_token")
@patch("app.domains.invites.service.send_group_invite_email")
def test_create_email_invite(mock_send, mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    async def _fake_send(to, subject, body):
        return {"sent": False, "error": "resend_not_configured"}

    mock_send.side_effect = _fake_send
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    resp = client.post(
        f"/api/v1/moments/{moment_id}/email-invites",
        json={"email": "friend@example.com"},
        headers=AUTH,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["moment_id"] == moment_id
    assert data["invitee_email"] == "friend@example.com"
    assert data["status"] == "pending"
    assert data["id"] and data["expires_at"] and data["created_at"]
    assert "sent" in data
    assert data.get("email_subject")


@patch("app.dependencies.auth.verify_firebase_token")
def test_list_email_invites_empty(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    resp = client.get(f"/api/v1/moments/{moment_id}/email-invites", headers=AUTH)
    assert resp.status_code == 200
    assert resp.json() == []


@patch("app.dependencies.auth.verify_firebase_token")
def test_share_invite_then_accept(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    share = client.get(f"/api/v1/moments/{moment_id}/share-invite", headers=AUTH)
    assert share.status_code == 200, share.text
    body = share.json()
    assert body["invite_url"] and body["trip_name"] == "Goa 2026"

    token = body["invite_url"].rsplit("/", 1)[-1]
    accepted = client.post(f"/api/v1/invites/{token}/accept", headers=AUTH)
    assert accepted.status_code == 200, accepted.text
    data = accepted.json()
    assert data["moment_id"] == moment_id
    assert data["moment_name"] == "Goa 2026"
    assert data["moment_type"] == "TRIP"
    # Owner accepting their own invite is already a member.
    assert data["already_member"] is True


@patch("app.dependencies.auth.verify_firebase_token")
def test_accept_rejects_garbage_token(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.post("/api/v1/invites/not-a-real-token/accept", headers=AUTH)
    assert resp.status_code == 400


@patch("app.dependencies.auth.verify_firebase_token")
def test_share_invite_unknown_moment_404(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/moments/00000000-0000-0000-0000-000000000000/share-invite",
        headers=AUTH,
    )
    assert resp.status_code == 404


def test_invites_require_auth(client: TestClient, mock_db):
    resp = client.get(
        "/api/v1/moments/00000000-0000-0000-0000-000000000000/share-invite"
    )
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
@patch("app.domains.invites.service.send_group_invite_email")
def test_invite_draft_payload(mock_send, mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    resp = client.get(f"/api/v1/moments/{moment_id}/invite-draft", headers=AUTH)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["invite_link"]
    assert data["invite_code"]
    assert data["qr_payload"] == data["invite_link"]
    assert data["email_subject"]
    assert data["email_body"]
    assert data["whatsapp_text"]
    assert data["sms_text"]
    assert data["invite_id"]
    assert "Goa 2026" in data["email_subject"] or "Goa 2026" in (data.get("experience_name") or "")


@patch("app.dependencies.auth.verify_firebase_token")
def test_invite_draft_reuses_active(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    first = client.get(f"/api/v1/moments/{moment_id}/invite-draft", headers=AUTH)
    assert first.status_code == 200, first.text
    second = client.get(f"/api/v1/moments/{moment_id}/invite-draft", headers=AUTH)
    assert second.status_code == 200, second.text
    assert first.json()["invite_id"] == second.json()["invite_id"]
    assert first.json()["invite_code"] == second.json()["invite_code"]


@patch("app.dependencies.auth.verify_firebase_token")
def test_invite_draft_refresh_rotates(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    first = client.get(f"/api/v1/moments/{moment_id}/invite-draft", headers=AUTH)
    assert first.status_code == 200, first.text
    refreshed = client.post(
        f"/api/v1/moments/{moment_id}/invite-draft/refresh",
        json={},
        headers=AUTH,
    )
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["invite_id"] != first.json()["invite_id"]
    assert refreshed.json()["invite_code"] != first.json()["invite_code"]


@patch("app.dependencies.auth.verify_firebase_token")
@patch("app.domains.invites.service.send_group_invite_email")
def test_email_invite_calls_resend_wrapper(
    mock_send, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    async def _fake_send(to, subject, body):
        return {"sent": True}

    mock_send.side_effect = _fake_send
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    resp = client.post(
        f"/api/v1/moments/{moment_id}/email-invites",
        json={"email": "friend@example.com"},
        headers=AUTH,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["sent"] is True
    assert data["invite_link"]
    assert data["email_subject"]
    assert mock_send.await_count == 1 or mock_send.call_count == 1


@patch("app.dependencies.auth.verify_firebase_token")
@patch("app.domains.invites.service.send_group_invite_email")
def test_email_invite_still_returns_copy_when_resend_fails(
    mock_send, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    async def _fake_send(to, subject, body):
        return {"sent": False, "error": "resend_not_configured"}

    mock_send.side_effect = _fake_send
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    resp = client.post(
        f"/api/v1/moments/{moment_id}/email-invites",
        json={"email": "friend@example.com"},
        headers=AUTH,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["sent"] is False
    assert data["invite_link"]
    assert data["email_body"]
    assert data.get("send_error")


@patch("app.dependencies.auth.verify_firebase_token")
def test_list_email_invites_after_create(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = _create_group_moment(client)

    with patch("app.domains.invites.service.send_group_invite_email") as mock_send:
        async def _fake_send(to, subject, body):
            return {"sent": False, "error": "resend_not_configured"}

        mock_send.side_effect = _fake_send
        client.post(
            f"/api/v1/moments/{moment_id}/email-invites",
            json={"email": "friend@example.com"},
            headers=AUTH,
        )

    resp = client.get(f"/api/v1/moments/{moment_id}/email-invites", headers=AUTH)
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) >= 1
    assert rows[0]["invitee_email"] == "friend@example.com"


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_invite_accept_binds_member(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Business JWT accept must activate business_moment_members, not Group store."""
    from datetime import datetime, timezone
    from uuid import uuid4

    from app.core.security import create_invite_token
    from app.domains.business.models import (
        BusinessMomentInvitations,
        BusinessMomentMembers,
        BusinessMoments,
    )
    from app.domains.business.setup.invites import invite_token_hash
    from app.domains.moments.models import MomentModel
    from app.tests.conftest import MOCK_USER_ID

    _auth(mock_verify)
    mock_db.add(sample_user)

    now = datetime.now(timezone.utc)
    moment_id = uuid4()
    invite_id = uuid4()
    member_id = uuid4()
    guest = UserModel(
        id=uuid4(),
        firebase_uid="guest456",
        email="guest@example.com",
        display_name="Guest",
        created_at=now,
        updated_at=now,
        last_login_at=now,
    )
    mock_db.add(guest)

    mock_db.add(
        MomentModel(
            id=moment_id,
            user_id=MOCK_USER_ID,
            context_type="BUSINESS",
            moment_type="TEAM_OPERATIONS",
            title="Ops Team",
            status="ACTIVE",
            setup_state="READY",
        )
    )
    mock_db.add(
        BusinessMoments(
            moment_id=moment_id,
            workspace_id=uuid4(),
            moment_type="team_operations",
            moment_name="Ops Team",
            status="active",
            created_by=MOCK_USER_ID,
            created_at=now.replace(tzinfo=None),
            updated_at=now.replace(tzinfo=None),
        )
    )
    mock_db.add(
        BusinessMomentMembers(
            member_id=member_id,
            moment_id=moment_id,
            name="Alex",
            role="Team Member",
            member_status="invited",
            added_by=MOCK_USER_ID,
            local_id="m-alex",
            is_team_lead=False,
            is_budget_owner=False,
            can_edit_own_entries=True,
            can_edit_team_entries=False,
            can_edit_expense_entries=False,
            can_add_runway_transactions=False,
            can_edit_financial_entries=False,
            can_manage_runway_settings=False,
            can_approve_runway_changes=False,
            can_add_operations_records=True,
            can_edit_operations_records=False,
            can_edit_own_operations_records=True,
            can_approve_operations_requests=False,
            can_delete_operations_records=False,
            can_manage_operations_settings=False,
            created_at=now.replace(tzinfo=None),
            updated_at=now.replace(tzinfo=None),
        )
    )
    token = create_invite_token(
        str(moment_id),
        "guest@example.com",
        participant_id="m-alex",
        invite_id=str(invite_id),
    )
    mock_db.add(
        BusinessMomentInvitations(
            invite_id=invite_id,
            moment_id=moment_id,
            invite_method="qr",
            invite_status="sent",
            invite_target="guest@example.com",
            send_on_activation=True,
            member_id=member_id,
            qr_token=invite_token_hash(token),
            local_id="m-alex",
            channel="QR",
            created_at=now.replace(tzinfo=None),
            updated_at=now.replace(tzinfo=None),
        )
    )

    mock_verify.return_value = {
        "uid": "guest456",
        "email": "guest@example.com",
        "name": "Guest",
    }
    accepted = client.post(f"/api/v1/invites/{token}/accept", headers=AUTH)
    assert accepted.status_code == 200, accepted.text
    data = accepted.json()
    assert data["moment_id"] == str(moment_id)
    assert data["moment_type"] == "TEAM_OPERATIONS"
    assert data["already_member"] is False
    assert data["participant_id"] == str(member_id)

    member = mock_db._stores["business_moment_members"][str(member_id)]
    assert str(member.user_id) == str(guest.id)
    assert member.member_status == "active"
    invite = mock_db._stores["business_moment_invitations"][str(invite_id)]
    assert invite.invite_status == "accepted"


@patch("app.dependencies.auth.verify_firebase_token")
def test_business_open_qr_accept_creates_member(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    from datetime import datetime, timezone
    from uuid import uuid4

    from app.core.security import create_invite_token
    from app.domains.business.models import BusinessMoments
    from app.domains.moments.models import MomentModel
    from app.tests.conftest import MOCK_USER_ID

    _auth(mock_verify)
    mock_db.add(sample_user)
    now = datetime.now(timezone.utc)
    moment_id = uuid4()
    guest = UserModel(
        id=uuid4(),
        firebase_uid="guest789",
        email="open@example.com",
        display_name="Open Guest",
        created_at=now,
        updated_at=now,
        last_login_at=now,
    )
    mock_db.add(guest)
    mock_db.add(
        MomentModel(
            id=moment_id,
            user_id=MOCK_USER_ID,
            context_type="BUSINESS",
            moment_type="TEAM_OPERATIONS",
            title="Open QR Team",
            status="ACTIVE",
            setup_state="READY",
        )
    )
    mock_db.add(
        BusinessMoments(
            moment_id=moment_id,
            workspace_id=uuid4(),
            moment_type="team_operations",
            moment_name="Open QR Team",
            status="active",
            created_by=MOCK_USER_ID,
            created_at=now.replace(tzinfo=None),
            updated_at=now.replace(tzinfo=None),
        )
    )
    token = create_invite_token(str(moment_id), None, invite_id="abcd1234efgh5678")

    mock_verify.return_value = {
        "uid": "guest789",
        "email": "open@example.com",
        "name": "Open Guest",
    }
    accepted = client.post(f"/api/v1/invites/{token}/accept", headers=AUTH)
    assert accepted.status_code == 200, accepted.text
    data = accepted.json()
    assert data["moment_id"] == str(moment_id)
    assert data["already_member"] is False
    assert data["participant_id"]
    members = list(mock_db._stores["business_moment_members"].values())
    assert any(str(m.user_id) == str(guest.id) and m.member_status == "active" for m in members)
