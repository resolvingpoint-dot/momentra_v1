"""Performance contract placeholders (non-blocking locally)."""

from __future__ import annotations

import statistics
import time

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.performance, pytest.mark.perf]


def test_ledger_accumulation_perf_smoke() -> None:
    from app.tests.integration.assertions.amounts import build_pre_settlement_ledger

    samples: list[float] = []
    for _ in range(50):
        t0 = time.perf_counter()
        build_pre_settlement_ledger()
        samples.append((time.perf_counter() - t0) * 1000)
    p95 = statistics.quantiles(samples, n=20)[18]
    # Extremely loose local bound — API p95 contracts need live env.
    assert p95 < 50.0, f"ledger p95 {p95}ms too high"
