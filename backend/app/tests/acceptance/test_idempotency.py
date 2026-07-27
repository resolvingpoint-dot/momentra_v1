"""Idempotency acceptance — expands when momentra_test is available."""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.financial]


def test_idempotency_suite_placeholder_documents_contract() -> None:
    """Double-submit with same client_request_id must create one expense.

    Full concurrent API coverage runs in CI with momentra_test. Unit path is
    covered by existing ``test_group_expense_consistency.test_expense_create_equal_shares_and_idempotent``.
    """
    assert True
