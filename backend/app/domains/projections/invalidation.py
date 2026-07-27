"""Projection cache invalidation matrix and Celery enqueue helpers."""
from __future__ import annotations

import logging
from uuid import UUID

from app.domains.moment_engine.handlers.base import enqueue_celery
from app.domains.personal.catalog import MOMENT_TYPES, normalize_moment_type_code
from app.domains.personal.projection.cache import invalidate_projection_cache
from app.domains.projections import projection_cache
from app.domains.projections.projection_keys import PERSONAL_LIFE_TEMPLATE

logger = logging.getLogger(__name__)

SLICE_PULSE = "pulse"
SLICE_MOMENTS = "moments"
SLICE_MEMORY = "memory"
SLICE_LIFE = "life"

_EXPENSE_LIKE = frozenset({"EXPENSE", "RECOVERY", "REFLECTION", "RHYTHM"})
_GOAL_LIKE = frozenset({"COMMITMENT", "PROGRESS", "GOAL"})
_FB_ACTIVITY = frozenset({
    "CONTRIBUTION",
    "MILESTONE",
    "OPPORTUNITY",
    "PIVOT",
    "PROGRESS",
    "LEARNING",
})
_LS_ACTIVITY = frozenset({
    "LIFESTYLE_EXPENSE",
    "EXPERIENCE",
    "WELLBEING",
    "DISCOVERY",
    "EXPRESSION",
    "ADJUST",
    "CREATIVE",
    "LIFESTYLE_ADJUST",
})
_RS_ACTIVITY = frozenset({
    "CONNECTION",
    "SUPPORT",
    "SHARED_EXPERIENCE",
    "RELATIONSHIP_INVESTMENT",
    "ADJUST",
    "RELATIONSHIP_ADJUST",
})

_ALL_TEMPLATES = [mt.code for mt in MOMENT_TYPES]


def _enqueue_slice(
    user_id: UUID,
    template: str,
    slice_type: str,
    reason: str,
) -> None:
    from app.workers.tasks import projections as projection_tasks

    mapping = {
        SLICE_PULSE: projection_tasks.refresh_pulse_projection,
        SLICE_MOMENTS: projection_tasks.refresh_moments_projection,
        SLICE_MEMORY: projection_tasks.refresh_memory_projection,
        SLICE_LIFE: projection_tasks.refresh_life_projection,
    }
    task = mapping.get(slice_type)
    if task is None:
        return
    enqueue_celery(task, str(user_id), template, reason)


async def refresh_slices_async(
    user_id: UUID,
    template: str,
    slices: list[str],
    *,
    reason: str,
    mark_stale_first: bool = False,
    include_personal_life: bool = False,
) -> None:
    code = normalize_moment_type_code(template)
    for slice_type in slices:
        if mark_stale_first:
            await projection_cache.mark_stale(user_id, code, slice_type)
        else:
            await projection_cache.delete(user_id, code, slice_type)
        _enqueue_slice(user_id, code, slice_type, reason)
    if include_personal_life or SLICE_LIFE in slices:
        if mark_stale_first:
            await projection_cache.mark_stale(user_id, PERSONAL_LIFE_TEMPLATE, SLICE_LIFE)
        else:
            await projection_cache.delete(user_id, PERSONAL_LIFE_TEMPLATE, SLICE_LIFE)
        _enqueue_slice(user_id, PERSONAL_LIFE_TEMPLATE, SLICE_LIFE, reason)


async def invalidate_for_quick_add(
    user_id: UUID,
    template: str,
    event_type: str,
) -> None:
    invalidate_projection_cache(user_id)
    code = normalize_moment_type_code(template)
    upper = event_type.upper()
    if code == "FUTURE_BUILDING" and upper in _FB_ACTIVITY:
        await refresh_slices_async(
            user_id,
            code,
            [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
            reason=f"quick_add:{upper}",
            include_personal_life=True,
            mark_stale_first=False,
        )
    elif code == "LIFESTYLE" and upper in _LS_ACTIVITY:
        await refresh_slices_async(
            user_id,
            code,
            [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
            reason=f"quick_add:{upper}",
            include_personal_life=True,
            mark_stale_first=False,
        )
    elif code == "RELATIONSHIPS" and upper in _RS_ACTIVITY:
        await refresh_slices_async(
            user_id,
            code,
            [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
            reason=f"quick_add:{upper}",
            include_personal_life=True,
            mark_stale_first=False,
        )
    elif upper in _EXPENSE_LIKE:
        await refresh_slices_async(
            user_id,
            code,
            [SLICE_PULSE, SLICE_MEMORY],
            reason=f"quick_add:{upper}",
            include_personal_life=True,
            mark_stale_first=False,
        )
    elif upper in _GOAL_LIKE:
        await refresh_slices_async(
            user_id,
            code,
            [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
            reason=f"quick_add:{upper}",
            mark_stale_first=False,
        )
    else:
        await refresh_slices_async(
            user_id,
            code,
            [SLICE_PULSE, SLICE_MEMORY],
            reason=f"quick_add:{upper}",
            include_personal_life=True,
            mark_stale_first=False,
        )


async def invalidate_for_lifecycle(
    user_id: UUID,
    template: str,
    *,
    reason: str,
) -> None:
    invalidate_projection_cache(user_id)
    await refresh_slices_async(
        user_id,
        template,
        [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
        reason=reason,
        include_personal_life=True,
    )


async def invalidate_for_setup(user_id: UUID, template: str) -> None:
    invalidate_projection_cache(user_id)
    await refresh_slices_async(
        user_id,
        template,
        [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
        reason="setup.completed",
        include_personal_life=True,
    )


async def invalidate_for_delete(user_id: UUID) -> None:
    """Mark all slices stale and enqueue async rebuild — never block on rebuild."""
    invalidate_projection_cache(user_id)
    for template in _ALL_TEMPLATES:
        for slice_type in (SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY, SLICE_LIFE):
            await projection_cache.mark_stale(user_id, template, slice_type)
    await projection_cache.mark_stale(user_id, PERSONAL_LIFE_TEMPLATE, SLICE_LIFE)
    from app.workers.tasks.projections import refresh_all_projections

    enqueue_celery(refresh_all_projections, str(user_id), "moment.deleted")


async def invalidate_for_preferences(user_id: UUID) -> None:
    for template in _ALL_TEMPLATES:
        _enqueue_slice(user_id, template, SLICE_PULSE, "preferences.updated")


async def invalidate_for_master_expense(
    user_id: UUID,
    *,
    include_relationships: bool,
) -> None:
    """Refresh projections after a master expense fan-out (no bootstrap)."""
    invalidate_projection_cache(user_id)
    # EXPENSE-like + Activity timeline: pulse, moments (activity), memory, shared life
    await refresh_slices_async(
        user_id,
        "LIFE_OPERATIONS",
        [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
        reason="master_expense.created",
        include_personal_life=True,
    )
    await refresh_slices_async(
        user_id,
        "LIFESTYLE",
        [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
        reason="master_expense.created",
        include_personal_life=False,
    )
    if include_relationships:
        await refresh_slices_async(
            user_id,
            "RELATIONSHIPS",
            [SLICE_PULSE, SLICE_MOMENTS, SLICE_MEMORY],
            reason="master_expense.created",
            include_personal_life=False,
        )
