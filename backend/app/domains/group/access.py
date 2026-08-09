"""Shared group moment access: owner OR active member.

Trip / shared-experience / read / settlement paths historically used
``MomentRepository.get_by_user_and_id`` (owner-only). Invitees who joined via
JWT or ``group_moment_members`` were blocked. This module is the single gate
those services should call.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group.models import GroupMomentMembers
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository

_BLOCKED_MEMBER_STATUS = frozenset({"LEFT", "REMOVED", "DECLINED"})


def _parse_uuid(raw: object) -> UUID | None:
    if raw is None:
        return None
    try:
        return UUID(str(raw))
    except (TypeError, ValueError):
        return None


async def list_group_member_user_ids(
    session: AsyncSession,
    moment_id: UUID,
    *,
    moment: MomentModel | None = None,
) -> set[UUID]:
    """Active member user IDs from relational roster ∪ runtime members ∪ owner."""
    ids: set[UUID] = set()
    target = moment
    if target is None:
        target = await MomentRepository(session).get_by_id(moment_id)
    if target is not None and target.user_id is not None:
        ids.add(target.user_id)

    mem_result = await session.execute(
        select(GroupMomentMembers).where(
            GroupMomentMembers.moment_id == moment_id,
            GroupMomentMembers.left_at.is_(None),
        )
    )
    for row in mem_result.scalars().all():
        if row.user_id is None:
            continue
        status_val = (row.status or "").upper()
        if status_val in _BLOCKED_MEMBER_STATUS:
            continue
        ids.add(row.user_id)

    if target is not None:
        for member in store.list_accepted_members(target):
            uid = _parse_uuid(member.get("user_id"))
            if uid is not None:
                ids.add(uid)

    return ids


async def is_active_group_member(
    session: AsyncSession, user_id: UUID, moment_id: UUID, moment: MomentModel | None = None
) -> bool:
    """True when the caller has active roster or runtime membership (not owner)."""
    result = await session.execute(
        select(GroupMomentMembers).where(
            GroupMomentMembers.moment_id == moment_id,
            GroupMomentMembers.user_id == user_id,
        )
    )
    row = result.scalar_one_or_none()
    if row is not None:
        status_val = (row.status or "").upper()
        if row.left_at is None and status_val not in _BLOCKED_MEMBER_STATUS:
            return True

    target = moment
    if target is None:
        target = await MomentRepository(session).get_by_id(moment_id)
    if target is None:
        return False

    uid = str(user_id)
    for member in store.list_accepted_members(target):
        if str(member.get("user_id") or "") == uid:
            return True
    return False


async def require_group_moment_access(
    session: AsyncSession, user_id: UUID, moment_id: UUID
) -> MomentModel:
    """Return the moment when the caller is the owner or an active member.

    Membership is accepted from either:
    - ``group_moment_members`` (relational roster), or
    - moment runtime store ``members`` (JWT invite accept path).

    Missing or unauthorized moments both surface as 404 to avoid IDOR probes.
    """
    moment = await MomentRepository(session).get_by_id(moment_id)
    if moment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
        )

    if moment.user_id == user_id:
        return moment

    if await is_active_group_member(session, user_id, moment_id, moment):
        return moment

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
    )
