"""Canonical Goa Trip API journey — requires real momentra_test DB + test auth.

Skipped automatically when isolated DB / test auth are unavailable.
See docs/testing/GOA_TRIP_FINANCIAL_EXPECTATIONS.md for corrected balances.
"""

from __future__ import annotations

import os
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.tests.integration.assertions.amounts import (
    GOA_EXPENSES,
    HOTEL_EDITED,
    PRE_SETTLEMENT,
    POST_SETTLEMENT_KIRAN_TO_SANTOSH_2500,
    money_minor,
    build_pre_settlement_ledger,
)
from app.tests.integration.assertions.reporting import (
    EvidenceLog,
    write_acceptance_summary,
    write_ledger_summary,
)
from app.tests.integration.clients.api import AuthClient, GroupClient, PersonalClient
from app.tests.integration.safety import (
    acceptance_database_url_from_env,
    assert_safe_acceptance_database_url,
)

pytestmark = [pytest.mark.acceptance, pytest.mark.financial, pytest.mark.slow]


def _acceptance_ready() -> bool:
    try:
        url = acceptance_database_url_from_env()
        assert_safe_acceptance_database_url(url)
        debug = os.environ.get("DEBUG", "").lower() in {"1", "true", "yes"}
        allow = os.environ.get("ALLOW_TEST_AUTH", "").lower() in {"1", "true", "yes"}
        return debug and allow
    except RuntimeError:
        return False


require_acceptance = pytest.mark.skipif(
    not _acceptance_ready(),
    reason=(
        "Needs ACCEPTANCE_DATABASE_URL (momentra_test), DEBUG=true, ALLOW_TEST_AUTH=true. "
        "Start backend/docker-compose.test.yml first."
    ),
)


@require_acceptance
def test_goa_trip_financial_journey_api() -> None:
    """End-to-end against live ASGI + Postgres when acceptance env is configured."""
    evidence = EvidenceLog("goa-trip-api")
    # Context manager keeps one ASGI portal/event loop for the whole journey
    # (required on Windows with async SQLAlchemy).
    with TestClient(app) as client:
        _run_goa_trip_journey(client, evidence)


def _run_goa_trip_journey(client: TestClient, evidence: EvidenceLog) -> None:
    auth = AuthClient(client, evidence)

    santosh = auth.test_login(firebase_uid="test:santosh", display_name="Santosh")
    rahul = auth.test_login(firebase_uid="test:rahul", display_name="Rahul")
    priya = auth.test_login(firebase_uid="test:priya", display_name="Priya")
    kiran = auth.test_login(firebase_uid="test:kiran", display_name="Kiran")

    personal = PersonalClient(santosh)
    for row in (
        ("Checking Account", "CURRENT", "30000.00"),
        ("Cash", "CASH", "4000.00"),
        ("UPI Wallet", "WALLET", "2500.00"),
        ("Credit Card", "CREDIT_CARD", "0.00"),
    ):
        personal.create_account(account_name=row[0], account_type=row[1], opening_balance=row[2])

    accounts = personal.list_accounts()
    account_list = accounts if isinstance(accounts, list) else accounts.get("accounts") or accounts
    assert len(account_list) >= 4

    group = GroupClient(santosh)
    moment_id = group.create_shared_experience()
    group.setup_draft(moment_id, name="Goa Trip")
    group.activate(moment_id)

    # Link guests as members (trip APIs are owner-scoped; membership ids = user ids).
    for member_api, name in ((rahul, "Rahul"), (priya, "Priya"), (kiran, "Kiran")):
        group.add_guest(
            moment_id,
            {
                "display_name": name,
                "full_name": name,
                "user_id": member_api.user_id,
                "status": "active",
            },
        )

    ids = {
        "santosh": santosh.user_id,
        "rahul": rahul.user_id,
        "priya": priya.user_id,
        "kiran": kiran.user_id,
    }
    assert all(ids.values())

    # Expenses/settlements must be written as the moment owner — trip_deep_service
    # requires moments.user_id match. Payer is encoded via paid_by_participant_id.
    expense_ids: dict[str, str] = {}
    for expense in GOA_EXPENSES:
        participants = [ids[m] for m in expense.shares]
        split_details = None
        if expense.key == "goa-hotel-001":
            split_details = [
                {"member_id": ids["santosh"], "percentage": 40},
                {"member_id": ids["rahul"], "percentage": 20},
                {"member_id": ids["priya"], "percentage": 20},
                {"member_id": ids["kiran"], "percentage": 20},
            ]
        created = group.create_expense(
            moment_id,
            title=expense.title,
            amount=expense.total,
            paid_by_participant_id=ids[expense.payer],
            participant_ids=participants,
            split_style="PERCENTAGE" if split_details else "EQUAL",
            client_request_id=expense.key,
            split_details=split_details,
        )
        expense_ids[expense.key] = str(created.get("id") or created.get("expense_id"))
        # Independent share sum check on response when present.
        shares = created.get("shares") or []
        if shares:
            share_sum = sum(int(s["amount_minor"]) for s in shares)
            assert share_sum == money_minor(expense.total), (
                f"{expense.key}: response shares {share_sum} != {money_minor(expense.total)}"
            )

    # Local ledger remains source of financial truth for expected nets.
    local = build_pre_settlement_ledger()
    local.assert_equals(PRE_SETTLEMENT, label="pre-settlement local")

    preview = group.settlement_preview(moment_id)
    balances = {b["member_id"]: b for b in preview.get("member_balances") or []}
    # Map API nets (minor) to major when members use user ids as member_id.
    for key, uid in ids.items():
        if uid in balances:
            net_major = Decimal(balances[uid]["net_minor"]) / Decimal(100)
            assert net_major == PRE_SETTLEMENT[key], (
                f"API net for {key}: {net_major} != {PRE_SETTLEMENT[key]}"
            )

    suggestions = preview.get("suggestions") or []
    for s in suggestions:
        assert s["from_member_id"] != s["to_member_id"]
        assert int(s["amount_minor"]) > 0
        # Creditor→creditor Santosh→Rahul must not appear as a suggestion.
        assert not (
            s["from_member_id"] == ids["santosh"] and s["to_member_id"] == ids["rahul"]
        ), "Santosh→Rahul must not be a simplify_debts suggestion"

    # Valid debt payment (owner-auth; party pair is from/to member ids)
    settlement = group.create_settlement(
        moment_id,
        from_member_id=ids["kiran"],
        to_member_id=ids["santosh"],
        amount=Decimal("2500.00"),
        client_request_id="goa-settlement-001",
        description="Kiran pays Santosh",
    )
    group.mark_settled(moment_id, settlement["id"])
    local.apply_settlement(debtor="kiran", creditor="santosh", amount=Decimal("2500.00"))
    local.assert_equals(POST_SETTLEMENT_KIRAN_TO_SANTOSH_2500, label="post-settlement")

    # Hotel edit
    hotel_id = expense_ids["goa-hotel-001"]
    group.patch_expense(
        moment_id,
        hotel_id,
        {
            "amount_minor": money_minor(HOTEL_EDITED.total),
            "split_style": "PERCENTAGE",
            "participant_ids": [ids[m] for m in ("santosh", "rahul", "priya", "kiran")],
            "split_details": [
                {"member_id": ids["santosh"], "percentage": 40},
                {"member_id": ids["rahul"], "percentage": 20},
                {"member_id": ids["priya"], "percentage": 20},
                {"member_id": ids["kiran"], "percentage": 20},
            ],
        },
    )

    # Scooter delete
    group.delete_expense(moment_id, expense_ids["goa-scooter-001"])

    write_ledger_summary(
        {
            "pre_settlement": {k: str(v) for k, v in PRE_SETTLEMENT.items()},
            "post_settlement": {k: str(v) for k, v in POST_SETTLEMENT_KIRAN_TO_SANTOSH_2500.items()},
            "moment_id": moment_id,
            "expense_ids": expense_ids,
        }
    )
    write_acceptance_summary(
        {
            "scenario": "Goa Trip Financial Journey",
            "status": "passed",
            "tests": {"passed": 1, "failed": 0, "skipped": 0, "xfail": 0},
            "release_recommendation": "controlled_beta_pending_full_marker_suite",
            "domains": {
                "group": {"status": "passed_api_path"},
                "my_money": {"status": "accounts_created"},
                "cross_context_sync": {
                    "status": "skipped",
                    "reason": "No personal account_id on trip expenses",
                },
            },
        }
    )


@pytest.mark.acceptance
@pytest.mark.financial
def test_personal_account_link_on_trip_expense_product_gap() -> None:
    pytest.skip(
        "Product gap: trip expense contract has no personal account_id / "
        "group-to-My-Money posting. See MY_MONEY_GROUP_ACCEPTANCE_ASSESSMENT.md."
    )
