"""Load / smoke harness for Business projection rebuild path.

Usage (from backend/):
  python scripts/load_test_business_projections.py [--iterations N]
"""
from __future__ import annotations

import argparse
import statistics
import time
from types import SimpleNamespace
from uuid import uuid4

from app.domains.business.templates.business_operations.pulse_mapper import (
    build_pulse as ops_pulse,
)
from app.domains.business.templates.business_runway.pulse_mapper import (
    build_pulse as runway_pulse,
)
from app.domains.business.templates.business_runway.series_helpers import (
    net_burn_minor,
    runway_months,
)
from app.domains.business.templates.team_operations.moments_mapper import (
    build_moments as team_moments,
)
from app.domains.business.templates.team_operations.pulse_mapper import (
    build_pulse as team_pulse,
)


def _team_ctx():
    return SimpleNamespace(
        moment_id=uuid4(),
        moment_type="TEAM_OPERATIONS",
        moment_name="Load Team",
        team_name="A",
        status="ACTIVE",
        is_active=True,
        member_count=12,
        activity_count=40,
        operating_currency="INR",
        open_issues=3,
        pending_approvals=2,
        recognition_count=1,
        meeting_count=2,
        escalation_count=1,
        activities=[],
    )


def _runway_ctx():
    burn = 250_000
    cash = 2_000_000
    return SimpleNamespace(
        moment_id=uuid4(),
        moment_type="BUSINESS_RUNWAY",
        moment_name="Load Runway",
        status="ACTIVE",
        is_active=True,
        operating_currency="INR",
        cash_available_minor=cash,
        total_inflow_minor=100_000,
        total_burn_minor=burn,
        net_burn_minor=net_burn_minor(100_000, burn),
        runway_months=runway_months(cash, burn),
        risk_count=1,
        decision_count=0,
    )


def _ops_ctx():
    return SimpleNamespace(
        moment_id=uuid4(),
        moment_type="BUSINESS_OPERATIONS",
        moment_name="Load Ops",
        status="ACTIVE",
        is_active=True,
        operating_currency="INR",
        total_budget_minor=1_000_000,
        total_spend_minor=250_000,
        budget_usage_pct=25.0,
        pending_approvals=1,
        vendor_count=2,
        improvement_count=0,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=200)
    args = parser.parse_args()

    samples: list[float] = []
    for _ in range(args.iterations):
        t0 = time.perf_counter()
        team_pulse(_team_ctx())
        team_moments(_team_ctx())
        runway_pulse(_runway_ctx())
        ops_pulse(_ops_ctx())
        samples.append((time.perf_counter() - t0) * 1000)

    print(
        "business_projection_load "
        f"n={args.iterations} "
        f"avg_ms={statistics.mean(samples):.3f} "
        f"p50_ms={statistics.median(samples):.3f} "
        f"p95_ms={sorted(samples)[int(len(samples) * 0.95) - 1]:.3f} "
        f"max_ms={max(samples):.3f}"
    )


if __name__ == "__main__":
    main()
