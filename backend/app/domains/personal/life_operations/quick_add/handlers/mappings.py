"""Map client expense payload fields to DB columns."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

_PRESSURE_MAP = {
    "essential": 20,
    "planned": 40,
    "unexpected": 70,
    "pressure source": 85,
}

_CREDIT_TYPES = {"INCOME", "CONTRIBUTION", "SAVINGS"}
_NEUTRAL_TYPES = {"TRANSFER"}


def parse_amount(raw: Any) -> Decimal:
    if raw is None or raw == "":
        return Decimal("0")
    try:
        value = Decimal(str(raw))
        return value if value >= 0 else Decimal("0")
    except (InvalidOperation, ValueError):
        return Decimal("0")


def money_direction(transaction_type: str) -> str:
    upper = (transaction_type or "EXPENSE").upper()
    if upper in _CREDIT_TYPES:
        return "CREDIT"
    if upper in _NEUTRAL_TYPES:
        return "NEUTRAL"
    return "DEBIT"


def pressure_score(impact: str | None) -> Decimal | None:
    if not impact:
        return None
    score = _PRESSURE_MAP.get(impact.strip().lower())
    return Decimal(str(score)) if score is not None else None
