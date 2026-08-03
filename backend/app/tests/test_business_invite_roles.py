"""Unit tests for business invite role helpers."""

from __future__ import annotations

import pytest

from app.domains.business.setup.invite_roles import (
    default_invitee_role,
    inviter_api_role_allowed,
    validate_invitee_role,
)


def test_validate_rejects_owner():
    with pytest.raises(ValueError, match="OWNER"):
        validate_invitee_role("OWNER", moment_type="TEAM_OPERATIONS")


def test_validate_team_ops_admin():
    assert validate_invitee_role("admin", moment_type="TEAM_OPERATIONS") == "ADMIN"


def test_validate_rejects_unknown_for_runway():
    with pytest.raises(ValueError, match="Invalid role"):
        validate_invitee_role("VENDOR_MANAGER", moment_type="BUSINESS_RUNWAY")


def test_default_invitee_prefers_member():
    assert default_invitee_role("TEAM_OPERATIONS") == "MEMBER"
    assert default_invitee_role("BUSINESS_RUNWAY") in {"CONTRIBUTOR", "OBSERVER", "MEMBER"}


def test_inviter_roles():
    assert inviter_api_role_allowed("OWNER")
    assert inviter_api_role_allowed("TEAM_LEAD")
    assert not inviter_api_role_allowed("MEMBER")
    assert not inviter_api_role_allowed("OBSERVER")
