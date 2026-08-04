"""Tests for member leave (Group + Business)."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.domains.business.models import BusinessMomentMembers
from app.domains.group.models import GroupMomentMembers
from app.domains.moments.models import MomentModel
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _seed_group_with_member(mock_db, owner: UserModel, member_user: UserModel):
    moment_id = uuid4()
    moment = MomentModel(
        id=moment_id,
        user_id=owner.id,
        context_type="GROUP",
        moment_type="SHARED_EXPERIENCE",
        title="Wedding",
        status="ACTIVE",
        setup_state="COMPLETE",
        description='{"runtime":{"members":[{"user_id":"%s","status":"ACTIVE"},{"user_id":"%s","status":"ACTIVE"}]}}'
        % (owner.id, member_user.id),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.add(moment)
    membership = GroupMomentMembers(
        member_id=uuid4(),
        moment_id=moment_id,
        display_name="Guest",
        role_code="PARTICIPANT",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc),
        user_id=member_user.id,
    )
    mock_db.add(membership)
    return moment, membership


@patch("app.dependencies.auth.verify_firebase_token")
def test_member_leave_group_moment(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    owner = UserModel(
        id=uuid4(),
        firebase_uid="owner-uid",
        email="owner@example.com",
        display_name="Owner",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.add(owner)
    moment, membership = _seed_group_with_member(mock_db, owner, sample_user)

    resp = client.post(
        f"/api/v1/group/moments/{moment.id}/leave",
        headers=AUTH,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("moment_id") == str(moment.id)
    assert membership.status == "LEFT"
    assert membership.left_at is not None
    assert moment.status == "ACTIVE"


@patch("app.dependencies.auth.verify_firebase_token")
def test_owner_cannot_leave_group_moment(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment, _ = _seed_group_with_member(
        mock_db,
        sample_user,
        UserModel(
            id=uuid4(),
            firebase_uid="guest-uid",
            email="guest@example.com",
            display_name="Guest",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    )

    resp = client.post(
        f"/api/v1/group/moments/{moment.id}/leave",
        headers=AUTH,
    )
    assert resp.status_code == 403, resp.text
    detail = resp.json().get("error") or resp.json().get("detail") or {}
    if isinstance(detail, dict):
        code = detail.get("code") or ""
        assert code == "owner_cannot_leave" or "owner" in str(detail).lower()
    else:
        assert "owner" in str(detail).lower() or resp.status_code == 403


@patch("app.dependencies.auth.verify_firebase_token")
def test_non_member_leave_group_404(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = uuid4()
    mock_db.add(
        MomentModel(
            id=moment_id,
            user_id=uuid4(),
            context_type="GROUP",
            moment_type="SHARED_EXPERIENCE",
            title="Wedding",
            status="ACTIVE",
            setup_state="COMPLETE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )

    resp = client.post(
        f"/api/v1/group/moments/{moment_id}/leave",
        headers=AUTH,
    )
    assert resp.status_code == 404, resp.text


@patch("app.dependencies.auth.verify_firebase_token")
def test_member_leave_drops_from_group_inventory(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    owner = UserModel(
        id=uuid4(),
        firebase_uid="owner-uid-2",
        email="owner2@example.com",
        display_name="Owner",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.add(owner)
    moment, membership = _seed_group_with_member(mock_db, owner, sample_user)

    before = client.get("/api/v1/group/session/bootstrap", headers=AUTH)
    assert before.status_code == 200, before.text
    before_ids = {m.get("id") for m in (before.json().get("moments") or [])}
    assert str(moment.id) in before_ids

    leave = client.post(f"/api/v1/group/moments/{moment.id}/leave", headers=AUTH)
    assert leave.status_code == 200, leave.text
    assert membership.status == "LEFT"

    after = client.get("/api/v1/group/session/bootstrap", headers=AUTH)
    assert after.status_code == 200, after.text
    after_ids = {m.get("id") for m in (after.json().get("moments") or [])}
    assert str(moment.id) not in after_ids


@patch("app.dependencies.auth.verify_firebase_token")
def test_member_leave_business_moment(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    owner_id = uuid4()
    moment_id = uuid4()
    mock_db.add(
        MomentModel(
            id=moment_id,
            user_id=owner_id,
            context_type="BUSINESS",
            moment_type="TEAM_OPERATIONS",
            title="Ops",
            status="ACTIVE",
            setup_state="COMPLETE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    member = BusinessMomentMembers(
        member_id=uuid4(),
        moment_id=moment_id,
        user_id=sample_user.id,
        name="Guest",
        role="Team Member",
        member_status="active",
        added_by=owner_id,
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
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    mock_db.add(member)

    resp = client.post(
        f"/api/v1/business/moments/{moment_id}/leave",
        headers=AUTH,
    )
    assert resp.status_code == 200, resp.text
    assert member.member_status == "removed"


@patch("app.dependencies.auth.verify_firebase_token")
def test_owner_cannot_leave_business_moment(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment_id = uuid4()
    mock_db.add(
        MomentModel(
            id=moment_id,
            user_id=sample_user.id,
            context_type="BUSINESS",
            moment_type="TEAM_OPERATIONS",
            title="Ops",
            status="ACTIVE",
            setup_state="COMPLETE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )

    resp = client.post(
        f"/api/v1/business/moments/{moment_id}/leave",
        headers=AUTH,
    )
    assert resp.status_code == 403, resp.text
