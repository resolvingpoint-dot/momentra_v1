"""Authorization / isolation acceptance markers."""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.security]


def test_stranger_cannot_read_foreign_group_documented() -> None:
    """Full multi-user isolation requires momentra_test + test auth (see journey skip)."""
    pytest.skip(
        "Runnable when ACCEPTANCE_DATABASE_URL=momentra_test with DEBUG/ALLOW_TEST_AUTH. "
        "Assert stranger gets 403/404 on trip expenses of another user's moment."
    )
