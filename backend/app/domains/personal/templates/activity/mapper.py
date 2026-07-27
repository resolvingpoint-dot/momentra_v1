"""Map timeline rows to template activity list items."""
from __future__ import annotations

from typing import Any

from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalMoneyEvents,
    PersonalQuickAddEvents,
)
from app.domains.reference_data.catalog import ReferenceCatalog, get_reference_catalog


def map_timeline_to_activity_item(
    item: PersonalActivityTimeline,
    *,
    event: PersonalQuickAddEvents | None = None,
    money: PersonalMoneyEvents | None = None,
    catalog: ReferenceCatalog | None = None,
) -> dict[str, Any]:
    ref = catalog or get_reference_catalog()
    base = map_timeline_to_recent_item(item, money=money, catalog=ref)
    amount_minor = int(money.amount_minor) if money and money.amount_minor else 0
    currency = money.currency_code if money else "INR"
    category_code = money.category_code if money else None
    subcategory_code = getattr(money, "subcategory_code", None) if money else None
    payload = (event.raw_payload if event else None) or {}
    return {
        "id": str(item.quick_add_event_id),
        "timeline_id": str(item.timeline_id),
        "moment_id": str(item.moment_id),
        "moment_type_code": item.moment_type_code,
        "activity_type": item.event_type,
        "title": item.display_title,
        "subtitle": item.display_subtitle or item.display_title,
        "occurred_at": item.event_occurred_at.isoformat(),
        "amount_minor": amount_minor,
        "currency_code": currency,
        "category_code": category_code,
        "subcategory_code": subcategory_code,
        "icon": base.get("icon"),
        "impact_label": base.get("impact_label"),
        "source": "quick_add",
        "relative_time": base.get("relative_time"),
        "edit_event_type": item.event_type,
        "can_edit": item.is_editable,
        "can_delete": True,
        "raw_payload": payload if event else {},
    }


def map_money_lookup(
    money_events: list[PersonalMoneyEvents],
) -> dict:
    return money_events_by_quick_add(money_events)
