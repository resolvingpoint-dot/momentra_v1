"""Platform foundation unit/contract tests (Phase 1)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.auth.principal import Principal, principal_from_auth
from app.core.errors import NotFoundError, PermissionDeniedError

FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def test_principal_from_auth_session():
    user_id = uuid4()
    auth_user = {
        "type": "session",
        "uid": "fb-uid-1",
        "payload": {"sub": "fb-uid-1", "type": "session"},
    }
    p = principal_from_auth(user_id=user_id, auth_user=auth_user)
    assert isinstance(p, Principal)
    assert p.user_id == user_id
    assert p.firebase_uid == "fb-uid-1"
    assert p.auth_type == "session"
    assert "momentra:user" in p.scopes


def test_principal_from_auth_firebase():
    user_id = uuid4()
    auth_user = {
        "type": "firebase",
        "uid": "fb-uid-2",
        "payload": {"uid": "fb-uid-2"},
    }
    p = principal_from_auth(user_id=user_id, auth_user=auth_user)
    assert p.auth_strength == "firebase"
    assert p.auth_type == "firebase"


def test_authorization_require_unknown_action():
    import asyncio

    from app.authorization import ResourceRef, require

    session = MagicMock()

    async def _run() -> None:
        with pytest.raises(PermissionDeniedError) as exc:
            await require(
                session,
                uuid4(),
                "totally.unknown.action",
                ResourceRef(kind="group_moment", id=uuid4()),
                use_cache=False,
            )
        assert exc.value.code == "unknown_authz_action"

    asyncio.run(_run())


def test_authorization_personal_moment_own_not_found():
    import asyncio

    from app.authorization import ResourceRef, require

    session = AsyncMock()

    async def _run() -> None:
        with patch(
            "app.domains.moments.repository.MomentRepository.get_by_user_and_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(NotFoundError):
                await require(
                    session,
                    uuid4(),
                    "personal.moment.own",
                    ResourceRef(kind="personal_moment", id=uuid4()),
                    use_cache=False,
                )

    asyncio.run(_run())


def test_security_headers_present(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert resp.headers.get("X-Request-ID")
    assert resp.headers.get("X-Correlation-ID")


def test_correlation_id_echo(client: TestClient):
    resp = client.get("/health", headers={"X-Correlation-ID": "corr-test-1"})
    assert resp.headers.get("X-Correlation-ID") == "corr-test-1"


def test_metrics_endpoint_in_debug(client: TestClient):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "momentra_up" in resp.text


def test_idempotency_store_roundtrip():
    import asyncio

    from app.security.idempotency import IdempotencyStore

    store = IdempotencyStore(ttl_seconds=60)
    uid = uuid4()

    async def _run() -> None:
        assert await store.begin_or_replay(uid, "POST /x", "key-1") is None
        await store.put_response(uid, "POST /x", "key-1", {"ok": True})
        replay = await store.begin_or_replay(uid, "POST /x", "key-1")
        assert replay == {"ok": True}

    asyncio.run(_run())


@patch("app.api.v1.auth.verify_firebase_token")
def test_list_and_revoke_sessions(mock_verify, client: TestClient, mock_db):
    from app.application.queries.list_auth_sessions import AuthSessionView

    mock_verify.return_value = FIREBASE_CLAIMS

    exchange = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    assert exchange.status_code == 200
    access = exchange.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {access}"}

    # MockSession equality filters don't express expires_at >; seed via store contents.
    rows = mock_db._get_store_values("auth_refresh_sessions")
    assert len(rows) >= 1
    row = rows[0]
    session_id = str(row.id)

    with patch(
        "app.application.queries.list_auth_sessions.list_auth_sessions",
        new_callable=AsyncMock,
        return_value=[
            AuthSessionView(
                id=row.id,
                user_agent=row.user_agent,
                ip=row.ip,
                created_at=row.created_at.isoformat(),
                last_used_at=None,
                expires_at=row.expires_at.isoformat(),
            )
        ],
    ):
        listed = client.get("/api/v1/auth/sessions", headers=headers)
    assert listed.status_code == 200
    sessions = listed.json()
    assert len(sessions) >= 1
    assert sessions[0]["id"] == session_id

    revoked = client.delete(f"/api/v1/auth/sessions/{session_id}", headers=headers)
    assert revoked.status_code == 204

    missing = client.delete(f"/api/v1/auth/sessions/{uuid4()}", headers=headers)
    assert missing.status_code == 404


def test_cursor_page_helper():
    from app.core.pagination import CursorPage

    page = CursorPage.create([{"id": 1}], next_cursor="abc")
    assert page.has_more is True
    assert page.next_cursor == "abc"
