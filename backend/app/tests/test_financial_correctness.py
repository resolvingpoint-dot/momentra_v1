"""Sprint B.5 — Financial correctness QA for minor-unit conversions."""
from __future__ import annotations

from decimal import Decimal

from app.domains.reference_data.catalog import get_reference_catalog


def test_inr_usd_eur_minor_conversion():
    catalog = get_reference_catalog()
    assert catalog.minor_from_major_string("4500", "INR") == 450_000
    assert catalog.minor_from_major_string("4500", "USD") == 450_000
    assert catalog.minor_from_major_string("4500.00", "EUR") == 450_000


def test_jpy_no_cent_multiplier():
    catalog = get_reference_catalog()
    assert catalog.minor_from_major_string("4500", "JPY") == 4500
    assert catalog.major_from_minor(4500, "JPY") == Decimal("4500")


def test_kwd_three_decimal_places():
    catalog = get_reference_catalog()
    assert catalog.minor_from_major_string("4.123", "KWD") == 4123
    assert catalog.major_from_minor(4123, "KWD") == Decimal("4.123")


def test_round_trip_inr():
    catalog = get_reference_catalog()
    minor = catalog.minor_from_major_string("45.50", "INR")
    assert minor == 4550
    assert catalog.major_from_minor(minor, "INR") == Decimal("45.50")


def test_negative_balance_minor_conversion():
    """Account balances may be negative (credit/overdraft)."""
    catalog = get_reference_catalog()
    assert catalog.minor_from_major_string("-1250.50", "INR") == -125_050
    assert catalog.major_from_minor(-125_050, "INR") == Decimal("-1250.50")
