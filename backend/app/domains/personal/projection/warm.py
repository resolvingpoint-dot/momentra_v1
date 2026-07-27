"""Warm projection slice caches after snapshot refresh."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moment_engine.handlers.base import enqueue_celery
from app.domains.moments.repository import MomentRepository
from app.domains.personal.catalog import PERSONAL_CONTEXT, normalize_moment_type_code
from app.workers.tasks.projections import refresh_all_projections

logger = logging.getLogger(__name__)

_ACTIVE = {"ACTIVE"}
_MY_MONEY = {"LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS"}


async def warm_projection_cache(session: AsyncSession, user_id: UUID) -> None:
    """Enqueue background projection refresh after Celery snapshot refresh."""
    try:
        repo = MomentRepository(session)
        moments = await repo.list_by_context(user_id, PERSONAL_CONTEXT)
        for moment in moments:
            if moment.status in _ACTIVE:
                code = normalize_moment_type_code(moment.moment_type or "")
                if code in _MY_MONEY:
                    pass
    except Exception:
        logger.warning("Failed to list moments for projection warm user=%s", user_id)
    enqueue_celery(refresh_all_projections, str(user_id), "snapshots.refresh")
