"""Shared Living quick-add module mapping and hub metadata."""
from __future__ import annotations

from app.domains.group.activity.types import ActivityType

LIVING_QUICK_ADD_MAP: dict[str, ActivityType] = {
    "residents": ActivityType.MEMBER_UPDATE,
    "expenses": ActivityType.EXPENSE,
    "contributions": ActivityType.CONTRIBUTION,
    "tasks": ActivityType.CHORE,
    "rules": ActivityType.NOTE,
    "assets": ActivityType.HOUSEHOLD_PURCHASE,
    "maintenance": ActivityType.MAINTENANCE,
    "updates": ActivityType.UPDATE,
    "polls": ActivityType.POLL,
    "memories": ActivityType.HOME_MEMORY,
}

LIVING_SECTION_ORDER: list[tuple[str, str]] = [
    ("people", "People"),
    ("money", "Money"),
    ("responsibilities", "Responsibilities"),
    ("home", "Home"),
    ("memory_decisions", "Memory & Decisions"),
]

LIVING_MODULE_SECTION: dict[str, str] = {
    "RESIDENTS": "people",
    "EXPENSES": "money",
    "CONTRIBUTIONS": "money",
    "TASKS": "responsibilities",
    "RULES": "responsibilities",
    "ASSETS": "home",
    "MAINTENANCE": "home",
    "UPDATES": "memory_decisions",
    "POLLS": "memory_decisions",
    "MEMORIES": "memory_decisions",
}

LIVING_MODULE_META: dict[str, dict[str, str]] = {
    "RESIDENTS": {
        "label": "Resident",
        "icon": "person_add",
        "description": "Invite people who live here",
    },
    "EXPENSES": {
        "label": "Expense",
        "icon": "payments",
        "description": "Rent, utilities, groceries",
    },
    "CONTRIBUTIONS": {
        "label": "Contribution",
        "icon": "savings",
        "description": "Record money put in",
    },
    "TASKS": {
        "label": "Task",
        "icon": "checklist",
        "description": "Chores and household tasks",
    },
    "RULES": {
        "label": "Rule",
        "icon": "gavel",
        "description": "House agreements",
    },
    "ASSETS": {
        "label": "Asset",
        "icon": "inventory_2",
        "description": "Shared belongings",
    },
    "MAINTENANCE": {
        "label": "Maintenance",
        "icon": "build",
        "description": "Repairs and upkeep",
    },
    "UPDATES": {
        "label": "Update",
        "icon": "campaign",
        "description": "Share news with residents",
    },
    "POLLS": {
        "label": "Poll",
        "icon": "how_to_vote",
        "description": "Decide together",
    },
    "MEMORIES": {
        "label": "Memory",
        "icon": "photo_library",
        "description": "Capture home moments",
    },
}


def _slug(module: str) -> str:
    return module.strip().lower().replace("_", "-")


def activity_type_for_module(module: str) -> ActivityType | None:
    slug = module.strip().lower().replace("_", "-")
    return LIVING_QUICK_ADD_MAP.get(slug) or LIVING_QUICK_ADD_MAP.get(slug.replace("-", ""))


def module_api_slug(module_code: str) -> str:
    return module_code.strip().lower().replace("_", "-")


def build_living_quick_add_categories(module_codes: list[str]) -> list[dict]:
    """Group enabled modules into sectioned hub categories (Stitch order)."""
    normalized: list[str] = []
    seen: set[str] = set()
    for code in module_codes:
        upper = code.upper().replace("-", "_")
        if upper not in LIVING_MODULE_META:
            continue
        if upper in seen:
            continue
        seen.add(upper)
        normalized.append(upper)

    if not normalized:
        normalized = list(LIVING_MODULE_META.keys())

    categories: list[dict] = []
    for section_id, section_label in LIVING_SECTION_ORDER:
        modules: list[dict] = []
        for upper in normalized:
            if LIVING_MODULE_SECTION.get(upper) != section_id:
                continue
            meta = LIVING_MODULE_META[upper]
            modules.append(
                {
                    "module_code": upper,
                    "label": meta["label"],
                    "icon": meta["icon"],
                    "description": meta["description"],
                }
            )
        if modules:
            categories.append(
                {
                    "id": section_id,
                    "label": section_label,
                    "modules": modules,
                }
            )
    return categories
