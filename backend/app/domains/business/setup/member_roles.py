"""Map setup API member role codes → business_moment_members.role CHECK values."""
from __future__ import annotations

# Mirrors chk_member_role on business_moment_members.
DB_MEMBER_ROLES: frozenset[str] = frozenset(
    {
        "Team Member",
        "Team Lead",
        "Budget Owner",
        "Approver",
        "Observer",
        "Runway Owner",
        "Finance Lead",
        "Operations Lead",
        "Financial Contributor",
        "Viewer",
        "Operations Owner",
        "Budget Controller",
        "Contributor",
    }
)

_OWNER_BY_TEMPLATE: dict[str, str] = {
    "team_operations": "Team Lead",
    "TEAM_OPERATIONS": "Team Lead",
    "business_operations": "Operations Owner",
    "BUSINESS_OPERATIONS": "Operations Owner",
    "business_runway": "Runway Owner",
    "BUSINESS_RUNWAY": "Runway Owner",
}

_API_TO_DB: dict[str, str] = {
    "MEMBER": "Team Member",
    "TEAM_MEMBER": "Team Member",
    "TEAM_LEAD": "Team Lead",
    "ADMIN": "Team Lead",
    "BUDGET_OWNER": "Budget Owner",
    "APPROVER": "Approver",
    "OBSERVER": "Observer",
    "VIEWER": "Viewer",
    "RUNWAY_OWNER": "Runway Owner",
    "FOUNDER": "Runway Owner",
    "FINANCE_LEAD": "Finance Lead",
    "OPERATIONS_LEAD": "Operations Lead",
    "FINANCIAL_CONTRIBUTOR": "Financial Contributor",
    "CONTRIBUTOR": "Contributor",
    "OPERATIONS_OWNER": "Operations Owner",
    "BUDGET_CONTROLLER": "Budget Controller",
}


def to_db_member_role(role: str | None, *, template_code: str = "team_operations") -> str:
    """Convert draft/API role codes to a value accepted by chk_member_role."""
    raw = str(role or "MEMBER").strip()
    if raw in DB_MEMBER_ROLES:
        return raw
    key = raw.upper().replace(" ", "_").replace("-", "_")
    if key == "OWNER":
        return _OWNER_BY_TEMPLATE.get(template_code, "Team Lead")
    return _API_TO_DB.get(key, "Team Member")
