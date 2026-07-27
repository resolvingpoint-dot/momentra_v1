"""Unit tests for Life Ops quick-add handler mappings."""
from __future__ import annotations

from app.domains.personal.life_operations.quick_add.handlers.mappings import (
    money_direction,
    parse_amount,
    pressure_score,
)
from app.domains.personal.life_operations.quick_add.handlers.registry import (
    get_handler,
)


def test_money_direction():
    assert money_direction("EXPENSE") == "DEBIT"
    assert money_direction("INCOME") == "CREDIT"
    assert money_direction("TRANSFER") == "NEUTRAL"


def test_resolve_money_event_title_prefers_expense_title():
    from app.domains.personal.life_operations.quick_add.handlers.expense import (
        resolve_money_event_title,
    )

    assert (
        resolve_money_event_title(
            {"title": "Coffee"},
            event_title="Money entry",
            category_label="Food",
        )
        == "Coffee"
    )
    assert (
        resolve_money_event_title(
            {},
            event_title="Money entry",
            category_label="Food",
        )
        == "Money entry"
    )
    assert (
        resolve_money_event_title(
            {},
            event_title="",
            category_label="Food",
        )
        == "Food"
    )
    assert (
        resolve_money_event_title(
            {"title": "  "},
            event_title="",
            category_label=None,
        )
        == "Money entry"
    )


def test_parse_amount():
    assert parse_amount("125.50") == parse_amount("125.5")
    assert parse_amount("") == parse_amount(None)


def test_pressure_score():
    assert pressure_score("Essential") == 20
    assert pressure_score("Pressure Source") == 85
    assert pressure_score(None) is None


def test_handler_registry_covers_life_ops():
    for event_type in ("EXPENSE", "COMMITMENT", "RECOVERY", "REFLECTION", "RHYTHM"):
        assert get_handler(event_type) is not None
    assert get_handler("UNKNOWN") is None
