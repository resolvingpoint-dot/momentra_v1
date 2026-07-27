"""Business activity permission checks against business_moment_members."""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessMomentMembers


class BusinessPermissionError(HTTPException):
    def __init__(self, detail_code: str, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": detail_code, "message": message},
        )


async def _active_member(
    session: AsyncSession, moment_id: UUID, user_id: UUID
) -> BusinessMomentMembers | None:
    result = await session.execute(
        select(BusinessMomentMembers).where(
            BusinessMomentMembers.moment_id == moment_id,
            BusinessMomentMembers.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


def _require_active(member: BusinessMomentMembers | None) -> BusinessMomentMembers:
    if member is None:
        raise BusinessPermissionError(
            "invalid_member", "User is not a member of this business moment."
        )
    if (member.member_status or "").lower() not in ("active", "configured"):
        raise BusinessPermissionError("member_inactive", "Member account is not active.")
    return member


def is_privileged_member(member: BusinessMomentMembers) -> bool:
    role = (member.role or "").strip().lower()
    return role in {
        "team lead",
        "budget owner",
        "approver",
        "runway owner",
        "finance lead",
        "operations lead",
        "operations owner",
        "budget controller",
    } or bool(member.is_team_lead) or bool(member.is_budget_owner)


# Back-compat alias for internal callers.
_is_privileged = is_privileged_member


async def can_create_activity(
    session: AsyncSession, moment_id: UUID, user_id: UUID, *, capability: str | None = None
) -> BusinessMomentMembers:
    member = await _active_member(session, moment_id, user_id)
    member = _require_active(member)
    if capability and not getattr(member, capability, False) and not _is_privileged(member):
        raise BusinessPermissionError(
            "business_permission_denied",
            f"Member lacks required capability: {capability}.",
        )
    return member


async def can_approve(
    session: AsyncSession, moment_id: UUID, user_id: UUID
) -> BusinessMomentMembers:
    member = await _active_member(session, moment_id, user_id)
    member = _require_active(member)
    has_approval = (
        getattr(member, "can_approve_runway_changes", False)
        or getattr(member, "can_approve_operations_requests", False)
        or _is_privileged(member)
    )
    if not has_approval:
        raise BusinessPermissionError(
            "approval_required", "Member does not have approval capability."
        )
    return member


def member_may_edit(
    member: BusinessMomentMembers, user_id: UUID, *, created_by: UUID | None = None
) -> bool:
    """Non-raising edit capability check for DTO flags."""
    is_own = created_by is not None and created_by == user_id
    can_edit_own = getattr(member, "can_edit_own_entries", True)
    can_edit_team = getattr(member, "can_edit_team_entries", False)
    if is_own and can_edit_own:
        return True
    return bool(can_edit_team or _is_privileged(member))


def member_may_delete(
    member: BusinessMomentMembers, user_id: UUID, *, created_by: UUID | None = None
) -> bool:
    """Non-raising delete capability check for DTO flags."""
    is_own = created_by is not None and created_by == user_id
    can_delete = getattr(member, "can_delete_operations_records", False)
    if is_own:
        return True
    return bool(can_delete or _is_privileged(member))


async def can_edit_activity(
    session: AsyncSession, moment_id: UUID, user_id: UUID, *, created_by: UUID | None = None
) -> BusinessMomentMembers:
    member = await _active_member(session, moment_id, user_id)
    member = _require_active(member)
    if member_may_edit(member, user_id, created_by=created_by):
        return member
    raise BusinessPermissionError(
        "business_permission_denied",
        "Member does not have edit capability for this activity.",
    )


async def can_delete_activity(
    session: AsyncSession, moment_id: UUID, user_id: UUID, *, created_by: UUID | None = None
) -> BusinessMomentMembers:
    member = await _active_member(session, moment_id, user_id)
    member = _require_active(member)
    if member_may_delete(member, user_id, created_by=created_by):
        return member
    raise BusinessPermissionError(
        "business_permission_denied",
        "Member does not have delete capability for this activity.",
    )


async def get_active_member(
    session: AsyncSession, moment_id: UUID, user_id: UUID
) -> BusinessMomentMembers | None:
    """Return active member row for DTO authorization flags (None if owner-only read)."""
    member = await _active_member(session, moment_id, user_id)
    if member is None:
        return None
    if (member.member_status or "").lower() not in ("active", "configured"):
        return None
    return member


async def require_moment_read_access(
    session: AsyncSession, moment_id: UUID, user_id: UUID
) -> None:
    """Gate projection + activity reads — active member or moment owner."""
    member = await _active_member(session, moment_id, user_id)
    if member is not None:
        _require_active(member)
        return

    from app.domains.business.models import BusinessMoments

    result = await session.execute(
        select(BusinessMoments.created_by).where(BusinessMoments.moment_id == moment_id)
    )
    created_by = result.scalar_one_or_none()
    if created_by is not None and created_by == user_id:
        return

    raise BusinessPermissionError(
        "invalid_member",
        "User is not a member of this business moment.",
    )


async def require_workspace_member(
    session: AsyncSession, workspace_id: UUID, user_id: UUID
) -> "BusinessWorkspaceMembers":
    """Gate company entry — active workspace member required."""
    from app.domains.business.models import BusinessWorkspaceMembers
    from app.domains.business.workspace_service import WorkspacePermissionError

    result = await session.execute(
        select(BusinessWorkspaceMembers).where(
            BusinessWorkspaceMembers.workspace_id == workspace_id,
            BusinessWorkspaceMembers.user_id == user_id,
            BusinessWorkspaceMembers.status == "ACTIVE",
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise WorkspacePermissionError(
            "workspace_permission_denied",
            "You are not a member of this company.",
        )
    return member
