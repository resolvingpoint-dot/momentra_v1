"""Map personal_activity_timeline rows to client recent-activity DTOs."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.domains.personal.models import PersonalActivityTimeline, PersonalMoneyEvents
from app.domains.reference_data.catalog import ReferenceCatalog, get_reference_catalog

_MONEY_EVENT_TYPES = frozenset(
    {"EXPENSE", "CONTRIBUTION", "SAVINGS", "INCOME", "TRANSFER"}
)

_DOMAIN_BY_MOMENT: dict[str, str] = {
    "LIFE_OPERATIONS": "Intelligence OS",
    "LIFESTYLE": "Lifestyle",
    "FUTURE_BUILDING": "Build Momentum",
    "RELATIONSHIPS": "Relationships",
}

_TYPE_LABELS: dict[str, str] = {
    "EXPENSE": "Expense",
    "CONTRIBUTION": "Contribution",
    "SAVINGS": "Savings",
    "INCOME": "Income",
    "TRANSFER": "Transfer",
    "REFLECTION": "Mood",
    "RECOVERY": "Recovery",
    "RHYTHM": "Rhythm",
    "COMMITMENT": "Commitment",
    "LEARNING": "Learning",
    "PROGRESS": "Progress",
    "MILESTONE": "Milestone",
    "OPPORTUNITY": "Opportunity",
    "CONNECTION": "Connection",
    "SHARED_EXPERIENCE": "Shared Experience",
    "SUPPORT": "Support",
    "ADJUST": "Adjustment",
    "WELLBEING": "Wellbeing",
    "EXPERIENCE": "Experience",
    "ENERGY": "Energy",
    "HABIT": "Habit",
}


def _as_utc(when: datetime) -> datetime:
    if when.tzinfo is None:
        return when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc)


def _iso_utc(when: datetime) -> str:
    """Emit unambiguous UTC ISO-8601 (always with Z)."""
    utc = _as_utc(when)
    # isoformat on aware UTC uses +00:00; normalize to Z for clients.
    return utc.isoformat().replace("+00:00", "Z")


def _relative_time(when: datetime, *, now: datetime | None = None) -> str:
    current = _as_utc(now or datetime.now(timezone.utc))
    event = _as_utc(when)
    seconds = (current - event).total_seconds()
    if seconds < 0:
        seconds = 0.0
    minutes = int(seconds // 60)
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


def _catalog_label(catalog: ReferenceCatalog, code: str | None) -> str | None:
    if not code:
        return None
    label = catalog.label_for("expense_categories", str(code))
    return label if label else None


def _humanize_code(raw: str) -> str:
    return raw.strip().replace("_", " ").title()


def _type_label(event_type: str | None) -> str:
    key = (event_type or "").strip().upper()
    if not key:
        return "Activity"
    return _TYPE_LABELS.get(key, _humanize_code(key))


def _domain_label(moment_type_code: str | None, event_type: str | None) -> str:
    moment = (moment_type_code or "").strip().upper()
    event = (event_type or "").strip().upper()
    if moment == "LIFE_OPERATIONS" and event in _MONEY_EVENT_TYPES:
        return "My Money"
    if moment in _DOMAIN_BY_MOMENT:
        return _DOMAIN_BY_MOMENT[moment]
    if moment:
        return _humanize_code(moment)
    return "Personal"


_MOOD_EMOJI: dict[str, str] = {
    "GREAT": "😄",
    "GOOD": "🙂",
    "OKAY": "😐",
    "LOW": "😔",
    "STRESSED": "😣",
    "GRATEFUL": "🙏",
    "ANXIOUS": "😟",
    "FOCUSED": "🎯",
    "TIRED": "😴",
    "MOTIVATED": "💪",
}

# Common quick-add payload keys that carry a place/venue or a companion, across
# the different personal templates (life ops, lifestyle, relationships). Only
# ever surfaced when present — never fabricated.
_PLACE_KEYS = ("place", "location_label", "location", "venue", "location_context", "merchant")
_WITH_WHOM_KEYS = ("with_whom", "person_name", "relationship_name", "companion", "attendees", "guest_name")


def _mood_code(impact_labels: dict[str, Any]) -> str | None:
    raw = impact_labels.get("mood_state") or impact_labels.get("feeling_state")
    if not isinstance(raw, str) or not raw.strip():
        return None
    return raw.strip().upper()


def _mood_label_from_code(code: str | None) -> str | None:
    if not code:
        return None
    return _humanize_code(code)


def _mood_emoji_from_code(code: str | None) -> str | None:
    if not code:
        return None
    return _MOOD_EMOJI.get(code.strip().upper())


def _mood_payload(impact_labels: dict[str, Any]) -> dict[str, Any] | None:
    code = _mood_code(impact_labels)
    if not code:
        return None
    return {
        "code": code,
        "label": _mood_label_from_code(code),
        "emoji": _mood_emoji_from_code(code),
        "intensity": None,
        "source": "PROJECTION",
    }


def _first_string(impact_labels: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    """Return the first present, non-empty string (or joined list) value for keys."""
    for key in keys:
        value = impact_labels.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list) and value:
            joined = ", ".join(str(v).strip() for v in value if str(v).strip())
            if joined:
                return joined
    return None


def _place_label(impact_labels: dict[str, Any]) -> str | None:
    return _first_string(impact_labels, _PLACE_KEYS)


def _with_whom_label(impact_labels: dict[str, Any]) -> str | None:
    return _first_string(impact_labels, _WITH_WHOM_KEYS)


def _primary_metric(
    *,
    amount_label: str | None,
    amount_minor: int | None,
    currency_code: str | None,
    impact_labels: dict[str, Any],
    event_type: str,
) -> dict[str, Any] | None:
    if amount_label:
        metric: dict[str, Any] = {
            "kind": "MONEY",
            "display": amount_label,
        }
        if amount_minor is not None and amount_minor > 0:
            metric["amount_minor"] = amount_minor
        if currency_code:
            metric["currency_code"] = currency_code
        return metric

    event = event_type.upper()
    if event == "RECOVERY":
        intensity = impact_labels.get("recovery_intensity") or impact_labels.get(
            "energy_impact"
        )
        if isinstance(intensity, str) and intensity.strip():
            return {
                "kind": "RECOVERY",
                "display": _humanize_code(intensity),
            }
    if event in {"LEARNING", "PROGRESS", "MILESTONE"}:
        relevance = impact_labels.get("relevance_level") or impact_labels.get(
            "impact_level"
        )
        if isinstance(relevance, str) and relevance.strip():
            return {
                "kind": "IMPACT",
                "display": _humanize_code(relevance),
            }
    if event in {"CONNECTION", "SHARED_EXPERIENCE", "SUPPORT"}:
        quality = (
            impact_labels.get("connection_quality")
            or impact_labels.get("support_type")
            or impact_labels.get("experience_type")
        )
        if isinstance(quality, str) and quality.strip():
            return {
                "kind": "QUALITY",
                "display": _humanize_code(quality),
            }
    return None


def _chips(
    *,
    impact_label: str | None,
    category_label: str | None,
    subcategory_label: str | None,
) -> list[dict[str, str]]:
    """Status chips only — never repeat type/category as a second Expense line."""
    chips: list[dict[str, str]] = []
    if impact_label:
        chips.append(
            {
                "code": impact_label.strip().upper().replace(" ", "_"),
                "label": impact_label.strip(),
            }
        )
    return chips[:2]


def map_timeline_to_recent_item(
    item: PersonalActivityTimeline,
    *,
    money: PersonalMoneyEvents | None = None,
    catalog: ReferenceCatalog | None = None,
) -> dict[str, Any]:
    ref = catalog or get_reference_catalog()
    impact_labels = item.impact_labels_json or {}
    if not isinstance(impact_labels, dict):
        impact_labels = {}

    pressure = impact_labels.get("pressure_impact")
    impact_label = pressure if isinstance(pressure, str) else None

    amount_minor = int(money.amount_minor) if money and money.amount_minor else None
    currency_code = money.currency_code if money else None
    category_code = money.category_code if money else None
    subcategory_code = getattr(money, "subcategory_code", None) if money else None
    icon, color = _category_meta(ref, category_code, subcategory_code)
    category_label = _catalog_label(ref, category_code)
    subcategory_label = _catalog_label(ref, subcategory_code)

    mood = _mood_payload(impact_labels)
    mood_label = mood["label"] if mood else None
    mood_emoji = mood["emoji"] if mood else None
    place = _place_label(impact_labels)
    with_whom = _with_whom_label(impact_labels)
    amount_label = _format_amount_label(
        ref, amount_minor, currency_code, item.display_amount
    )

    domain = (item.moment_type_code or "").strip().upper() or None
    domain_label = _domain_label(item.moment_type_code, item.event_type)
    type_label = _type_label(item.event_type)
    domain_type_subtitle = f"{domain_label} · {type_label}"
    primary_metric = _primary_metric(
        amount_label=amount_label,
        amount_minor=amount_minor,
        currency_code=currency_code,
        impact_labels=impact_labels,
        event_type=item.event_type,
    )
    chips = _chips(
        impact_label=impact_label,
        category_label=category_label,
        subcategory_label=subcategory_label,
    )

    return {
        "id": str(item.quick_add_event_id),
        "timeline_id": str(item.timeline_id),
        "activity_type": item.event_type,
        "title": item.display_title,
        "subtitle": item.display_subtitle or item.display_title,
        "amount_label": amount_label,
        "occurred_at": _iso_utc(item.event_occurred_at),
        "relative_time": _relative_time(item.event_occurred_at),
        "icon": icon,
        "color": color,
        "impact_label": impact_label,
        "impact_direction": _impact_direction(impact_label),
        "edit_event_type": item.event_type,
        "can_edit": item.is_editable,
        "can_delete": True,
        "editable": bool(item.is_editable),
        "category_code": category_code,
        "subcategory_code": subcategory_code,
        "category_label": category_label,
        "subcategory_label": subcategory_label,
        "mood_label": mood_label,
        "mood_emoji": mood_emoji,
        "mood": mood,
        "place": place,
        "with_whom": with_whom,
        "domain": domain,
        "domain_label": domain_label,
        "type_label": type_label,
        "domain_type_subtitle": domain_type_subtitle,
        "primary_metric": primary_metric,
        "chips": chips,
        # Full projection payload — lets clients/search surface any evidence-backed
        # field (place, with_whom, notes, ...) without widening this signature again.
        "raw_payload": impact_labels,
        # Legacy aliases for activity screen DTOs
        "event_type": item.event_type,
        "detail_line": item.display_subtitle or item.display_title,
        "captured_at": _iso_utc(item.event_occurred_at),
    }


def money_events_by_quick_add(
    money_events: list[PersonalMoneyEvents],
) -> dict[UUID, PersonalMoneyEvents]:
    return {e.quick_add_event_id: e for e in money_events}
