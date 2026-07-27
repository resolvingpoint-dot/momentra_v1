"""Pure Decimal ledger tests — always runnable (no DB).

Correct pre-settlement: Santosh +6250 / Rahul +2250 / Priya -3950 / Kiran -4550.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.tests.integration.assertions.amounts import (
    GOA_EXPENSES,
    HOTEL_EDITED,
    POST_HOTEL_EDIT_AFTER_SETTLEMENT,
    POST_SCOOTER_DELETE_AFTER_EDIT,
    POST_SETTLEMENT_KIRAN_TO_SANTOSH_2500,
    PRE_SETTLEMENT,
    ZERO,
    apply_hotel_edit_in_place,
    build_pre_settlement_ledger,
    reverse_scooter,
)

pytestmark = [pytest.mark.financial, pytest.mark.acceptance]


def test_each_expense_shares_sum_to_total() -> None:
    for expense in GOA_EXPENSES:
        expense.validate_shares()
    HOTEL_EDITED.validate_shares()


def test_accumulate_pre_settlement_independently() -> None:
    ledger = build_pre_settlement_ledger()
    assert sum(ledger.balances.values(), ZERO) == ZERO
    ledger.assert_equals(PRE_SETTLEMENT, label="canonical pre-settlement")


def test_obsolete_incorrect_balances_are_rejected() -> None:
    """Guard against reintroducing the wrong +4050/+3350/-3450/-3950 numbers."""
    wrong = {
        "santosh": Decimal("4050.00"),
        "rahul": Decimal("3350.00"),
        "priya": Decimal("-3450.00"),
        "kiran": Decimal("-3950.00"),
    }
    ledger = build_pre_settlement_ledger()
    with pytest.raises(AssertionError):
        ledger.assert_equals(wrong, label="obsolete")


def test_kiran_pays_santosh_2500_after_expenses() -> None:
    ledger = build_pre_settlement_ledger()
    ledger.apply_settlement(debtor="kiran", creditor="santosh", amount=Decimal("2500.00"))
    ledger.assert_equals(POST_SETTLEMENT_KIRAN_TO_SANTOSH_2500, label="post-settlement")


def test_hotel_edit_then_scooter_delete_ordered() -> None:
    ledger = build_pre_settlement_ledger()
    ledger.apply_settlement(debtor="kiran", creditor="santosh", amount=Decimal("2500.00"))
    apply_hotel_edit_in_place(ledger)
    ledger.assert_equals(POST_HOTEL_EDIT_AFTER_SETTLEMENT, label="post-hotel-edit")
    reverse_scooter(ledger)
    ledger.assert_equals(POST_SCOOTER_DELETE_AFTER_EDIT, label="post-scooter-delete")


def test_santosh_and_rahul_are_creditors_pre_settlement() -> None:
    ledger = build_pre_settlement_ledger()
    assert ledger.balances["santosh"] > ZERO
    assert ledger.balances["rahul"] > ZERO
    assert ledger.balances["priya"] < ZERO
    assert ledger.balances["kiran"] < ZERO
