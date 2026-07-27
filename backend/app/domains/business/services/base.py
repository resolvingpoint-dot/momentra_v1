"""Shared base for the modular Business services.

Business data is authorized by *membership*: a caller may act on a moment when
they hold a non-removed ``business_moment_members`` row for it (the moment's
``created_by`` is also allowed). Child records key off ``moment_id``; some team_*
tables reference ``member_id`` while operations_*/runway_* tables store the
actor's ``user_id`` directly, so helpers expose both.

This base wires the moment + member repositories once and provides reusable
serialization/pagination helpers so feature modules stay thin (no duplicated
query/serialization code). Everything returns generated schemas / ``Page`` and
never SQLAlchemy models.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, PermissionDeniedError, StateTransitionError
from app.core.repository import AsyncRepository
from app.core.service import Page
from app.domains.business.repository import (
    BusinessMomentMembersRepository,
    BusinessMomentsRepository,
)

_REMOVED_MEMBER = "removed"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class BusinessModuleService:
    """Base class for every Business feature module."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments_repo = BusinessMomentsRepository(session)
        self.members_repo = BusinessMomentMembersRepository(session)

    # ------------------------------------------------------------------ #
    # serialization / pagination helpers (reused by all modules)
    # ------------------------------------------------------------------ #
    async def _created(self, repo: AsyncRepository, schema_cls, data: Mapping[str, Any]):
        obj = await repo.create(data)
        await self.session.refresh(obj)  # load server defaults before serializing
        return schema_cls.model_validate(obj)

    async def _page(
        self,
        repo: AsyncRepository,
        schema_cls,
        *,
        filters: Mapping[str, Any] | None,
        order_by: str | None,
        page: int,
        per_page: int,
    ) -> Page:
        limit, offset = per_page, (page - 1) * per_page
        total = await repo.count(filters=filters)
        items = await repo.list(filters=filters, order_by=order_by, limit=limit, offset=offset)
        return Page[schema_cls](
            items=[schema_cls.model_validate(o) for o in items], total=total, limit=limit, offset=offset
        )

    async def _list(self, repo: AsyncRepository, schema_cls, *, filters, order_by=None, limit=50):
        items = await repo.list(filters=filters, order_by=order_by, limit=limit)
        return [schema_cls.model_validate(o) for o in items]

    # ------------------------------------------------------------------ #
    # membership authorization
    # ------------------------------------------------------------------ #
    async def _access(self, user_id: UUID, moment_id: UUID):
        """Return ``(moment, member|None)``. ``member`` is None when the caller is
        the moment creator without a member row. Raises when the moment is missing
        or the caller has no access."""
        moment = await self.moments_repo.get_by_id(moment_id)
        if moment is None:
            raise NotFoundError("Business moment not found")
        member = await self.members_repo.get_by(moment_id=moment_id, user_id=user_id)
        if member is not None and member.member_status != _REMOVED_MEMBER:
            return moment, member
        if moment.created_by == user_id:
            return moment, None
        raise PermissionDeniedError("You are not a member of this business moment")

    async def _require_member(self, user_id: UUID, moment_id: UUID):
        _moment, member = await self._access(user_id, moment_id)
        if member is None:
            raise PermissionDeniedError("An active membership is required for this action")
        return member

    async def _resolve_member_id(self, user_id: UUID, moment_id: UUID, provided: UUID | None = None) -> UUID:
        if provided is not None:
            return provided
        member = await self._require_member(user_id, moment_id)
        return member.member_id

    # ------------------------------------------------------------------ #
    # generic status transition (reused by state engine + approvals + risks)
    # ------------------------------------------------------------------ #
    async def _apply_transition(
        self,
        obj: Any,
        status_field: str,
        to_status: str,
        allowed_from: set[str],
        *,
        extra: Mapping[str, Any] | None = None,
        label: str = "record",
    ) -> None:
        current = getattr(obj, status_field)
        if current not in allowed_from:
            raise StateTransitionError(f"Cannot move {label} from {current} to {to_status}")
        setattr(obj, status_field, to_status)
        if "updated_at" in obj.__table__.columns:
            obj.updated_at = now_utc()
        for key, value in (extra or {}).items():
            setattr(obj, key, value)
        await self.session.flush()
