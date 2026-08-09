"""Build Life Operations pulse block from personal snapshot tables."""
from __future__ import annotations

import asyncio
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalLifeAdjustEvents,
    PersonalLifeAttentionEvents,
    PersonalLifeMoodEvents,
    PersonalLifeRecoveryEvents,
    PersonalMetricSnapshots,
    PersonalMoneyEvents,
    PersonalRuntimeSnapshots,
)

from app.domains.personal.life_operations.activity_mapper import (
    _category_meta,
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.reference_data.catalog import get_reference_catalog


def _int_score(value: Decimal | float | int | None, default: int = 70) -> int:
    if value is None:
        return default
    return max(0, min(100, int(round(float(value)))))


_LIFE_OPS = "LIFE_OPERATIONS"


def _money_minor(event: PersonalMoneyEvents) -> int:
    if getattr(event, "amount_minor", None) is not None and int(event.amount_minor) > 0:
        return int(event.amount_minor)
    catalog = get_reference_catalog()
    minor_unit = catalog.minor_unit_for(event.currency_code or "INR")
    multiplier = 10 ** minor_unit
    return int(float(event.amount) * multiplier)


def _metric_value(metrics: list[PersonalMetricSnapshots], code: str, default: int) -> int:
    for m in metrics:
        if m.metric_code == code:
            return _int_score(m.metric_value, default)
    return default


async def _count_rows(session: AsyncSession, stmt) -> int:
    result = await session.execute(stmt)
    return int(result.scalar_one() or 0)


async def _signal_event_count(session: AsyncSession, moment_id: UUID) -> int:
    """Count wellbeing/signal events that drive Life Ops health scores."""
    counts = await asyncio.gather(
        *(
            _count_rows(
                session,
                select(func.count()).select_from(model).where(model.moment_id == moment_id),
            )
            for model in (
                PersonalLifeAttentionEvents,
                PersonalLifeRecoveryEvents,
                PersonalLifeMoodEvents,
                PersonalLifeAdjustEvents,
            )
        )
    )
    return int(sum(counts))


def _month_bounds(today: date | None = None) -> tuple[date, date]:
    today = today or date.today()
    start = today.replace(day=1)
    if today.month == 12:
        end = date(today.year + 1, 1, 1)
    else:
        end = date(today.year, today.month + 1, 1)
    return start, end


async def build_life_operations_pulse(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    moment_name: str,
) -> dict[str, Any] | None:
    month_start, month_end = _month_bounds()

    runtime_coro = session.execute(
        select(PersonalRuntimeSnapshots)
        .where(
            PersonalRuntimeSnapshots.moment_id == moment_id,
            PersonalRuntimeSnapshots.moment_type_code == _LIFE_OPS,
        )
        .order_by(PersonalRuntimeSnapshots.snapshot_date.desc())
        .limit(1)
    )
    metrics_coro = session.execute(
        select(PersonalMetricSnapshots)
        .where(
            PersonalMetricSnapshots.moment_id == moment_id,
            PersonalMetricSnapshots.moment_type_code == _LIFE_OPS,
        )
        .order_by(PersonalMetricSnapshots.snapshot_date.desc())
        .limit(10)
    )
    timeline_coro = session.execute(
        select(PersonalActivityTimeline)
        .where(
            PersonalActivityTimeline.moment_id == moment_id,
            PersonalActivityTimeline.is_voided.is_(False),
        )
        .order_by(PersonalActivityTimeline.event_occurred_at.desc())
        .limit(8)
    )
    month_money_coro = session.execute(
        select(PersonalMoneyEvents).where(
            PersonalMoneyEvents.moment_id == moment_id,
            PersonalMoneyEvents.is_voided.is_(False),
            PersonalMoneyEvents.event_date >= month_start,
            PersonalMoneyEvents.event_date < month_end,
        )
    )
    money_coro = session.execute(
        select(PersonalMoneyEvents)
        .where(
            PersonalMoneyEvents.moment_id == moment_id,
            PersonalMoneyEvents.is_voided.is_(False),
        )
        .order_by(PersonalMoneyEvents.event_date.desc())
        .limit(40)
    )

    (
        runtime_result,
        metrics_result,
        timeline_result,
        month_money_result,
        money_result,
        signal_count,
    ) = await asyncio.gather(
        runtime_coro,
        metrics_coro,
        timeline_coro,
        month_money_coro,
        money_coro,
        _signal_event_count(session, moment_id),
    )

    runtime = runtime_result.scalar_one_or_none()
    metrics = list(metrics_result.scalars().all())
    timeline = list(timeline_result.scalars().all())
    month_money = list(month_money_result.scalars().all())
    money_events = list(money_result.scalars().all())
    money_by_qa = money_events_by_quick_add(money_events)
    catalog = get_reference_catalog()
    data_sufficient = signal_count > 0

    if data_sufficient:
        ops_index: int | None = _int_score(runtime.primary_score if runtime else None, 70)
        status_band = runtime.runtime_state_label if runtime else "Mostly Stable"
        pressure = _metric_value(metrics, "PRESSURE_SCORE", max(0, 100 - (ops_index or 70)))
        recovery = _metric_value(metrics, "RECOVERY_SCORE", ops_index or 70)
        stability = _metric_value(metrics, "STABILITY_SCORE", ops_index or 70)
        cognitive = _metric_value(metrics, "COGNITIVE_LOAD_SCORE", pressure)
        attention = max(0, min(100, 100 - cognitive))
        axis_scores = {
            "pressure": pressure,
            "recovery": recovery,
            "discipline": stability,
            "attention": attention,
        }
        rhythm_label = status_band
        hero_subtitle = runtime.runtime_summary if runtime else None
    else:
        ops_index = None
        status_band = "Insufficient data"
        pressure = recovery = stability = attention = 0
        axis_scores = {
            "pressure": 0,
            "recovery": 0,
            "discipline": 0,
            "attention": 0,
        }
        rhythm_label = status_band
        hero_subtitle = "Log attention, recovery, mood, or adjust events to build your health score."

    used_minor = sum(_money_minor(e) for e in month_money if e.direction == "DEBIT")
    budget_minor = sum(_money_minor(e) for e in month_money if e.direction == "CREDIT")
    has_budget = budget_minor > 0
    if has_budget:
        remaining = max(0, budget_minor - used_minor)
        utilization = min(100, int(round(used_minor / budget_minor * 100)))
    else:
        remaining = None
        utilization = None

    segments: dict[str, int] = {}
    segment_meta: dict[str, tuple[str | None, str | None]] = {}
    for e in month_money:
        if e.direction != "DEBIT":
            continue
        key = e.category_code or "other"
        segments[key] = segments.get(key, 0) + _money_minor(e)
        if key not in segment_meta:
            icon, color = _category_meta(catalog, e.category_code, getattr(e, "subcategory_code", None))
            segment_meta[key] = (icon, color)
    total_seg = sum(segments.values()) or 1
    financial_segments = [
        {
            "category_id": cat,
            "category_name": cat,
            "amount_minor": amt,
            "share_percent": int(round(amt / total_seg * 100)),
            "icon": segment_meta.get(cat, (None, None))[0],
            "color": segment_meta.get(cat, (None, None))[1],
        }
        for cat, amt in segments.items()
    ]

    recent_items = [
        map_timeline_to_recent_item(
            item,
            money=money_by_qa.get(item.quick_add_event_id),
            catalog=catalog,
        )
        for item in timeline
    ]

    kpi_ops = "—" if ops_index is None else str(ops_index)

    return {
        "rhythm_label": rhythm_label,
        "hero_subtitle": hero_subtitle,
        "dashboard_card": {
            "moment_id": str(moment_id),
            "moment_name": moment_name,
            "moment_type_code": _LIFE_OPS,
            "kpis": [
                {"kpi_id": "ops_index", "label": "Ops Index", "value": kpi_ops},
                {
                    "kpi_id": "entries",
                    "label": "Recent",
                    "value": str(len(timeline)),
                },
            ],
            "recent_items": recent_items,
            "empty_recent_message": "No activity yet. Log your first event.",
        },
        "metrics": {
            "data_sufficient": data_sufficient,
            "ops_index": ops_index,
            "ops_index_delta_month": None,
            "status_band": status_band,
            "axis_scores": axis_scores,
            "capacity": {
                "budget_minor": budget_minor,
                "used_minor": used_minor,
                "remaining_minor": remaining,
                "utilization_percent": utilization,
                "has_budget": has_budget,
            },
            "signals": (
                []
                if not data_sufficient
                else [
                    {"signal_id": "recovery", "trend": "UP" if recovery >= 70 else "STABLE"},
                    {"signal_id": "pressure", "trend": "DOWN" if pressure >= 60 else "STABLE"},
                    {"signal_id": "money", "trend": "STABLE"},
                ]
            ),
            "financial_segments": financial_segments,
            "trends_30d": {"recovery": [], "pressure": []},
            "score_drivers": (
                []
                if not data_sufficient
                else [
                    {"driver_id": "mood", "impact": recovery - 50},
                    {"driver_id": "money", "impact": 100 - pressure - 50},
                ]
            ),
            "gauges": (
                []
                if not data_sufficient
                else [
                    {"gauge_id": "stability", "percent": stability},
                    {"gauge_id": "recovery", "percent": recovery},
                ]
            ),
            "opportunity": {
                "priority_id": "recovery",
                "stress_impact": pressure if data_sufficient else 0,
                "capacity_boost": recovery if data_sufficient else 0,
            },
            "intelligence": {
                "pattern_id": "life_ops_baseline",
                "confidence_percent": (
                    0 if not data_sufficient else min(95, 40 + len(timeline) * 5)
                ),
            },
        },
    }
