"""Cache-first Business projection reads with single-flight protection.

Moment slices (pulse/moments/quick_add) use a frozen ``_bundle`` lock owned by
``BusinessActiveService._build_slice`` — this module does NOT take a per-slice
lock or write Redis again (avoids nested locks + double write).

Life/Memory use a separate user-agg lock under ``BUSINESS_USER``.
"""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from app.core.request_context import (
    set_build_coalesced,
    set_cache_hit,
    set_projection_build_ms,
    set_projection_version,
)
from app.domains.business.projection_cache import (
    USER_AGG_TEMPLATE,
    enqueue_business_projection_refresh,
    get_cached_envelope,
    get_user_agg_envelope,
    set_user_agg_slice,
    template_key,
)
from app.domains.projections import projection_cache
from app.domains.projections.projection_metrics import record_cache_hit, record_cache_miss

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 0.05
_POLL_TIMEOUT = 2.0

BuildFn = Callable[[], Awaitable[dict[str, Any]]]


def _log_projection_read(
    *,
    moment_id: UUID | None,
    moment_type: str,
    slice_type: str,
    cache_source: str,
    lock_role: str,
    redis_read_ms: float,
    context_ms: float = 0.0,
    map_ms: float = 0.0,
    redis_write_ms: float = 0.0,
    total_ms: float,
) -> None:
    logger.info(
        "BusinessProjectionRead momentId=%s momentType=%s slice=%s "
        "cacheSource=%s lockRole=%s redisReadMs=%.1f contextMs=%.1f "
        "mapMs=%.1f redisWriteMs=%.1f totalMs=%.1f",
        moment_id,
        moment_type,
        slice_type,
        cache_source,
        lock_role,
        redis_read_ms,
        context_ms,
        map_ms,
        redis_write_ms,
        total_ms,
    )


async def cached_or_build(
    user_id: UUID,
    moment_id: UUID,
    slice_type: str,
    build_fn: BuildFn,
    *,
    moment_type: str = "TEAM_OPERATIONS",
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Redis-first moment slice read. Miss → build_fn (owns bundle lock + Redis writes).

    ``force_refresh`` purges active+stale and sync-rebuilds (post-mutation path).
    """
    t0 = time.perf_counter()
    template = template_key(moment_type, moment_id)

    if force_refresh:
        await projection_cache.purge(user_id, template, slice_type)
        record_cache_miss()
        start = time.perf_counter()
        payload = await build_fn()
        build_ms = (time.perf_counter() - start) * 1000
        set_projection_build_ms(build_ms)
        set_cache_hit(False)
        _log_projection_read(
            moment_id=moment_id,
            moment_type=moment_type,
            slice_type=slice_type,
            cache_source="force_refresh",
            lock_role="builder",
            redis_read_ms=0.0,
            context_ms=build_ms,
            total_ms=(time.perf_counter() - t0) * 1000,
        )
        return payload

    envelope = await get_cached_envelope(
        user_id, moment_id, slice_type, moment_type=moment_type
    )
    redis_read_ms = (time.perf_counter() - t0) * 1000

    if envelope is not None and not envelope.stale:
        record_cache_hit()
        set_cache_hit(True)
        set_projection_version(envelope.version)
        _log_projection_read(
            moment_id=moment_id,
            moment_type=moment_type,
            slice_type=slice_type,
            cache_source="fresh",
            lock_role="none",
            redis_read_ms=redis_read_ms,
            total_ms=(time.perf_counter() - t0) * 1000,
        )
        return envelope.payload

    if envelope is not None and envelope.stale:
        record_cache_hit()
        set_cache_hit(True)
        set_build_coalesced(True)
        set_projection_version(envelope.version)
        # Return immediately; queue at most one background refresh.
        try:
            enqueue_business_projection_refresh(
                user_id,
                moment_id,
                moment_type=moment_type,
                reason="stale_swr",
                slices="moments",
            )
        except Exception:  # noqa: BLE001
            logger.debug("Failed to enqueue stale SWR refresh", exc_info=True)
        _log_projection_read(
            moment_id=moment_id,
            moment_type=moment_type,
            slice_type=slice_type,
            cache_source="stale",
            lock_role="none",
            redis_read_ms=redis_read_ms,
            total_ms=(time.perf_counter() - t0) * 1000,
        )
        return envelope.payload

    record_cache_miss()
    # Bundle single-flight + Redis writes live entirely inside build_fn.
    start = time.perf_counter()
    payload = await build_fn()
    build_ms = (time.perf_counter() - start) * 1000
    set_projection_build_ms(build_ms)
    set_cache_hit(False)
    _log_projection_read(
        moment_id=moment_id,
        moment_type=moment_type,
        slice_type=slice_type,
        cache_source="miss",
        lock_role="builder",
        redis_read_ms=redis_read_ms,
        context_ms=build_ms,
        total_ms=(time.perf_counter() - t0) * 1000,
    )
    return payload


async def cached_or_build_user_agg(
    user_id: UUID,
    slice_type: str,
    build_fn: BuildFn,
    *,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Redis-first Life/Memory aggregates (user-scoped template BUSINESS_USER).

    ``force_refresh`` purges active+stale and sync-rebuilds under the user-agg lock.
    """
    t0 = time.perf_counter()

    if force_refresh:
        await projection_cache.purge(user_id, USER_AGG_TEMPLATE, slice_type)

    envelope = await get_user_agg_envelope(user_id, slice_type)
    redis_read_ms = (time.perf_counter() - t0) * 1000

    if not force_refresh and envelope is not None and not envelope.stale:
        record_cache_hit()
        set_cache_hit(True)
        set_projection_version(envelope.version)
        _log_projection_read(
            moment_id=None,
            moment_type=USER_AGG_TEMPLATE,
            slice_type=slice_type,
            cache_source="fresh",
            lock_role="none",
            redis_read_ms=redis_read_ms,
            total_ms=(time.perf_counter() - t0) * 1000,
        )
        return envelope.payload

    if not force_refresh and envelope is not None and envelope.stale:
        record_cache_hit()
        set_cache_hit(True)
        set_build_coalesced(True)
        set_projection_version(envelope.version)
        try:
            from app.domains.business.projection_cache import (
                enqueue_business_user_agg_refresh,
            )

            enqueue_business_user_agg_refresh(user_id, reason="stale_swr_user_agg")
        except Exception:  # noqa: BLE001
            logger.debug("Failed to enqueue user-agg stale refresh", exc_info=True)
        _log_projection_read(
            moment_id=None,
            moment_type=USER_AGG_TEMPLATE,
            slice_type=slice_type,
            cache_source="stale",
            lock_role="none",
            redis_read_ms=redis_read_ms,
            total_ms=(time.perf_counter() - t0) * 1000,
        )
        return envelope.payload

    record_cache_miss()
    acquired = await projection_cache.acquire_build_lock(
        user_id, USER_AGG_TEMPLATE, slice_type
    )
    lock_role = "builder" if acquired else "waiter"
    try:
        if not acquired:
            waited = await _wait_for_slice(user_id, USER_AGG_TEMPLATE, slice_type)
            if waited is not None:
                set_build_coalesced(True)
                set_cache_hit(True)
                set_projection_version(waited.version)
                _log_projection_read(
                    moment_id=None,
                    moment_type=USER_AGG_TEMPLATE,
                    slice_type=slice_type,
                    cache_source="fresh",
                    lock_role="waiter",
                    redis_read_ms=redis_read_ms,
                    total_ms=(time.perf_counter() - t0) * 1000,
                )
                return waited.payload
            acquired = await projection_cache.acquire_build_lock(
                user_id, USER_AGG_TEMPLATE, slice_type
            )
            lock_role = "builder" if acquired else "none"

        start = time.perf_counter()
        payload = await build_fn()
        write_start = time.perf_counter()
        await set_user_agg_slice(user_id, slice_type, payload)
        redis_write_ms = (time.perf_counter() - write_start) * 1000
        set_projection_build_ms((time.perf_counter() - start) * 1000)
        set_cache_hit(False)
        _log_projection_read(
            moment_id=None,
            moment_type=USER_AGG_TEMPLATE,
            slice_type=slice_type,
            cache_source="miss",
            lock_role=lock_role,
            redis_read_ms=redis_read_ms,
            context_ms=(write_start - start) * 1000,
            redis_write_ms=redis_write_ms,
            total_ms=(time.perf_counter() - t0) * 1000,
        )
        return payload
    finally:
        if acquired:
            await projection_cache.release_build_lock(
                user_id, USER_AGG_TEMPLATE, slice_type
            )


async def _wait_for_slice(
    user_id: UUID, template: str, slice_type: str
) -> projection_cache.ProjectionEnvelope | None:
    deadline = time.monotonic() + _POLL_TIMEOUT
    while time.monotonic() < deadline:
        envelope = await projection_cache.get(user_id, template, slice_type)
        if envelope is not None:
            return envelope
        await asyncio.sleep(_POLL_INTERVAL)
    return await projection_cache.get_stale(user_id, template, slice_type)
