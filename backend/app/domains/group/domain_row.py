"""Ensure relational ``group_moments`` stub exists for app Group moments.

App Group moments live primarily on ``moments`` (+ description runtime JSON).
Many Group tables FK ``group_moments.moment_id``. Create/activate historically
only wrote ``moments``, so ACTIVE inventory could exist without a domain row —
roster/expense FKs and invitee gates then fail. Invite accept already upserts a
stub; create/activate must too.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group.models import GroupMomentMembers, GroupMoments
from app.domains.moments.models import MomentModel


def _naive_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def ensure_group_moments_row(
    session: AsyncSession,
    moment: MomentModel,
    *,
    ensure_owner_member: bool = True,
    owner_display_name: str = "You",
) -> GroupMoments:
    """Upsert stub ``group_moments`` (+ optional owner roster row)."""
    mid = moment.id
    now = _naive_now()
    result = await session.execute(
        select(GroupMoments).where(GroupMoments.moment_id == mid)
    )
    row = result.scalar_one_or_none()
    status = str(moment.status or "DRAFT")
    name = str(moment.title or "Group moment")
    mtype = str(moment.moment_type or "SHARED_EXPERIENCE")

    if row is None:
        row = GroupMoments(
            moment_id=mid,
            moment_type=mtype,
            moment_profile="DEFAULT",
            moment_name=name,
            status=status if status in {"DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"} else "DRAFT",
            stage="CREATED",
            created_by=moment.user_id,
            created_at=now,
            updated_at=now,
            activation_status="ACTIVE" if status == "ACTIVE" else "PLANNING",
            activated_at=now if status == "ACTIVE" else None,
        )
        session.add(row)
    else:
        row.moment_name = name or row.moment_name
        row.moment_type = mtype or row.moment_type
        if status in {"DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"}:
            row.status = status
        if status == "ACTIVE":
            row.activation_status = "ACTIVE"
            row.activated_at = row.activated_at or now
        row.updated_at = now

    if ensure_owner_member and moment.user_id is not None:
        await _ensure_owner_member(
            session,
            moment_id=mid,
            user_id=moment.user_id,
            display_name=owner_display_name,
            now=now,
        )

    await session.flush()
    return row


async def _ensure_owner_member(
    session: AsyncSession,
    *,
    moment_id: UUID,
    user_id: UUID,
    display_name: str,
    now: datetime,
) -> None:
    from uuid import uuid4

    mem_result = await session.execute(
        select(GroupMomentMembers).where(
            GroupMomentMembers.moment_id == moment_id,
            GroupMomentMembers.user_id == user_id,
        )
    )
    existing = list(mem_result.scalars().all())
    active = next(
        (
            m
            for m in existing
            if (m.status or "").upper() not in {"LEFT", "REMOVED", "DECLINED"}
            and m.left_at is None
        ),
        None,
    )
    if active is not None:
        active.status = "ACTIVE"
        active.joined_at = active.joined_at or now
        if display_name:
            active.display_name = display_name
        return

    session.add(
        GroupMomentMembers(
            member_id=uuid4(),
            moment_id=moment_id,
            user_id=user_id,
            display_name=display_name or "You",
            role_code="ORGANIZER",
            status="ACTIVE",
            joined_at=now,
            created_at=now,
        )
    )
