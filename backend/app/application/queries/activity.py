"""Composed Activity reads for GraphQL — reuse personal/group/business feeds."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal
from app.core.config import settings


class ActivityScope(str, Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    BUSINESS = "BUSINESS"


@dataclass
class PersonalActivityDTO:
    snapshot: dict[str, Any]
    insights: list[dict[str, Any]] = field(default_factory=list)
    items: list[dict[str, Any]] = field(default_factory=list)
    next_cursor: str | None = None


@dataclass
class MomentActivityDTO:
    scope: ActivityScope
    moment_id: UUID
    items: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    page: int | None = None
    page_size: int | None = None
    summary: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)


ActivityDTO = PersonalActivityDTO | MomentActivityDTO


def _page_limit(first: int | None) -> int:
    ceiling = max(1, int(settings.graphql_max_page_size))
    return max(1, min(int(first or 50), ceiling, 100))


async def get_activity(
    session: AsyncSession,
    principal: Principal,
    scope: ActivityScope | str,
    *,
    moment_id: UUID | None = None,
    range: str = "all",
    domain: str = "all",
    kind: str = "all",
    q: str | None = None,
    after: str | None = None,
    first: int = 50,
    page: int = 1,
    status_filter: str = "active",
) -> ActivityDTO:
    """Return Unified Activity (PERSONAL) or moment-scoped GROUP/BUSINESS feeds."""
    from app.authorization import ResourceRef, require
    from app.authorization.require import (
        BUSINESS_MOMENT_VIEW,
        GROUP_MOMENT_VIEW,
    )
    from app.core.errors import NotFoundError

    scope_val = ActivityScope(scope) if not isinstance(scope, ActivityScope) else scope
    user_id = principal.user_id
    limit = _page_limit(first)

    if scope_val is ActivityScope.PERSONAL:
        from app.domains.personal.app_service import PersonalAppService

        data = await PersonalAppService(session).unified_activity(
            user_id,
            range=range,
            domain=domain,
            kind=kind,
            q=q,
            cursor=after,
            limit=limit,
        )
        return PersonalActivityDTO(
            snapshot=dict(data.get("snapshot") or {}),
            insights=[i for i in (data.get("insights") or []) if isinstance(i, dict)],
            items=[i for i in (data.get("items") or []) if isinstance(i, dict)],
            next_cursor=data.get("next_cursor"),
        )

    if moment_id is None:
        raise NotFoundError(
            "momentId is required for GROUP and BUSINESS activity",
            code="not_found",
        )

    if scope_val is ActivityScope.GROUP:
        moment = await require(
            session,
            principal,
            GROUP_MOMENT_VIEW,
            ResourceRef(kind="group_moment", id=moment_id),
        )
        return await _group_activity(session, user_id, moment_id, moment)

    if scope_val is ActivityScope.BUSINESS:
        await require(
            session,
            principal,
            BUSINESS_MOMENT_VIEW,
            ResourceRef(kind="business_moment", id=moment_id),
        )
        from app.domains.business.active_service import BusinessActiveService

        data = await BusinessActiveService(session).list_activity(
            user_id,
            moment_id,
            search=q,
            status_filter=status_filter,  # type: ignore[arg-type]
            page=max(1, int(page or 1)),
            page_size=limit,
        )
        if not isinstance(data, dict):
            data = {}
        items = [i for i in (data.get("items") or []) if isinstance(i, dict)]
        return MomentActivityDTO(
            scope=ActivityScope.BUSINESS,
            moment_id=moment_id,
            items=items,
            total=int(data.get("total") or len(items)),
            page=data.get("page"),
            page_size=data.get("page_size"),
            payload=data,
        )

    raise ValueError(f"Unsupported activity scope: {scope_val}")


async def _group_activity(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    moment: Any = None,
) -> MomentActivityDTO:
    from app.domains.group.read_service import GroupReadService
    from app.domains.group.shared_experience_service import SharedExperienceService
    from app.domains.group.shared_purchase_service import SharedPurchaseService

    code = str(getattr(moment, "moment_type", None) or "")

    data: dict[str, Any]
    if code == "SHARED_LIVING":
        data = await GroupReadService(session).living_list_activity(user_id, moment_id)
    elif code == "SHARED_PURCHASE":
        rows = await SharedPurchaseService(session).list_activity(user_id, moment_id)
        items = [r for r in (rows or []) if isinstance(r, dict)]
        data = {
            "moment_id": str(moment_id),
            "items": items,
            "summary": {"total": len(items)},
        }
    else:
        # SHARED_EXPERIENCE and unknown types use experience/timeline serialize.
        data = await SharedExperienceService(session).list_activity(user_id, moment_id)

    if not isinstance(data, dict):
        data = {}
    items = [i for i in (data.get("items") or []) if isinstance(i, dict)]
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else None
    total = int((summary or {}).get("total") or len(items))
    return MomentActivityDTO(
        scope=ActivityScope.GROUP,
        moment_id=moment_id,
        items=items,
        total=total,
        summary=summary,
        payload=data,
    )
