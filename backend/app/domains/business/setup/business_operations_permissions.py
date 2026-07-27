"""Versioned Business Operations permission presets (v1)."""
from __future__ import annotations

from typing import Any

PERMISSION_VERSION_V1 = 1

PROFILES_V1: dict[str, dict[str, Any]] = {
    "OWNER_V1": {
        "permission_version": 1,
        "capabilities": {
            "full_control": True,
            "lifecycle": True,
            "manage_members": True,
            "edit_governance": True,
            "edit_budget": True,
            "approvals": True,
        },
    },
    "ADMIN_V1": {
        "permission_version": 1,
        "capabilities": {
            "manage_members": True,
            "edit_governance": True,
            "cannot_remove_owner": True,
        },
    },
    "OPERATIONS_LEAD_V1": {
        "permission_version": 1,
        "capabilities": {"operational_activities": True, "issue_management": True},
    },
    "BUDGET_CONTROLLER_V1": {
        "permission_version": 1,
        "capabilities": {"budget_visibility": True, "allocation_management": True},
    },
    "FINANCE_LEAD_V1": {
        "permission_version": 1,
        "capabilities": {"budget_visibility": True, "financial_actions": True},
    },
    "APPROVER_V1": {
        "permission_version": 1,
        "capabilities": {"approve_reject": True},
    },
    "VENDOR_MANAGER_V1": {
        "permission_version": 1,
        "capabilities": {"vendor_changes": True},
    },
    "CONTRIBUTOR_V1": {
        "permission_version": 1,
        "capabilities": {"create_permitted_actions": True},
    },
    "MEMBER_V1": {
        "permission_version": 1,
        "capabilities": {"create_permitted_actions": True},
    },
    "OBSERVER_V1": {
        "permission_version": 1,
        "capabilities": {"read_only": True},
    },
}

ROLE_TO_PROFILE_V1: dict[str, str] = {
    "OWNER": "OWNER_V1",
    "ADMIN": "ADMIN_V1",
    "OPERATIONS_LEAD": "OPERATIONS_LEAD_V1",
    "BUDGET_CONTROLLER": "BUDGET_CONTROLLER_V1",
    "FINANCE_LEAD": "FINANCE_LEAD_V1",
    "APPROVER": "APPROVER_V1",
    "VENDOR_MANAGER": "VENDOR_MANAGER_V1",
    "CONTRIBUTOR": "CONTRIBUTOR_V1",
    "MEMBER": "MEMBER_V1",
    "OBSERVER": "OBSERVER_V1",
}

SUPPORTED_ROLES_V1 = tuple(ROLE_TO_PROFILE_V1.keys())


def default_profile_for_role(role: str) -> str:
    return ROLE_TO_PROFILE_V1.get((role or "MEMBER").upper(), "MEMBER_V1")


def member_permission_flags(
    role: str,
    *,
    is_approver: bool = False,
    is_budget_controller: bool = False,
    is_operations_lead: bool = False,
    is_vendor_manager: bool = False,
    is_observer: bool = False,
) -> dict[str, bool]:
    r = (role or "MEMBER").upper()
    return {
        "is_team_lead": r in {"OWNER", "ADMIN", "OPERATIONS_LEAD"} or is_operations_lead,
        "is_budget_owner": is_budget_controller or r in {"OWNER", "BUDGET_CONTROLLER", "FINANCE_LEAD"},
        "can_edit_own_entries": r != "OBSERVER" and not is_observer,
        "can_edit_team_entries": r in {"OWNER", "ADMIN", "OPERATIONS_LEAD"},
        "can_approve_requests": is_approver or r in {"OWNER", "APPROVER", "BUDGET_CONTROLLER"},
        "can_manage_vendors": is_vendor_manager or r in {"OWNER", "VENDOR_MANAGER"},
    }
