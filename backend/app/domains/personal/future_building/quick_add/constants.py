"""Future Building quick-add constants — mirrors web registry metadata."""
from __future__ import annotations

from typing import Any

from app.domains.personal.future_building.quick_add.handlers.mappings import (
    CONFIDENCE_LEVELS,
    EFFORT_LEVELS,
    IMPACT_LEVELS,
    LEARNING_TYPES,
    MILESTONE_NATURES,
    OPPORTUNITY_SOURCES,
    OPPORTUNITY_STATUSES,
    PIVOT_ADJUSTMENTS,
    PIVOT_REASONS,
    POTENTIAL_LEVELS,
    PROGRESS_LEVELS,
    RELEVANCE_LEVELS,
)

EVENT_TO_TAB: dict[str, str] = {
    "CONTRIBUTION": "INVESTMENT",
    "MILESTONE": "MILESTONE",
    "OPPORTUNITY": "OPPORTUNITY",
    "PIVOT": "PIVOT",
    "PROGRESS": "PROGRESS",
    "LEARNING": "LEARNING",
}

# Selector one-liners (description) + guiding questions (hero_subtitle).
FUTURE_BUILDING_QUICK_ADD_TABS: list[dict[str, Any]] = [
    {
        "event_type": "CONTRIBUTION",
        "tab_code": "INVESTMENT",
        "label": "Investment",
        "display_order": 1,
        "hero_title": "Investment",
        "hero_subtitle": "What did you invest in?",
        "description": "Put in money or energy",
        "cta_label": "Save Investment",
    },
    {
        "event_type": "MILESTONE",
        "tab_code": "MILESTONE",
        "label": "Milestone",
        "display_order": 2,
        "hero_title": "Milestone",
        "hero_subtitle": "What did you achieve?",
        "description": "Celebrate an achievement",
        "cta_label": "Save Milestone",
    },
    {
        "event_type": "OPPORTUNITY",
        "tab_code": "OPPORTUNITY",
        "label": "Opportunity",
        "display_order": 3,
        "hero_title": "Opportunity",
        "hero_subtitle": "What opportunity appeared?",
        "description": "Capture a new possibility",
        "cta_label": "Save Opportunity",
    },
    {
        "event_type": "PIVOT",
        "tab_code": "PIVOT",
        "label": "Pivot",
        "display_order": 4,
        "hero_title": "Pivot",
        "hero_subtitle": "What direction changed?",
        "description": "Record a change in direction",
        "cta_label": "Save Pivot",
    },
    {
        "event_type": "PROGRESS",
        "tab_code": "PROGRESS",
        "label": "Progress",
        "display_order": 5,
        "hero_title": "Progress",
        "hero_subtitle": "What moved forward?",
        "description": "Log forward movement",
        "cta_label": "Save Progress",
    },
    {
        "event_type": "LEARNING",
        "tab_code": "LEARNING",
        "label": "Learning",
        "display_order": 6,
        "hero_title": "Learning",
        "hero_subtitle": "What did you learn?",
        "description": "Save a lesson or insight",
        "cta_label": "Save Learning",
    },
]

_FIELD = lambda key, label, field_type, **extra: {  # noqa: E731
    "group_key": key,
    "label": label,
    "field_type": field_type,
    **extra,
}

FUTURE_BUILDING_TAB_FIELDS: list[dict[str, Any]] = [
    {
        "event_type": "CONTRIBUTION",
        "field_groups": [
            _FIELD("amount", "Amount", "amount", required=True),
            _FIELD("category_name", "Category", "single_select"),
            _FIELD("impact_level", "How important is this investment?", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "MILESTONE",
        "field_groups": [
            _FIELD(
                "milestone_nature",
                "What kind of milestone was this?",
                "single_select",
                required=True,
            ),
            _FIELD("celebration_level", "How big does this feel?", "chip_grid"),
            _FIELD("outcome_value", "Measurable outcome", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "OPPORTUNITY",
        "field_groups": [
            _FIELD(
                "opportunity_source",
                "Where did this opportunity come from?",
                "single_select",
                required=True,
            ),
            _FIELD("opportunity_status", "Status", "chip_grid"),
            _FIELD("confidence_level", "How promising is it?", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "PIVOT",
        "field_groups": [
            _FIELD("pivot_change", "What changed?", "chip_grid", required=True),
            _FIELD("pivot_reason", "Why did you change direction?", "chip_grid"),
            _FIELD("confidence_level", "How confident are you in this change?", "chip_grid"),
            _FIELD("notes", "Notes", "textarea", required=True),
        ],
    },
    {
        "event_type": "PROGRESS",
        "field_groups": [
            _FIELD("progress_type", "Progress type", "single_select", required=True),
            _FIELD("time_invested", "Time invested", "chip_grid"),
            _FIELD("effort_level", "How much effort did this take?", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "LEARNING",
        "field_groups": [
            _FIELD("learning_type", "What type of learning was this?", "single_select", required=True),
            _FIELD("learning_topic", "Topic — optional", "text"),
            _FIELD("relevance", "How useful is this?", "chip_grid"),
            _FIELD("application", "How will you apply it?", "textarea"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
]

CELEBRATION_LEVELS = ["Personal Win", "Shared Win", "Life Moment"]
OUTCOME_VALUES = [
    "Income Increase",
    "Savings Increase",
    "Revenue Increase",
    "Cost Reduction",
    "No Financial Impact",
]
TIME_INVESTED_PRESETS = ["15 min", "30 min", "1 hour", "2 hours"]

# Ordered lists for UI (match prior metadata order where it existed).
_MILESTONE_NATURE_ORDER = [
    "Achievement",
    "Recognition",
    "Completion",
    "Launch",
    "Certification",
    "Promotion",
    "Revenue Event",
    "Breakthrough",
]
_OPPORTUNITY_SOURCE_ORDER = [
    "New Connection",
    "New Skill",
    "New Resource",
    "New Funding",
    "New Role",
    "New Client",
    "New Market",
    "New Idea",
    "New Partnership",
    "New Exposure",
    "Unexpected Event",
    "Other",
]
_PROGRESS_TYPE_ORDER = [
    "Small Step",
    "Moderate Progress",
    "Major Progress",
    "Breakthrough",
]
_LEARNING_TYPE_ORDER = [
    "Skill",
    "Knowledge",
    "Insight",
    "Experience",
    "Mentorship",
    "Mistake",
]
_IMPACT_ORDER = ["Minor", "Meaningful", "Major", "Transformational"]
_STATUS_ORDER = ["Exploring", "Considering", "Acting", "Captured"]
_POTENTIAL_ORDER = ["Low", "Moderate", "High", "Game-Changing"]
_CONFIDENCE_ORDER = ["Low", "Medium", "High"]
_EFFORT_ORDER = ["Low", "Medium", "High", "Exceptional"]
_RELEVANCE_ORDER = ["Useful", "Important", "High Leverage", "Transformational"]
_PIVOT_CHANGE_ORDER = [
    "New Priority",
    "New Goal",
    "Reduce Scope",
    "Increase Focus",
    "Change Timeline",
    "Change Direction",
]
_PIVOT_REASON_ORDER = [
    "New Information",
    "Opportunity",
    "Constraint",
    "Personal Decision",
    "Market Change",
]


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


FUTURE_BUILDING_QUICK_ADD_METADATA: dict[str, Any] = {
    "milestone_nature_options": _ordered(_MILESTONE_NATURE_ORDER, MILESTONE_NATURES),
    "impact_level_options": _ordered(_IMPACT_ORDER, IMPACT_LEVELS),
    "celebration_level_options": list(CELEBRATION_LEVELS),
    "outcome_value_options": list(OUTCOME_VALUES),
    "opportunity_source_options": _ordered(_OPPORTUNITY_SOURCE_ORDER, OPPORTUNITY_SOURCES),
    "opportunity_status_options": _ordered(_STATUS_ORDER, OPPORTUNITY_STATUSES),
    "potential_level_options": _ordered(_POTENTIAL_ORDER, POTENTIAL_LEVELS),
    "confidence_level_options": _ordered(_CONFIDENCE_ORDER, CONFIDENCE_LEVELS),
    "pivot_change_options": _ordered(_PIVOT_CHANGE_ORDER, PIVOT_ADJUSTMENTS),
    "pivot_reason_options": _ordered(_PIVOT_REASON_ORDER, PIVOT_REASONS),
    "progress_type_options": _ordered(_PROGRESS_TYPE_ORDER, PROGRESS_LEVELS),
    "time_invested_options": list(TIME_INVESTED_PRESETS),
    "effort_level_options": _ordered(_EFFORT_ORDER, EFFORT_LEVELS),
    "learning_type_options": _ordered(_LEARNING_TYPE_ORDER, LEARNING_TYPES),
    "relevance_level_options": _ordered(_RELEVANCE_ORDER, RELEVANCE_LEVELS),
    "future_building_tabs": FUTURE_BUILDING_TAB_FIELDS,
}

# Group key → metadata options key for hydrating field_group.options
FIELD_GROUP_OPTIONS_KEY: dict[str, str] = {
    "milestone_nature": "milestone_nature_options",
    "impact_level": "impact_level_options",
    "celebration_level": "celebration_level_options",
    "outcome_value": "outcome_value_options",
    "opportunity_source": "opportunity_source_options",
    "opportunity_status": "opportunity_status_options",
    "confidence_level": "potential_level_options",  # opportunity; pivot override below
    "pivot_change": "pivot_change_options",
    "pivot_reason": "pivot_reason_options",
    "progress_type": "progress_type_options",
    "time_invested": "time_invested_options",
    "effort_level": "effort_level_options",
    "learning_type": "learning_type_options",
    "relevance": "relevance_level_options",
}

# Pivot confidence uses CONFIDENCE_LEVELS, not potential levels.
PIVOT_CONFIDENCE_OPTIONS_KEY = "confidence_level_options"
