"""Regression: projection build must not await its own inflight task on lock miss."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.errors import SnapshotRebuildingError
from app.domains.personal.projection import service as projection_service_mod
from app.domains.personal.projection.cache import CachedProjection
from app.domains.personal.projection.service import ProjectionService, _inflight


def _cached(user_id) -> CachedProjection:
    ctx = MagicMock()
    ctx.user_id = user_id
    return CachedProjection(
        version=1,
        generated_at=datetime.now(timezone.utc),
        context=ctx,
    )


@pytest.fixture(autouse=True)
def _clear_inflight():
    _inflight.clear()
    yield
    _inflight.clear()


@pytest.mark.asyncio
async def test_lock_miss_polls_cache_without_self_await(monkeypatch):
    """Reproduce production: current task is in _inflight while Redis lock is held elsewhere."""
    user_id = uuid4()
    expected = _cached(user_id)
    polls = {"n": 0}

    async def acquire_lock(_key: str, ttl: int = 30) -> bool:
        return False

    def get_cached_side_effect(uid):
        polls["n"] += 1
        if polls["n"] >= 3:
            return expected
        return None

    monkeypatch.setattr(projection_service_mod, "_LOCK_MISS_POLLS", 20)
    monkeypatch.setattr(projection_service_mod, "_LOCK_MISS_SLEEP", 0.001)
    monkeypatch.setattr(projection_service_mod.core_cache, "acquire_lock", acquire_lock)
    monkeypatch.setattr(projection_service_mod, "get_cached", get_cached_side_effect)
    monkeypatch.setattr(
        projection_service_mod,
        "set_build_coalesced",
        lambda *_a, **_k: None,
    )

    svc = ProjectionService(session=MagicMock())

    async def run_like_get_cached_context():
        task = __import__("asyncio").create_task(svc._build_and_cache(user_id))
        _inflight[user_id] = task
        try:
            return await task
        finally:
            _inflight.pop(user_id, None)

    result = await run_like_get_cached_context()
    assert result is expected
    assert polls["n"] >= 3


@pytest.mark.asyncio
async def test_lock_miss_timeout_raises_snapshot_rebuilding(monkeypatch):
    user_id = uuid4()

    async def acquire_lock(_key: str, ttl: int = 30) -> bool:
        return False

    monkeypatch.setattr(projection_service_mod, "_LOCK_MISS_POLLS", 3)
    monkeypatch.setattr(projection_service_mod, "_LOCK_MISS_SLEEP", 0.001)
    monkeypatch.setattr(projection_service_mod.core_cache, "acquire_lock", acquire_lock)
    monkeypatch.setattr(projection_service_mod, "get_cached", lambda _uid: None)

    svc = ProjectionService(session=MagicMock())
    task = __import__("asyncio").create_task(svc._build_and_cache(user_id))
    _inflight[user_id] = task
    try:
        with pytest.raises(SnapshotRebuildingError):
            await task
    finally:
        _inflight.pop(user_id, None)


@pytest.mark.asyncio
async def test_get_cached_context_coalesces_concurrent_callers(monkeypatch):
    """Callers outside the builder still await the shared inflight task."""
    user_id = uuid4()
    expected = _cached(user_id)
    builds = {"n": 0}

    async def slow_build(_session, _uid):
        builds["n"] += 1
        await __import__("asyncio").sleep(0.05)
        return expected.context

    async def acquire_lock(_key: str, ttl: int = 30) -> bool:
        return True

    async def release_lock(_key: str) -> None:
        return None

    monkeypatch.setattr(projection_service_mod.core_cache, "acquire_lock", acquire_lock)
    monkeypatch.setattr(projection_service_mod.core_cache, "release_lock", release_lock)
    monkeypatch.setattr(projection_service_mod, "get_cached", lambda _uid: None)
    monkeypatch.setattr(projection_service_mod, "set_cached", lambda *_a, **_k: None)
    monkeypatch.setattr(
        projection_service_mod.ProjectionBuilder,
        "build",
        slow_build,
    )
    monkeypatch.setattr(projection_service_mod, "current_version", lambda _uid: 1)
    monkeypatch.setattr(
        projection_service_mod, "set_projection_build_ms", lambda *_a, **_k: None
    )
    monkeypatch.setattr(
        projection_service_mod, "set_build_coalesced", lambda *_a, **_k: None
    )

    svc = ProjectionService(session=MagicMock())
    asyncio = __import__("asyncio")
    a, b = await asyncio.gather(
        svc.get_cached_context(user_id),
        svc.get_cached_context(user_id),
    )
    assert a.context is expected.context
    assert b.context is expected.context
    assert builds["n"] == 1
