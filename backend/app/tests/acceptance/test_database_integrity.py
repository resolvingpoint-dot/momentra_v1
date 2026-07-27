"""Database integrity helpers (pure)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.tests.integration.assertions.amounts import GOA_EXPENSES, ZERO, build_pre_settlement_ledger

pytestmark = [pytest.mark.acceptance, pytest.mark.financial]


def test_group_net_sum_zero() -> None:
    ledger = build_pre_settlement_ledger()
    assert sum(ledger.balances.values(), ZERO) == ZERO


def test_every_expense_share_sum_equals_total() -> None:
    for e in GOA_EXPENSES:
        assert sum((Decimal(str(v)) for v in e.shares.values()), ZERO) == e.total
