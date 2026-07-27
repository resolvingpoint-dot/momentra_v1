"""Build business projection context via the template registry."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessMoments
from app.domains.business.templates.registry import builders_for


async def build_projection_context(
    session: AsyncSession, user_id: UUID, moment_id: UUID
):
    """Resolve moment_type then delegate to the appropriate template builder."""
    result = await session.execute(
        select(BusinessMoments).where(BusinessMoments.moment_id == moment_id)
    )
    moment = result.scalar_one_or_none()
    if moment is None:
        return None
    moment_type = (moment.moment_type or "TEAM_OPERATIONS").upper()
    builders = builders_for(moment_type, session)
    if builders is None:
        return None
    return await builders["build"](user_id, moment_id)
