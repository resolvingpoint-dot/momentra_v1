"""Shared business moment access: owner OR active/configured member.

Session inventory and app-service lifecycle paths historically used
``MomentRepository.get_by_user_and_id`` (owner-only). Invitees bound via
``business_moment_members`` were blocked from home inventory and some gates.
This module is the single gate those services should call.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessMomentMembers
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository

_ALLOWED_MEMBER_STATUS = frozenset({"active", "configured"})


async def require_business_moment_access(
    session: AsyncSession, user_id: UUID, moment_id: UUID
) -> MomentModel:
    """Return the moment when the caller is the owner or an active/configured member.

    Missing or unauthorized moments both surface as 404 to avoid IDOR probes.
    """
    moment = await MomentRepository(session).get_by_id(moment_id)
    if moment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
        )

    if moment.user_id == user_id:
        return moment

    result = await session.execute(
        select(BusinessMomentMembers).where(
            BusinessMomentMembers.moment_id == moment_id,
            BusinessMomentMembers.user_id == user_id,
        )
    )
    row = result.scalar_one_or_none()
    if row is not None:
        status_val = (row.member_status or "").lower()
        if status_val in _ALLOWED_MEMBER_STATUS:
            return moment

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
    )
