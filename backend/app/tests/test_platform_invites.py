"""Opaque platform invite codes + company invite API."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.domains.invites import codes as invite_codes
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


def test_opaque_code_alphabet_excludes_confusable():
    for _ in range(40):
        code = invite_codes.generate_opaque_code(8)
        assert len(code) == 8
        assert all(ch in invite_codes.OPAQUE_ALPHABET for ch in code)
        assert "0" not in code and "1" not in code
        assert "O" not in code and "I" not in code and "L" not in code


def test_hash_invite_code_stable_and_case_insensitive():
    a = invite_codes.hash_invite_code("AB7K9Q2M")
    b = invite_codes.hash_invite_code("ab7k9q2m")
    assert a == b
    assert len(a) == 64


def test_is_opaque_code_shape():
    assert invite_codes.is_opaque_code_shape("AB7K9Q2M")
    assert not invite_codes.is_opaque_code_shape("eyJhbGciOi.abc.def")
    assert not invite_codes.is_opaque_code_shape("short")
    assert invite_codes.looks_like_jwt("aaa.bbb.ccc.dddddddd")


def test_redact_invite_path():
    assert "[REDACTED]" in invite_codes.redact_invite_path("/invite/AB7K9Q2M")
    assert "[REDACTED]" in invite_codes.redact_invite_path(
        "/api/v1/business/company-invites/SECRET12/accept"
    )


@patch("app.dependencies.auth.verify_firebase_token")
def test_company_opaque_create_preview_accept(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    from app.domains.business.models import BusinessWorkspaceMembers, BusinessWorkspaces
    from app.tests.conftest import MOCK_USER_ID

    _auth(mock_verify)
    mock_db.add(sample_user)
    now = datetime.now(timezone.utc)
    ws_id = uuid4()
    mock_db.add(
        BusinessWorkspaces(
            workspace_id=ws_id,
            owned_by=MOCK_USER_ID,
            created_by=MOCK_USER_ID,
            name="Acme Co",
            status="ACTIVE",
            created_at=now.replace(tzinfo=None),
            updated_at=now.replace(tzinfo=None),
        )
    )
    mock_db.add(
        BusinessWorkspaceMembers(
            member_id=uuid4(),
            workspace_id=ws_id,
            user_id=MOCK_USER_ID,
            role="OWNER",
            status="ACTIVE",
            created_at=now.replace(tzinfo=None),
            updated_at=now.replace(tzinfo=None),
        )
    )

    created = client.post(
        f"/api/v1/business/workspaces/{ws_id}/invites/opaque",
        json={"role_code": "MEMBER", "max_uses": 1, "expires_in_days": 7},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["code"]
    assert body["invite_url"].endswith(body["code"])
    code = body["code"]

    preview = client.get(f"/api/v1/business/company-invites/{code}")
    assert preview.status_code == 200, preview.text
    assert preview.json()["invite_type"] == "COMPANY"
    assert preview.json()["company"]["display_name"] == "Acme Co"
    assert preview.json()["status"] == "ACTIVE"

    guest = UserModel(
        id=uuid4(),
        firebase_uid="guest-opaque",
        email="opaque@example.com",
        display_name="Opaque Guest",
        created_at=now,
        updated_at=now,
        last_login_at=now,
    )
    mock_db.add(guest)
    mock_verify.return_value = {
        "uid": "guest-opaque",
        "email": "opaque@example.com",
        "name": "Opaque Guest",
    }
    accepted = client.post(
        f"/api/v1/business/company-invites/{code}/accept",
        headers=AUTH,
    )
    assert accepted.status_code == 200, accepted.text
    data = accepted.json()
    assert data["result"] == "ACCEPTED"
    assert data["workspace_id"] == str(ws_id)

    # Second accept → already member, does not fail hard
    again = client.post(
        f"/api/v1/business/company-invites/{code}/accept",
        headers=AUTH,
    )
    assert again.status_code == 200, again.text
    assert again.json()["result"] in {"ALREADY_MEMBER", "EXHAUSTED", "ACCEPTED"}


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_opaque_draft_accept(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/group/moments",
        json={"moment_type_code": "TRIP", "moment_name": "Opaque Trip"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]
    client.post(f"/api/v1/group/setup/moments/{moment_id}/activate", headers=AUTH)

    draft = client.get(f"/api/v1/moments/{moment_id}/invite-draft", headers=AUTH)
    assert draft.status_code == 200, draft.text
    code = draft.json()["invite_code"]
    assert invite_codes.is_opaque_code_shape(code)
    assert draft.json()["qr_payload"] == draft.json()["invite_link"]

    now = datetime.now(timezone.utc)
    invitee = UserModel(
        id=uuid4(),
        firebase_uid="invitee-opaque",
        email="io@example.com",
        display_name="IO",
        created_at=now,
        updated_at=now,
        last_login_at=now,
    )
    mock_db.add(invitee)
    mock_verify.return_value = {
        "uid": "invitee-opaque",
        "email": "io@example.com",
        "name": "IO",
    }
    accepted = client.post(f"/api/v1/invites/{code}/accept", headers=AUTH)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["moment_id"] == moment_id
    assert accepted.json()["already_member"] is False

    boot = client.get("/api/v1/group/session/bootstrap", headers=AUTH)
    assert boot.status_code == 200
    ids = {str(m.get("id")) for m in boot.json().get("moments") or []}
    assert moment_id in ids
