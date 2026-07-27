"""Shared Purchase quick-add module mapping and hub metadata."""
from __future__ import annotations

from app.domains.group.activity.types import ActivityType

# API path slugs (lowercase, hyphenated) → activity type
PURCHASE_QUICK_ADD_MAP: dict[str, ActivityType] = {
    "contributors": ActivityType.PARTICIPANT,
    "participants": ActivityType.PARTICIPANT,
    "purchase-items": ActivityType.TASK,
    "vendors": ActivityType.VENDOR,
    "expenses": ActivityType.EXPENSE,
    "polls": ActivityType.POLL,
    "updates": ActivityType.UPDATE,
    "ownership": ActivityType.OWNERSHIP_UPDATE,
    "delivery": ActivityType.MILESTONE,
    "memories": ActivityType.MEMORY,
    "contributions": ActivityType.CONTRIBUTION,
    "payments": ActivityType.PAYMENT,
    "installments": ActivityType.INSTALLMENT,
    "decisions": ActivityType.DECISION,
    "notes": ActivityType.NOTE,
    "documents": ActivityType.DOCUMENT_PLACEHOLDER,
}

# Stitch hub order: Contributors → Purchase → Decisions → Ownership → Memory
PURCHASE_SECTION_ORDER: list[tuple[str, str]] = [
    ("contributors", "Contributors"),
    ("purchase", "Purchase"),
    ("decisions", "Decisions"),
    ("ownership", "Ownership"),
    ("memory", "Memory"),
]

PURCHASE_MODULE_SECTION: dict[str, str] = {
    "CONTRIBUTORS": "contributors",
    "PARTICIPANTS": "contributors",
    "PURCHASE_ITEMS": "purchase",
    "VENDORS": "purchase",
    "EXPENSES": "purchase",
    "POLLS": "decisions",
    "UPDATES": "decisions",
    "OWNERSHIP": "ownership",
    "DELIVERY": "ownership",
    "MEMORIES": "memory",
}

PURCHASE_MODULE_META: dict[str, dict[str, str]] = {
    "CONTRIBUTORS": {
        "label": "Contributor",
        "icon": "person_add",
        "description": "Invite people funding this purchase",
    },
    "PARTICIPANTS": {
        "label": "Participants",
        "icon": "group_add",
        "description": "Manage who is involved",
    },
    "PURCHASE_ITEMS": {
        "label": "Purchase Item",
        "icon": "shopping_cart",
        "description": "Add items and targets",
    },
    "VENDORS": {
        "label": "Vendor",
        "icon": "storefront",
        "description": "Compare vendors and quotes",
    },
    "EXPENSES": {
        "label": "Expense",
        "icon": "receipt_long",
        "description": "Record purchase spend",
    },
    "POLLS": {
        "label": "Poll",
        "icon": "how_to_vote",
        "description": "Decide together",
    },
    "UPDATES": {
        "label": "Update",
        "icon": "campaign",
        "description": "Share progress with the group",
    },
    "OWNERSHIP": {
        "label": "Ownership",
        "icon": "supervised_user_circle",
        "description": "Assign shares and usage rights",
    },
    "DELIVERY": {
        "label": "Delivery / Handover",
        "icon": "local_shipping",
        "description": "Track shipping and handover",
    },
    "MEMORIES": {
        "label": "Memory",
        "icon": "photo_library",
        "description": "Capture purchase highlights",
    },
}


def _slug(module: str) -> str:
    return module.strip().lower().replace("_", "-")


def activity_type_for_module(module: str) -> ActivityType | None:
    return PURCHASE_QUICK_ADD_MAP.get(_slug(module))


def module_api_slug(module_code: str) -> str:
    """Hub module_code → REST path segment."""
    return _slug(module_code)


def build_purchase_quick_add_categories(module_codes: list[str]) -> list[dict]:
    """Group enabled modules into sectioned hub categories (Stitch order)."""
    # Normalize legacy activity-style codes to Stitch hub codes
    legacy_alias = {
        "CONTRIBUTION": "CONTRIBUTORS",
        "PARTICIPANT": "PARTICIPANTS",
        "VENDOR": "VENDORS",
        "EXPENSE": "EXPENSES",
        "POLL": "POLLS",
        "UPDATE": "UPDATES",
        "OWNERSHIP_UPDATE": "OWNERSHIP",
        "MILESTONE": "DELIVERY",
        "MEMORY": "MEMORIES",
        "TASK": "PURCHASE_ITEMS",
        "PAYMENT": "EXPENSES",
        "INSTALLMENT": "EXPENSES",
        "DECISION": "POLLS",
        "NOTE": "UPDATES",
    }
    normalized: list[str] = []
    seen: set[str] = set()
    for code in module_codes:
        upper = code.upper().replace("-", "_")
        mapped = legacy_alias.get(upper, upper)
        if mapped not in PURCHASE_MODULE_META:
            continue
        if mapped in seen:
            continue
        seen.add(mapped)
        normalized.append(mapped)

    # If profile still empty after aliasing, fall back to full Stitch set
    if not normalized:
        normalized = list(PURCHASE_MODULE_META.keys())

    categories: list[dict] = []
    for section_id, section_label in PURCHASE_SECTION_ORDER:
        modules: list[dict] = []
        for upper in normalized:
            if PURCHASE_MODULE_SECTION.get(upper) != section_id:
                continue
            meta = PURCHASE_MODULE_META[upper]
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
