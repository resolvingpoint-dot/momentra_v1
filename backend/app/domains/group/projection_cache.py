"""Group projection cache helpers: stale-while-revalidate + Celery enqueue."""
from __future__ import annotations

import logging
from uuid import UUID

from app.domains.moment_engine.handlers.base import enqueue_celery
from app.domains.projections import projection_cache

logger = logging.getLogger(__name__)

SLICES = ("pulse", "moments", "memory", "life", "live_hub")


def template_key(moment_type: str, moment_id: UUID) -> str:
    mt = (moment_type or "SHARED_EXPERIENCE").upper()
    return f"{mt}_{moment_id}"


def parse_template_key(template: str) -> tuple[str, UUID]:
    """Parse SHARED_EXPERIENCE_{uuid} → (moment_type, moment_id)."""
    parts = template.rsplit("_", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid group template key: {template}")
    # moment types have underscores: SHARED_EXPERIENCE
    # template is SHARED_EXPERIENCE_{uuid} — uuid is last segment only if we split wrong.
    # Better: find last underscore before uuid (36 chars with hyphens = 36)
    if len(template) < 40:
        raise ValueError(f"Invalid group template key: {template}")
    # UUID is last 36 characters
    moment_id = UUID(template[-36:])
    moment_type = template[: -(36 + 1)]  # drop _{uuid}
    return moment_type, moment_id


async def get_cached_slice(
    user_id: UUID,
    moment_id: UUID,
    slice_type: str,
    *,
    moment_type: str = "SHARED_EXPERIENCE",
) -> dict | None:
    template = template_key(moment_type, moment_id)
    env = await projection_cache.get(user_id, template, slice_type)
    if env is not None:
        return env.payload
    stale = await projection_cache.get_stale(user_id, template, slice_type)
    return stale.payload if stale else None


async def get_cached_envelope(
    user_id: UUID,
    moment_id: UUID,
    slice_type: str,
    *,
    moment_type: str = "SHARED_EXPERIENCE",
):
    template = template_key(moment_type, moment_id)
    env = await projection_cache.get(user_id, template, slice_type)
    if env is not None:
        return env
    return await projection_cache.get_stale(user_id, template, slice_type)


async def set_cached_slice(
    user_id: UUID,
    moment_id: UUID,
    slice_type: str,
    payload: dict,
    *,
    moment_type: str = "SHARED_EXPERIENCE",
) -> None:
    await projection_cache.set(
        user_id, template_key(moment_type, moment_id), slice_type, payload
    )


def enqueue_group_projection_refresh(
    user_id: UUID,
    moment_id: UUID,
    *,
    moment_type: str = "SHARED_EXPERIENCE",
    reason: str = "group_activity",
) -> None:
    from app.workers.tasks.group_projections import refresh_group_projections

    template = template_key(moment_type, moment_id)
    enqueue_celery(refresh_group_projections, str(user_id), template, reason)


async def invalidate_group_projections(
    user_id: UUID,
    moment_id: UUID,
    *,
    moment_type: str = "SHARED_EXPERIENCE",
    reason: str = "group_activity",
) -> None:
    """Mark slices stale and enqueue background rebuild — never hard-delete only."""
    template = template_key(moment_type, moment_id)
    for slice_type in SLICES:
        await projection_cache.mark_stale(user_id, template, slice_type)
    enqueue_group_projection_refresh(
        user_id, moment_id, moment_type=moment_type, reason=reason
    )
    try:
        from app.domains.group.group_moment_events import publish_group_moment_invalidate

        await publish_group_moment_invalidate(moment_id, reason=reason, slices=SLICES)
    except Exception:
        logger.warning(
            "Group moment invalidate publish failed moment=%s reason=%s",
            moment_id,
            reason,
            exc_info=True,
        )
    logger.debug(
        "GroupLoad invalidate user=%s template=%s reason=%s",
        user_id,
        template,
        reason,
    )


async def invalidate_for_moment(
    user_id: UUID,
    moment_id: UUID,
    moment_type: str | None,
    *,
    reason: str = "manual",
) -> None:
    await invalidate_group_projections(
        user_id,
        moment_id,
        moment_type=moment_type or "SHARED_EXPERIENCE",
        reason=reason,
    )
