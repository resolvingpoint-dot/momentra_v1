"""Shared fixture + normalizer + payload pipeline tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.domains.quick_add_contract.aliases import normalize_action_id, normalize_moment_type_code
from app.domains.quick_add_contract.hash import fixtures_root
from app.domains.quick_add_contract.normalize import normalize_payload
from app.domains.quick_add_contract.payloads import pipeline_build

FIXTURES = [
    "personal_life_ops_expense.json",
    "personal_future_contribution.json",
    "personal_lifestyle_experience.json",
    "personal_relationship_connection.json",
    "group_experience_expense.json",
    "group_purchase_contribution.json",
    "group_living_rent.json",
]


@pytest.mark.parametrize("name", FIXTURES)
def test_fixture_loads_and_has_wire(name: str):
    path = fixtures_root() / name
    data = json.loads(path.read_text(encoding="utf-8"))
    expected_version = "v2" if name in {
        "personal_life_ops_expense.json",
        "group_experience_expense.json",
    } else "v1"
    assert data["contract_version"] == expected_version
    assert "wire" in data
    assert data["wire"]


def test_moment_type_aliases():
    assert normalize_moment_type_code("TRIP") == "SHARED_EXPERIENCE"
    assert normalize_moment_type_code("EMOTIONAL_SECURITY") == "RELATIONSHIPS"
    assert normalize_moment_type_code("RELATIONSHIPS") == "RELATIONSHIPS"


def test_action_aliases():
    assert normalize_action_id("RENT") == "EXPENSE"
    assert normalize_action_id("UTILITY") == "EXPENSE"
    assert normalize_action_id("CONTRIBUTOR") == "CONTRIBUTOR"


def test_normalize_payer_and_amount():
    out = normalize_payload(
        {
            "amount": "12.50",
            "paid_by": "abc",
            "currency": "usd",
            "category": "food",
        },
        moment_type_code="TRIP",
        action_id="EXPENSE",
    )
    assert out["moment_type_code"] == "SHARED_EXPERIENCE"
    assert out["action_id"] == "EXPENSE"
    assert out["amount_minor"] == 1250
    assert out["paid_by_participant_id"] == "abc"
    assert out["currency_code"] == "USD"
    assert out["category_code"] == "FOOD"
    assert out["contract_version"] == "v1"


def test_normalize_subcategory_alias_and_v2():
    out = normalize_payload(
        {
            "amount_minor": 100,
            "currency_code": "INR",
            "category_code": "FOOD",
            "expense_subcategory": "groceries",
        },
        action_id="EXPENSE",
    )
    assert out["category_code"] == "FOOD"
    assert out["subcategory_code"] == "GROCERIES"
    assert out["contract_version"] == "v2"


def test_rent_alias_sets_category():
    out = normalize_payload(
        {"amount_major": "10", "currency_code": "INR"},
        moment_type_code="SHARED_LIVING",
        action_id="RENT",
    )
    assert out["action_id"] == "EXPENSE"
    assert out["category_code"] == "rent"
    assert out.get("subcategory_code") in (None, "")
    assert out["amount_minor"] == 1000


def test_pipeline_build_group_expense():
    fixture = json.loads((fixtures_root() / "group_experience_expense.json").read_text())
    built = pipeline_build(
        fixture["ui_form"] | {"client_request_id": fixture["wire"]["client_request_id"]},
        moment_type_code="SHARED_EXPERIENCE",
        action_id="EXPENSE",
        required=["amount", "paid_by", "currency"],
        builder_id="group.experience.expense",
    )
    assert built["amount_minor"] == 9000
    assert built["paid_by_participant_id"] == fixture["wire"]["paid_by_participant_id"]
    assert built["currency_code"] == "USD"
    assert built.get("subcategory_code") == "DINING_OUT" or built.get("category_code") == "FOOD"
