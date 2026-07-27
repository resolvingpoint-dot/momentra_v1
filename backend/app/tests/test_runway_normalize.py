"""Business Runway mapper unit tests."""
from app.domains.business.setup.runway_mappers import (
    compute_derived_preview,
    currency_exponent,
    minor_to_major,
    normalize_runway_answers,
)


def test_alias_normalization_and_owner_inject():
    answers = normalize_runway_answers(
        {
            "currency": "usd",
            "cash_available_minor": 10000,
            "business_stage": "growth",
            "revenue_status": "NO_REVENUE",
            "member_drafts": [
                {"local_id": "m1", "name": "Alex", "email": "a@x.com", "role": "FOUNDER"},
            ],
        },
        owner_user_id="owner-1",
    )
    assert answers["operating_currency_code"] == "USD"
    assert answers["current_cash_minor"] == 10000
    assert answers["business_stage"] == "GROWTH"
    assert answers["members"][0]["role"] == "OWNER"
    assert answers["members"][0]["user_id"] == "owner-1"
    assert answers["runway_owner_id"] == "owner-1"


def test_dedupe_members():
    answers = normalize_runway_answers(
        {
            "members": [
                {"local_id": "a", "name": "A", "email": "same@x.com", "role": "FOUNDER"},
                {"local_id": "b", "name": "B", "email": "same@x.com", "role": "ADVISOR"},
            ]
        },
        owner_user_id="o1",
    )
    emails = [m.get("email") for m in answers["members"] if m.get("email")]
    assert emails.count("same@x.com") == 1


def test_jpy_kwd_minor_major():
    assert currency_exponent("JPY") == 0
    assert currency_exponent("KWD") == 3
    assert int(minor_to_major(500, "JPY")) == 500
    assert str(minor_to_major(1234, "KWD")) == "1.234"


def test_preview_derived_integer_safe():
    derived = compute_derived_preview(
        {
            "current_cash_minor": 10000,
            "monthly_burn_minor": 3000,
            "estimated_monthly_revenue_minor": 500,
            "runway_goal_months": 6,
        }
    )
    assert derived["estimated_runway_months"] == 3
    assert derived["net_monthly_burn_minor"] == 2500
    assert derived["goal_gap_months"] == 3
    assert compute_derived_preview({"current_cash_minor": 100, "monthly_burn_minor": 0})[
        "estimated_runway_months"
    ] is None
