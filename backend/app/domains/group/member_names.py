"""Resolve and enrich Group member display names from UserModel."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group.models import GroupMomentMembers
from app.domains.moments.models import MomentModel
from app.domains.users.models import UserModel

logger = logging.getLogger(__name__)

_GENERIC_NAMES = frozenset({"", "member", "someone", "you"})


def is_generic_member_name(name: object) -> bool:
    text = str(name or "").strip()
    if not text:
        return True
    lower = text.lower()
    if lower in _GENERIC_NAMES:
        return True
    # "Member 1", "Member 2", …
    if lower.startswith("member ") and lower[7:].strip().isdigit():
        return True
    return False


def display_name_from_user(user: UserModel | None, *, fallback: str = "Member") -> str:
    if user is None:
        return fallback
    name = (user.display_name or "").strip()
    if name:
        return name
    email = (user.email or "").strip()
    if email:
        local = email.split("@", 1)[0].strip()
        if local:
            return local
    return fallback


async def resolve_user_display_name(
    session: AsyncSession,
    user_id: UUID,
    *,
    fallback: str = "Member",
) -> str:
    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    return display_name_from_user(user, fallback=fallback)


async def batch_user_display_names(
    session: AsyncSession, user_ids: list[UUID]
) -> dict[UUID, str]:
    if not user_ids:
        return {}
    unique = list({uid for uid in user_ids if uid is not None})
    if not unique:
        return {}
    result = await session.execute(select(UserModel).where(UserModel.id.in_(unique)))
    out: dict[UUID, str] = {}
    for user in result.scalars().all():
        out[user.id] = display_name_from_user(user)
    return out


async def enrich_member_display_names(
    session: AsyncSession,
    moment: MomentModel,
    members: list[dict],
    *,
    write_back: bool = True,
) -> list[dict]:
    """Replace generic Member labels with UserModel names; optionally persist."""
    need: list[UUID] = []
    for row in members:
        if not is_generic_member_name(row.get("display_name")):
            continue
        raw = row.get("user_id")
        if not raw:
            continue
        try:
            need.append(UUID(str(raw)))
        except (TypeError, ValueError):
            continue
    if not need:
        return members

    names = await batch_user_display_names(session, need)
    if not names:
        return members

    changed_runtime = False
    state = store.read_state(moment) if write_back else None
    runtime_members = (
        (state or {}).get("runtime", {}).get("members") if state is not None else None
    )

    for row in members:
        raw = row.get("user_id")
        if not raw:
            continue
        try:
            uid = UUID(str(raw))
        except (TypeError, ValueError):
            continue
        resolved = names.get(uid)
        if not resolved:
            continue
        if not is_generic_member_name(row.get("display_name")):
            continue
        row["display_name"] = resolved
        if runtime_members is None:
            continue
        for rt in runtime_members:
            if rt.get("deleted"):
                continue
            rt_uid = str(rt.get("user_id") or "")
            if rt_uid != str(uid):
                continue
            if is_generic_member_name(rt.get("display_name")):
                rt["display_name"] = resolved
                changed_runtime = True

    if write_back and changed_runtime and state is not None:
        store.write_state(moment, state)
        try:
            result = await session.execute(
                select(GroupMomentMembers).where(
                    GroupMomentMembers.moment_id == moment.id,
                    GroupMomentMembers.left_at.is_(None),
                )
            )
            for gmm in result.scalars().all():
                if gmm.user_id is None:
                    continue
                resolved = names.get(gmm.user_id)
                if resolved and is_generic_member_name(gmm.display_name):
                    gmm.display_name = resolved
        except Exception:
            logger.warning(
                "Failed to write-back enriched group_moment_members names moment=%s",
                moment.id,
                exc_info=True,
            )

    return members
