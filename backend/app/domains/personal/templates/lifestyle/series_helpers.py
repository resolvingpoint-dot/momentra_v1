"""Time-series helpers for Lifestyle pulse and moments projections."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any

from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalMoneyEvents,
)

_JOY_TYPES = frozenset({"EXPERIENCE", "DISCOVERY", "EXPRESSION", "CREATIVE"})
_VITALITY_TYPES = frozenset({"WELLBEING", "EXPERIENCE", "ADJUST", "LIFESTYLE_ADJUST"})


def _event_day(when: datetime | date) -> date:
    if isinstance(when, datetime):
        return when.date()
    return when


def daily_counts(
    timeline: list[PersonalActivityTimeline],
    event_types: frozenset[str],
    *,
    days: int = 30,
) -> list[int]:
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=days - 1)
    counts = [0] * days
    for item in timeline:
        if (item.event_type or "").upper() not in event_types:
            continue
        day = _event_day(item.event_occurred_at)
        if day < start or day > today:
            continue
        index = (day - start).days
        counts[index] += 1
    return counts


def _counts_to_trend_points(counts: list[int]) -> list[dict[str, Any]]:
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=len(counts) - 1)
    return [
        {"date": (start + timedelta(days=index)).isoformat(), "value": value}
        for index, value in enumerate(counts)
    ]


def build_trends_30d(timeline: list[PersonalActivityTimeline]) -> dict[str, list[dict[str, Any]]]:
    return {
        "joy": _counts_to_trend_points(daily_counts(timeline, _JOY_TYPES)),
        "vitality": _counts_to_trend_points(daily_counts(timeline, _VITALITY_TYPES)),
    }


def build_money_journey_series(
    money_events: list[PersonalMoneyEvents],
    *,
    months: int = 6,
) -> list[dict[str, Any]]:
    today = datetime.now(timezone.utc).date()
    month_starts: list[tuple[str, date]] = []
    cursor = today.replace(day=1)
    for _ in range(months):
        month_starts.append((cursor.strftime("%b"), cursor))
        if cursor.month == 1:
            cursor = cursor.replace(year=cursor.year - 1, month=12)
        else:
            cursor = cursor.replace(month=cursor.month - 1)
    month_starts.reverse()
    by_month: dict[str, int] = defaultdict(int)
    category_totals: dict[str, int] = defaultdict(int)
    for ev in money_events:
        if (ev.direction or "").upper() != "DEBIT":
            continue
        minor = _money_minor(ev)
        if ev.event_date:
            by_month[ev.event_date.strftime("%Y-%m")] += minor
        cat = (ev.category_code or "lifestyle").lower()
        category_totals[cat] += minor
    series = []
    for label, month_start in month_starts:
        key = month_start.strftime("%Y-%m")
        series.append(
            {
                "category_id": "spend",
                "category_name": "Lifestyle Spend",
                "points": [{"date": key, "value_minor": by_month.get(key, 0)}],
            }
        )
    return series[:1] if series else []


def money_journey_highlights(
    money_events: list[PersonalMoneyEvents],
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_month: dict[str, int] = defaultdict(int)
    by_cat: dict[str, int] = defaultdict(int)
    for ev in money_events:
        if (ev.direction or "").upper() != "DEBIT":
            continue
        minor = _money_minor(ev)
        if ev.event_date:
            by_month[ev.event_date.strftime("%b %Y")] += minor
        cat = (ev.category_code or "lifestyle").replace("_", " ").title()
        by_cat[cat] += minor
    best_month = max(by_month.items(), key=lambda x: x[1], default=("—", 0))
    best_area = max(by_cat.items(), key=lambda x: x[1], default=("—", 0))
    return (
        {"label": best_month[0], "amount_minor": best_month[1]},
        {"label": best_area[0], "amount_minor": best_area[1]},
    )
