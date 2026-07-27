"""Map personal_activity_timeline rows to client recent-activity DTOs."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.domains.personal.models import PersonalActivityTimeline, PersonalMoneyEvents
from app.domains.reference_data.catalog import ReferenceCatalog, get_reference_catalog


def _relative_time(when: datetime) -> str:
    now = datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    delta = now - when
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "Just now"
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"


def _impact_direction(pressure: str | None) -> str | None:
    if not pressure:
        return None
    lower = pressure.strip().lower()
    if lower in {"essential", "pressure source", "unexpected"}:
        return "negative"
    if lower in {"planned"}:
        return "neutral"
    return "positive"


def _format_amount_label(
    catalog: ReferenceCatalog,
    amount_minor: int | None,
    currency_code: str | None,
    display_amount: Decimal | None,
) -> str | None:
    code = (currency_code or "INR").upper()
    if amount_minor is not None and amount_minor > 0:
        major = catalog.major_from_minor(int(amount_minor), code)
    elif display_amount is not None and display_amount > 0:
        major = display_amount
    else:
        return None
    for row in catalog.get("currencies", active_only=True):
        if row["code"] == code:
            symbol = str(row.get("symbol") or code)
            minor_unit = int(row.get("minor_unit", 2))
            if minor_unit == 0:
                return f"{symbol}{int(major)}"
            return f"{symbol}{major:,.{minor_unit}f}"
    return f"{code} {major}"


def _category_meta(
    catalog: ReferenceCatalog,
    category_code: str | None,
    subcategory_code: str | None = None,
) -> tuple[str | None, str | None]:
    """Return (icon, color) preferring subcategory, then parent category."""
    flat = catalog.get_flat("expense_categories", active_only=True)
    by_code = {str(row["code"]).upper(): row for row in flat}

    def _from_row(row: dict[str, Any] | None) -> tuple[str | None, str | None]:
        if not row:
            return None, None
        icon = row.get("icon")
        color = row.get("color")
        return (str(icon) if icon else None, str(color) if color else None)

    sub = by_code.get((subcategory_code or "").upper()) if subcategory_code else None
    parent = by_code.get((category_code or "").upper()) if category_code else None
    icon, color = _from_row(sub)
    if not icon:
        p_icon, p_color = _from_row(parent)
        icon = icon or p_icon
        color = color or p_color
    elif not color:
        _, p_color = _from_row(parent)
        color = p_color
    return icon, color


def _category_icon(
    catalog: ReferenceCatalog,
    category_code: str | None,
    subcategory_code: str | None = None,
) -> str | None:
    icon, _ = _category_meta(catalog, category_code, subcategory_code)
    return icon


def map_timeline_to_recent_item(
    item: PersonalActivityTimeline,
    *,
    money: PersonalMoneyEvents | None = None,
    catalog: ReferenceCatalog | None = None,
) -> dict[str, Any]:
    ref = catalog or get_reference_catalog()
    impact_labels = item.impact_labels_json or {}
    pressure = impact_labels.get("pressure_impact")
    if isinstance(pressure, str):
        impact_label = pressure
    else:
        impact_label = None

    amount_minor = int(money.amount_minor) if money and money.amount_minor else None
    currency_code = money.currency_code if money else None
    category_code = money.category_code if money else None
    subcategory_code = getattr(money, "subcategory_code", None) if money else None
    icon, color = _category_meta(ref, category_code, subcategory_code)

    return {
        "id": str(item.quick_add_event_id),
        "timeline_id": str(item.timeline_id),
        "activity_type": item.event_type,
        "title": item.display_title,
        "subtitle": item.display_subtitle or item.display_title,
        "amount_label": _format_amount_label(
            ref, amount_minor, currency_code, item.display_amount
        ),
        "occurred_at": item.event_occurred_at.isoformat(),
        "relative_time": _relative_time(item.event_occurred_at),
        "icon": icon,
        "color": color,
        "impact_label": impact_label,
        "impact_direction": _impact_direction(impact_label),
        "edit_event_type": item.event_type,
        "can_edit": item.is_editable,
        "can_delete": True,
        "category_code": category_code,
        "subcategory_code": subcategory_code,
        # Legacy aliases for activity screen DTOs
        "event_type": item.event_type,
        "category_label": item.event_type.replace("_", " ").title(),
        "detail_line": item.display_subtitle or item.display_title,
        "captured_at": item.event_occurred_at.isoformat(),
    }


def money_events_by_quick_add(
    money_events: list[PersonalMoneyEvents],
) -> dict[UUID, PersonalMoneyEvents]:
    return {e.quick_add_event_id: e for e in money_events}
