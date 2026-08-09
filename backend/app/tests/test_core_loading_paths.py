from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_aggregate_pulse_reads_templates_concurrently(monkeypatch):
    from app.domains.projections.projection_service import ProjectionReadService

    service = ProjectionReadService(SimpleNamespace())
    entered: set[str] = set()
    both_entered = asyncio.Event()

    async def get_slice(_user_id, code, _slice_type, **_kwargs):
        entered.add(code)
        if len(entered) == 2:
            both_entered.set()
        await asyncio.wait_for(both_entered.wait(), timeout=0.2)
        return {"status": "ACTIVE", "pulse": {"code": code}}

    monkeypatch.setattr(service, "get_slice", get_slice)

    result = await service.get_aggregate_pulse(
        uuid4(), ["LIFE_OPERATIONS", "LIFESTYLE"], active_count=2
    )

    assert result["life_operations"] == {"code": "LIFE_OPERATIONS"}
    assert result["lifestyle"] == {"code": "LIFESTYLE"}


@pytest.mark.asyncio
async def test_session_bearer_short_circuits_firebase(monkeypatch):
    from app.dependencies import auth as auth_dependency

    request = SimpleNamespace(state=SimpleNamespace())
    credentials = SimpleNamespace(credentials="session-token")
    firebase_calls = {"n": 0}

    monkeypatch.setattr(
        auth_dependency,
        "decode_session_token",
        lambda _token: {"sub": "firebase-uid", "type": "session"},
    )

    def verify_firebase(_token):
        firebase_calls["n"] += 1
        raise AssertionError("Firebase must not run for a valid session JWT")

    monkeypatch.setattr(auth_dependency, "verify_firebase_token", verify_firebase)

    result = await auth_dependency.get_current_user(request, credentials)

    assert result["type"] == "session"
    assert result["uid"] == "firebase-uid"
    assert firebase_calls["n"] == 0


def test_firebase_verification_uses_short_ttl_cache(monkeypatch):
    from app.core import firebase

    firebase._verified_token_cache.clear()
    monkeypatch.setattr(firebase, "_firebase_app", object())
    calls = {"n": 0}

    def verify(_token, app):
        assert app is firebase._firebase_app
        calls["n"] += 1
        return {"uid": "cached-user"}

    monkeypatch.setattr(firebase.auth, "verify_id_token", verify)

    first = firebase.verify_firebase_token("firebase-token")
    second = firebase.verify_firebase_token("firebase-token")

    assert first == second == {"uid": "cached-user"}
    assert calls["n"] == 1
