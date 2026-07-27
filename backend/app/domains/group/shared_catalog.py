"""Reference data for the Android Group *shared-\\** subsystem.

The Android client models three shared-moment *categories* — ``SHARED_EXPERIENCE``,
``SHARED_PURCHASE`` and ``SHARED_LIVING`` — each with its own profile picker and
setup enum options (money-tracking / funding / management styles, coordination
modules). This mirrors the client's expected contract so the dedicated
``/group/shared-*`` setup endpoints return real, stable option lists without the
Postgres-only ``group_*`` reference tables.
"""
from __future__ import annotations

import uuid

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

EXPERIENCE = "SHARED_EXPERIENCE"
PURCHASE = "SHARED_PURCHASE"
LIVING = "SHARED_LIVING"


class SharedProfile:
    def __init__(
        self,
        code: str,
        name: str,
        display_order: int,
        description: str | None = None,
        icon_name: str | None = None,
    ) -> None:
        self.code = code
        self.name = name
        self.display_order = display_order
        self.description = description
        self.icon_name = icon_name

    @property
    def profile_id(self) -> str:
        return str(uuid.uuid5(_NAMESPACE, f"shared-profile:{self.code}"))


class EnumOption:
    def __init__(self, code: str, label: str, description: str | None = None) -> None:
        self.code = code
        self.label = label
        self.description = description


class ModuleOption:
    def __init__(self, code: str, label: str, is_default: bool = False, icon_name: str | None = None) -> None:
        self.code = code
        self.label = label
        self.is_default = is_default
        self.icon_name = icon_name


PROFILES: dict[str, list[SharedProfile]] = {
    EXPERIENCE: [
        SharedProfile("TRIP_VACATION", "Trip / Vacation", 1, "Travel, adventures and shared journeys.", "airplane"),
        SharedProfile("WEDDING", "Wedding", 2, "Ceremonies and celebrations.", "rings"),
        SharedProfile("CELEBRATION", "Celebration", 3, "Birthdays and social gatherings.", "party"),
        SharedProfile("OFFICE_OUTING", "Office Outing", 4, "Team retreats and colleague experiences.", "briefcase"),
    ],
    PURCHASE: [
        SharedProfile("GIFT_POOL", "Gift Pool", 1, "Pool money for a group gift.", "gift"),
        SharedProfile("GROUP_PURCHASE", "Group Purchase", 2, "Buy items together as a group.", "cart"),
        SharedProfile("SHARED_ASSET", "Shared Asset", 3, "Co-own an asset together.", "key"),
        SharedProfile("CUSTOM_PURCHASE", "Custom Purchase", 4, "Define your own shared purchase.", "sliders"),
    ],
    LIVING: [
        SharedProfile("FLATMATES", "Flatmates", 1, "Shared apartment with roommates.", "house"),
        SharedProfile("FAMILY_HOUSEHOLD", "Family Household", 2, "Multi-generational family home.", "family"),
        SharedProfile("COLIVING", "Co-Living", 3, "Community-focused shared spaces.", "community"),
        SharedProfile("CUSTOM_LIVING", "Custom Living", 4, "Your own arrangement.", "sliders"),
    ],
}

MONEY_TRACKING_MODES: list[EnumOption] = [
    EnumOption("NO_MONEY", "No money tracking", "Just coordinate — no shared costs."),
    EnumOption("SPLIT_LATER", "Split expenses", "Track shared costs and settle up later."),
    EnumOption("SHARED_POOL", "Shared pool", "Everyone contributes to a common pool."),
]

PLANNING_STYLES: list[EnumOption] = [
    EnumOption("SIMPLE", "Simple", "A light checklist to stay in sync."),
    EnumOption("DETAILED", "Detailed", "Full itinerary, tasks and approvals."),
]

FUNDING_STYLES: list[EnumOption] = [
    EnumOption("SUGGESTED", "Suggested amounts", "Suggest a per-person amount."),
    EnumOption("EQUAL", "Equal split", "Split the target equally."),
    EnumOption("OPEN", "Open contributions", "Anyone contributes any amount."),
]

MANAGEMENT_STYLES: list[EnumOption] = [
    EnumOption("SHARED", "Shared equally", "Everyone manages together."),
    EnumOption("LEAD", "Lead-managed", "One person coordinates."),
    EnumOption("ROTATION", "Rotating", "Responsibilities rotate."),
]

EXPERIENCE_MODULES: list[ModuleOption] = [
    ModuleOption("ITINERARY", "Itinerary", True, "map"),
    ModuleOption("EXPENSES", "Expenses", True, "wallet"),
    ModuleOption("POLLS", "Polls", False, "check-circle"),
    ModuleOption("TASKS", "Tasks", False, "list"),
    ModuleOption("MEMORIES", "Memories", True, "camera"),
]

PURCHASE_MODULES: list[ModuleOption] = [
    ModuleOption("CONTRIBUTIONS", "Contributions", True, "wallet"),
    ModuleOption("VENDORS", "Vendors", True, "store"),
    ModuleOption("OWNERSHIP", "Ownership", False, "key"),
    ModuleOption("DELIVERY", "Delivery", False, "truck"),
    ModuleOption("UPDATES", "Updates", True, "bell"),
]

LIVING_MODULES: list[ModuleOption] = [
    ModuleOption("RESIDENTS", "Residents", True, "users"),
    ModuleOption("EXPENSES", "Expenses", True, "wallet"),
    ModuleOption("TASKS", "Chores", True, "list"),
    ModuleOption("RULES", "House rules", False, "book"),
    ModuleOption("ASSETS", "Assets", False, "box"),
]

AUDIENCE_TAGS: list[tuple[str, str]] = [
    ("FRIENDS", "Friends"),
    ("FAMILY", "Family"),
    ("COLLEAGUES", "Colleagues"),
    ("COUPLE", "Couple"),
]


def profiles_for(category: str) -> list[SharedProfile]:
    return PROFILES.get(category, [])


def profile(category: str, code: str) -> SharedProfile | None:
    for p in profiles_for(category):
        if p.code == code:
            return p
    return None


def profile_name(category: str, code: str | None) -> str:
    if code:
        p = profile(category, code)
        if p:
            return p.name
    profs = profiles_for(category)
    return profs[0].name if profs else (code or "").replace("_", " ").title()


def default_modules(category: str) -> list[str]:
    mods = {EXPERIENCE: EXPERIENCE_MODULES, PURCHASE: PURCHASE_MODULES, LIVING: LIVING_MODULES}.get(category, [])
    return [m.code for m in mods if m.is_default]


def enum_label(options: list[EnumOption], code: str | None) -> str:
    for o in options:
        if o.code == code:
            return o.label
    return (code or "").replace("_", " ").title()
