"""Unified personal activity timeline across all personal moment types."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.life_operations.activity_mapper import (
    _domain_label,
    map_timeline_to_recent_item,
)
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalMoneyEvents,
    PersonalQuickAddEvents,
)
from app.domains.personal.templates.activity.mapper import map_timeline_to_activity_item
from app.domains.reference_data.catalog import get_reference_catalog

_PERSONAL_TYPES = (
    "LIFE_OPERATIONS",
    "LIFESTYLE",
    "FUTURE_BUILDING",
    "RELATIONSHIPS",
)

_DOMAIN_FILTER: dict[str, frozenset[str]] = {
    "money": frozenset({"LIFE_OPERATIONS"}),
    "lifestyle": frozenset({"LIFESTYLE"}),
    "relationships": frozenset({"RELATIONSHIPS"}),
    "future": frozenset({"FUTURE_BUILDING"}),
}

_KIND_EVENT_TYPES: dict[str, frozenset[str]] = {
    "expense": frozenset({"EXPENSE"}),
    "experience": frozenset(
        {"EXPERIENCE", "SHARED_EXPERIENCE", "WELLBEING", "ENERGY", "HABIT", "RHYTHM", "RECOVERY"}
    ),
    "mood": frozenset({"REFLECTION"}),
    "learning": frozenset({"LEARNING"}),
    "investment": frozenset({"SAVINGS", "CONTRIBUTION", "INCOME"}),
    "milestone": frozenset({"MILESTONE", "PROGRESS", "OPPORTUNITY", "COMMITMENT"}),
}

_MONEY_TYPES = frozenset({"EXPENSE", "CONTRIBUTION", "SAVINGS", "INCOME", "TRANSFER"})

# Chip-facing labels for Life OS
_LIFE_DOMAIN_LABEL: dict[str, str] = {
    "LIFE_OPERATIONS": "Money",
    "LIFESTYLE": "Lifestyle",
    "FUTURE_BUILDING": "Future",
    "RELATIONSHIPS": "Relationships",
}


def _as_utc(when: datetime) -> datetime:
    if when.tzinfo is None:
        return when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc)


def _start_of_local_day(now: datetime) -> datetime:
    """UTC-naive store: treat event_occurred_at as UTC-naive."""
    current = _as_utc(now)
    return current.replace(hour=0, minute=0, second=0, microsecond=0)


def _range_bounds(range_key: str, now: datetime) -> tuple[datetime | None, datetime | None]:
    key = (range_key or "all").strip().lower()
    start_today = _start_of_local_day(now).replace(tzinfo=None)
    if key == "today":
        return start_today, None
    if key == "yesterday":
        return start_today - timedelta(days=1), start_today
    if key == "week":
        return start_today - timedelta(days=7), None
    if key == "month":
        return start_today - timedelta(days=30), None
    if key == "year":
        return start_today - timedelta(days=365), None
    return None, None


def _item_search_blob(item: dict[str, Any]) -> str:
    parts = [
        item.get("title"),
        item.get("subtitle"),
        item.get("category_label"),
        item.get("subcategory_label"),
        item.get("mood_label"),
        item.get("impact_label"),
        item.get("type_label"),
        item.get("domain_label"),
        item.get("amount_label"),
        str(item.get("amount_minor") or ""),
    ]
    mood = item.get("mood")
    if isinstance(mood, dict):
        parts.append(mood.get("label"))
        parts.append(mood.get("code"))
    payload = item.get("raw_payload") or {}
    if isinstance(payload, dict):
        for key in ("notes", "note", "merchant", "person_name", "relationship_name", "tags", "with_whom"):
            val = payload.get(key)
            if isinstance(val, str):
                parts.append(val)
            elif isinstance(val, list):
                parts.extend(str(v) for v in val)
    return " ".join(str(p) for p in parts if p).lower()


def _matches_domain(item: dict[str, Any], domain: str) -> bool:
    key = (domain or "all").strip().lower()
    if key in {"", "all"}:
        return True
    allowed = _DOMAIN_FILTER.get(key)
    if not allowed:
        return True
    mtc = str(item.get("moment_type_code") or "").upper()
    if key == "money":
        # Money chip: LO money events, or rows labeled My Money
        event = str(item.get("activity_type") or item.get("event_type") or "").upper()
        if mtc == "LIFE_OPERATIONS" and event in _MONEY_TYPES:
            return True
        label = str(item.get("domain_label") or "")
        return "Money" in label or label == "My Money"
    return mtc in allowed


def _matches_kind(item: dict[str, Any], kind: str) -> bool:
    key = (kind or "all").strip().lower()
    if key in {"", "all"}:
        return True
    allowed = _KIND_EVENT_TYPES.get(key)
    if not allowed:
        return True
    event = str(item.get("activity_type") or item.get("event_type") or "").upper()
    return event in allowed


def _life_domain_chip_label(moment_type_code: str, event_type: str) -> str:
    mtc = (moment_type_code or "").upper()
    event = (event_type or "").upper()
    if mtc == "LIFE_OPERATIONS" and event in _MONEY_TYPES:
        return "Money"
    if mtc == "LIFE_OPERATIONS":
        return "Money"  # Intelligence OS still surfaces under personal money OS for chips
    return _LIFE_DOMAIN_LABEL.get(mtc, _domain_label(mtc, event))


def _enrich_item(base: dict[str, Any], recent: dict[str, Any]) -> dict[str, Any]:
    return {
        **base,
        "occurred_at": recent.get("occurred_at") or base.get("occurred_at"),
        "domain_label": recent.get("domain_label"),
        "type_label": recent.get("type_label"),
        "domain_type_subtitle": recent.get("domain_type_subtitle"),
        "mood": recent.get("mood"),
        "mood_label": recent.get("mood_label") or base.get("mood_label"),
        "primary_metric": recent.get("primary_metric"),
        "chips": recent.get("chips"),
        "editable": recent.get("editable", base.get("can_edit", True)),
        "life_domain": _life_domain_chip_label(
            str(base.get("moment_type_code") or ""),
            str(base.get("activity_type") or ""),
        ),
    }


def _build_snapshot(today_items: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(today_items)
    amount = sum(int(i.get("amount_minor") or 0) for i in today_items)
    mood_label = None
    for item in today_items:
        label = (item.get("mood_label") or "").strip()
        if not label and isinstance(item.get("mood"), dict):
            label = str(item["mood"].get("label") or "").strip()
        if label:
            mood_label = label
            break
    domains: list[str] = []
    seen: set[str] = set()
    for item in today_items:
        d = (item.get("life_domain") or item.get("domain_label") or "").strip()
        if d and d not in seen:
            seen.add(d)
            domains.append(d)
    if count == 0:
        headline = "Start logging moments and your life story will appear here."
    elif count == 1:
        headline = "You logged 1 moment today"
    else:
        headline = f"You logged {count} moments today"
    return {
        "headline": headline,
        "today_activity_count": count,
        "today_amount_minor": amount,
        "today_mood_label": mood_label,
        "today_domain_labels": domains,
    }


def _build_insights(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []
    if not items:
        return insights

    # Most active — top category or type label by count
    cat_counter: Counter[str] = Counter()
    for item in items:
        label = (item.get("category_label") or item.get("type_label") or "").strip()
        if label:
            cat_counter[label] += 1
    if cat_counter:
        top_label, _ = cat_counter.most_common(1)[0]
        insights.append(
            {
                "id": "most_active",
                "kind": "most_active",
                "title": "Most active",
                "value": top_label,
            }
        )

    # Biggest purchase — highest money title
    money_rows = [
        i
        for i in items
        if int(i.get("amount_minor") or 0) > 0
        and str(i.get("activity_type") or "").upper() in _MONEY_TYPES
    ]
    if money_rows:
        biggest = max(money_rows, key=lambda i: int(i.get("amount_minor") or 0))
        title = (biggest.get("title") or "").strip()
        if title:
            insights.append(
                {
                    "id": "biggest_purchase",
                    "kind": "biggest_purchase",
                    "title": "Biggest purchase",
                    "value": title,
                }
            )

    # Latest mood
    for item in items:
        label = (item.get("mood_label") or "").strip()
        if not label and isinstance(item.get("mood"), dict):
            label = str(item["mood"].get("label") or "").strip()
        if label:
            insights.append(
                {
                    "id": "latest_mood",
                    "kind": "latest_mood",
                    "title": "Latest mood",
                    "value": label,
                }
            )
            break

    # Strongest relationship — person from payload / title on relationship rows
    for item in items:
        if str(item.get("moment_type_code") or "").upper() != "RELATIONSHIPS":
            continue
        payload = item.get("raw_payload") or {}
        person = None
        if isinstance(payload, dict):
            for key in ("person_name", "relationship_name", "with_whom", "name"):
                raw = payload.get(key)
                if isinstance(raw, str) and raw.strip():
                    person = raw.strip()
                    break
        if not person:
            person = (item.get("title") or "").strip() or None
        if person:
            insights.append(
                {
                    "id": "strongest_relationship",
                    "kind": "strongest_relationship",
                    "title": "Strongest relationship",
                    "value": person,
                }
            )
            break

    return insights


class UnifiedPersonalActivityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_activity(
        self,
        user_id: UUID,
        *,
        range: str = "all",
        domain: str = "all",
        kind: str = "all",
        q: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        current = _as_utc(now or datetime.now(timezone.utc))
        limit = max(1, min(int(limit or 50), 100))

        # Fetch a generous window for snapshot/insights; filter then paginate.
        fetch_limit = 200
        timeline_result = await self.session.execute(
            select(PersonalActivityTimeline)
            .where(
                PersonalActivityTimeline.user_id == user_id,
                PersonalActivityTimeline.moment_type_code.in_(_PERSONAL_TYPES),
                PersonalActivityTimeline.is_voided.is_(False),
            )
            .order_by(PersonalActivityTimeline.event_occurred_at.desc())
            .limit(fetch_limit)
        )
        timeline = list(timeline_result.scalars().all())
        if not timeline:
            return {
                "snapshot": _build_snapshot([]),
                "insights": [],
                "items": [],
                "next_cursor": None,
            }

        qa_ids = [row.quick_add_event_id for row in timeline]
        events_result = await self.session.execute(
            select(PersonalQuickAddEvents).where(
                PersonalQuickAddEvents.quick_add_event_id.in_(qa_ids),
                PersonalQuickAddEvents.is_voided.is_(False),
            )
        )
        events_by_id = {e.quick_add_event_id: e for e in events_result.scalars().all()}

        money_result = await self.session.execute(
            select(PersonalMoneyEvents).where(
                PersonalMoneyEvents.user_id == user_id,
                PersonalMoneyEvents.quick_add_event_id.in_(qa_ids),
                PersonalMoneyEvents.is_voided.is_(False),
            )
        )
        money_by_qa = {m.quick_add_event_id: m for m in money_result.scalars().all()}
        catalog = get_reference_catalog()

        items: list[dict[str, Any]] = []
        for row in timeline:
            money = money_by_qa.get(row.quick_add_event_id)
            event = events_by_id.get(row.quick_add_event_id)
            base = map_timeline_to_activity_item(row, event=event, money=money, catalog=catalog)
            recent = map_timeline_to_recent_item(row, money=money, catalog=catalog)
            items.append(_enrich_item(base, recent))

        start_today = _start_of_local_day(current).replace(tzinfo=None)
        today_items = [
            i
            for i in items
            if self._parse_occurred(i.get("occurred_at")) is not None
            and self._parse_occurred(i.get("occurred_at")) >= start_today  # type: ignore[operator]
        ]
        snapshot = _build_snapshot(today_items)

        range_start, range_end = _range_bounds(range, current)
        filtered = items
        if range_start is not None or range_end is not None:
            next_filtered: list[dict[str, Any]] = []
            for item in filtered:
                when = self._parse_occurred(item.get("occurred_at"))
                if when is None:
                    continue
                if range_start is not None and when < range_start:
                    continue
                if range_end is not None and when >= range_end:
                    continue
                next_filtered.append(item)
            filtered = next_filtered

        filtered = [i for i in filtered if _matches_domain(i, domain)]
        filtered = [i for i in filtered if _matches_kind(i, kind)]

        query = (q or "").strip().lower()
        if query:
            filtered = [i for i in filtered if query in _item_search_blob(i)]

        # Insights from filtered window (prefer last 30d of filtered if large)
        insights = _build_insights(filtered[:100])

        if cursor:
            cursor_dt = self._parse_occurred(cursor)
            if cursor_dt is not None:
                filtered = [
                    i
                    for i in filtered
                    if (self._parse_occurred(i.get("occurred_at")) or datetime.min)
                    < cursor_dt
                ]

        page = filtered[:limit]
        next_cursor = None
        if len(filtered) > limit and page:
            next_cursor = page[-1].get("occurred_at")

        return {
            "snapshot": snapshot,
            "insights": insights,
            "items": page,
            "next_cursor": next_cursor,
        }

    @staticmethod
    def _parse_occurred(raw: Any) -> datetime | None:
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return raw.replace(tzinfo=None) if raw.tzinfo else raw
        text = str(raw).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
        return dt.replace(tzinfo=None) if dt.tzinfo else dt
