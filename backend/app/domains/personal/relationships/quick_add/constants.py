"""Relationships quick-add constants — mirrors web registry metadata."""
from __future__ import annotations

from typing import Any

from app.domains.personal.relationships.quick_add.handlers.mappings import (
    ADJUSTMENT_AREAS,
    CONFIDENCE_LEVELS,
    CONNECTION_QUALITIES,
    CONNECTION_TYPES,
    EMOTIONAL_TONES,
    EXPERIENCE_TYPES,
    INVESTMENT_PURPOSES,
    INVESTMENT_TYPES,
    PERCEIVED_VALUES,
    PRIORITY_LEVELS,
    RELATIONSHIP_FOCUSES,
    RELATIONSHIP_TYPES,
    SPEND_CATEGORIES,
    SUPPORT_DIRECTIONS,
    SUPPORT_IMPACTS,
    SUPPORT_TYPES,
    TIME_INVESTED_OPTIONS,
    VALUE_RECEIVED,
)

EVENT_TO_TAB: dict[str, str] = {
    "SHARED_EXPERIENCE": "SHARED_EXPERIENCE",
    "CONNECTION": "CONNECTION",
    "SUPPORT": "SUPPORT",
    "RELATIONSHIP_INVESTMENT": "INVESTMENT",
    "ADJUST": "ADJUST",
}

EVENT_ALIASES: dict[str, str] = {
    "RELATIONSHIP_ADJUST": "ADJUST",
}


def _sorted_options(values: set[str] | list[str]) -> list[str]:
    return sorted(values)


RELATIONSHIPS_QUICK_ADD_TABS: list[dict[str, Any]] = [
    {
        "event_type": "SHARED_EXPERIENCE",
        "tab_code": "SHARED_EXPERIENCE",
        "label": "Shared Experience",
        "display_order": 1,
        "hero_title": "Shared Experience",
        "hero_subtitle": "We spent meaningful time together.",
        "description": "Record time shared together",
        "guiding_question": "What did you do together?",
        "cta_label": "Save Shared Experience",
    },
    {
        "event_type": "CONNECTION",
        "tab_code": "CONNECTION",
        "label": "Connection",
        "display_order": 2,
        "hero_title": "Connection",
        "hero_subtitle": "We had meaningful contact or presence.",
        "description": "Capture meaningful contact",
        "guiding_question": "Who did you connect with?",
        "cta_label": "Save Connection",
    },
    {
        "event_type": "SUPPORT",
        "tab_code": "SUPPORT",
        "label": "Support",
        "display_order": 3,
        "hero_title": "Support",
        "hero_subtitle": "Care or help was given, received, or shared.",
        "description": "Record care or help",
        "guiding_question": "What support happened?",
        "cta_label": "Save Support",
    },
    {
        "event_type": "RELATIONSHIP_INVESTMENT",
        "tab_code": "INVESTMENT",
        "label": "Investment",
        "display_order": 4,
        "hero_title": "Relationship Investment",
        "hero_subtitle": "I intentionally invested time, effort, care, or money.",
        "description": "Log intentional relationship effort",
        "guiding_question": "What did you invest in this relationship?",
        "cta_label": "Save Relationship Investment",
    },
    {
        "event_type": "ADJUST",
        "tab_code": "ADJUST",
        "label": "Adjust",
        "display_order": 5,
        "hero_title": "Adjust Relationships",
        "hero_subtitle": "I want to change a relationship priority.",
        "description": "Change a relationship priority",
        "guiding_question": "What would you like to change?",
        "cta_label": "Update Relationship",
    },
]

_FIELD = lambda key, label, field_type, **extra: {  # noqa: E731
    "group_key": key,
    "label": label,
    "field_type": field_type,
    **extra,
}

RELATIONSHIPS_TAB_FIELDS: list[dict[str, Any]] = [
    {
        "event_type": "SHARED_EXPERIENCE",
        "field_groups": [
            _FIELD("experience_type", "Experience type", "chip_grid", required=True),
            _FIELD("value_received", "What made it meaningful?", "chip_grid"),
            _FIELD("amount", "Amount", "amount"),
            _FIELD("spend_category", "Category", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "CONNECTION",
        "field_groups": [
            _FIELD("connection_type", "What kind of connection?", "chip_grid", required=True),
            _FIELD("relationship_type", "Relationship type", "chip_grid"),
            _FIELD("connection_quality", "How connected did it feel?", "chip_grid"),
            _FIELD("emotional_tone", "What was the tone?", "chip_grid"),
            _FIELD("time_invested", "Time invested", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "SUPPORT",
        "field_groups": [
            _FIELD("support_type", "Support type", "chip_grid", required=True),
            _FIELD("support_direction", "Which direction did the support flow?", "chip_grid", required=True),
            _FIELD("support_impact", "How helpful was it?", "chip_grid"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "RELATIONSHIP_INVESTMENT",
        "field_groups": [
            _FIELD("investment_type", "Investment type", "chip_grid", required=True),
            _FIELD("investment_purpose", "Why did you make this investment?", "chip_grid"),
            _FIELD("perceived_value", "How valuable did this feel?", "chip_grid"),
            _FIELD("amount", "Amount", "amount"),
            _FIELD("notes", "Notes", "textarea"),
        ],
    },
    {
        "event_type": "ADJUST",
        "field_groups": [
            _FIELD("adjustment_area", "Adjustment area", "chip_grid", required=True),
            _FIELD("relationship_focus", "What should get more attention?", "chip_grid"),
            _FIELD("priority_level", "How important is this change?", "chip_grid"),
            _FIELD("confidence_level", "How confident are you?", "chip_grid"),
            _FIELD("notes", "Why does this matter?", "textarea"),
        ],
    },
]

RELATIONSHIPS_QUICK_ADD_METADATA: dict[str, Any] = {
    "experience_type_options": _sorted_options(EXPERIENCE_TYPES),
    "relationship_type_options": _sorted_options(RELATIONSHIP_TYPES),
    "value_received_options": _sorted_options(VALUE_RECEIVED),
    "spend_category_options": list(SPEND_CATEGORIES),
    "connection_type_options": _sorted_options(CONNECTION_TYPES),
    "connection_quality_options": _sorted_options(CONNECTION_QUALITIES),
    "emotional_tone_options": list(EMOTIONAL_TONES),
    "time_invested_options": list(TIME_INVESTED_OPTIONS),
    "support_type_options": _sorted_options(SUPPORT_TYPES),
    "support_direction_options": list(SUPPORT_DIRECTIONS),
    "support_impact_options": list(SUPPORT_IMPACTS),
    "investment_type_options": _sorted_options(INVESTMENT_TYPES),
    "investment_purpose_options": _sorted_options(INVESTMENT_PURPOSES),
    "perceived_value_options": list(PERCEIVED_VALUES),
    "adjustment_area_options": _sorted_options(ADJUSTMENT_AREAS),
    "relationship_focus_options": _sorted_options(RELATIONSHIP_FOCUSES),
    "priority_level_options": list(PRIORITY_LEVELS),
    "confidence_level_options": list(CONFIDENCE_LEVELS),
    "emotional_security_tabs": RELATIONSHIPS_TAB_FIELDS,
}

FIELD_GROUP_OPTIONS_KEY: dict[str, str] = {
    "experience_type": "experience_type_options",
    "relationship_type": "relationship_type_options",
    "value_received": "value_received_options",
    "spend_category": "spend_category_options",
    "connection_type": "connection_type_options",
    "connection_quality": "connection_quality_options",
    "emotional_tone": "emotional_tone_options",
    "time_invested": "time_invested_options",
    "support_type": "support_type_options",
    "support_direction": "support_direction_options",
    "support_impact": "support_impact_options",
    "investment_type": "investment_type_options",
    "investment_purpose": "investment_purpose_options",
    "perceived_value": "perceived_value_options",
    "adjustment_area": "adjustment_area_options",
    "relationship_focus": "relationship_focus_options",
    "priority_level": "priority_level_options",
    "confidence_level": "confidence_level_options",
}
