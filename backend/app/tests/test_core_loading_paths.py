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


@pytest.mark.asyncio
async def test_personal_force_refresh_serves_stale_no_sync_build(monkeypatch):
    from types import SimpleNamespace
    from uuid import uuid4

    from app.domains.projections.projection_cache import ProjectionEnvelope
    from app.domains.projections.projection_service import ProjectionReadService

    service = ProjectionReadService(SimpleNamespace())
    user_id = uuid4()
    payload = {"pulse": True}
    builds = {"n": 0}
    marks: list = []
    delays: list = []

    async def mark_stale(*a, **_k):
        marks.append(a)

    async def get(*_a, **_k):
        return ProjectionEnvelope(version=1, updated_at="t", payload=payload, stale=True)

    async def build_and_store(*_a, **_k):
        builds["n"] += 1
        return {"built": True}

    monkeypatch.setattr(
        "app.domains.projections.projection_service.projection_cache.mark_stale",
        mark_stale,
    )
    monkeypatch.setattr(
        "app.domains.projections.projection_service.projection_cache.get",
        get,
    )
    monkeypatch.setattr(service, "_build_and_store", build_and_store)
    monkeypatch.setattr(
        service,
        "_enqueue_stale_rebuild",
        lambda *a, **k: delays.append((a, k)) or True,
    )

    out = await service.get_slice(user_id, "LIFE_OPERATIONS", "pulse", force_refresh=True)
    assert out == payload
    assert builds["n"] == 0
    assert len(marks) == 1
    assert delays and delays[0][1].get("reason") == "manual"


@pytest.mark.asyncio
async def test_quick_add_invalidation_marks_stale_not_delete(monkeypatch):
    from uuid import uuid4

    from app.domains.projections import invalidation

    user_id = uuid4()
    marks: list = []
    deletes: list = []

    async def mark_stale(*a, **_k):
        marks.append(a)

    async def delete(*a, **_k):
        deletes.append(a)

    monkeypatch.setattr(invalidation.projection_cache, "mark_stale", mark_stale)
    monkeypatch.setattr(invalidation.projection_cache, "delete", delete)
    monkeypatch.setattr(invalidation, "invalidate_projection_cache", lambda *_a: None)
    monkeypatch.setattr(invalidation, "_enqueue_slice", lambda *_a, **_k: None)

    await invalidation.invalidate_for_quick_add(user_id, "LIFE_OPERATIONS", "EXPENSE")
    assert marks
    assert not deletes


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
