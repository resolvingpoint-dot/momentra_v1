"""Business projection read / single-flight / persist gates (P0)."""
from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from app.domains.projections.projection_cache import ProjectionEnvelope


@pytest.mark.asyncio
async def test_cached_or_build_fresh_hit_does_not_build(monkeypatch):
    from app.domains.business import projection_read

    user_id = uuid4()
    moment_id = uuid4()
    payload = {"ok": True}
    builds = {"n": 0}

    async def fake_envelope(*_a, **_k):
        return ProjectionEnvelope(version=3, updated_at="t", payload=payload, stale=False)

    async def build():
        builds["n"] += 1
        return {"built": True}

    monkeypatch.setattr(projection_read, "get_cached_envelope", fake_envelope)
    monkeypatch.setattr(projection_read, "record_cache_hit", lambda: None)
    monkeypatch.setattr(projection_read, "set_cache_hit", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "set_projection_version", lambda *_a, **_k: None)

    out = await projection_read.cached_or_build(
        user_id, moment_id, "moments", build, moment_type="TEAM_OPERATIONS"
    )
    assert out == payload
    assert builds["n"] == 0


@pytest.mark.asyncio
async def test_stale_returns_immediately_and_enqueues_one_refresh(monkeypatch):
    from app.domains.business import projection_read

    user_id = uuid4()
    moment_id = uuid4()
    payload = {"stale": True}
    enqueues: list[tuple] = []

    async def fake_envelope(*_a, **_k):
        return ProjectionEnvelope(version=2, updated_at="t", payload=payload, stale=True)

    async def build():
        return {"built": True}

    def fake_enqueue(*args, **kwargs):
        enqueues.append((args, kwargs))

    monkeypatch.setattr(projection_read, "get_cached_envelope", fake_envelope)
    monkeypatch.setattr(projection_read, "record_cache_hit", lambda: None)
    monkeypatch.setattr(projection_read, "set_cache_hit", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "set_build_coalesced", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "set_projection_version", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "enqueue_business_projection_refresh", fake_enqueue)

    out = await projection_read.cached_or_build(
        user_id, moment_id, "moments", build, moment_type="TEAM_OPERATIONS"
    )
    assert out == payload
    assert len(enqueues) == 1
    assert enqueues[0][1].get("slices") == "moments" or (
        len(enqueues[0][0]) >= 1
    )


@pytest.mark.asyncio
async def test_ten_parallel_misses_share_one_build_fn(monkeypatch):
    """Pulse/Moments miss path calls build_fn; single-flight lives in build_fn (_bundle)."""
    from app.domains.business import projection_read

    user_id = uuid4()
    moment_id = uuid4()
    builds = {"n": 0}
    shared: dict = {"payload": None, "event": asyncio.Event()}

    async def fake_envelope(*_a, **_k):
        return None

    monkeypatch.setattr(projection_read, "get_cached_envelope", fake_envelope)
    monkeypatch.setattr(projection_read, "record_cache_miss", lambda: None)
    monkeypatch.setattr(projection_read, "set_cache_hit", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "set_projection_build_ms", lambda *_a, **_k: None)

    async def coalesced_build():
        if shared["payload"] is not None:
            return shared["payload"]
        if builds["n"] == 0:
            builds["n"] = 1
            await asyncio.sleep(0.05)
            shared["payload"] = {"pulse": True}
            shared["event"].set()
            return shared["payload"]
        await shared["event"].wait()
        return shared["payload"]

    results = await asyncio.gather(
        *[
            projection_read.cached_or_build(
                user_id,
                moment_id,
                "pulse" if i % 2 == 0 else "moments",
                coalesced_build,
                moment_type="TEAM_OPERATIONS",
            )
            for i in range(10)
        ]
    )
    assert builds["n"] == 1
    assert all(r == results[0] for r in results)


def test_team_ops_refresh_accepts_persist_false():
    """Cold GET path must not TypeError on persist=False."""
    import inspect

    from app.domains.business.templates.team_operations.projector import (
        TeamOpsProjector,
        refresh_team_ops_projections,
    )

    sig = inspect.signature(TeamOpsProjector.refresh)
    assert "persist" in sig.parameters
    sig2 = inspect.signature(refresh_team_ops_projections)
    assert "persist" in sig2.parameters
    assert sig.parameters["persist"].default is False


@pytest.mark.asyncio
async def test_activation_warmup_enqueue_user_agg_only(monkeypatch):
    """Activate path enqueues Life/Memory via user_agg slices flag."""
    from app.domains.business import projection_cache as biz_cache

    calls: list[tuple] = []

    def fake_enqueue(task, *args):
        calls.append((getattr(task, "name", str(task)), args))

    monkeypatch.setattr(biz_cache, "enqueue_celery", fake_enqueue)
    biz_cache.enqueue_business_user_agg_refresh(uuid4(), reason="activate_warmup")
    assert len(calls) == 1
    assert calls[0][1][-1] == "user_agg"
