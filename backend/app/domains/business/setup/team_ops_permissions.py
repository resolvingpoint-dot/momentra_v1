"""Versioned Team Operations permission presets (v1)."""
from __future__ import annotations

from typing import Any

PERMISSION_VERSION_V1 = 1

# Capabilities are declarative for clients; server enforcement lands later runs.
_OWNER_CAPS = {
    "full_control": True,
    "activate_archive_complete": True,
    "manage_roles": True,
    "manage_approvals": True,
    "edit_governance": True,
    "manage_members": True,
}

_ADMIN_CAPS = {
    "full_control": False,
    "activate_archive_complete": False,
    "manage_roles": True,
    "manage_approvals": True,
    "edit_governance": True,
    "manage_members": True,
    "cannot_remove_owner": True,
}

_LEAD_CAPS = {
    "manage_day_to_day": True,
    "create_update_team_activities": True,
    "limited_member_management": True,
}

_FINANCE_CAPS = {
    "financial_visibility": True,
    "budget_actions": True,
    "approval_participation": True,
}

_APPROVER_CAPS = {
    "approve_reject": True,
}

_CONTRIBUTOR_CAPS = {
    "create_permitted_activities": True,
    "view_allowed_data": True,
}

_OBSERVER_CAPS = {
    "read_only": True,
}

PROFILES_V1: dict[str, dict[str, Any]] = {
    "OWNER_V1": {"permission_version": 1, "capabilities": _OWNER_CAPS},
    "ADMIN_V1": {"permission_version": 1, "capabilities": _ADMIN_CAPS},
    "TEAM_LEAD_V1": {"permission_version": 1, "capabilities": _LEAD_CAPS},
    "OPERATIONS_LEAD_V1": {"permission_version": 1, "capabilities": _LEAD_CAPS},
    "FINANCE_LEAD_V1": {"permission_version": 1, "capabilities": _FINANCE_CAPS},
    "BUDGET_OWNER_V1": {"permission_version": 1, "capabilities": _FINANCE_CAPS},
    "APPROVER_V1": {"permission_version": 1, "capabilities": _APPROVER_CAPS},
    "CONTRIBUTOR_V1": {"permission_version": 1, "capabilities": _CONTRIBUTOR_CAPS},
    "TEAM_MEMBER_V1": {"permission_version": 1, "capabilities": _CONTRIBUTOR_CAPS},
    "OBSERVER_V1": {"permission_version": 1, "capabilities": _OBSERVER_CAPS},
}

ROLE_TO_PROFILE_V1: dict[str, str] = {
    "OWNER": "OWNER_V1",
    "ADMIN": "ADMIN_V1",
    "TEAM_LEAD": "TEAM_LEAD_V1",
    "OPERATIONS_LEAD": "OPERATIONS_LEAD_V1",
    "FINANCE_LEAD": "FINANCE_LEAD_V1",
    "BUDGET_OWNER": "BUDGET_OWNER_V1",
    "APPROVER": "APPROVER_V1",
    "CONTRIBUTOR": "CONTRIBUTOR_V1",
    "MEMBER": "TEAM_MEMBER_V1",
    "OBSERVER": "OBSERVER_V1",
}

SUPPORTED_ROLES_V1 = tuple(ROLE_TO_PROFILE_V1.keys())


def default_profile_for_role(role: str) -> str:
    return ROLE_TO_PROFILE_V1.get((role or "MEMBER").upper(), "TEAM_MEMBER_V1")


def profile_capabilities(profile: str, version: int = 1) -> dict[str, Any]:
    if version != 1:
        return {}
    entry = PROFILES_V1.get(profile) or PROFILES_V1["TEAM_MEMBER_V1"]
    return dict(entry["capabilities"])


def member_permission_flags(role: str, *, is_approver: bool = False, is_budget_owner: bool = False) -> dict[str, bool]:
    """Map role → BusinessMomentMembers boolean columns (legacy table flags)."""
    r = (role or "MEMBER").upper()
    flags = {
        "is_team_lead": r in {"TEAM_LEAD", "OPERATIONS_LEAD", "OWNER", "ADMIN"},
        "is_budget_owner": is_budget_owner or r in {"BUDGET_OWNER", "FINANCE_LEAD", "OWNER"},
        "can_edit_own_entries": r != "OBSERVER",
        "can_edit_team_entries": r in {"OWNER", "ADMIN", "TEAM_LEAD", "OPERATIONS_LEAD"},
        "can_edit_expense_entries": r in {"OWNER", "ADMIN", "FINANCE_LEAD", "BUDGET_OWNER"},
        "can_add_runway_transactions": False,
        "can_edit_financial_entries": r in {"OWNER", "ADMIN", "FINANCE_LEAD", "BUDGET_OWNER"},
        "can_manage_runway_settings": False,
        "can_approve_runway_changes": False,
        "can_add_operations_records": r not in {"OBSERVER"},
        "can_edit_operations_records": r in {"OWNER", "ADMIN", "OPERATIONS_LEAD", "TEAM_LEAD"},
        "can_edit_own_operations_records": r != "OBSERVER",
        "can_approve_operations_requests": is_approver or r in {"OWNER", "ADMIN", "APPROVER"},
        "can_delete_operations_records": r in {"OWNER", "ADMIN"},
    }
    return flags
