"""Life Operations quick-add options — mirrors client registry metadata."""
from __future__ import annotations

from typing import Any

EVENT_TO_TAB: dict[str, str] = {
    "EXPENSE": "MONEY",
    "COMMITMENT": "ATTENTION",
    "RECOVERY": "RECOVERY",
    "REFLECTION": "MOOD",
    "RHYTHM": "ADJUST",
}

LIFE_OPS_QUICK_ADD_TABS: list[dict[str, Any]] = [
    {
        "event_type": "EXPENSE",
        "tab_code": "MONEY",
        "label": "Money",
        "display_order": 1,
        "hero_title": "Money",
        "hero_subtitle": "Track spending, income, and financial pressure.",
        "cta_label": "Save Expense",
    },
    {
        "event_type": "COMMITMENT",
        "tab_code": "ATTENTION",
        "label": "Attention",
        "display_order": 2,
        "hero_title": "Attention",
        "hero_subtitle": "Log where your focus and energy are going.",
        "cta_label": "Log Attention State",
    },
    {
        "event_type": "RECOVERY",
        "tab_code": "RECOVERY",
        "label": "Recovery",
        "display_order": 3,
        "hero_title": "Recovery",
        "hero_subtitle": "Capture rest and recharge activities.",
        "cta_label": "Log Recovery",
    },
    {
        "event_type": "REFLECTION",
        "tab_code": "MOOD",
        "label": "Mood",
        "display_order": 4,
        "hero_title": "Mood",
        "hero_subtitle": "Reflect on how you feel right now.",
        "cta_label": "Save Mood",
    },
    {
        "event_type": "RHYTHM",
        "tab_code": "ADJUST",
        "label": "Adjust",
        "display_order": 5,
        "hero_title": "Adjust",
        "hero_subtitle": "Tune your runtime rhythm and priorities.",
        "cta_label": "Update Rhythm",
    },
]

for _tab in LIFE_OPS_QUICK_ADD_TABS:
    _tab.setdefault("description", _tab["hero_subtitle"])

LIFE_OPS_QUICK_ADD_METADATA: dict[str, Any] = {
    "expense_entry_types": [
        {"value": "EXPENSE", "label": "Expense"},
        {"value": "INCOME", "label": "Income"},
        {"value": "TRANSFER", "label": "Transfer"},
        {"value": "CONTRIBUTION", "label": "Contribution"},
        {"value": "SAVINGS", "label": "Savings"},
        {"value": "INVESTMENT", "label": "Investment"},
    ],
    "pressure_impact_chips": [
        "Essential",
        "Planned",
        "Unexpected",
        "Pressure Source",
    ],
    "expense_category_names": [
        "Food",
        "Transport",
        "Housing",
        "Health",
        "Entertainment",
        "Other",
    ],
    "commitment_types": [
        {"value": "TASK", "label": "Task"},
        {"value": "MEETING", "label": "Meeting"},
        {"value": "DEEP_WORK", "label": "Deep Work"},
        {"value": "ADMIN", "label": "Admin"},
    ],
    "commitment_status_options": [
        {"value": "COMPLETED", "label": "Completed"},
        {"value": "IN_PROGRESS", "label": "In Progress"},
        {"value": "DELAYED", "label": "Delayed"},
    ],
    "attention_focus_areas": [
        "Work",
        "Health",
        "Family",
        "Finance",
        "Learning",
    ],
    "intensity_options": ["LIGHT", "MODERATE", "HEAVY"],
    "recovery_types": [
        {"value": "REST", "label": "Rest"},
        {"value": "SLEEP", "label": "Sleep"},
        {"value": "EXERCISE", "label": "Exercise"},
        {"value": "MEDITATION", "label": "Meditation"},
        {"value": "SOCIAL", "label": "Social"},
    ],
    "recovery_duration_options": [
        {"value": "15", "label": "15 min"},
        {"value": "30", "label": "30 min"},
        {"value": "60", "label": "1 hour"},
        {"value": "120", "label": "2+ hours"},
    ],
    "energy_impact_options": ["LOW", "MODERATE", "HIGH"],
    "mood_feeling_options": [
        {"value": "GREAT", "label": "Great"},
        {"value": "GOOD", "label": "Good"},
        {"value": "OKAY", "label": "Okay"},
        {"value": "LOW", "label": "Low"},
        {"value": "STRESSED", "label": "Stressed"},
    ],
    "reflection_tags": [
        "Grateful",
        "Anxious",
        "Focused",
        "Tired",
        "Motivated",
    ],
    "rhythm_actions": [
        {"value": "More Rest", "label": "More Rest"},
        {"value": "More Balance", "label": "More Balance"},
        {"value": "More Focus", "label": "More Focus"},
        {"value": "More Recovery", "label": "More Recovery"},
    ],
    "runtime_modes": [
        "FLOW_MODE",
        "SURVIVAL_MODE",
        "RECOVERY_MODE",
        "BUILD_MODE",
    ],
    "runtime_priorities": ["LOW", "MEDIUM", "HIGH"],
    "runtime_signal_dimensions": [
        {"key": "pressure", "label": "Pressure", "description": "Load and stress"},
        {"key": "recovery", "label": "Recovery", "description": "Rest and recharge"},
        {"key": "focus", "label": "Focus", "description": "Attention quality"},
        {"key": "momentum", "label": "Momentum", "description": "Forward motion"},
    ],
}
