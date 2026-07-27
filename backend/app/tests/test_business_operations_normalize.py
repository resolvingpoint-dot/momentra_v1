"""Business Operations mapper unit tests."""
from app.domains.business.setup.business_operations_mappers import (
    compute_derived_preview,
    normalize_operations_answers,
    resolve_allocations,
)


def test_alias_and_owner():
    answers = normalize_operations_answers(
        {
            "currency": "usd",
            "operations_scope": "department",
            "operating_model": "hybrid",
            "monthly_budget_minor": 10000,
            "member_drafts": [{"local_id": "a", "name": "Alex", "email": "a@x.com", "role": "MEMBER"}],
        },
        owner_user_id="owner-1",
    )
    assert answers["operating_currency_code"] == "USD"
    assert answers["operations_scope"] == "DEPARTMENT"
    assert answers["operating_model"] == "HYBRID"
    assert answers["members"][0]["role"] == "OWNER"


def test_percentage_rounding_deterministic():
    allocs = resolve_allocations(
        monthly_budget_minor=100,
        allocation_mode="PERCENTAGE",
        allocations=[
            {"allocation_id": "b", "percentage": 33, "category_code": "payroll"},
            {"allocation_id": "a", "percentage": 33, "category_code": "ops"},
            {"allocation_id": "c", "percentage": 34, "category_code": "vendor"},
        ],
    )
    assert [a["allocation_id"] for a in allocs] == ["a", "b", "c"]
    assert sum(a["amount_minor"] for a in allocs) == 100


def test_derived_preview():
    derived = compute_derived_preview(
        {
            "monthly_budget_minor": 1000,
            "budget_allocations": [
                {"amount_minor": 400},
                {"amount_minor": 250},
            ],
            "members": [
                {"role": "OWNER"},
                {"role": "APPROVER", "is_approver": True},
            ],
        }
    )
    assert derived["allocated_budget_minor"] == 650
    assert derived["unallocated_budget_minor"] == 350
    assert derived["approver_count"] == 1
