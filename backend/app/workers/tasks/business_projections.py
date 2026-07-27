"""Celery tasks for Business template projection refresh."""
from __future__ import annotations

import logging
import time
from uuid import UUID

from app.domains.business.projection_cache import (
    MOMENT_SLICES,
    USER_AGG_SLICES,
    USER_AGG_TEMPLATE,
    parse_template_key,
    set_cached_slice,
    set_user_agg_slice,
)
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session

logger = logging.getLogger(__name__)


@celery_app.task(name="projections.refresh_business", bind=True, **RETRY_OPTS)
def refresh_business_projections(
    self,
    user_id: str,
    template: str,
    reason: str = "",
    slices: str = "all",
) -> dict:
    return run_async(_refresh_business(UUID(user_id), template, reason, slices))


async def _refresh_user_agg(user_id: UUID, reason: str) -> dict:
    start = time.perf_counter()
    refreshed: list[str] = []
    async with worker_session() as session:
        from app.domains.business.life.builder import build_life
        from app.domains.business.memory.builder import build_memory

        life_payload = await build_life(session, user_id)
        await set_user_agg_slice(user_id, "life", life_payload)
        refreshed.append("life")
        memory_payload = await build_memory(session, user_id)
        await set_user_agg_slice(user_id, "memory", memory_payload)
        refreshed.append("memory")
        await session.commit()
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "Refreshed business user-agg user=%s reason=%s slices=%s ms=%.1f",
        user_id, reason, refreshed, elapsed,
    )
    return {
        "user_id": str(user_id),
        "template": USER_AGG_TEMPLATE,
        "reason": reason,
        "slices": refreshed,
        "elapsed_ms": round(elapsed, 2),
        "status": "refreshed",
    }


async def _refresh_business(
    user_id: UUID, template: str, reason: str, slices: str = "all"
) -> dict:
    if template == USER_AGG_TEMPLATE or slices == "user_agg":
        return await _refresh_user_agg(user_id, reason)

    start = time.perf_counter()
    moment_type, moment_id = parse_template_key(template)
    refreshed: list[str] = []
    do_moments = slices in ("all", "moments")
    do_user_agg = slices in ("all",)

    async with worker_session() as session:
        from app.domains.business.life.builder import build_life
        from app.domains.business.memory.builder import build_memory
        from app.domains.business.templates.registry import builders_for

        if do_moments:
            builders = builders_for(moment_type, session)
            if builders is None:
                logger.warning("Unknown business moment type %s", moment_type)
                return {"status": "skipped", "template": template}
            ctx = await builders["build"](user_id, moment_id)
            for slice_type in MOMENT_SLICES:
                mapper = builders["mappers"].get(slice_type)
                if mapper is None:
                    continue
                payload = mapper(ctx)
                await set_cached_slice(
                    user_id, moment_id, slice_type, payload, moment_type=moment_type
                )
                refreshed.append(slice_type)

        if do_user_agg:
            life_payload = await build_life(session, user_id)
            await set_user_agg_slice(user_id, "life", life_payload)
            refreshed.append("life")
            memory_payload = await build_memory(session, user_id)
            await set_user_agg_slice(user_id, "memory", memory_payload)
            refreshed.append("memory")

        await session.commit()
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "Refreshed business projections user=%s template=%s reason=%s slices=%s ms=%.1f",
        user_id, template, reason, refreshed, elapsed,
    )
    return {
        "user_id": str(user_id),
        "template": template,
        "reason": reason,
        "slices": refreshed,
        "user_agg_slices": list(USER_AGG_SLICES) if do_user_agg else [],
        "elapsed_ms": round(elapsed, 2),
        "status": "refreshed",
    }
