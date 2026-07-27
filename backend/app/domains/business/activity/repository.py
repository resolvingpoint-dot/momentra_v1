"""CRUD operations on BusinessActivityEvents + activity audit insertion."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityAudit, BusinessActivityEvents


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def find_by_client_request_id(
    session: AsyncSession, moment_id: UUID, client_request_id: str
) -> BusinessActivityEvents | None:
    result = await session.execute(
        select(BusinessActivityEvents).where(
            BusinessActivityEvents.business_moment_id == moment_id,
            BusinessActivityEvents.client_request_id == client_request_id,
            BusinessActivityEvents.is_voided.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def insert_event(
    session: AsyncSession,
    *,
    event_id: UUID,
    business_moment_id: UUID,
    user_id: UUID,
    moment_type_code: str,
    action_type: str,
    title: str,
    subtitle: str | None = None,
    payload: dict[str, Any] | None = None,
    client_request_id: str | None = None,
    source: str = "quick_add",
) -> BusinessActivityEvents:
    row = BusinessActivityEvents(
        event_id=event_id,
        business_moment_id=business_moment_id,
        user_id=user_id,
        moment_type_code=moment_type_code,
        action_type=action_type,
        title=title,
        subtitle=subtitle,
        occurred_at=_now(),
        created_by=user_id,
        source=source,
        payload=payload or {},
        client_request_id=client_request_id,
        is_voided=False,
    )
    session.add(row)
    await session.flush()
    return row


async def get_event(
    session: AsyncSession, event_id: UUID
) -> BusinessActivityEvents | None:
    result = await session.execute(
        select(BusinessActivityEvents).where(BusinessActivityEvents.event_id == event_id)
    )
    return result.scalar_one_or_none()


def _apply_list_filters(
    q,
    moment_id: UUID,
    *,
    action: str | None = None,
    member: UUID | None = None,
    status: Literal["all", "active", "voided"] = "active",
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
):
    q = q.where(BusinessActivityEvents.business_moment_id == moment_id)
    if status == "active":
        q = q.where(BusinessActivityEvents.is_voided.is_(False))
    elif status == "voided":
        q = q.where(BusinessActivityEvents.is_voided.is_(True))
    # status == "all" → no void filter

    if action:
        actions = [a.strip().upper() for a in action.split(",") if a.strip()]
        if len(actions) == 1:
            q = q.where(BusinessActivityEvents.action_type == actions[0])
        elif actions:
            q = q.where(BusinessActivityEvents.action_type.in_(actions))

    if member is not None:
        q = q.where(BusinessActivityEvents.created_by == member)

    if date_from is not None:
        q = q.where(BusinessActivityEvents.occurred_at >= date_from)
    if date_to is not None:
        q = q.where(BusinessActivityEvents.occurred_at <= date_to)

    if search and search.strip():
        like = f"%{search.strip().lower()}%"
        q = q.where(
            or_(
                func.lower(BusinessActivityEvents.title).like(like),
                func.lower(BusinessActivityEvents.action_type).like(like),
                func.lower(func.coalesce(BusinessActivityEvents.subtitle, "")).like(like),
            )
        )
    return q


async def list_events(
    session: AsyncSession,
    moment_id: UUID,
    *,
    include_voided: bool = False,
    action: str | None = None,
    member: UUID | None = None,
    status: Literal["all", "active", "voided"] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    search: str | None = None,
    sort: Literal["newest", "oldest"] = "newest",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[BusinessActivityEvents], int]:
    """Filtered, paginated activity list. Returns (page_rows, total_count)."""
    resolved_status: Literal["all", "active", "voided"]
    if status is not None:
        resolved_status = status
    elif include_voided:
        resolved_status = "all"
    else:
        resolved_status = "active"

    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    count_q = _apply_list_filters(
        select(func.count()).select_from(BusinessActivityEvents),
        moment_id,
        action=action,
        member=member,
        status=resolved_status,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    total = int((await session.execute(count_q)).scalar_one() or 0)

    list_q = _apply_list_filters(
        select(BusinessActivityEvents),
        moment_id,
        action=action,
        member=member,
        status=resolved_status,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    if sort == "oldest":
        list_q = list_q.order_by(BusinessActivityEvents.occurred_at.asc())
    else:
        list_q = list_q.order_by(BusinessActivityEvents.occurred_at.desc())
    list_q = list_q.offset((page - 1) * page_size).limit(page_size)

    result = await session.execute(list_q)
    return list(result.scalars().all()), total


async def patch_event(
    session: AsyncSession, event_id: UUID, values: dict[str, Any]
) -> BusinessActivityEvents | None:
    values = {**values, "updated_at": _now()}
    await session.execute(
        update(BusinessActivityEvents)
        .where(BusinessActivityEvents.event_id == event_id)
        .values(**values)
    )
    await session.flush()
    return await get_event(session, event_id)


async def soft_void_event(session: AsyncSession, event_id: UUID) -> bool:
    result = await session.execute(
        update(BusinessActivityEvents)
        .where(
            BusinessActivityEvents.event_id == event_id,
            BusinessActivityEvents.is_voided.is_(False),
        )
        .values(is_voided=True, voided_at=_now(), updated_at=_now())
    )
    await session.flush()
    return (result.rowcount or 0) > 0


async def insert_audit(
    session: AsyncSession,
    *,
    event_id: UUID,
    action: str,
    actor_id: UUID,
    before_payload: dict[str, Any] | None = None,
    after_payload: dict[str, Any] | None = None,
) -> None:
    session.add(
        BusinessActivityAudit(
            event_id=event_id,
            action=action,
            actor_id=actor_id,
            before_payload=before_payload,
            after_payload=after_payload,
            occurred_at=_now(),
        )
    )
    await session.flush()
