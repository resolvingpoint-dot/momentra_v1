"""Unit tests for Team Operations answer normalization (Run 3.1)."""
from __future__ import annotations

from app.domains.business.setup.team_ops_mappers import (
    inject_owner_member,
    normalize_team_ops_answers,
    normalize_team_size,
    normalize_work_style,
)


def test_team_size_legacy_alias_equivalence():
    assert normalize_team_size("just_me") == "SOLO"
    assert normalize_team_size("2_5") == "SMALL"
    assert normalize_team_size("SOLO") == "SOLO"


def test_work_style_refuses_legacy_false_mapping():
    assert normalize_work_style("REMOTE") == "REMOTE"
    assert normalize_work_style("HYBRID") == "HYBRID"
    assert normalize_work_style("planned") is None
    assert normalize_work_style("mixed") is None


def test_normalize_injects_owner_and_dedupes():
    owner = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    answers = normalize_team_ops_answers(
        {
            "purpose": "Ship",
            "currency": "usd",
            "team_size": "SMALL",
            "work_style": "HYBRID",
            "team_owner_id": "someone-else",
            "member_drafts": [
                {
                    "name": "Alex",
                    "email": "alex@example.com",
                    "role": "MEMBER",
                },
                {
                    "name": "Alex Dup",
                    "email": "ALEX@example.com",
                    "role": "CONTRIBUTOR",
                },
            ],
            "members": [
                {
                    "local_id": "m2",
                    "name": "Sam",
                    "email": "sam@example.com",
                    "phone": "+1555",
                    "role": "APPROVER",
                    "is_approver": True,
                }
            ],
        },
        owner_user_id=owner,
    )
    assert answers["team_purpose"] == "Ship"
    assert answers["operating_currency_code"] == "USD"
    assert answers["team_owner_id"] == owner
    members = answers["members"]
    assert members[0]["role"] == "OWNER"
    assert members[0]["user_id"] == owner
    assert members[0]["permission_profile"] == "OWNER_V1"
    assert members[0]["permission_version"] == 1
    emails = [m.get("email") for m in members if m.get("email")]
    assert emails.count("alex@example.com") == 1
    assert any(m.get("email") == "sam@example.com" for m in members)


def test_inject_owner_downgrades_competing_owner():
    owner = "owner-1"
    members = inject_owner_member(
        [
            {
                "local_id": "x",
                "user_id": "other",
                "name": "Fake",
                "role": "OWNER",
                "permission_profile": "OWNER_V1",
                "permission_version": 1,
                "invite_method": "EMAIL",
                "invite_status": "DRAFT",
                "is_approver": False,
                "is_budget_owner": False,
                "email": None,
                "phone": None,
            }
        ],
        owner,
    )
    assert members[0]["user_id"] == owner
    assert members[0]["role"] == "OWNER"
    assert sum(1 for m in members if m["role"] == "OWNER") == 1
    assert any(m["user_id"] == "other" and m["role"] == "MEMBER" for m in members)


def test_legacy_planned_work_style_dropped():
    out = normalize_team_ops_answers({"work_style": "planned"}, owner_user_id="u1")
    assert out.get("work_style") is None
