"""Business projection cache helpers: stale-while-revalidate + Celery enqueue.

Moment-scoped slices: pulse, moments, quick_add (template = {MOMENT_TYPE}_{moment_id})
User-scoped aggregates: life, memory (template = BUSINESS_USER)
"""
from __future__ import annotations

import logging
from uuid import UUID

from app.domains.moment_engine.handlers.base import enqueue_celery
from app.domains.projections import projection_cache

logger = logging.getLogger(__name__)

MOMENT_SLICES = ("pulse", "moments", "quick_add")
USER_AGG_SLICES = ("life", "memory")
# Kept for callers that still iterate a combined list
SLICES = MOMENT_SLICES + USER_AGG_SLICES

USER_AGG_TEMPLATE = "BUSINESS_USER"


def template_key(moment_type: str, moment_id: UUID) -> str:
    mt = (moment_type or "TEAM_OPERATIONS").upper()
    return f"{mt}_{moment_id}"


def parse_template_key(template: str) -> tuple[str, UUID]:
    if template == USER_AGG_TEMPLATE:
        raise ValueError("USER_AGG_TEMPLATE has no moment_id")
    if len(template) < 40:
        raise ValueError(f"Invalid business template key: {template}")
    moment_id = UUID(template[-36:])
    moment_type = template[: -(36 + 1)]
    return moment_type, moment_id


async def get_cached_slice(
    user_id: UUID,
    moment_id: UUID,
    slice_type: str,
    *,
    moment_type: str = "TEAM_OPERATIONS",
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
    moment_type: str = "TEAM_OPERATIONS",
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
    moment_type: str = "TEAM_OPERATIONS",
) -> None:
    await projection_cache.set(
        user_id, template_key(moment_type, moment_id), slice_type, payload
    )


async def get_user_agg_envelope(user_id: UUID, slice_type: str):
    env = await projection_cache.get(user_id, USER_AGG_TEMPLATE, slice_type)
    if env is not None:
        return env
    return await projection_cache.get_stale(user_id, USER_AGG_TEMPLATE, slice_type)


async def set_user_agg_slice(user_id: UUID, slice_type: str, payload: dict) -> None:
    await projection_cache.set(user_id, USER_AGG_TEMPLATE, slice_type, payload)


def enqueue_business_projection_refresh(
    user_id: UUID,
    moment_id: UUID,
    *,
    moment_type: str = "TEAM_OPERATIONS",
    reason: str = "business_activity",
    slices: str = "all",
) -> None:
    """Enqueue Celery refresh.

    ``slices``:
      - ``all`` — moment slices + life/memory
      - ``moments`` — pulse/moments/quick_add only
      - ``user_agg`` — life/memory only (moment_id ignored)
    """
    from app.workers.tasks.business_projections import refresh_business_projections

    if slices == "user_agg":
        enqueue_celery(
            refresh_business_projections,
            str(user_id),
            USER_AGG_TEMPLATE,
            reason,
            "user_agg",
        )
        return
    template = template_key(moment_type, moment_id)
    enqueue_celery(
        refresh_business_projections, str(user_id), template, reason, slices
    )


def enqueue_business_user_agg_refresh(
    user_id: UUID, *, reason: str = "activate_warmup"
) -> None:
    enqueue_business_projection_refresh(
        user_id,
        UUID(int=0),
        moment_type=USER_AGG_TEMPLATE,
        reason=reason,
        slices="user_agg",
    )


# Mutation → projection slices (avoid invalidate-everything).
# notes-only / lightweight edits: activity only via quick_add warm; pulse when money/ops KPIs change.
_ACTION_SLICE_MATRIX: dict[str, tuple[str, ...]] = {
    "SPEND_ENTRY": ("pulse", "moments", "quick_add"),
    "VENDOR_UPDATE": ("pulse", "moments", "quick_add"),
    "APPROVAL_REQUEST": ("pulse", "moments", "quick_add"),
    "ISSUE_RISK": ("pulse", "moments", "quick_add"),
    "OPERATIONAL_IMPROVEMENT": ("pulse", "moments", "quick_add"),
    "TEAM_UPDATE": ("pulse", "moments", "quick_add"),
    "RECOGNITION": ("pulse", "moments", "quick_add"),
    "GENERAL_UPDATE": ("moments", "quick_add"),
    "NOTE": ("moments", "quick_add"),
}


async def invalidate_business_projections(
    user_id: UUID,
    moment_id: UUID,
    *,
    moment_type: str = "TEAM_OPERATIONS",
    reason: str = "business_activity",
    slices: tuple[str, ...] | None = None,
) -> None:
    template = template_key(moment_type, moment_id)
    moment_slices = slices or MOMENT_SLICES
    for slice_type in moment_slices:
        if slice_type in MOMENT_SLICES:
            await projection_cache.mark_stale(user_id, template, slice_type)
    # User-agg only when pulse is affected (money / recognition surfaces).
    touch_user_agg = slices is None or "pulse" in moment_slices
    if touch_user_agg:
        for slice_type in USER_AGG_SLICES:
            await projection_cache.mark_stale(user_id, USER_AGG_TEMPLATE, slice_type)
    # Celery accepts all | moments | user_agg
    enqueue_mode = "all" if (slices is None or touch_user_agg) else "moments"
    enqueue_business_projection_refresh(
        user_id,
        moment_id,
        moment_type=moment_type,
        reason=reason,
        slices=enqueue_mode,
    )
    logger.debug(
        "BusinessLoad invalidate user=%s template=%s reason=%s slices=%s enqueue=%s",
        user_id,
        template,
        reason,
        moment_slices,
        enqueue_mode,
    )


async def invalidate_business_projections_for_action(
    user_id: UUID,
    moment_id: UUID,
    *,
    action_type: str,
    moment_type: str = "TEAM_OPERATIONS",
    reason: str = "business_activity",
) -> None:
    key = (action_type or "").upper()
    slices = _ACTION_SLICE_MATRIX.get(key, MOMENT_SLICES)
    await invalidate_business_projections(
        user_id,
        moment_id,
        moment_type=moment_type,
        reason=reason,
        slices=slices,
    )


async def invalidate_for_moment(
    user_id: UUID,
    moment_id: UUID,
    moment_type: str | None,
    *,
    reason: str = "manual",
) -> None:
    await invalidate_business_projections(
        user_id,
        moment_id,
        moment_type=moment_type or "TEAM_OPERATIONS",
        reason=reason,
    )
