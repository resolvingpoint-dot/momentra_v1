"""Shared Personal inventory load + module-state sync (one list_by_context per call)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.module_states.service import ModuleStateService
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository
from app.domains.personal.catalog import PERSONAL_CONTEXT, normalize_moment_type_code

_ACTIVE_STATUSES = {"ACTIVE"}
_VISIBLE_STATUSES = {"DRAFT", "ACTIVE", "PAUSED", "COMPLETED", "SETUP"}
_LINK_STATUS_PRIORITY = {
    "ACTIVE": 0,
    "PAUSED": 1,
    "COMPLETED": 2,
    "SETUP": 3,
    "DRAFT": 4,
}


def latest_by_code(moments: list[MomentModel]) -> dict[str, MomentModel]:
    """Pick the best linked moment per type (ACTIVE beats newer DRAFT duplicates)."""
    best: dict[str, MomentModel] = {}
    for m in moments:
        code = normalize_moment_type_code(m.moment_type or "")
        if not code:
            continue
        existing = best.get(code)
        if existing is None:
            best[code] = m
            continue
        m_rank = _LINK_STATUS_PRIORITY.get(m.status or "", 99)
        e_rank = _LINK_STATUS_PRIORITY.get(existing.status or "", 99)
        if m_rank < e_rank:
            best[code] = m
        elif m_rank == e_rank:
            m_at = m.updated_at or m.created_at
            e_at = existing.updated_at or existing.created_at
            if m_at and e_at and m_at > e_at:
                best[code] = m
    return best


async def load_moment_inventories(
    session: AsyncSession, user_id: UUID
) -> tuple[list[MomentModel], list[MomentModel], list[MomentModel], dict[str, MomentModel]]:
    """One list_by_context — return all, visible, active, latest_by_code."""
    all_moments = await MomentRepository(session).list_by_context(user_id, PERSONAL_CONTEXT)
    visible = [m for m in all_moments if m.status in _VISIBLE_STATUSES]
    active = [m for m in visible if m.status in _ACTIVE_STATUSES]
    return all_moments, visible, active, latest_by_code(visible)


async def sync_module_states(
    session: AsyncSession,
    user_id: UUID,
    *,
    visible_moments: list[MomentModel] | None = None,
    invalidate_projection: bool = False,
) -> str:
    """Flip MY_MONEY/PULSE/MOMENTS(+MEMORY when active) from inventory.

    Returns the resulting module state: ACTIVE | SETUP | EMPTY.
    When ``visible_moments`` is provided, skips an extra list_by_context.
    """
    modules = ModuleStateService(session)
    bootstrap = AppBootstrapService(session)
    if visible_moments is None:
        _, visible_moments, active, _ = await load_moment_inventories(session, user_id)
    else:
        active = [m for m in visible_moments if m.status in _ACTIVE_STATUSES]
    drafts = [m for m in visible_moments if m.status == "DRAFT"]
    if active:
        await modules.set_state(user_id, "MY_MONEY", "ACTIVE", "personal_moment")
        await modules.set_state(user_id, "PULSE", "ACTIVE", "personal_moment")
        await modules.set_state(user_id, "MOMENTS", "ACTIVE", "personal_moment")
        await modules.set_state(user_id, "MEMORY", "ACTIVE", "personal_moment")
        await bootstrap.invalidate_cache(user_id)
        if invalidate_projection:
            from app.domains.personal.projection.cache import invalidate_projection_cache

            invalidate_projection_cache(user_id)
        return "ACTIVE"
    if drafts:
        await modules.set_state(user_id, "MY_MONEY", "SETUP", "personal_moment")
        await modules.set_state(user_id, "PULSE", "SETUP", "personal_moment")
        await modules.set_state(user_id, "MOMENTS", "SETUP", "personal_moment")
        module_state = "SETUP"
    else:
        await modules.set_state(user_id, "MY_MONEY", "EMPTY", "personal_moment")
        await modules.set_state(user_id, "PULSE", "EMPTY", "personal_moment")
        await modules.set_state(user_id, "MOMENTS", "EMPTY", "personal_moment")
        module_state = "EMPTY"
    await bootstrap.invalidate_cache(user_id)
    if invalidate_projection:
        from app.domains.personal.projection.cache import invalidate_projection_cache

        invalidate_projection_cache(user_id)
    return module_state
