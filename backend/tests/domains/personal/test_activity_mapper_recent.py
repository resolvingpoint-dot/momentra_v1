"""Unit tests for canonical recent-activity projection fields."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.domains.personal.life_operations.activity_mapper import (
    _domain_label,
    _iso_utc,
    _mood_payload,
    _relative_time,
    _type_label,
    map_timeline_to_recent_item,
)


class _FakeCatalog:
    def label_for(self, collection_key: str, code: str) -> str:
        return {
            "FOOD": "Food",
            "DINING": "Dining",
        }.get(code.upper(), code)

    def get_flat(self, key: str, *, active_only: bool = False):
        return [
            {"code": "FOOD", "label": "Food", "icon": "restaurant", "color": "#AABBCC"},
            {"code": "DINING", "label": "Dining", "icon": "restaurant", "color": "#AABBCC"},
        ]

    def get(self, key: str, *, active_only: bool = False):
        if key == "currencies":
            return [{"code": "INR", "symbol": "₹", "minor_unit": 2}]
        return []

    def major_from_minor(self, amount_minor: int, currency_code: str):
        return amount_minor / 100


def _timeline(**kwargs):
    defaults = dict(
        quick_add_event_id=uuid4(),
        timeline_id=uuid4(),
        event_type="EXPENSE",
        moment_type_code="LIFE_OPERATIONS",
        display_title="Coffee",
        display_subtitle="Food · Planned",
        display_amount=None,
        event_occurred_at=datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
        impact_labels_json={"pressure_impact": "Planned"},
        is_editable=True,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _money(**kwargs):
    defaults = dict(
        amount_minor=24000,
        currency_code="INR",
        category_code="FOOD",
        subcategory_code="DINING",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_domain_and_type_labels():
    assert _domain_label("LIFE_OPERATIONS", "EXPENSE") == "My Money"
    assert _domain_label("LIFE_OPERATIONS", "REFLECTION") == "Intelligence OS"
    assert _domain_label("FUTURE_BUILDING", "MILESTONE") == "Build Momentum"
    assert _type_label("SHARED_EXPERIENCE") == "Shared Experience"
    assert _type_label("EXPENSE") == "Expense"


def test_mood_projection_only_from_explicit_labels():
    assert _mood_payload({"mood_state": "GOOD"}) == {
        "code": "GOOD",
        "label": "Good",
        "intensity": None,
        "source": "PROJECTION",
    }
    assert _mood_payload({"pressure_impact": "Planned"}) is None


def test_map_timeline_expense_canonical_fields():
    item = map_timeline_to_recent_item(
        _timeline(),
        money=_money(),
        catalog=_FakeCatalog(),
    )
    assert item["title"] == "Coffee"
    assert item["domain_type_subtitle"] == "My Money · Expense"
    assert item["category_label"] == "Food"
    assert item["subcategory_label"] == "Dining"
    assert item["primary_metric"]["display"].startswith("₹")
    assert item["mood"] is None
    assert item["impact_label"] == "Planned"
    assert item["editable"] is True


def test_map_timeline_reflection_mood():
    item = map_timeline_to_recent_item(
        _timeline(
            event_type="REFLECTION",
            display_title="Mood check-in",
            display_subtitle="Good",
            impact_labels_json={"mood_state": "GOOD"},
        ),
        money=None,
        catalog=_FakeCatalog(),
    )
    assert item["domain_type_subtitle"] == "Intelligence OS · Mood"
    assert item["mood_label"] == "Good"
    assert item["mood"]["code"] == "GOOD"
    assert item["primary_metric"] is None


def test_relative_time_thresholds():
    now = datetime(2026, 7, 27, 12, 0, 0, tzinfo=timezone.utc)
    assert _relative_time(now, now=now) == "Just now"
    assert _relative_time(now - timedelta(seconds=30), now=now) == "Just now"
    fifteen = datetime(2026, 7, 27, 11, 45, 0, tzinfo=timezone.utc)
    assert _relative_time(fifteen, now=now) == "15m ago"
    two_hours = datetime(2026, 7, 27, 10, 0, 0, tzinfo=timezone.utc)
    assert _relative_time(two_hours, now=now) == "2h ago"
    three_days = datetime(2026, 7, 24, 12, 0, 0, tzinfo=timezone.utc)
    assert _relative_time(three_days, now=now) == "3d ago"


def test_relative_time_clamps_future_to_just_now():
    now = datetime(2026, 7, 27, 12, 0, 0, tzinfo=timezone.utc)
    future = datetime(2026, 7, 27, 12, 15, 0, tzinfo=timezone.utc)
    assert _relative_time(future, now=now) == "Just now"
    # Naive timestamps are treated as UTC
    naive_future = datetime(2026, 7, 27, 12, 15, 0)
    assert _relative_time(naive_future, now=now) == "Just now"


def test_iso_utc_appends_z_for_naive():
    naive = datetime(2026, 7, 27, 11, 45, 0)
    assert _iso_utc(naive) == "2026-07-27T11:45:00Z"
    aware = datetime(2026, 7, 27, 11, 45, 0, tzinfo=timezone.utc)
    assert _iso_utc(aware) == "2026-07-27T11:45:00Z"


def test_map_timeline_occurred_at_has_z():
    when = datetime(2026, 7, 27, 11, 45, 0)  # naive UTC store shape
    item = map_timeline_to_recent_item(
        _timeline(event_occurred_at=when),
        money=_money(),
        catalog=_FakeCatalog(),
    )
    assert item["occurred_at"].endswith("Z")
    assert item["captured_at"].endswith("Z")
