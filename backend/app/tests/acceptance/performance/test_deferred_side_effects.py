"""Failure-mode verification for deferred notify/invalidate paths."""
from __future__ import annotations

import asyncio

import pytest

from app.domains.projections.projection_metrics import get_counters, reset_metrics_for_tests
from app.domains.shared.deferred_side_effects import (
    run_deferred_side_effect,
    schedule_deferred_side_effect,
)


@pytest.fixture(autouse=True)
def _reset_metrics():
    reset_metrics_for_tests()
    yield
    reset_metrics_for_tests()


@pytest.mark.asyncio
async def test_deferred_success_increments_ok_counter():
    calls = {"n": 0}

    async def ok():
        calls["n"] += 1

    assert await run_deferred_side_effect("unit_ok", ok, retries=0) is True
    assert calls["n"] == 1
    assert get_counters()["deferred_side_effect_ok"] == 1
    assert get_counters()["deferred_side_effect_fail"] == 0


@pytest.mark.asyncio
async def test_deferred_failure_retries_then_records_fail():
    calls = {"n": 0}

    async def boom():
        calls["n"] += 1
        raise RuntimeError("celery enqueue failed")

    assert await run_deferred_side_effect("unit_fail", boom, retries=1, retry_delay_sec=0.001) is False
    assert calls["n"] == 2  # initial + 1 retry
    assert get_counters()["deferred_side_effect_fail"] >= 2
    assert get_counters()["deferred_side_effect_retry"] == 1
    assert get_counters()["deferred_side_effect_ok"] == 0


@pytest.mark.asyncio
async def test_deferred_recovers_on_retry():
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("redis unavailable")

    assert await run_deferred_side_effect("unit_retry_ok", flaky, retries=1, retry_delay_sec=0.001) is True
    assert calls["n"] == 2
    assert get_counters()["deferred_side_effect_ok"] == 1
    assert get_counters()["deferred_side_effect_retry"] == 1


@pytest.mark.asyncio
async def test_schedule_does_not_block_and_survives_failure():
    """Mutation path returns before deferred work; failures stay off the critical path."""
    done = asyncio.Event()

    async def boom():
        await asyncio.sleep(0.01)
        done.set()
        raise RuntimeError("notification failure")

    task = schedule_deferred_side_effect("unit_schedule", boom, retries=0)
    # Critical path continues immediately
    assert not done.is_set()
    await task
    assert done.is_set()
    assert get_counters()["deferred_side_effect_fail"] == 1


@pytest.mark.asyncio
async def test_worker_unavailable_and_projection_delay_do_not_raise_to_caller():
    async def worker_down():
        raise ConnectionError("worker unavailable")

    async def redis_down():
        raise TimeoutError("Redis unavailable")

    async def celery_fail():
        raise RuntimeError("Celery enqueue failure")

    async def notify_fail():
        raise RuntimeError("notification failure")

    async def projection_delayed():
        await asyncio.sleep(0.02)
        raise TimeoutError("projection refresh delayed")

    for name, fn in [
        ("worker_unavailable", worker_down),
        ("redis_unavailable", redis_down),
        ("celery_enqueue_failure", celery_fail),
        ("notification_failure", notify_fail),
        ("projection_refresh_delayed", projection_delayed),
    ]:
        ok = await run_deferred_side_effect(name, fn, retries=0, retry_delay_sec=0.001)
        assert ok is False

    assert get_counters()["deferred_side_effect_fail"] == 5
    assert get_counters()["deferred_side_effect_ok"] == 0


def test_action_slice_matrix_maps_to_celery_modes():
    """Client/backend invalidation is action-aware; worker rebuild remains mode-granular."""
    from app.domains.business.projection_cache import _ACTION_SLICE_MATRIX

    assert "pulse" in _ACTION_SLICE_MATRIX["SPEND_ENTRY"]
    assert "pulse" not in _ACTION_SLICE_MATRIX["NOTE"]
    assert "quick_add" in _ACTION_SLICE_MATRIX["NOTE"]
