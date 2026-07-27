"""Shared memory tab projection from activity timeline."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentModel
from app.domains.personal.life_operations.activity_mapper import money_events_by_quick_add
from app.domains.personal.life_operations.pulse_mapper import _money_minor
from app.domains.personal.models import PersonalActivityTimeline, PersonalMoneyEvents

_ACTIVITY_TO_MEMORY = {
    "EXPENSE": "expense",
    "MONEY_EXPENSE": "expense",
    "RECOVERY": "recovery",
    "MOOD": "mood",
    "REFLECTION": "mood",
    "RHYTHM": "rhythm",
    "ATTENTION": "attention",
    "COMMITMENT": "attention",
}


def _memory_type(activity_type: str | None) -> str:
    if not activity_type:
        return "pattern"
    upper = activity_type.upper()
    return _ACTIVITY_TO_MEMORY.get(upper, "pattern")


def _importance(activity_type: str, amount_minor: int = 0) -> str:
    if amount_minor >= 500_000:
        return "high"
    if activity_type.upper() in {"RECOVERY", "MOOD"}:
        return "medium"
    if amount_minor >= 100_000:
        return "medium"
    return "low"


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


async def build_memory_projection(
    session: AsyncSession,
    user_id: UUID,
    moment: MomentModel | None,
    moment_type_code: str,
) -> dict[str, Any]:
    code = moment_type_code.upper().replace("-", "_")
    empty = {
        "moment_type_code": code,
        "status": "EMPTY",
        "memories": [],
        "patterns": [],
        "insights": [],
        "timeline": [],
    }
    if moment is None:
        return empty
    if moment.status != "ACTIVE":
        return {**empty, "status": "SETUP"}

    moment_id = moment.id
    timeline_result = await session.execute(
        select(PersonalActivityTimeline)
        .where(
            PersonalActivityTimeline.moment_id == moment_id,
            PersonalActivityTimeline.is_voided.is_(False),
        )
        .order_by(PersonalActivityTimeline.event_occurred_at.desc())
        .limit(200)
    )
    timeline = list(timeline_result.scalars().all())

    money_result = await session.execute(
        select(PersonalMoneyEvents).where(
            PersonalMoneyEvents.moment_id == moment_id,
            PersonalMoneyEvents.is_voided.is_(False),
        )
    )
    money_by_qa = money_events_by_quick_add(list(money_result.scalars().all()))

    memories: list[dict[str, Any]] = []
    for row in timeline[:50]:
        money = money_by_qa.get(row.quick_add_event_id)
        amount_minor = _money_minor(money) if money else 0
        mtype = _memory_type(row.event_type)
        event_ids = [str(row.quick_add_event_id)] if row.quick_add_event_id else []
        memories.append(
            {
                "id": str(row.timeline_id),
                "title": row.display_title or row.event_type or "Life signal",
                "subtitle": row.display_subtitle or row.display_title,
                "memory_type": mtype,
                "occurred_at": _iso(row.event_occurred_at),
                "source_event_ids": event_ids,
                "tags": list((row.impact_labels_json or {}).keys())[:3],
                "importance": _importance(row.event_type or "", amount_minor),
            }
        )

    patterns = _build_patterns(timeline, money_by_qa)
    insights = _build_insights(
        timeline, money_by_qa, recovery_count=_count_type(timeline, "RECOVERY")
    )
    grouped = _group_timeline(memories)

    return {
        "moment_type_code": code,
        "status": "ACTIVE",
        "memories": memories,
        "patterns": patterns,
        "insights": insights,
        "timeline": grouped,
    }


def _count_type(timeline: list[PersonalActivityTimeline], event_type: str) -> int:
    upper = event_type.upper()
    return sum(1 for t in timeline if (t.event_type or "").upper() == upper)


def _build_patterns(
    timeline: list[PersonalActivityTimeline],
    money_by_qa: dict[UUID, PersonalMoneyEvents],
) -> list[dict[str, Any]]:
    if len(timeline) < 3:
        return []

    by_type: dict[str, int] = defaultdict(int)
    by_category: dict[str, int] = defaultdict(int)
    for row in timeline:
        by_type[_memory_type(row.event_type)] += 1
        money = money_by_qa.get(row.quick_add_event_id)
        if money and money.category_code:
            by_category[money.category_code] += 1

    patterns: list[dict[str, Any]] = []
    if by_type:
        top_type, count = max(by_type.items(), key=lambda x: x[1])
        patterns.append(
            {
                "id": str(uuid4()),
                "title": f"Mostly {top_type} signals",
                "subtitle": f"{count} of your recent logs are {top_type} related.",
                "occurrence_count": count,
                "tags": [top_type],
            }
        )
    if by_category:
        top_cat, count = max(by_category.items(), key=lambda x: x[1])
        if count >= 2:
            patterns.append(
                {
                    "id": str(uuid4()),
                    "title": f"Top spend: {top_cat}",
                    "subtitle": f"{count} expenses in {top_cat} recently.",
                    "occurrence_count": count,
                    "tags": ["expense", top_cat],
                }
            )
    return patterns


def _build_insights(
    timeline: list[PersonalActivityTimeline],
    money_by_qa: dict[UUID, PersonalMoneyEvents],
    *,
    recovery_count: int,
) -> list[dict[str, Any]]:
    if len(timeline) < 3:
        return []

    insights: list[dict[str, Any]] = []

    expense_hours: list[int] = []
    expense_timeline: list[PersonalActivityTimeline] = []
    for row in timeline:
        if (row.event_type or "").upper() not in {"EXPENSE", "MONEY_EXPENSE"}:
            continue
        if row.quick_add_event_id not in money_by_qa:
            continue
        expense_timeline.append(row)
        when = row.event_occurred_at
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        expense_hours.append(when.hour)

    if len(expense_hours) >= 5:
        evening = sum(1 for h in expense_hours if h >= 19)
        ratio = evening / len(expense_hours)
        if ratio >= 0.5:
            confidence = round(min(0.95, 0.5 + ratio * 0.4), 2)
            insights.append(
                {
                    "id": str(uuid4()),
                    "title": "Most expenses occurred after 7 PM",
                    "subtitle": f"{int(ratio * 100)}% of recent spending is in the evening.",
                    "confidence": confidence,
                    "insight_type": "spending_time",
                    "tags": ["expense", "evening"],
                }
            )

    if recovery_count >= 3:
        streak = _recovery_streak_days(timeline)
        if streak >= 3:
            confidence = round(min(0.95, 0.55 + streak * 0.1), 2)
            insights.append(
                {
                    "id": str(uuid4()),
                    "title": f"Recovery logged {streak} days in a row",
                    "subtitle": "Consistency in recovery supports operating stability.",
                    "confidence": confidence,
                    "insight_type": "recovery_streak",
                    "tags": ["recovery"],
                }
            )

    week_spend, prev_week_spend = _week_spend_totals(expense_timeline, money_by_qa)
    if prev_week_spend > 0 and week_spend > 0:
        delta = int(round((week_spend - prev_week_spend) / prev_week_spend * 100))
        if abs(delta) >= 15:
            direction = "up" if delta > 0 else "down"
            insights.append(
                {
                    "id": str(uuid4()),
                    "title": f"Spending {direction} {abs(delta)}% vs last week",
                    "subtitle": "Week-over-week money movement from your activity log.",
                    "confidence": round(min(0.9, 0.6 + abs(delta) / 200), 2),
                    "insight_type": "spending_trend",
                    "tags": ["expense", "week"],
                }
            )

    return insights


def _recovery_streak_days(timeline: list[PersonalActivityTimeline]) -> int:
    days: set[datetime.date] = set()
    for row in timeline:
        if (row.event_type or "").upper() != "RECOVERY":
            continue
        when = row.event_occurred_at
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        days.add(when.date())
    if not days:
        return 0
    sorted_days = sorted(days, reverse=True)
    streak = 1
    for i in range(1, len(sorted_days)):
        if (sorted_days[i - 1] - sorted_days[i]).days == 1:
            streak += 1
        else:
            break
    return streak


def _week_spend_totals(
    expense_timeline: list[PersonalActivityTimeline],
    money_by_qa: dict[UUID, PersonalMoneyEvents],
) -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    last_week_start = week_start - timedelta(days=7)

    def naive(dt: datetime) -> datetime:
        return dt.replace(tzinfo=None) if dt.tzinfo else dt

    this_week = 0
    prev_week = 0
    for row in expense_timeline:
        money = money_by_qa.get(row.quick_add_event_id)
        if not money or money.direction != "DEBIT":
            continue
        when = row.event_occurred_at
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        amt = _money_minor(money)
        if naive(when) >= naive(week_start):
            this_week += amt
        elif naive(last_week_start) <= naive(when) < naive(week_start):
            prev_week += amt
    return this_week, prev_week


def _group_timeline(memories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_day: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for mem in memories:
        occurred = mem.get("occurred_at") or ""
        day_key = occurred[:10] if len(occurred) >= 10 else "unknown"
        by_day[day_key].append(mem)

    result: list[dict[str, Any]] = []
    for day_key in sorted(by_day.keys(), reverse=True):
        try:
            dt = datetime.strptime(day_key, "%Y-%m-%d")
            label = dt.strftime("%A, %b %d")
        except ValueError:
            label = day_key
        result.append(
            {
                "period_label": label,
                "period_start": f"{day_key}T00:00:00+00:00" if day_key != "unknown" else None,
                "memories": by_day[day_key],
            }
        )
    return result[:14]
