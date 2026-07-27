"""Runway financial calculations from real spend/inflow rows."""
from __future__ import annotations


def net_burn_minor(total_inflow_minor: int, total_burn_minor: int) -> int:
    return total_burn_minor - total_inflow_minor


def runway_months(cash_available_minor: int, monthly_burn_minor: int) -> float | None:
    """Return months of runway; None when burn <= 0 (positive cashflow)."""
    if monthly_burn_minor <= 0:
        return None
    return cash_available_minor / monthly_burn_minor
