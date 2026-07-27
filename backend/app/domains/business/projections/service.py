"""Business projection build service — used by the Celery task."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.projection_cache import set_cached_slice
from app.domains.business.templates.registry import builders_for

logger = logging.getLogger(__name__)


async def refresh_all_slices(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    moment_type: str,
) -> list[str]:
    builders = builders_for(moment_type, session)
    if builders is None:
        logger.warning("No builder for business moment type %s", moment_type)
        return []
    ctx = await builders["build"](user_id, moment_id)
    refreshed: list[str] = []
    for slice_type, mapper in builders["mappers"].items():
        payload = mapper(ctx)
        await set_cached_slice(
            user_id, moment_id, slice_type, payload, moment_type=moment_type
        )
        refreshed.append(slice_type)
    return refreshed
