"""Shared activity query helpers."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.domains.moments.repository import MomentRepository
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalMoneyEvents,
    PersonalQuickAddEvents,
)
from app.domains.personal.quick_add.edit_service import PersonalQuickAddEditService
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.templates.activity.edit_schema import build_edit_schema
from app.domains.personal.templates.activity.mapper import map_timeline_to_activity_item


async def require_owned_moment(
    session: AsyncSession, user_id: UUID, moment_id: str
):
    try:
        mid = UUID(str(moment_id))
    except ValueError as exc:
        raise ValidationError("Invalid moment_id") from exc
    moment = await MomentRepository(session).get_by_user_and_id(user_id, mid)
    if moment is None:
        raise NotFoundError("Moment not found")
    return moment


async def load_activity_list(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    *,
    moment_type_code: str,
    limit: int = 50,
) -> list[dict]:
    timeline_result = await session.execute(
        select(PersonalActivityTimeline)
        .where(
            PersonalActivityTimeline.moment_id == moment_id,
            PersonalActivityTimeline.user_id == user_id,
            PersonalActivityTimeline.moment_type_code == moment_type_code,
            PersonalActivityTimeline.is_voided.is_(False),
        )
        .order_by(PersonalActivityTimeline.event_occurred_at.desc())
        .limit(limit)
    )
    timeline = list(timeline_result.scalars().all())
    if not timeline:
        return []

    qa_ids = [row.quick_add_event_id for row in timeline]
    events_result = await session.execute(
        select(PersonalQuickAddEvents).where(
            PersonalQuickAddEvents.quick_add_event_id.in_(qa_ids),
            PersonalQuickAddEvents.is_voided.is_(False),
        )
    )
    events_by_id = {
        e.quick_add_event_id: e for e in events_result.scalars().all()
    }

    money_result = await session.execute(
        select(PersonalMoneyEvents).where(
            PersonalMoneyEvents.moment_id == moment_id,
            PersonalMoneyEvents.is_voided.is_(False),
        )
    )
    money_by_qa = {m.quick_add_event_id: m for m in money_result.scalars().all()}

    return [
        map_timeline_to_activity_item(
            row,
            event=events_by_id.get(row.quick_add_event_id),
            money=money_by_qa.get(row.quick_add_event_id),
        )
        for row in timeline
    ]


async def build_activity_detail(
    session: AsyncSession,
    user_id: UUID,
    event_id: str,
    *,
    moment_type_code: str,
) -> dict:
    edit = PersonalQuickAddEditService(session)
    detail = await edit.detail(user_id, event_id)
    if detail.get("moment_id"):
        moment = await require_owned_moment(
            session, user_id, str(detail["moment_id"])
        )
        if moment.moment_type and normalize_moment_type_code(moment.moment_type) != moment_type_code:
            raise NotFoundError("Activity not found")
    event_type = str(detail.get("event_type") or "GENERIC")
    return {
        **detail,
        "id": detail.get("quick_add_event_id"),
        "activity_type": event_type,
        "title": detail.get("event_title"),
        "subtitle": detail.get("event_summary"),
        "edit_schema": build_edit_schema(moment_type_code, event_type),
        "allowed_actions": ["edit", "delete"],
        "values": detail,
    }
