"""Celery tasks for Group template projection refresh."""
from __future__ import annotations

import logging
import time
from uuid import UUID

from app.domains.group.projection_cache import SLICES, parse_template_key, set_cached_slice
from app.workers.base import RETRY_OPTS
from app.workers.celery_app import celery_app
from app.workers.db import run_async, worker_session

logger = logging.getLogger(__name__)


@celery_app.task(name="projections.refresh_group", bind=True, **RETRY_OPTS)
def refresh_group_projections(self, user_id: str, template: str, reason: str = "") -> dict:
    return run_async(_refresh_group(UUID(user_id), template, reason))


async def _refresh_group(user_id: UUID, template: str, reason: str) -> dict:
    start = time.perf_counter()
    moment_type, moment_id = parse_template_key(template)
    refreshed: list[str] = []
    async with worker_session() as session:
        builders = _builders_for(moment_type, session)
        if builders is None:
            logger.warning("Unknown group moment type %s", moment_type)
            return {"status": "skipped", "template": template}
        ctx = await builders["build"](user_id, moment_id)
        for slice_type, mapper in builders["mappers"].items():
            payload = mapper(ctx)
            await set_cached_slice(
                user_id, moment_id, slice_type, payload, moment_type=moment_type
            )
            refreshed.append(slice_type)
        await session.commit()
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "Refreshed group projections user=%s template=%s reason=%s slices=%s ms=%.1f",
        user_id,
        template,
        reason,
        refreshed,
        elapsed,
    )
    return {
        "user_id": str(user_id),
        "template": template,
        "reason": reason,
        "slices": refreshed,
        "elapsed_ms": round(elapsed, 2),
        "status": "refreshed",
    }


def _builders_for(moment_type: str, session):
    mt = moment_type.upper()
    if mt == "SHARED_EXPERIENCE":
        from app.domains.group.templates.shared_experience.life_mapper import build_life
        from app.domains.group.templates.shared_experience.live_hub_mapper import build_live_hub
        from app.domains.group.templates.shared_experience.memory_mapper import build_memory_projection
        from app.domains.group.templates.shared_experience.moments_mapper import build_moments
        from app.domains.group.templates.shared_experience.projection_builder import (
            SharedExperienceProjectionBuilder,
        )
        from app.domains.group.templates.shared_experience.pulse_mapper import build_pulse

        builder = SharedExperienceProjectionBuilder(session)
        return {
            "build": builder.build,
            "mappers": {
                "pulse": build_pulse,
                "moments": build_moments,
                "memory": build_memory_projection,
                "life": build_life,
                "live_hub": build_live_hub,
            },
        }
    if mt == "SHARED_PURCHASE":
        from app.domains.group.templates.shared_purchase.life_mapper import build_life
        from app.domains.group.templates.shared_purchase.live_hub_mapper import build_live_hub
        from app.domains.group.templates.shared_purchase.memory_mapper import build_memory_projection
        from app.domains.group.templates.shared_purchase.moments_mapper import build_moments
        from app.domains.group.templates.shared_purchase.projection_builder import (
            SharedPurchaseProjectionBuilder,
        )
        from app.domains.group.templates.shared_purchase.pulse_mapper import build_pulse

        builder = SharedPurchaseProjectionBuilder(session)
        return {
            "build": builder.build,
            "mappers": {
                "pulse": build_pulse,
                "moments": build_moments,
                "memory": build_memory_projection,
                "life": build_life,
                "live_hub": build_live_hub,
            },
        }
    if mt == "SHARED_LIVING":
        from app.domains.group.templates.shared_living.life_mapper import build_life
        from app.domains.group.templates.shared_living.live_hub_mapper import build_live_hub
        from app.domains.group.templates.shared_living.memory_mapper import build_memory_projection
        from app.domains.group.templates.shared_living.moments_mapper import build_moments
        from app.domains.group.templates.shared_living.projection_builder import (
            SharedLivingProjectionBuilder,
        )
        from app.domains.group.templates.shared_living.pulse_mapper import build_pulse

        builder = SharedLivingProjectionBuilder(session)
        return {
            "build": builder.build,
            "mappers": {
                "pulse": build_pulse,
                "moments": build_moments,
                "memory": build_memory_projection,
                "life": build_life,
                "live_hub": build_live_hub,
            },
        }
    return None
