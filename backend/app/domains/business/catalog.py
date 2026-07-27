"""Reference data for the Business context (mobile contract).

Canonical v1 templates (Run 0 freeze):
  TEAM_OPERATIONS, BUSINESS_RUNWAY, BUSINESS_OPERATIONS

Unsupported / future catalog cards (gated — not creatable in v1):
  PROJECT_OPERATIONS, EVENT_OPERATIONS, VENDOR_OPERATIONS, CUSTOM_OPERATIONAL_MOMENT

Ids are deterministic (UUID5) so clients can cache them. This catalog powers
empty-state surfaces (pulse dimension cards / moments-home / create-options).
"""
from __future__ import annotations

import uuid

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

BUSINESS_CONTEXT = "BUSINESS"

# Canonical UPPER codes clients must use.
TEAM_OPERATIONS = "TEAM_OPERATIONS"
BUSINESS_RUNWAY = "BUSINESS_RUNWAY"
BUSINESS_OPERATIONS = "BUSINESS_OPERATIONS"

PROJECT_OPERATIONS = "PROJECT_OPERATIONS"
EVENT_OPERATIONS = "EVENT_OPERATIONS"
VENDOR_OPERATIONS = "VENDOR_OPERATIONS"
CUSTOM_OPERATIONAL_MOMENT = "CUSTOM_OPERATIONAL_MOMENT"

# Read/write aliases → canonical UPPER.
_TYPE_ALIASES: dict[str, str] = {
    "team_operations": TEAM_OPERATIONS,
    "TEAM_OPERATIONS": TEAM_OPERATIONS,
    "business_runway": BUSINESS_RUNWAY,
    "BUSINESS_RUNWAY": BUSINESS_RUNWAY,
    "business-runway": BUSINESS_RUNWAY,
    "runway": BUSINESS_RUNWAY,
    "business_operations": BUSINESS_OPERATIONS,
    "BUSINESS_OPERATIONS": BUSINESS_OPERATIONS,
    "business-operations": BUSINESS_OPERATIONS,
    "operations": BUSINESS_OPERATIONS,
    "department_operations": BUSINESS_OPERATIONS,
    "DEPARTMENT_OPERATIONS": BUSINESS_OPERATIONS,
    "project_operations": PROJECT_OPERATIONS,
    "PROJECT_OPERATIONS": PROJECT_OPERATIONS,
    "event_operations": EVENT_OPERATIONS,
    "EVENT_OPERATIONS": EVENT_OPERATIONS,
    "vendor_operations": VENDOR_OPERATIONS,
    "VENDOR_OPERATIONS": VENDOR_OPERATIONS,
    "custom_operational_moment": CUSTOM_OPERATIONAL_MOMENT,
    "CUSTOM_OPERATIONAL_MOMENT": CUSTOM_OPERATIONAL_MOMENT,
}


class BusinessDimension:
    def __init__(
        self,
        code: str,
        name: str,
        display_order: int,
        tagline: str,
        description: str,
        badge_label: str,
        icon_name: str,
        accent_main: str,
        accent_soft_tint: str,
        *,
        is_available: bool = True,
        implementation_status: str = "active",
    ) -> None:
        self.code = code
        self.name = name
        self.display_order = display_order
        self.tagline = tagline
        self.description = description
        self.badge_label = badge_label
        self.icon_name = icon_name
        self.accent_main = accent_main
        self.accent_soft_tint = accent_soft_tint
        self.is_available = is_available
        self.implementation_status = implementation_status

    @property
    def type_id(self) -> str:
        return str(uuid.uuid5(_NAMESPACE, f"business:{self.code}"))


# v1 creatable templates — also drive pulse / moments-home dimension cards.
BUSINESS_DIMENSIONS: list[BusinessDimension] = [
    BusinessDimension(
        code=TEAM_OPERATIONS,
        name="Team Operations",
        display_order=1,
        tagline=(
            "Coordinate your people, meetings, responsibilities and "
            "day-to-day execution from one shared place."
        ),
        description="Coordinate work, approvals, participation and escalation for your operating team.",
        badge_label="Recommended First",
        icon_name="groups",
        accent_main="#5B5CEB",
        accent_soft_tint="#E8EDFF",
    ),
    BusinessDimension(
        code=BUSINESS_RUNWAY,
        name="Business Runway",
        display_order=2,
        tagline=(
            "Monitor cash flow, spending and runway so your business can "
            "make confident financial decisions."
        ),
        description="Watch cash in, cash out and how many months of runway you have.",
        badge_label="Most Popular",
        icon_name="wallet",
        accent_main="#10B981",
        accent_soft_tint="#D1FAE5",
    ),
    BusinessDimension(
        code=BUSINESS_OPERATIONS,
        name="Business Operations",
        display_order=3,
        tagline=(
            "Keep everyday business operations organized across departments, "
            "processes and workflows."
        ),
        description="Manage spend, vendors, approvals and operational improvements.",
        badge_label="Run Efficiently",
        icon_name="settings",
        accent_main="#F97316",
        accent_soft_tint="#FFEDD5",
    ),
]

# Catalog-gated future templates — shown on create options, not creatable in v1.
BUSINESS_UNSUPPORTED_DIMENSIONS: list[BusinessDimension] = [
    BusinessDimension(
        code=PROJECT_OPERATIONS,
        name="Project Operations",
        display_order=10,
        tagline=(
            "Plan, coordinate and deliver projects while keeping teams, "
            "timelines and milestones aligned."
        ),
        description="Coming in a future release — not available for create in v1.",
        badge_label="Deliver Projects",
        icon_name="folder",
        accent_main="#3B82F6",
        accent_soft_tint="#CFFAFE",
        is_available=False,
        implementation_status="coming_soon",
    ),
    BusinessDimension(
        code=EVENT_OPERATIONS,
        name="Event Operations",
        display_order=11,
        tagline=(
            "Organize business events from planning through execution with "
            "complete team coordination."
        ),
        description="Coming in a future release — not available for create in v1.",
        badge_label="Coordinate Events",
        icon_name="calendar",
        accent_main="#F59E0B",
        accent_soft_tint="#FEF3C7",
        is_available=False,
        implementation_status="coming_soon",
    ),
    BusinessDimension(
        code=VENDOR_OPERATIONS,
        name="Vendor Operations",
        display_order=12,
        tagline=(
            "Manage vendors, procurement, contracts and supplier "
            "relationships from one organized workspace."
        ),
        description="Coming in a future release — not available for create in v1.",
        badge_label="Partner Management",
        icon_name="handshake",
        accent_main="#8B5A2B",
        accent_soft_tint="#EDE9FE",
        is_available=False,
        implementation_status="coming_soon",
    ),
    BusinessDimension(
        code=CUSTOM_OPERATIONAL_MOMENT,
        name="Custom Operational Moment",
        display_order=13,
        tagline="Build a completely custom operational system.",
        description="Coming in a future release — not available for create in v1.",
        badge_label="Coming Soon",
        icon_name="sparkles",
        accent_main="#5B5CEB",
        accent_soft_tint="#E8EDFF",
        is_available=False,
        implementation_status="coming_soon",
    ),
]

BUSINESS_CREATE_CATALOG: list[BusinessDimension] = [
    *BUSINESS_DIMENSIONS,
    *BUSINESS_UNSUPPORTED_DIMENSIONS,
]

BUSINESS_DIMENSIONS_BY_CODE: dict[str, BusinessDimension] = {
    d.code: d for d in BUSINESS_CREATE_CATALOG
}

V1_CREATABLE_CODES: frozenset[str] = frozenset(d.code for d in BUSINESS_DIMENSIONS)
UNSUPPORTED_CODES: frozenset[str] = frozenset(d.code for d in BUSINESS_UNSUPPORTED_DIMENSIONS)


def normalize_moment_type_code(code: str | None) -> str | None:
    """Map aliases / mixed case to canonical UPPER. Returns None if unknown."""
    if not code:
        return None
    raw = code.strip()
    if not raw:
        return None
    if raw in _TYPE_ALIASES:
        return _TYPE_ALIASES[raw]
    upper = raw.upper()
    if upper in _TYPE_ALIASES:
        return _TYPE_ALIASES[upper]
    return None


def business_type_id(code: str) -> str:
    canonical = normalize_moment_type_code(code) or (code or "").upper()
    d = BUSINESS_DIMENSIONS_BY_CODE.get(canonical)
    if d is not None:
        return d.type_id
    return str(uuid.uuid5(_NAMESPACE, f"business:{canonical}"))


def business_type_name(code: str) -> str:
    canonical = normalize_moment_type_code(code) or (code or "").upper()
    d = BUSINESS_DIMENSIONS_BY_CODE.get(canonical)
    return d.name if d else (canonical or "").replace("_", " ").title() or "Business Moment"
