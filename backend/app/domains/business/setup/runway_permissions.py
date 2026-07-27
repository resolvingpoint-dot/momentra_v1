"""Versioned Business Runway permission presets (v1)."""
from __future__ import annotations

from typing import Any

PERMISSION_VERSION_V1 = 1

_OWNER_CAPS = {
    "full_control": True,
    "activate_archive_complete": True,
    "manage_roles": True,
    "manage_approvals": True,
    "edit_governance": True,
    "manage_members": True,
    "edit_financials": True,
}

_FOUNDER_CAPS = {
    "manage_day_to_day": True,
    "edit_financials": True,
    "manage_members": True,
    "view_runway": True,
}

_FINANCE_CAPS = {
    "financial_visibility": True,
    "edit_financials": True,
    "approval_participation": True,
    "view_runway": True,
}

_OPS_CAPS = {
    "manage_day_to_day": True,
    "view_runway": True,
    "create_permitted_activities": True,
}

_ADVISOR_CAPS = {
    "view_runway": True,
    "advise": True,
    "read_only": True,
}

_APPROVER_CAPS = {
    "approve_reject": True,
    "view_runway": True,
}

_CONTRIBUTOR_CAPS = {
    "create_permitted_activities": True,
    "view_allowed_data": True,
}

_OBSERVER_CAPS = {
    "read_only": True,
    "view_runway": True,
}

PROFILES_V1: dict[str, dict[str, Any]] = {
    "OWNER_V1": {"permission_version": 1, "capabilities": _OWNER_CAPS},
    "FOUNDER_V1": {"permission_version": 1, "capabilities": _FOUNDER_CAPS},
    "FINANCE_LEAD_V1": {"permission_version": 1, "capabilities": _FINANCE_CAPS},
    "OPERATIONS_LEAD_V1": {"permission_version": 1, "capabilities": _OPS_CAPS},
    "ADVISOR_V1": {"permission_version": 1, "capabilities": _ADVISOR_CAPS},
    "APPROVER_V1": {"permission_version": 1, "capabilities": _APPROVER_CAPS},
    "CONTRIBUTOR_V1": {"permission_version": 1, "capabilities": _CONTRIBUTOR_CAPS},
    "OBSERVER_V1": {"permission_version": 1, "capabilities": _OBSERVER_CAPS},
}

ROLE_TO_PROFILE_V1: dict[str, str] = {
    "OWNER": "OWNER_V1",
    "FOUNDER": "FOUNDER_V1",
    "FINANCE_LEAD": "FINANCE_LEAD_V1",
    "OPERATIONS_LEAD": "OPERATIONS_LEAD_V1",
    "ADVISOR": "ADVISOR_V1",
    "APPROVER": "APPROVER_V1",
    "CONTRIBUTOR": "CONTRIBUTOR_V1",
    "OBSERVER": "OBSERVER_V1",
}

SUPPORTED_ROLES_V1 = tuple(ROLE_TO_PROFILE_V1.keys())


def default_profile_for_role(role: str) -> str:
    return ROLE_TO_PROFILE_V1.get((role or "CONTRIBUTOR").upper(), "CONTRIBUTOR_V1")


def profile_capabilities(profile: str, version: int = 1) -> dict[str, Any]:
    if version != 1:
        return {}
    entry = PROFILES_V1.get(profile) or PROFILES_V1["CONTRIBUTOR_V1"]
    return dict(entry["capabilities"])


def member_permission_flags(
    role: str,
    *,
    is_finance_lead: bool = False,
    is_operations_lead: bool = False,
    is_advisor: bool = False,
    is_observer: bool = False,
) -> dict[str, bool]:
    """Map role → BusinessMomentMembers boolean columns."""
    r = (role or "CONTRIBUTOR").upper()
    return {
        "is_team_lead": r in {"OWNER", "FOUNDER", "OPERATIONS_LEAD"} or is_operations_lead,
        "is_budget_owner": is_finance_lead or r in {"OWNER", "FINANCE_LEAD"},
        "can_edit_own_entries": r != "OBSERVER" and not is_observer,
        "can_edit_team_entries": r in {"OWNER", "FOUNDER", "OPERATIONS_LEAD", "FINANCE_LEAD"},
        "can_approve_requests": r in {"OWNER", "APPROVER", "FINANCE_LEAD"},
        "can_add_runway_transactions": r in {"OWNER", "FOUNDER", "FINANCE_LEAD", "CONTRIBUTOR"},
        "can_view_all_financials": r in {"OWNER", "FOUNDER", "FINANCE_LEAD", "ADVISOR"} or is_finance_lead,
    }
