"""Reference data for the Group context (mobile contract).

Deterministic ids (UUID5) keep ``moment_type_id`` / ``profile_id`` stable across
restarts so both apps can cache them. This catalog powers the empty-state
surfaces (pulse / moments-home / create-options / templates) and the setup
profile pickers without needing the Postgres-only ``group_*`` reference tables.
"""
from __future__ import annotations

import uuid

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

GROUP_CONTEXT = "GROUP"


class GroupProfile:
    def __init__(
        self,
        code: str,
        name: str,
        display_order: int,
        description: str | None = None,
        icon_name: str | None = None,
        image_url: str | None = None,
    ) -> None:
        self.code = code
        self.name = name
        self.display_order = display_order
        self.description = description
        self.icon_name = icon_name
        self.image_url = image_url

    @property
    def profile_id(self) -> str:
        return str(uuid.uuid5(_NAMESPACE, f"group-profile:{self.code}"))


class GroupMomentType:
    def __init__(
        self,
        code: str,
        name: str,
        category: str,
        display_order: int,
        tagline: str,
        description: str,
        icon_name: str,
        accent_main: str,
        accent_soft_tint: str,
        card_layout: str,
        default_name: str,
        image_url: str | None,
        profiles: list[GroupProfile],
    ) -> None:
        self.code = code
        self.name = name
        self.category = category
        self.display_order = display_order
        self.tagline = tagline
        self.description = description
        self.icon_name = icon_name
        self.accent_main = accent_main
        self.accent_soft_tint = accent_soft_tint
        self.card_layout = card_layout
        self.default_name = default_name
        self.image_url = image_url
        self.profiles = profiles

    @property
    def type_id(self) -> str:
        return str(uuid.uuid5(_NAMESPACE, f"group:{self.code}"))


GROUP_MOMENT_TYPES: list[GroupMomentType] = [
    GroupMomentType(
        code="TRIP",
        name="Trips",
        category="trips",
        display_order=1,
        tagline="Plan and live shared journeys together.",
        description="Coordinate itineraries, budgets and people for any trip.",
        icon_name="airplane",
        accent_main="#4C6FFF",
        accent_soft_tint="#E8EDFF",
        card_layout="wide",
        default_name="Our Trip",
        image_url=None,
        profiles=[
            GroupProfile("TRIP_GETAWAY", "Weekend Getaway", 1, "A short shared escape."),
            GroupProfile("TRIP_ADVENTURE", "Adventure Trip", 2, "A bigger journey with more moving parts."),
            GroupProfile("TRIP_FAMILY", "Family Vacation", 3, "Travel with the whole family."),
        ],
    ),
    GroupMomentType(
        code="CELEBRATION",
        name="Celebrations",
        category="celebrations",
        display_order=2,
        tagline="Bring people together for the big moments.",
        description="Organise events, guests and shared costs in one place.",
        icon_name="party",
        accent_main="#EC4899",
        accent_soft_tint="#FCE7F3",
        card_layout="standard",
        default_name="Our Celebration",
        image_url=None,
        profiles=[
            GroupProfile("CELEBRATION_BIRTHDAY", "Birthday", 1, "Plan a birthday to remember."),
            GroupProfile("CELEBRATION_WEDDING", "Wedding", 2, "Coordinate a wedding with everyone involved."),
            GroupProfile("CELEBRATION_PARTY", "Party", 3, "Throw a get-together with shared effort."),
        ],
    ),
    GroupMomentType(
        code="HOUSEHOLD",
        name="Shared Living",
        category="ownership",
        display_order=3,
        tagline="Run a shared home with less friction.",
        description="Split chores, bills and shared purchases fairly.",
        icon_name="house",
        accent_main="#22C55E",
        accent_soft_tint="#DCFCE7",
        card_layout="standard",
        default_name="Our Home",
        image_url=None,
        profiles=[
            GroupProfile("HOUSEHOLD_ROOMMATES", "Roommates", 1, "Share a place with roommates."),
            GroupProfile("HOUSEHOLD_FAMILY", "Family Home", 2, "Coordinate a family household."),
        ],
    ),
    GroupMomentType(
        code="GOAL",
        name="Goals",
        category="goals",
        display_order=4,
        tagline="Chase shared goals as a team.",
        description="Track progress toward a goal you are building together.",
        icon_name="target",
        accent_main="#F59E0B",
        accent_soft_tint="#FEF3C7",
        card_layout="standard",
        default_name="Our Goal",
        image_url=None,
        profiles=[
            GroupProfile("GOAL_SAVINGS", "Savings Goal", 1, "Save toward something together."),
            GroupProfile("GOAL_PROJECT", "Group Project", 2, "Deliver a shared project."),
        ],
    ),
    GroupMomentType(
        code="FAMILY",
        name="Family",
        category="family",
        display_order=5,
        tagline="Coordinate everyday family life.",
        description="Keep the family in sync on plans, tasks and money.",
        icon_name="heart",
        accent_main="#F97316",
        accent_soft_tint="#FFEDD5",
        card_layout="standard",
        default_name="Our Family",
        image_url=None,
        profiles=[
            GroupProfile("FAMILY_HOUSEHOLD", "Household", 1, "Run the family household."),
            GroupProfile("FAMILY_CARE", "Care Circle", 2, "Coordinate care for loved ones."),
        ],
    ),
    GroupMomentType(
        code="SHARED_EXPERIENCE",
        name="Shared Experience",
        category="trips",
        display_order=10,
        tagline="Plan and live shared experiences together.",
        description="Coordinate trips, celebrations and shared experiences.",
        icon_name="sparkles",
        accent_main="#4C6FFF",
        accent_soft_tint="#E8EDFF",
        card_layout="wide",
        default_name="Our Experience",
        image_url=None,
        profiles=[
            GroupProfile("TRIP_VACATION", "Trip / Vacation", 1, "A shared trip or getaway."),
        ],
    ),
    GroupMomentType(
        code="SHARED_PURCHASE",
        name="Shared Purchase",
        category="goals",
        display_order=11,
        tagline="Buy or fund something together.",
        description="Track contributions toward a shared purchase or goal.",
        icon_name="cart",
        accent_main="#F59E0B",
        accent_soft_tint="#FEF3C7",
        card_layout="standard",
        default_name="Our Purchase",
        image_url=None,
        profiles=[
            GroupProfile("GROUP_GIFT", "Group Gift", 1, "A gift you are buying together."),
        ],
    ),
    GroupMomentType(
        code="SHARED_LIVING",
        name="Shared Living",
        category="ownership",
        display_order=12,
        tagline="Run a shared home with less friction.",
        description="Split chores, bills and household coordination fairly.",
        icon_name="house",
        accent_main="#22C55E",
        accent_soft_tint="#DCFCE7",
        card_layout="standard",
        default_name="Our Home",
        image_url=None,
        profiles=[
            GroupProfile("ROOMMATES", "Roommates", 1, "Share a place with roommates."),
        ],
    ),
]

GROUP_TYPES_BY_CODE: dict[str, GroupMomentType] = {mt.code: mt for mt in GROUP_MOMENT_TYPES}


def group_type_id(code: str) -> str:
    mt = GROUP_TYPES_BY_CODE.get(code)
    if mt is not None:
        return mt.type_id
    return str(uuid.uuid5(_NAMESPACE, f"group:{code}"))


def group_type_name(code: str) -> str:
    mt = GROUP_TYPES_BY_CODE.get(code)
    return mt.name if mt else (code or "").replace("_", " ").title() or "Group Moment"


def group_default_name(code: str) -> str:
    mt = GROUP_TYPES_BY_CODE.get(code)
    return mt.default_name if mt else group_type_name(code)


def group_profiles_for(code: str) -> list[GroupProfile]:
    mt = GROUP_TYPES_BY_CODE.get(code)
    return list(mt.profiles) if mt else []
