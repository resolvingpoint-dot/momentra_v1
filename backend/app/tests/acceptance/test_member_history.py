"""Historical membership rules."""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.financial]


def test_anjali_add_after_expenses_requires_live_api() -> None:
    pytest.skip(
        "Requires momentra_test multi-user journey: Anjali balance 0, no historical splits."
    )
