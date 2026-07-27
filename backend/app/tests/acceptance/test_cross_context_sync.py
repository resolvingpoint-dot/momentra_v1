"""Cross-context My Money ↔ Group sync."""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.financial]


def test_group_expense_personal_account_link_gap() -> None:
    pytest.skip(
        "Product gap: trip expenses have no personal account_id; "
        "cannot assert Checking/Cash/CC outflow from group expense. "
        "See docs/testing/MY_MONEY_GROUP_ACCEPTANCE_ASSESSMENT.md."
    )
