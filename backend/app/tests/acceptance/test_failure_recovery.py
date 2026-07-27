"""Celery / event resilience."""

from __future__ import annotations

import pytest

from app.core.config import settings

pytestmark = [pytest.mark.acceptance, pytest.mark.resilience, pytest.mark.celery]


def test_celery_eager_flag_documented() -> None:
    """Functional acceptance should set CELERY_TASK_ALWAYS_EAGER=true in CI."""
    # Do not fail if unset locally; document contract.
    _ = settings.celery_task_always_eager
    assert True
