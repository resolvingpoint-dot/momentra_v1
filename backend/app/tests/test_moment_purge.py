"""Tests for permanent moment purge (delete keeping analytics)."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.domains.group.models import GroupMomentMembers
from app.domains.moments.models import MomentModel
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def _seed_group_moment(mock_db, owner: UserModel, *, title: str = "Wedding"):
    moment_id = uuid4()
    moment = MomentModel(
        id=moment_id,
        user_id=owner.id,
        context_type="GROUP",
        moment_type="SHARED_EXPERIENCE",
        title=title,
        status="ACTIVE",
        setup_state="COMPLETE",
        description='{"runtime":{"members":[{"user_id":"%s","status":"ACTIVE"}]}}'
        % owner.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db.add(moment)
    member = GroupMomentMembers(
        member_id=uuid4(),
        moment_id=moment_id,
        display_name="Guest",
        role_code="PARTICIPANT",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc),
        user_id=uuid4(),
    )
    mock_db.add(member)
    return moment, member


@patch("app.dependencies.auth.verify_firebase_token")
def test_owner_delete_group_moment_tombstones_and_exits_members(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment, member = _seed_group_moment(mock_db, sample_user)

    resp = client.post(
        f"/api/v1/group/moments/{moment.id}/delete",
        headers=AUTH,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "DELETED"
    assert body.get("is_deleted") is True
    assert moment.status == "DELETED"
    assert moment.title == "Deleted Moment"
    assert moment.description is None
    assert member.status == "LEFT"
    assert member.left_at is not None


@patch("app.dependencies.auth.verify_firebase_token")
def test_member_cannot_delete_group_moment(
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
            context_type="GROUP",
            moment_type="SHARED_EXPERIENCE",
            title="Wedding",
            status="ACTIVE",
            setup_state="COMPLETE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    mock_db.add(
        GroupMomentMembers(
            member_id=uuid4(),
            moment_id=moment_id,
            display_name="Guest",
            role_code="PARTICIPANT",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
            user_id=sample_user.id,
        )
    )

    resp = client.post(
        f"/api/v1/group/moments/{moment_id}/delete",
        headers=AUTH,
    )
    assert resp.status_code == 403
    body = resp.json()
    err = body.get("error") or {}
    code = err.get("code") or ""
    assert "moment_not_owned" in str(code) or "owner" in str(err.get("message", "")).lower()


@patch("app.dependencies.auth.verify_firebase_token")
def test_deleted_moment_hidden_from_group_inventory(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    moment, _ = _seed_group_moment(mock_db, sample_user, title="KeepMe")

    delete_resp = client.post(
        f"/api/v1/group/moments/{moment.id}/delete",
        headers=AUTH,
    )
    assert delete_resp.status_code == 200

    inv = client.get("/api/v1/group/session/bootstrap", headers=AUTH)
    assert inv.status_code == 200
    data = inv.json()
    moments = data.get("moments") or data.get("session", {}).get("moments") or []
    ids = {str(m.get("id") or m.get("moment_id") or "") for m in moments}
    assert str(moment.id) not in ids
