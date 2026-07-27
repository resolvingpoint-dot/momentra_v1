"""Shared Experience (trip) quick-add module mapping and hub metadata."""
from __future__ import annotations

from app.domains.group.activity.types import ActivityType

TRIP_QUICK_ADD_MAP: dict[str, ActivityType] = {
    "participant": ActivityType.PARTICIPANT,
    "planning_item": ActivityType.PLANNING_ITEM,
    "planning-item": ActivityType.PLANNING_ITEM,
    "booking": ActivityType.BOOKING,
    "expense": ActivityType.EXPENSE,
    "contribution": ActivityType.CONTRIBUTION,
    "vendor": ActivityType.VENDOR,
    "attendance": ActivityType.ATTENDANCE,
    "update": ActivityType.UPDATE,
    "memory": ActivityType.MEMORY,
    "poll": ActivityType.POLL,
}

TRIP_SECTION_ORDER: list[tuple[str, str]] = [
    ("people", "People"),
    ("planning", "Planning"),
    ("money", "Money"),
    ("support", "Support"),
    ("memory_decisions", "Memory & Decisions"),
]

TRIP_MODULE_SECTION: dict[str, str] = {
    "PARTICIPANT": "people",
    "PLANNING_ITEM": "planning",
    "BOOKING": "planning",
    "EXPENSE": "money",
    "CONTRIBUTION": "money",
    "BUDGET": "money",
    "VENDOR": "support",
    "ATTENDANCE": "support",
    "UPDATE": "support",
    "MEMORY": "memory_decisions",
    "POLL": "memory_decisions",
}

TRIP_MODULE_META: dict[str, dict[str, str]] = {
    "PARTICIPANT": {
        "label": "Participant",
        "icon": "person_add",
        "description": "Invite people and assign roles",
    },
    "PLANNING_ITEM": {
        "label": "Planning Item",
        "icon": "task_alt",
        "description": "Tasks, reminders, and milestones",
    },
    "BOOKING": {
        "label": "Booking",
        "icon": "flight_takeoff",
        "description": "Stays, travel, and activities",
    },
    "EXPENSE": {
        "label": "Expense",
        "icon": "payments",
        "description": "Split costs with the group",
    },
    "CONTRIBUTION": {
        "label": "Contribution",
        "icon": "savings",
        "description": "Track pooled contributions",
    },
    "BUDGET": {
        "label": "Budget",
        "icon": "account_balance_wallet",
        "description": "Plan expected costs and contribution share",
    },
    "VENDOR": {
        "label": "Vendor",
        "icon": "handshake",
        "description": "Add vendors and contacts",
    },
    "ATTENDANCE": {
        "label": "Attendance",
        "icon": "checklist",
        "description": "Log who is coming",
    },
    "UPDATE": {
        "label": "Update",
        "icon": "campaign",
        "description": "Share news with the group",
    },
    "MEMORY": {
        "label": "Capture Memory",
        "icon": "photo_library",
        "description": "Photos and highlights",
    },
    "POLL": {
        "label": "Poll",
        "icon": "how_to_vote",
        "description": "Decide together",
    },
}


def activity_type_for_module(module: str) -> ActivityType | None:
    key = module.strip().lower().replace("-", "_")
    return TRIP_QUICK_ADD_MAP.get(key)


def build_trip_quick_add_categories(module_codes: list[str]) -> list[dict]:
    """Group enabled modules into sectioned hub categories."""
    enabled = {code.upper() for code in module_codes}
    categories: list[dict] = []
    for section_id, section_label in TRIP_SECTION_ORDER:
        modules: list[dict] = []
        for code in module_codes:
            upper = code.upper()
            if upper not in enabled:
                continue
            if TRIP_MODULE_SECTION.get(upper) != section_id:
                continue
            meta = TRIP_MODULE_META.get(upper, {})
            modules.append(
                {
                    "module_code": upper,
                    "label": meta.get("label", upper.replace("_", " ").title()),
                    "icon": meta.get("icon", "add"),
                    "description": meta.get("description", ""),
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
