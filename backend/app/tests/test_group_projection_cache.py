"""Group projection cache / read path smoke tests."""
from __future__ import annotations

from uuid import uuid4

import pytest

from app.domains.group.projection_cache import parse_template_key, template_key


def test_template_key_roundtrip():
    mid = uuid4()
    key = template_key("SHARED_EXPERIENCE", mid)
    mt, parsed = parse_template_key(key)
    assert mt == "SHARED_EXPERIENCE"
    assert parsed == mid


def test_template_key_purchase_living():
    mid = uuid4()
    for mt in ("SHARED_PURCHASE", "SHARED_LIVING"):
        key = template_key(mt, mid)
        out_mt, out_id = parse_template_key(key)
        assert out_mt == mt
        assert out_id == mid


@pytest.mark.asyncio
async def test_cached_or_build_serves_memory_cache(monkeypatch):
    from app.domains.group import projection_read
    from app.domains.projections.projection_cache import ProjectionEnvelope

    user_id = uuid4()
    moment_id = uuid4()
    payload = {"trip_name": "Test", "moment_id": str(moment_id)}
    builds = {"n": 0}

    async def fake_envelope(*_a, **_k):
        return ProjectionEnvelope(version=1, updated_at="t", payload=payload, stale=False)

    async def build():
        builds["n"] += 1
        return {"built": True}

    monkeypatch.setattr(projection_read, "get_cached_envelope", fake_envelope)
    monkeypatch.setattr(projection_read, "record_cache_hit", lambda: None)
    monkeypatch.setattr(projection_read, "set_cache_hit", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "set_projection_version", lambda *_a, **_k: None)

    out = await projection_read.cached_or_build(
        user_id, moment_id, "pulse", build, moment_type="SHARED_EXPERIENCE"
    )
    assert out == payload
    assert builds["n"] == 0


@pytest.mark.asyncio
async def test_cached_or_build_serves_stale_and_enqueues(monkeypatch):
    from app.domains.group import projection_read
    from app.domains.projections.projection_cache import ProjectionEnvelope

    user_id = uuid4()
    moment_id = uuid4()
    payload = {"stale": True}
    builds = {"n": 0}
    enqueues: list[tuple] = []

    async def fake_envelope(*_a, **_k):
        return ProjectionEnvelope(version=7, updated_at="t", payload=payload, stale=True)

    async def build():
        builds["n"] += 1
        return {"built": True}

    monkeypatch.setattr(projection_read, "get_cached_envelope", fake_envelope)
    monkeypatch.setattr(
        projection_read,
        "enqueue_group_projection_refresh",
        lambda *a, **k: enqueues.append((a, k)),
    )
    monkeypatch.setattr(projection_read, "record_cache_hit", lambda: None)
    monkeypatch.setattr(projection_read, "set_cache_hit", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "set_build_coalesced", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "set_projection_version", lambda *_a, **_k: None)

    out = await projection_read.cached_or_build(
        user_id, moment_id, "pulse", build, moment_type="SHARED_EXPERIENCE"
    )

    assert out == payload
    assert builds["n"] == 0
    assert len(enqueues) == 1
    assert enqueues[0][1]["reason"] == "stale_serve"


@pytest.mark.asyncio
async def test_cached_or_build_force_refresh_still_builds(monkeypatch):
    from app.domains.group import projection_read

    user_id = uuid4()
    moment_id = uuid4()
    builds = {"n": 0}

    async def purge(*_a, **_k):
        return None

    async def build():
        builds["n"] += 1
        return {"fresh": True}

    async def get_stale(*_a, **_k):
        return None

    async def acquire(*_a, **_k):
        return True

    async def release(*_a, **_k):
        return None

    async def cache(*_a, **_k):
        return None

    monkeypatch.setattr(projection_read.projection_cache, "purge", purge)
    monkeypatch.setattr(projection_read.projection_cache, "get_stale", get_stale)
    monkeypatch.setattr(projection_read.projection_cache, "acquire_build_lock", acquire)
    monkeypatch.setattr(projection_read.projection_cache, "release_build_lock", release)
    monkeypatch.setattr(projection_read, "set_cached_slice", cache)
    monkeypatch.setattr(projection_read, "record_cache_miss", lambda: None)
    monkeypatch.setattr(projection_read, "set_projection_build_ms", lambda *_a, **_k: None)
    monkeypatch.setattr(projection_read, "set_cache_hit", lambda *_a, **_k: None)

    out = await projection_read.cached_or_build(
        user_id, moment_id, "pulse", build, force_refresh=True
    )

    assert out == {"fresh": True}
    assert builds["n"] == 1
