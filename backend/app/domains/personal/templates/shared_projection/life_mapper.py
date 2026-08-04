"""Shared My Money life tab operating view projection."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentModel
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.life_operations.pulse_mapper import _int_score, _metric_value, _money_minor
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalLifeOperationsProfile,
    PersonalLifeRecoveryEvents,
    PersonalMetricSnapshots,
    PersonalMoneyEvents,
    PersonalRuntimeSnapshots,
)
from app.domains.reference_data.catalog import get_reference_catalog

_LIFE_OPS = "LIFE_OPERATIONS"


def _dimension(score: int, label: str, detail: str) -> dict[str, Any]:
    return {"score": score, "label": label, "detail": detail}


async def _load_lo_profile(session: AsyncSession, moment_id: UUID) -> PersonalLifeOperationsProfile | None:
    result = await session.execute(
        select(PersonalLifeOperationsProfile).where(
            PersonalLifeOperationsProfile.moment_id == moment_id
        )
    )
    return result.scalar_one_or_none()


def _momentum_direction(this_week: int, last_week: int) -> str:
    if this_week > last_week:
        return "up"
    if this_week < last_week:
        return "down"
    return "flat"


async def build_life_operating_view(
    session: AsyncSession,
    user_id: UUID,
    moment: MomentModel | None,
    moment_type_code: str,
) -> dict[str, Any]:
    code = moment_type_code.upper().replace("-", "_")
    if moment is None or moment.status != "ACTIVE":
        return {
            "moment_type_code": code,
            "status": "SETUP" if moment else "EMPTY",
            "headline": "Getting started",
            "subtitle": "Activate your moment to see how your life is operating.",
            "operating_summary": {
                "ops_index": 0,
                "momentum": {"direction": "flat", "label": "Waiting"},
                "today_vs_week": {"spend_delta_percent": 0, "recovery_sessions": 0},
            },
            "dimensions": {
                "financial_health": _dimension(50, "Neutral", "No spending data yet."),
                "recovery": _dimension(50, "Neutral", "Log recovery to track integrity."),
                "attention": _dimension(50, "Neutral", "Attention load unknown."),
                "rhythm": _dimension(50, "Neutral", "Rhythm forming."),
                "workload": _dimension(50, "Neutral", "No workload signals."),
                "momentum": _dimension(50, "Flat", "Build momentum with quick adds."),
            },
            "pressure_sources": [],
            "recovery_supports": [],
            "today": {"event_count": 0, "spend_minor": 0},
            "week": {"event_count": 0, "spend_minor": 0},
            "signals": [],
            "recent_activity": [],
        }

    moment_id = moment.id
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    from app.domains.personal.preferences_service import (
        PersonalPreferencesService,
        compute_week_bounds,
    )

    personal_pref = await PersonalPreferencesService(session).get_by_user_id(user_id)
    week_start, last_week_start = compute_week_bounds(
        now, personal_pref.week_start_day if personal_pref else "MONDAY"
    )
    # Align to same date-only semantics as today_start when tz-naive comparisons follow.
    if week_start.tzinfo and not today_start.tzinfo:
        week_start = week_start.replace(tzinfo=None)
        last_week_start = last_week_start.replace(tzinfo=None)

    runtime_result = await session.execute(
        select(PersonalRuntimeSnapshots)
        .where(
            PersonalRuntimeSnapshots.moment_id == moment_id,
            PersonalRuntimeSnapshots.moment_type_code == code,
        )
        .order_by(PersonalRuntimeSnapshots.snapshot_date.desc())
        .limit(1)
    )
    runtime = runtime_result.scalar_one_or_none()

    metrics_result = await session.execute(
        select(PersonalMetricSnapshots)
        .where(
            PersonalMetricSnapshots.moment_id == moment_id,
            PersonalMetricSnapshots.moment_type_code == code,
        )
        .order_by(PersonalMetricSnapshots.snapshot_date.desc())
        .limit(10)
    )
    metrics = list(metrics_result.scalars().all())

    timeline_result = await session.execute(
        select(PersonalActivityTimeline)
        .where(
            PersonalActivityTimeline.moment_id == moment_id,
            PersonalActivityTimeline.is_voided.is_(False),
        )
        .order_by(PersonalActivityTimeline.event_occurred_at.desc())
        .limit(50)
    )
    timeline = list(timeline_result.scalars().all())

    money_result = await session.execute(
        select(PersonalMoneyEvents).where(
            PersonalMoneyEvents.moment_id == moment_id,
            PersonalMoneyEvents.is_voided.is_(False),
        )
    )
    money_events = list(money_result.scalars().all())
    money_by_qa = money_events_by_quick_add(money_events)
    catalog = get_reference_catalog()

    recovery_events: list[PersonalLifeRecoveryEvents] = []
    if code == _LIFE_OPS:
        recovery_result = await session.execute(
            select(PersonalLifeRecoveryEvents).where(
                PersonalLifeRecoveryEvents.moment_id == moment_id,
                PersonalLifeRecoveryEvents.user_id == user_id,
            )
        )
        recovery_events = list(recovery_result.scalars().all())

    profile = await _load_lo_profile(session, moment_id) if code == _LIFE_OPS else None

    ops_index = _int_score(runtime.primary_score if runtime else None, 70)
    pressure = _metric_value(metrics, "PRESSURE_SCORE", max(0, 100 - ops_index))
    recovery = _metric_value(metrics, "RECOVERY_SCORE", ops_index)
    stability = _metric_value(metrics, "STABILITY_SCORE", ops_index)
    cognitive = _metric_value(metrics, "COGNITIVE_LOAD_SCORE", pressure)
    attention_score = max(0, min(100, 100 - cognitive))
    financial_score = max(0, min(100, 100 - min(pressure, 80)))

    def _naive(dt: datetime) -> datetime:
        return dt.replace(tzinfo=None) if dt.tzinfo else dt

    today_events = [
        t for t in timeline if _naive(t.event_occurred_at) >= _naive(today_start)
    ]
    week_events = [
        t for t in timeline if _naive(t.event_occurred_at) >= _naive(week_start)
    ]
    last_week_events = [
        t
        for t in timeline
        if _naive(last_week_start) <= _naive(t.event_occurred_at) < _naive(week_start)
    ]

    def spend_for_period(events: list[PersonalActivityTimeline]) -> int:
        total = 0
        for row in events:
            money = money_by_qa.get(row.quick_add_event_id)
            if money and money.direction == "DEBIT":
                total += _money_minor(money)
        return total

    today_spend = spend_for_period(today_events)
    week_spend = spend_for_period(week_events)
    last_week_spend = spend_for_period(last_week_events)
    spend_delta = 0
    if last_week_spend > 0:
        spend_delta = int(round((week_spend - last_week_spend) / last_week_spend * 100))

    recovery_today = sum(
        1
        for r in recovery_events
        if r.created_at and _naive(r.created_at) >= _naive(today_start)
    )
    recovery_week = sum(
        1
        for r in recovery_events
        if r.created_at and _naive(r.created_at) >= _naive(week_start)
    )

    momentum_dir = _momentum_direction(len(week_events), len(last_week_events))
    momentum_label = {"up": "Building", "down": "Slowing", "flat": "Steady"}[momentum_dir]

    status_band = runtime.runtime_state_label if runtime else "Mostly Stable"
    headline = status_band or "Operating steadily"
    subtitle_parts: list[str] = []
    if recovery >= 70:
        subtitle_parts.append("Recovery is holding")
    elif recovery < 50:
        subtitle_parts.append("Recovery needs attention")
    if spend_delta > 10:
        subtitle_parts.append("spending picked up this week")
    elif spend_delta < -10:
        subtitle_parts.append("spending eased this week")
    subtitle = "; ".join(subtitle_parts) if subtitle_parts else (
        runtime.runtime_summary if runtime else "Your operating picture is forming."
    )

    recent_activity = [
        map_timeline_to_recent_item(
            item, money=money_by_qa.get(item.quick_add_event_id), catalog=catalog
        )
        for item in timeline[:8]
    ]

    workload_score = max(0, min(100, pressure))
    momentum_score = max(0, min(100, ops_index))

    signals = [
        {"signal_id": "recovery", "trend": "UP" if recovery >= 70 else "STABLE"},
        {"signal_id": "pressure", "trend": "DOWN" if pressure >= 60 else "STABLE"},
        {"signal_id": "momentum", "trend": momentum_dir.upper()},
    ]

    return {
        "moment_type_code": code,
        "status": "ACTIVE",
        "headline": headline,
        "subtitle": subtitle,
        "operating_summary": {
            "ops_index": ops_index,
            "momentum": {"direction": momentum_dir, "label": momentum_label},
            "today_vs_week": {
                "spend_delta_percent": spend_delta,
                "recovery_sessions": recovery_week,
            },
        },
        "dimensions": {
            "financial_health": _dimension(
                financial_score,
                "Healthy" if financial_score >= 70 else "Watch",
                f"₹{today_spend // 100:,} spent today.",
            ),
            "recovery": _dimension(
                recovery,
                "Strong" if recovery >= 70 else "Building",
                f"{recovery_week} recovery logs this week.",
            ),
            "attention": _dimension(
                attention_score,
                "Clear" if attention_score >= 70 else "Loaded",
                "Cognitive load from recent activity.",
            ),
            "rhythm": _dimension(
                stability,
                "Stable" if stability >= 70 else "Shifting",
                f"{len(week_events)} life signals this week.",
            ),
            "workload": _dimension(
                workload_score,
                "Light" if workload_score < 50 else "Elevated",
                f"Pressure score {pressure}.",
            ),
            "momentum": _dimension(
                momentum_score,
                momentum_label,
                f"{len(today_events)} signals logged today.",
            ),
        },
        "pressure_sources": list(profile.pressure_sources) if profile else [],
        "recovery_supports": list(profile.recovery_supports) if profile else [],
        "today": {
            "event_count": len(today_events),
            "spend_minor": today_spend,
            "recovery_sessions": recovery_today,
        },
        "week": {
            "event_count": len(week_events),
            "spend_minor": week_spend,
            "recovery_sessions": recovery_week,
        },
        "signals": signals,
        "recent_activity": recent_activity,
    }
