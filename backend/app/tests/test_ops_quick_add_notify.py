"""Unit tests for Ops Quick Add notify policy + approval approver parsing."""
from __future__ import annotations

from app.domains.business.activity.handlers.business_operations.approval_request import (
    _normalize_request_type,
    _parse_approver_ids,
)


def test_normalize_request_type_aliases():
    assert _normalize_request_type("purchase") == "purchase"
    assert _normalize_request_type("expense") == "expense_approval"
    assert _normalize_request_type("vendor_payment") == "vendor_approval"
    assert _normalize_request_type("unknown_thing") == "other"


def test_parse_approver_ids_dedupes_and_primary():
    primary = "11111111-1111-1111-1111-111111111111"
    second = "22222222-2222-2222-2222-222222222222"
    ids = _parse_approver_ids(
        {
            "approver_id": primary,
            "approver_ids": [second, primary, ""],
        }
    )
    assert [str(x) for x in ids] == [primary, second]
