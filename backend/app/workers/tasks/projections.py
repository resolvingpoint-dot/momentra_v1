"""Celery tasks for background projection slice refresh."""
from __future__ import annotations

import logging
import time
from uuid import UUID

from app.domains.personal.catalog import MOMENT_TYPES, normalize_moment_type_code
from app.domains.personal.templates.registry import get_template_projection_registry
from app.domains.projections.projection_builder import ProjectionSliceBuilder
from app.domains.projections.projection_keys import PERSONAL_LIFE_TEMPLATE
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session

logger = logging.getLogger(__name__)

_MY_MONEY_TEMPLATES = [mt.code for mt in MOMENT_TYPES]


@celery_app.task(name="projections.refresh_pulse", bind=True, **RETRY_OPTS)
def refresh_pulse_projection(self, user_id: str, template: str, reason: str = "") -> dict:
    return run_async(_refresh_slice(UUID(user_id), template, "pulse", reason))


@celery_app.task(name="projections.refresh_moments", bind=True, **RETRY_OPTS)
def refresh_moments_projection(self, user_id: str, template: str, reason: str = "") -> dict:
    return run_async(_refresh_slice(UUID(user_id), template, "moments", reason))


@celery_app.task(name="projections.refresh_memory", bind=True, **RETRY_OPTS)
def refresh_memory_projection(self, user_id: str, template: str, reason: str = "") -> dict:
    return run_async(_refresh_slice(UUID(user_id), template, "memory", reason))


@celery_app.task(name="projections.refresh_life", bind=True, **RETRY_OPTS)
def refresh_life_projection(self, user_id: str, template: str, reason: str = "") -> dict:
    return run_async(_refresh_slice(UUID(user_id), template, "life", reason))


@celery_app.task(name="projections.refresh_all", bind=True, **RETRY_OPTS)
def refresh_all_projections(self, user_id: str, reason: str = "") -> dict:
    return run_async(_refresh_all(UUID(user_id), reason))


async def _refresh_slice(
    user_id: UUID, template: str, slice_type: str, reason: str
) -> dict:
    start = time.perf_counter()
    code = normalize_moment_type_code(template)
    async with worker_session() as session:
        builder = ProjectionSliceBuilder(session)
        if slice_type == "pulse":
            await builder.build_pulse(user_id, code, reason=reason or "worker")
        elif slice_type == "moments":
            await builder.build_moments(user_id, code, reason=reason or "worker")
        elif slice_type == "memory":
            await builder.build_memory(user_id, code, reason=reason or "worker")
        elif slice_type == "life":
            if code == PERSONAL_LIFE_TEMPLATE:
                await builder.build_personal_life(
                    user_id, reason=reason or "worker", force_refresh=True
                )
            else:
                await builder.build_template_life(user_id, code, reason=reason or "worker")
        await session.commit()
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "Refreshed projection slice user=%s template=%s slice=%s reason=%s ms=%.1f",
        user_id,
        code,
        slice_type,
        reason,
        elapsed,
    )
    return {
        "user_id": str(user_id),
        "template": code,
        "slice": slice_type,
        "reason": reason,
        "status": "refreshed",
        "elapsed_ms": round(elapsed, 2),
    }


async def _refresh_all(user_id: UUID, reason: str) -> dict:
    refreshed: list[dict] = []
    registry = get_template_projection_registry()
    for template in _MY_MONEY_TEMPLATES:
        if not registry.is_registered(template):
            continue
        for slice_type in ("pulse", "moments", "memory", "life"):
            try:
                result = await _refresh_slice(user_id, template, slice_type, reason)
                refreshed.append(result)
            except Exception:
                logger.exception(
                    "Failed to refresh %s/%s for user %s", template, slice_type, user_id
                )
    try:
        refreshed.append(
            await _refresh_slice(user_id, PERSONAL_LIFE_TEMPLATE, "life", reason)
        )
    except Exception:
        logger.exception("Failed to refresh personal life for user %s", user_id)
    return {"user_id": str(user_id), "reason": reason, "refreshed": len(refreshed)}
