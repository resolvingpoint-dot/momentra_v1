"""Cache-first Group projection reads with single-flight protection."""
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
from app.domains.group.projection_cache import (
    get_cached_envelope,
    set_cached_slice,
    template_key,
)
from app.domains.projections import projection_cache
from app.domains.projections.projection_metrics import record_cache_hit, record_cache_miss

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 0.05
_POLL_TIMEOUT = 2.0

BuildFn = Callable[[], Awaitable[dict[str, Any]]]


async def cached_or_build(
    user_id: UUID,
    moment_id: UUID,
    slice_type: str,
    build_fn: BuildFn,
    *,
    moment_type: str = "SHARED_EXPERIENCE",
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Redis-first read with stale serve + single-flight rebuild.

    ``force_refresh`` purges active+stale and sync-rebuilds (post-mutation path).
    """
    template = template_key(moment_type, moment_id)
    t0 = time.perf_counter()

    if force_refresh:
        await projection_cache.purge(user_id, template, slice_type)
        record_cache_miss()
        return await _get_or_build(
            user_id,
            moment_id,
            slice_type,
            build_fn,
            moment_type=moment_type,
            template=template,
        )

    envelope = await get_cached_envelope(
        user_id, moment_id, slice_type, moment_type=moment_type
    )
    if envelope is not None and not envelope.stale:
        record_cache_hit()
        set_cache_hit(True)
        set_projection_version(envelope.version)
        logger.debug(
            "GroupLoad template=%s moment=%s tab=%s source=cache durationMs=%.1f cacheHit=true",
            moment_type,
            moment_id,
            slice_type,
            (time.perf_counter() - t0) * 1000,
        )
        return envelope.payload

    if envelope is not None and envelope.stale:
        # Serve stale immediately; rebuild in background so Pulse GETs stay fast.
        record_cache_hit()
        set_cache_hit(True)
        set_projection_version(envelope.version)
        logger.debug(
            "GroupLoad template=%s moment=%s tab=%s source=stale-serve durationMs=%.1f",
            moment_type,
            moment_id,
            slice_type,
            (time.perf_counter() - t0) * 1000,
        )

        async def _bg_rebuild() -> None:
            try:
                await _get_or_build(
                    user_id,
                    moment_id,
                    slice_type,
                    build_fn,
                    moment_type=moment_type,
                    template=template,
                )
            except Exception:  # noqa: BLE001
                logger.debug(
                    "GroupLoad background rebuild failed template=%s moment=%s tab=%s",
                    moment_type,
                    moment_id,
                    slice_type,
                    exc_info=True,
                )

        try:
            asyncio.get_running_loop().create_task(_bg_rebuild())
        except RuntimeError:
            pass
        return envelope.payload

    record_cache_miss()
    return await _get_or_build(
        user_id, moment_id, slice_type, build_fn, moment_type=moment_type, template=template
    )


async def _get_or_build(
    user_id: UUID,
    moment_id: UUID,
    slice_type: str,
    build_fn: BuildFn,
    *,
    moment_type: str,
    template: str,
) -> dict[str, Any]:
    stale = await projection_cache.get_stale(user_id, template, slice_type)
    acquired = await projection_cache.acquire_build_lock(user_id, template, slice_type)
    if not acquired:
        if stale is not None:
            set_build_coalesced(True)
            set_cache_hit(True)
            set_projection_version(stale.version)
            logger.debug(
                "GroupLoad template=%s moment=%s tab=%s source=stale duplicateSuppressed=true",
                moment_type,
                moment_id,
                slice_type,
            )
            return stale.payload
        waited = await _wait_for_slice(user_id, template, slice_type)
        if waited is not None:
            set_build_coalesced(True)
            set_cache_hit(True)
            set_projection_version(waited.version)
            return waited.payload
        acquired = await projection_cache.acquire_build_lock(user_id, template, slice_type)

    try:
        if acquired:
            start = time.perf_counter()
            payload = await build_fn()
            await set_cached_slice(
                user_id, moment_id, slice_type, payload, moment_type=moment_type
            )
            build_ms = (time.perf_counter() - start) * 1000
            set_projection_build_ms(build_ms)
            set_cache_hit(False)
            logger.debug(
                "GroupLoad template=%s moment=%s tab=%s source=network durationMs=%.1f cacheHit=false",
                moment_type,
                moment_id,
                slice_type,
                build_ms,
            )
            return payload
        if stale is not None:
            set_build_coalesced(True)
            set_cache_hit(True)
            set_projection_version(stale.version)
            return stale.payload
        payload = await build_fn()
        await set_cached_slice(
            user_id, moment_id, slice_type, payload, moment_type=moment_type
        )
        set_cache_hit(False)
        return payload
    finally:
        if acquired:
            await projection_cache.release_build_lock(user_id, template, slice_type)


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
