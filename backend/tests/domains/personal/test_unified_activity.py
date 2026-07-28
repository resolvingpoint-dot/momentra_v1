"""Unit tests for unified personal activity helpers."""
from __future__ import annotations

from datetime import datetime, timezone

from app.domains.personal.activity.unified_service import (
    _build_insights,
    _build_snapshot,
    _matches_domain,
    _matches_kind,
    _range_bounds,
)


def test_snapshot_headline_and_domains():
    items = [
        {
            "amount_minor": 51700,
            "mood_label": "Calm",
            "life_domain": "Money",
            "occurred_at": "2026-07-27T10:00:00Z",
        },
        {
            "amount_minor": 0,
            "mood_label": None,
            "life_domain": "Lifestyle",
            "occurred_at": "2026-07-27T11:00:00Z",
        },
    ]
    snap = _build_snapshot(items)
    assert snap["headline"] == "You logged 2 moments today"
    assert snap["today_activity_count"] == 2
    assert snap["today_amount_minor"] == 51700
    assert snap["today_mood_label"] == "Calm"
    assert snap["today_domain_labels"] == ["Money", "Lifestyle"]


def test_snapshot_empty_copy():
    snap = _build_snapshot([])
    assert "life story" in snap["headline"].lower()


def test_insights_narrative():
    items = [
        {
            "title": "Laptop",
            "activity_type": "EXPENSE",
            "amount_minor": 8000000,
            "category_label": "Food",
            "mood_label": "Focused",
            "moment_type_code": "LIFE_OPERATIONS",
        },
        {
            "title": "Coffee",
            "activity_type": "EXPENSE",
            "amount_minor": 50000,
            "category_label": "Food",
            "moment_type_code": "LIFE_OPERATIONS",
        },
        {
            "title": "Kiran",
            "activity_type": "CONNECTION",
            "amount_minor": 0,
            "moment_type_code": "RELATIONSHIPS",
            "raw_payload": {"person_name": "Kiran"},
        },
    ]
    insights = _build_insights(items)
    kinds = {i["kind"]: i["value"] for i in insights}
    assert kinds["most_active"] == "Food"
    assert kinds["biggest_purchase"] == "Laptop"
    assert kinds["latest_mood"] == "Focused"
    assert kinds["strongest_relationship"] == "Kiran"


def test_domain_and_kind_filters():
    expense = {
        "moment_type_code": "LIFE_OPERATIONS",
        "activity_type": "EXPENSE",
        "domain_label": "My Money",
    }
    mood = {
        "moment_type_code": "LIFE_OPERATIONS",
        "activity_type": "REFLECTION",
        "domain_label": "Intelligence OS",
    }
    assert _matches_domain(expense, "money")
    assert not _matches_domain(mood, "money")
    assert _matches_kind(expense, "expense")
    assert _matches_kind(mood, "mood")
    assert not _matches_kind(expense, "mood")


def test_range_bounds_today():
    now = datetime(2026, 7, 27, 15, 0, tzinfo=timezone.utc)
    start, end = _range_bounds("today", now)
    assert start == datetime(2026, 7, 27, 0, 0, 0)
    assert end is None
