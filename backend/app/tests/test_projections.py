"""Phase 6.9 — projection cache, invalidation, and read path tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.domains.projections import projection_cache
from app.domains.projections.projection_keys import slice_key, stale_key
from app.domains.projections.projection_metrics import (
    get_counters,
    record_cache_hit,
    record_cache_miss,
    reset_metrics_for_tests,
)


@pytest.fixture(autouse=True)
def _reset_projection_state():
    projection_cache.reset_projection_cache_for_tests()
    reset_metrics_for_tests()
    yield
    projection_cache.reset_projection_cache_for_tests()
    reset_metrics_for_tests()


@pytest.mark.asyncio
async def test_projection_cache_versioned_envelope():
    user_id = uuid4()
    payload = {"status": "ACTIVE", "pulse": {"score": 1}}

    env = await projection_cache.set(user_id, "LIFE_OPERATIONS", "pulse", payload)
    assert env.version == 1
    assert env.payload == payload

    loaded = await projection_cache.get(user_id, "LIFE_OPERATIONS", "pulse")
    assert loaded is not None
    assert loaded.version == 1
    assert loaded.payload == payload
    assert loaded.stale is False

    env2 = await projection_cache.set(user_id, "LIFE_OPERATIONS", "pulse", payload)
    assert env2.version == 2


@pytest.mark.asyncio
async def test_mark_stale_serves_last_known_until_rebuild():
    user_id = uuid4()
    payload = {"status": "ACTIVE", "pulse": {"score": 9}}
    await projection_cache.set(user_id, "FUTURE_BUILDING", "pulse", payload)

    await projection_cache.mark_stale(user_id, "FUTURE_BUILDING", "pulse")

    stale = await projection_cache.get(user_id, "FUTURE_BUILDING", "pulse")
    assert stale is not None
    assert stale.stale is True
    assert stale.payload == payload


@pytest.mark.asyncio
async def test_slice_key_personal_life():
    user_id = uuid4()
    assert slice_key(user_id, "personal", "life") == f"projection:user:{user_id}:personal:life"


@pytest.mark.asyncio
async def test_metrics_counters():
    record_cache_hit()
    record_cache_hit()
    record_cache_miss()
    counters = get_counters()
    assert counters["projection_cache_hit"] == 2
    assert counters["projection_cache_miss"] == 1


@pytest.mark.asyncio
@patch("app.domains.projections.invalidation._enqueue_slice")
async def test_invalidate_for_quick_add_expense_skips_moments(mock_enqueue):
    from app.domains.projections.invalidation import invalidate_for_quick_add

    user_id = uuid4()
    await invalidate_for_quick_add(user_id, "LIFE_OPERATIONS", "EXPENSE")

    enqueued_slices = {call.args[2] for call in mock_enqueue.call_args_list}
    assert "pulse" in enqueued_slices
    assert "memory" in enqueued_slices
    assert "life" in enqueued_slices
    assert "moments" not in enqueued_slices


@pytest.mark.asyncio
@patch("app.domains.projections.invalidation._enqueue_slice")
async def test_invalidate_for_delete_enqueues_refresh_all(mock_enqueue):
    from app.domains.projections.invalidation import invalidate_for_delete

    user_id = uuid4()
    await projection_cache.set(user_id, "LIFE_OPERATIONS", "pulse", {"pulse": {}})
    await invalidate_for_delete(user_id)

    stale = await projection_cache.get(user_id, "LIFE_OPERATIONS", "pulse")
    assert stale is not None
    assert stale.stale is True


@pytest.mark.asyncio
async def test_exists_and_ttl():
    user_id = uuid4()
    assert await projection_cache.exists(user_id, "LIFE_OPERATIONS", "pulse") is False
    await projection_cache.set(user_id, "LIFE_OPERATIONS", "pulse", {"ok": True})
    assert await projection_cache.exists(user_id, "LIFE_OPERATIONS", "pulse") is True
    ttl = await projection_cache.ttl(user_id, "LIFE_OPERATIONS", "pulse")
    assert ttl is not None
    assert ttl > 0


@pytest.mark.asyncio
async def test_build_lock_keys():
    user_id = uuid4()
    acquired = await projection_cache.acquire_build_lock(user_id, "LIFE_OPERATIONS", "pulse")
    assert acquired is True
    acquired_again = await projection_cache.acquire_build_lock(user_id, "LIFE_OPERATIONS", "pulse")
    assert acquired_again is False
    await projection_cache.release_build_lock(user_id, "LIFE_OPERATIONS", "pulse")
