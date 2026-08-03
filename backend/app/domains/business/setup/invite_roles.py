"""Role catalogs and authorization for Business setup / switcher invites."""

from __future__ import annotations

from app.domains.business.catalog import (
    BUSINESS_OPERATIONS,
    BUSINESS_RUNWAY,
    TEAM_OPERATIONS,
    normalize_moment_type_code,
)
from app.domains.business.setup.business_operations_permissions import (
    SUPPORTED_ROLES_V1 as OPS_ROLES,
)
from app.domains.business.setup.runway_permissions import (
    SUPPORTED_ROLES_V1 as RUNWAY_ROLES,
)
from app.domains.business.setup.team_ops_permissions import (
    SUPPORTED_ROLES_V1 as TEAM_ROLES,
)

# Inviter must hold one of these API role codes (or be moment owner).
INVITER_API_ROLES: frozenset[str] = frozenset(
    {
        "OWNER",
        "ADMIN",
        "TEAM_LEAD",
        "OPERATIONS_LEAD",
        "FOUNDER",
    }
)

# DB title-case roles that can invite (BusinessMomentMembers.role).
INVITER_DB_ROLES: frozenset[str] = frozenset(
    {
        "Team Lead",
        "Operations Lead",
        "Operations Owner",
        "Runway Owner",
        "Budget Owner",  # not primary, but finance leads often manage roster
        "Finance Lead",
    }
)

_ROLES_BY_CODE: dict[str, frozenset[str]] = {
    TEAM_OPERATIONS: frozenset(TEAM_ROLES),
    "TEAM_OPERATIONS": frozenset(TEAM_ROLES),
    BUSINESS_RUNWAY: frozenset(RUNWAY_ROLES),
    "BUSINESS_RUNWAY": frozenset(RUNWAY_ROLES),
    BUSINESS_OPERATIONS: frozenset(OPS_ROLES),
    "BUSINESS_OPERATIONS": frozenset(OPS_ROLES),
}


def roles_for_moment_type(moment_type: str | None) -> frozenset[str]:
    code = normalize_moment_type_code(moment_type or TEAM_OPERATIONS) or TEAM_OPERATIONS
    return _ROLES_BY_CODE.get(code, frozenset(TEAM_ROLES))


def default_invitee_role(moment_type: str | None) -> str:
    allowed = roles_for_moment_type(moment_type)
    if "MEMBER" in allowed:
        return "MEMBER"
    if "CONTRIBUTOR" in allowed:
        return "CONTRIBUTOR"
    if "OBSERVER" in allowed:
        return "OBSERVER"
    return next(iter(sorted(r for r in allowed if r != "OWNER")), "MEMBER")


def normalize_api_role(role: str | None) -> str:
    return str(role or "").strip().upper().replace(" ", "_").replace("-", "_")


def validate_invitee_role(role: str | None, *, moment_type: str | None) -> str:
    """Return normalized invitee role or raise ValueError."""
    key = normalize_api_role(role)
    if not key:
        raise ValueError("role is required")
    if key == "OWNER":
        raise ValueError("Cannot invite as OWNER")
    allowed = roles_for_moment_type(moment_type)
    if key not in allowed:
        raise ValueError(f"Invalid role for this moment type: {key}")
    return key


def inviter_api_role_allowed(role: str | None) -> bool:
    key = normalize_api_role(role)
    return key in INVITER_API_ROLES


def inviter_db_role_allowed(db_role: str | None) -> bool:
    raw = str(db_role or "").strip()
    if raw in INVITER_DB_ROLES:
        return True
    # Map common API codes stored incorrectly as uppercase.
    return inviter_api_role_allowed(raw)
