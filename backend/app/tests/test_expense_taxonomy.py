"""Tests for expense taxonomy nesting and subcategory validation."""
from __future__ import annotations

import pytest

from app.domains.reference_data.catalog import get_reference_catalog
from app.domains.reference_data.expense_taxonomy import (
    InvalidExpenseSubcategoryError,
    nest_expense_categories,
    normalize_expense_category_code,
    validate_expense_category_pair,
)


def test_nest_expense_categories_has_children():
    catalog = get_reference_catalog()
    nested = catalog.get("expense_categories")
    food = next(r for r in nested if r["code"] == "FOOD")
    child_codes = {c["code"] for c in food.get("children") or []}
    assert {"GROCERIES", "DINING_OUT", "COFFEE"} <= child_codes
    assert all("parent_code" not in c for c in food["children"])
    assert food.get("taxonomy") == "EXPENSE"


def test_validate_food_groceries_ok():
    cat, sub = validate_expense_category_pair("FOOD", "GROCERIES")
    assert cat == "FOOD"
    assert sub == "GROCERIES"


def test_validate_food_fuel_rejects():
    with pytest.raises(InvalidExpenseSubcategoryError) as exc:
        validate_expense_category_pair("FOOD", "FUEL")
    assert exc.value.code == "invalid_expense_subcategory"


def test_validate_null_subcategory_ok():
    cat, sub = validate_expense_category_pair("FOOD", None)
    assert cat == "FOOD"
    assert sub is None


def test_validate_alias_casing():
    cat, sub = validate_expense_category_pair("food", "groceries")
    assert cat == "FOOD"
    assert sub == "GROCERIES"


def test_legacy_living_rent_preserved():
    assert normalize_expense_category_code("rent") == "rent"
    cat, sub = validate_expense_category_pair("rent", None, allow_legacy_living=True)
    assert cat == "rent"
    assert sub is None


def test_unknown_subcategory_rejects():
    with pytest.raises(InvalidExpenseSubcategoryError):
        validate_expense_category_pair("FOOD", "NOT_A_REAL_SUB")


def test_child_as_category_rejects():
    with pytest.raises(InvalidExpenseSubcategoryError):
        validate_expense_category_pair("GROCERIES", None)


def test_transport_category_change_incompatible_sub():
    with pytest.raises(InvalidExpenseSubcategoryError):
        validate_expense_category_pair("TRANSPORT", "GROCERIES")


def test_residential_rent_child_ok():
    cat, sub = validate_expense_category_pair("HOUSING", "RESIDENTIAL_RENT")
    assert cat == "HOUSING"
    assert sub == "RESIDENTIAL_RENT"


def test_nest_helper_standalone():
    rows = [
        {"code": "FOOD", "label": "Food", "sort_order": 10, "taxonomy": "EXPENSE"},
        {
            "code": "GROCERIES",
            "label": "Groceries",
            "sort_order": 11,
            "taxonomy": "EXPENSE",
            "parent_code": "FOOD",
        },
    ]
    nested = nest_expense_categories(rows)
    assert len(nested) == 1
    assert nested[0]["children"][0]["code"] == "GROCERIES"
