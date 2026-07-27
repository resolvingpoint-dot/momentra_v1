"""Bridge shared ``moments`` rows to ``business_moments`` (+ company workspace)."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.catalog import normalize_moment_type_code
from app.domains.business.models import (
    BusinessMoments,
    BusinessWorkspaceMembers,
    BusinessWorkspaces,
)
from app.domains.moments.models import MomentModel

_SHARED_TO_BUSINESS_STATUS = {
    "DRAFT": "draft",
    "SETUP": "configured",
    "ACTIVE": "active",
    "PAUSED": "active",
    "ARCHIVED": "archived",
    "COMPLETED": "completed",
}

_TYPE_TO_SQL = {
    "TEAM_OPERATIONS": "team_operations",
    "BUSINESS_RUNWAY": "business_runway",
    "BUSINESS_OPERATIONS": "business_operations",
}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def _ensure_owner_membership(
    session: AsyncSession, workspace_id: UUID, owner_user_id: UUID
) -> None:
    result = await session.execute(
        select(BusinessWorkspaceMembers).where(
            BusinessWorkspaceMembers.workspace_id == workspace_id,
            BusinessWorkspaceMembers.user_id == owner_user_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        if (existing.status or "").upper() != "ACTIVE":
            existing.status = "ACTIVE"
            existing.role = "OWNER"
            existing.updated_at = _now()
        return
    now = _now()
    session.add(
        BusinessWorkspaceMembers(
            member_id=uuid4(),
            workspace_id=workspace_id,
            user_id=owner_user_id,
            role="OWNER",
            status="ACTIVE",
            created_at=now,
            updated_at=now,
        )
    )
    await session.flush()


async def ensure_owner_business_workspace(
    session: AsyncSession,
    owner_user_id: UUID,
    *,
    name: str | None = None,
    workspace_id: UUID | None = None,
) -> UUID:
    """Return a company workspace for the owner.

    If ``workspace_id`` is provided, validates ownership/membership and returns it.
    Otherwise returns the first ACTIVE workspace for the owner, creating one if needed.
    """
    if workspace_id is not None:
        result = await session.execute(
            select(BusinessWorkspaces).where(
                BusinessWorkspaces.workspace_id == workspace_id,
                BusinessWorkspaces.status == "ACTIVE",
            )
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            raise ValueError("workspace_not_found")
        await _ensure_owner_membership(session, existing.workspace_id, owner_user_id)
        return existing.workspace_id

    result = await session.execute(
        select(BusinessWorkspaces)
        .where(
            BusinessWorkspaces.owned_by == owner_user_id,
            BusinessWorkspaces.status == "ACTIVE",
        )
        .order_by(BusinessWorkspaces.created_at.asc())
    )
    existing = result.scalars().first()
    if existing is not None:
        await _ensure_owner_membership(session, existing.workspace_id, owner_user_id)
        return existing.workspace_id

    now = _now()
    row = BusinessWorkspaces(
        owned_by=owner_user_id,
        created_by=owner_user_id,
        name=(name or "My Business")[:255],
        status="ACTIVE",
        currency_code="INR",
        timezone="Asia/Kolkata",
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    await session.flush()
    await _ensure_owner_membership(session, row.workspace_id, owner_user_id)
    return row.workspace_id


async def ensure_business_moment(
    session: AsyncSession,
    shared_moment: MomentModel,
    *,
    owner_user_id: UUID | None = None,
    answers: dict | None = None,
    workspace_id: UUID | None = None,
) -> UUID:
    """Upsert ``business_moments`` using the same id as the shared moment."""
    owner_id = owner_user_id or shared_moment.user_id
    code = normalize_moment_type_code(shared_moment.moment_type or "") or (
        shared_moment.moment_type or ""
    )
    sql_type = _TYPE_TO_SQL.get(code, "team_operations")
    moment_id = shared_moment.id
    answers = answers or {}
    display_name = (
        answers.get("moment_name")
        or answers.get("team_name")
        or shared_moment.title
        or "Team Operations"
    )

    resolved_workspace_id = await ensure_owner_business_workspace(
        session,
        owner_id,
        name=str(answers.get("team_name") or display_name)[:255],
        workspace_id=workspace_id,
    )

    result = await session.execute(
        select(BusinessMoments).where(BusinessMoments.moment_id == moment_id)
    )
    existing = result.scalar_one_or_none()
    now = _now()
    biz_status = _SHARED_TO_BUSINESS_STATUS.get(shared_moment.status or "DRAFT", "draft")

    if existing is None:
        row = BusinessMoments(
            moment_id=moment_id,
            workspace_id=resolved_workspace_id,
            moment_type=sql_type,
            moment_name=str(display_name)[:255],
            status=biz_status,
            created_by=owner_id,
            created_at=now,
            updated_at=now,
            activated_at=now if biz_status == "active" else None,
        )
        session.add(row)
        await session.flush()
        return moment_id

    existing.workspace_id = resolved_workspace_id
    existing.moment_type = sql_type
    existing.moment_name = str(display_name)[:255]
    existing.status = biz_status
    existing.updated_at = now
    if biz_status == "active" and existing.activated_at is None:
        existing.activated_at = now
    await session.flush()
    return moment_id
