"""Operations financial calculations from real spend rows."""
from __future__ import annotations


def budget_usage_pct(total_spend_minor: int, total_budget_minor: int) -> float:
    if total_budget_minor <= 0:
        return 0.0
    return min(100.0, (total_spend_minor / total_budget_minor) * 100)
