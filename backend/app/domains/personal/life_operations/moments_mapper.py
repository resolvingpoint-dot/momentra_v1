"""Build Life Operations moments tab projection."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentModel
from app.domains.personal.catalog import moment_type_id, moment_type_name, normalize_moment_type_code
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalLifeOperationsProfile,
    PersonalMoneyEvents,
    PersonalMetricSnapshots,
    PersonalRuntimeSnapshots,
)
from app.domains.reference_data.catalog import get_reference_catalog

_LIFE_OPS = "LIFE_OPERATIONS"
_ACTIVE = {"ACTIVE"}


def _map_moment(moment: MomentModel | None) -> dict[str, Any] | None:
    if moment is None:
        return None
    code = normalize_moment_type_code(moment.moment_type or "")
    is_active = moment.status in _ACTIVE
    return {
        "moment_id": str(moment.id),
        "moment_type_id": moment_type_id(code),
        "moment_type_code": code or None,
        "moment_name": moment.title or moment_type_name(code) or "Untitled",
        "moment_description": moment.description,
        "status": moment.status,
        "current_runtime_state": moment.setup_state,
        "activated_at": (
            moment.updated_at.isoformat() if is_active and moment.updated_at else None
        ),
    }


async def _load_profile(
    session: AsyncSession, moment_id: UUID
) -> PersonalLifeOperationsProfile | None:
    result = await session.execute(
        select(PersonalLifeOperationsProfile).where(
            PersonalLifeOperationsProfile.moment_id == moment_id
        )
    )
    return result.scalar_one_or_none()


def _setup_summary(
    moment: MomentModel | None, profile: PersonalLifeOperationsProfile | None
) -> dict[str, Any]:
    if profile is not None:
        return {
            "pressure_sources": list(profile.pressure_sources or []),
            "recovery_supports": list(profile.recovery_supports or []),
            "runtime_priorities": list(profile.desired_directions or []),
            "identity_chips": [profile.runtime_identity] if profile.runtime_identity else [],
        }
    name = moment.title if moment else moment_type_name(_LIFE_OPS)
    return {
        "pressure_sources": [],
        "recovery_supports": [],
        "runtime_priorities": ["Consistency", "Recovery", "Focus"],
        "identity_chips": [name or "Life Operations"],
    }


def _progress_blocks(
    runtime: PersonalRuntimeSnapshots | None,
    metrics: list[PersonalMetricSnapshots],
    timeline_count: int,
) -> dict[str, Any]:
    ops_index = 70
    if runtime and runtime.primary_score is not None:
        ops_index = max(0, min(100, int(round(float(runtime.primary_score)))))
    recovery = 70
    for m in metrics:
        if m.metric_code == "RECOVERY_SCORE" and m.metric_value is not None:
            recovery = max(0, min(100, int(round(float(m.metric_value)))))
    label = runtime.runtime_state_label if runtime else "Getting started"
    return {
        "label": label,
        "subtitle": runtime.runtime_summary if runtime else "Log activity to build your operating picture.",
        "blocks": [
            {"key": "ops_index", "label": "Ops Index", "value": str(ops_index), "tone": "neutral"},
            {"key": "recovery", "label": "Recovery", "value": str(recovery), "tone": "positive" if recovery >= 70 else "neutral"},
            {"key": "activity", "label": "Events", "value": str(timeline_count), "tone": "neutral"},
        ],
    }


async def build_moments_projection(
    session: AsyncSession,
    user_id: UUID,
    moment: MomentModel | None,
    *,
    accounts_summary: dict[str, Any],
) -> dict[str, Any]:
    if moment is None:
        return {
            "moment_type_code": _LIFE_OPS,
            "status": "EMPTY",
            "moment": None,
            "setup_summary": _setup_summary(None, None),
            "recent_events": [],
            "accounts_summary": accounts_summary,
            "timeline_count": 0,
            "last_activity_at": None,
            "progress": _progress_blocks(None, [], 0),
        }

    moment_id = moment.id
    status = "ACTIVE" if moment.status in _ACTIVE else "SETUP"

    timeline_result = await session.execute(
        select(PersonalActivityTimeline)
        .where(
            PersonalActivityTimeline.moment_id == moment_id,
            PersonalActivityTimeline.is_voided.is_(False),
        )
        .order_by(PersonalActivityTimeline.event_occurred_at.desc())
        .limit(8)
    )
    timeline = list(timeline_result.scalars().all())

    count_result = await session.execute(
        select(func.count())
        .select_from(PersonalActivityTimeline)
        .where(
            PersonalActivityTimeline.moment_id == moment_id,
            PersonalActivityTimeline.is_voided.is_(False),
        )
    )
    timeline_count = int(count_result.scalar_one() or 0)

    money_result = await session.execute(
        select(PersonalMoneyEvents).where(
            PersonalMoneyEvents.moment_id == moment_id,
            PersonalMoneyEvents.is_voided.is_(False),
        )
    )
    money_by_qa = money_events_by_quick_add(list(money_result.scalars().all()))
    catalog = get_reference_catalog()

    recent_events = [
        map_timeline_to_recent_item(
            item, money=money_by_qa.get(item.quick_add_event_id), catalog=catalog
        )
        for item in timeline
    ]

    runtime_result = await session.execute(
        select(PersonalRuntimeSnapshots)
        .where(
            PersonalRuntimeSnapshots.moment_id == moment_id,
            PersonalRuntimeSnapshots.moment_type_code == _LIFE_OPS,
        )
        .order_by(PersonalRuntimeSnapshots.snapshot_date.desc())
        .limit(1)
    )
    runtime = runtime_result.scalar_one_or_none()

    metrics_result = await session.execute(
        select(PersonalMetricSnapshots)
        .where(
            PersonalMetricSnapshots.moment_id == moment_id,
            PersonalMetricSnapshots.moment_type_code == _LIFE_OPS,
        )
        .order_by(PersonalMetricSnapshots.snapshot_date.desc())
        .limit(10)
    )
    metrics = list(metrics_result.scalars().all())

    profile = await _load_profile(session, moment_id)
    last_at: str | None = None
    if timeline:
        when = timeline[0].event_occurred_at
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        last_at = when.isoformat()

    return {
        "moment_type_code": _LIFE_OPS,
        "status": status,
        "moment": _map_moment(moment),
        "setup_summary": _setup_summary(moment, profile),
        "recent_events": recent_events,
        "accounts_summary": accounts_summary,
        "timeline_count": timeline_count,
        "last_activity_at": last_at,
        "progress": _progress_blocks(runtime, metrics, timeline_count),
    }
