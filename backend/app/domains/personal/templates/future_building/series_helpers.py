"""Time-series helpers for Future Building pulse and moments projections."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any

from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalMoneyEvents,
)

_LEARNING_TYPES = frozenset({"LEARNING"})
_EXECUTION_TYPES = frozenset({"PROGRESS", "CONTRIBUTION", "PIVOT"})
_PROGRESS_TYPES = frozenset({"MILESTONE", "OPPORTUNITY"})


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
    """Return oldest-to-newest daily counts for the last ``days`` days."""
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
        "learning": _counts_to_trend_points(daily_counts(timeline, _LEARNING_TYPES)),
        "execution": _counts_to_trend_points(daily_counts(timeline, _EXECUTION_TYPES)),
        "progress": _counts_to_trend_points(daily_counts(timeline, _PROGRESS_TYPES)),
    }


def build_money_journey_series(
    money_events: list[PersonalMoneyEvents],
    *,
    months: int = 6,
) -> list[dict[str, Any]]:
    """Six-month investment series grouped by category (debit contributions only)."""
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
        cat = (ev.category_code or "investment").lower()
        category_totals[cat] += minor

    if not category_totals:
        return []

    series: list[dict[str, Any]] = []
    for cat, _total in sorted(category_totals.items(), key=lambda x: -x[1])[:3]:
        points = []
        for _label, month_start in month_starts:
            key = month_start.strftime("%Y-%m")
            points.append(
                {
                    "date": month_start.isoformat(),
                    "value_minor": by_month.get(key, 0),
                }
            )
        series.append(
            {
                "category_id": cat,
                "category_name": cat.replace("_", " ").title(),
                "points": points,
            }
        )
    return series


def money_journey_highlights(
    money_events: list[PersonalMoneyEvents],
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_month: dict[str, int] = defaultdict(int)
    category_totals: dict[str, int] = defaultdict(int)
    for ev in money_events:
        if (ev.direction or "").upper() != "DEBIT":
            continue
        minor = _money_minor(ev)
        if ev.event_date:
            by_month[ev.event_date.strftime("%Y-%m")] += minor
        cat = (ev.category_code or "investment").lower()
        category_totals[cat] += minor

    if by_month:
        highest_key, highest_val = max(by_month.items(), key=lambda x: x[1])
        highest_month = {"label": highest_key, "amount_minor": highest_val}
    else:
        highest_month = {"label": "Recent", "amount_minor": 0}

    if category_totals:
        best_cat, best_val = max(category_totals.items(), key=lambda x: x[1])
        highest_area = {
            "label": best_cat.replace("_", " ").title(),
            "amount_minor": best_val,
        }
    else:
        highest_area = {"label": "Learning", "amount_minor": 0}

    return highest_month, highest_area
