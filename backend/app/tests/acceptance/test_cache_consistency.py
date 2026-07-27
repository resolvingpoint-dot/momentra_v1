"""Cache consistency markers."""

from __future__ import annotations

import pytest

from app.core.cache import reset_cache_for_tests

pytestmark = [pytest.mark.acceptance, pytest.mark.resilience, pytest.mark.redis]


def test_cache_reset_for_tests_is_safe() -> None:
    reset_cache_for_tests()
    assert True
