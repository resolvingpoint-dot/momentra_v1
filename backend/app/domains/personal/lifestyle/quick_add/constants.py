"""Lifestyle quick-add constants — mirrors web registry metadata."""
from __future__ import annotations

from typing import Any

from app.domains.personal.lifestyle.quick_add.handlers.mappings import (
    ADJUSTMENT_AREAS,
    CONFIDENCE_LEVELS,
    DISCOVERY_IMPACTS,
    ENERGY_IMPACTS,
    EXPERIENCE_QUALITIES,
    PRIORITY_LEVELS,
    SATISFACTION_LEVELS,
    VALUE_RECEIVED,
    WELLBEING_STATES,
)

EVENT_TO_TAB: dict[str, str] = {
    "LIFESTYLE_EXPENSE": "EXPENSE",
    "EXPERIENCE": "EXPERIENCE",
    "WELLBEING": "WELLBEING",
    "DISCOVERY": "DISCOVERY",
    "EXPRESSION": "EXPRESSION",
    "ADJUST": "ADJUST",
}

EVENT_ALIASES: dict[str, str] = {
    "CREATIVE": "EXPRESSION",
    "LIFESTYLE_ADJUST": "ADJUST",
}

LIFESTYLE_QUICK_ADD_TABS: list[dict[str, Any]] = [
    {
        "event_type": "LIFESTYLE_EXPENSE",
        "tab_code": "EXPENSE",
        "label": "Expense",
        "display_order": 1,
        "hero_title": "Expense",
        "hero_subtitle": "What was this expense for?",
        "description": "Record lifestyle spending",
        "cta_label": "Save Expense",
    },
    {
        "event_type": "EXPERIENCE",
        "tab_code": "EXPERIENCE",
        "label": "Experience",
        "display_order": 2,
        "hero_title": "Experience",
        "hero_subtitle": "What did you experience?",
        "description": "Save a memorable moment",
        "cta_label": "Save Experience",
    },
    {
        "event_type": "WELLBEING",
        "tab_code": "WELLBEING",
        "label": "Wellbeing",
        "display_order": 3,
        "hero_title": "Wellbeing",
        "hero_subtitle": "Which life area are you checking in on?",
        "description": "Check in on a life area",
        "cta_label": "Save Wellbeing Check-in",
    },
    {
        "event_type": "DISCOVERY",
        "tab_code": "DISCOVERY",
        "label": "Discover",
        "display_order": 4,
        "hero_title": "Discover",
        "hero_subtitle": "What did you discover?",
        "description": "Capture a new curiosity",
        "cta_label": "Save Discovery",
    },
    {
        "event_type": "EXPRESSION",
        "tab_code": "EXPRESSION",
        "label": "Create",
        "display_order": 5,
        "hero_title": "Create",
        "hero_subtitle": "What did you create?",
        "description": "Record something you made",
        "cta_label": "Save Creation",
    },
    {
        "event_type": "ADJUST",
        "tab_code": "ADJUST",
        "label": "Adjust",
        "display_order": 6,
        "hero_title": "Adjust",
        "hero_subtitle": "What would you like to change?",
        "description": "Change a lifestyle priority",
        "cta_label": "Update Lifestyle",
    },
]

_FIELD = lambda key, label, field_type, **extra: {  # noqa: E731
    "group_key": key,
    "label": label,
    "field_type": field_type,
    **extra,
}

LIFESTYLE_TAB_FIELDS: list[dict[str, Any]] = [
    {
        "event_type": "LIFESTYLE_EXPENSE",
        "field_groups": [
            _FIELD("amount", "Amount", "amount", required=True),
            _FIELD("spend_category", "Category", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "EXPERIENCE",
        "field_groups": [
            _FIELD("experience_type", "Experience type", "single_select", required=True),
            _FIELD("experience_quality", "How was it?", "chip_grid"),
            _FIELD("energy_impact", "How did it affect your energy?", "chip_grid"),
            _FIELD("people_context", "Who were you with? — optional", "chip_grid"),
            _FIELD("location_context", "Where was it? — optional", "chip_grid"),
            _FIELD("value_received", "What did you get from it?", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "WELLBEING",
        "field_groups": [
            _FIELD("wellbeing_areas", "Which life area?", "chip_grid", required=True),
            _FIELD("wellbeing_state", "How does this area feel right now?", "single_select", required=True),
            _FIELD("contributors", "What is shaping this?", "multi_select"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "DISCOVERY",
        "field_groups": [
            _FIELD("discovery_type", "Discovery type", "single_select", required=True),
            _FIELD("curiosity_level", "Why did this catch your attention?", "chip_grid"),
            _FIELD("discovery_impact", "How relevant could this be?", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "EXPRESSION",
        "field_groups": [
            _FIELD("creation_type", "Creation type", "single_select", required=True),
            _FIELD("satisfaction_level", "How satisfied are you with it?", "chip_grid"),
            _FIELD("time_invested", "Time invested", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "ADJUST",
        "field_groups": [
            _FIELD("adjustment_area", "What area do you want to adjust?", "single_select", required=True),
            _FIELD("priority_level", "How important is this change?", "chip_grid"),
            _FIELD("confidence_level", "How confident are you?", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
]

# DB-constrained option sets (existing contract).
PEOPLE_CONTEXT_OPTIONS = ["Alone", "Partner", "Friends", "Family", "Group"]
LOCATION_CONTEXT_OPTIONS = ["Home", "Local", "Outing", "Travel"]
CURIOSITY_LEVEL_OPTIONS = ["Low", "Moderate", "High"]
TIME_INVESTED_OPTIONS = [
    {"value": "<30", "label": "Under 30 min"},
    {"value": "30_60", "label": "30–60 min"},
    {"value": "1_2_HOURS", "label": "1–2 hours"},
    {"value": "2_PLUS_HOURS", "label": "2+ hours"},
]
# Free-string arrays (no DB enum) — product suggestion chips only.
WELLBEING_AREA_OPTIONS = [
    "Health",
    "Relationships",
    "Work",
    "Money",
    "Home",
    "Social",
    "Rest",
    "Growth",
]
CONTRIBUTOR_OPTIONS = [
    "Sleep",
    "Workload",
    "Relationships",
    "Money",
    "Health",
    "Environment",
    "Routine",
]

SPEND_CATEGORY_ORDER = [
    "Travel",
    "Food & Dining",
    "Entertainment",
    "Wellbeing",
    "Fitness",
    "Learning",
    "Shopping",
    "Hobbies",
    "Experiences",
    "Other",
]

# Lifestyle chip labels → EXPENSE taxonomy parent codes.
SPEND_CATEGORY_TO_EXPENSE_CODE: dict[str, str] = {
    "Travel": "TRANSPORT",
    "Food & Dining": "FOOD",
    "Entertainment": "ENTERTAINMENT",
    "Wellbeing": "HEALTH",
    "Fitness": "HEALTH",
    "Learning": "OTHER",
    "Shopping": "OTHER",
    "Hobbies": "OTHER",
    "Experiences": "OTHER",
    "Other": "OTHER",
}


def _ordered(preferred: list[str], allowed: set[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in preferred:
        if item in allowed and item not in seen:
            out.append(item)
            seen.add(item)
    for item in sorted(allowed - seen):
        out.append(item)
    return out


LIFESTYLE_QUICK_ADD_METADATA: dict[str, Any] = {
    "spend_category_options": list(SPEND_CATEGORY_ORDER),
    "experience_type_options": [
        "Travel",
        "Food",
        "Nature",
        "Adventure",
        "Entertainment",
        "Social",
        "Family",
        "Personal",
        "Wellbeing",
        "Hobby",
        "Other",
    ],
    "experience_quality_options": _ordered(
        ["Ordinary", "Enjoyable", "Memorable", "Exceptional"],
        EXPERIENCE_QUALITIES,
    ),
    "energy_impact_options": _ordered(
        ["Drained", "Neutral", "Refreshed", "Energized"],
        ENERGY_IMPACTS,
    ),
    "people_context_options": list(PEOPLE_CONTEXT_OPTIONS),
    "location_context_options": list(LOCATION_CONTEXT_OPTIONS),
    "value_received_options": _ordered(
        ["Not Worth It", "Okay", "Worth It", "Excellent Value", "Life Enriching"],
        VALUE_RECEIVED,
    ),
    "wellbeing_area_options": list(WELLBEING_AREA_OPTIONS),
    "wellbeing_state_options": _ordered(
        ["Low", "Moderate", "Good", "Excellent"],
        WELLBEING_STATES,
    ),
    "contributor_options": list(CONTRIBUTOR_OPTIONS),
    "discovery_type_options": [
        "Place",
        "Idea",
        "Activity",
        "Person",
        "Skill",
        "Experience",
        "Opportunity",
        "Other",
    ],
    "curiosity_level_options": list(CURIOSITY_LEVEL_OPTIONS),
    "discovery_impact_options": _ordered(
        ["Interesting", "Useful", "Inspiring", "Life-Changing"],
        DISCOVERY_IMPACTS,
    ),
    "creation_type_options": [
        "Writing",
        "Art",
        "Music",
        "Design",
        "Content",
        "Photography",
        "Problem Solving",
        "Planning",
        "Other",
    ],
    "satisfaction_level_options": _ordered(
        ["Low", "Moderate", "High", "Exceptional"],
        SATISFACTION_LEVELS,
    ),
    "time_invested_options": list(TIME_INVESTED_OPTIONS),
    "adjustment_area_options": _ordered(
        [
            "More Rest",
            "More Travel",
            "More Creativity",
            "More Social Time",
            "More Exercise",
            "More Personal Time",
            "More Exploration",
            "More Balance",
            "More Presence",
        ],
        ADJUSTMENT_AREAS,
    ),
    "priority_level_options": _ordered(["Low", "Medium", "High"], PRIORITY_LEVELS),
    "confidence_level_options": _ordered(
        ["Not Sure", "Somewhat Sure", "Very Sure"],
        CONFIDENCE_LEVELS,
    ),
    "lifestyle_tabs": LIFESTYLE_TAB_FIELDS,
}

FIELD_GROUP_OPTIONS_KEY: dict[str, str] = {
    "spend_category": "spend_category_options",
    "experience_type": "experience_type_options",
    "experience_quality": "experience_quality_options",
    "energy_impact": "energy_impact_options",
    "people_context": "people_context_options",
    "location_context": "location_context_options",
    "value_received": "value_received_options",
    "wellbeing_areas": "wellbeing_area_options",
    "wellbeing_state": "wellbeing_state_options",
    "contributors": "contributor_options",
    "discovery_type": "discovery_type_options",
    "curiosity_level": "curiosity_level_options",
    "discovery_impact": "discovery_impact_options",
    "creation_type": "creation_type_options",
    "satisfaction_level": "satisfaction_level_options",
    "time_invested": "time_invested_options",
    "adjustment_area": "adjustment_area_options",
    "priority_level": "priority_level_options",
    "confidence_level": "confidence_level_options",
}
