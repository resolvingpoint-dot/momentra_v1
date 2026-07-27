"""Relationships quick-add enum mappings."""
from __future__ import annotations

EXPERIENCE_TYPES = {
    "Dining",
    "Travel",
    "Celebration",
    "Entertainment",
    "Activity",
    "Learning",
    "Family Event",
    "Milestone",
    "Other",
}
RELATIONSHIP_TYPES = {
    "Partner",
    "Family",
    "Friend",
    "Parent",
    "Child",
    "Mentor",
    "Professional",
    "Community",
}
RELATIONSHIP_TYPE_ALIASES = {
    "Group": "Community",
    "GROUP": "Community",
    "group": "Community",
}
VALUE_RECEIVED = {
    "Okay",
    "Worth It",
    "Excellent Value",
    "Relationship Building",
    "Life Enriching",
}
CONNECTION_TYPES = {
    "Conversation",
    "Call",
    "Message",
    "Visit",
    "Shared Time",
    "Meal Together",
    "Celebration",
    "Check-In",
    "Other",
}
CONNECTION_QUALITIES = {"Routine", "Meaningful", "Deep", "Memorable"}
# Chip values stay as UI labels (unique); handler maps to DB enum codes.
EMOTIONAL_TONES = [
    {"value": "Warm", "label": "Warm"},
    {"value": "Calm", "label": "Calm"},
    {"value": "Joyful", "label": "Joyful"},
    {"value": "Serious", "label": "Serious"},
    {"value": "Tense", "label": "Tense"},
    {"value": "Supportive", "label": "Supportive"},
]
EMOTIONAL_TONE_VALUES = {
    "Positive",
    "Neutral",
    "Difficult",
    "Supportive",
    "Celebratory",
}
EMOTIONAL_TONE_ALIASES = {
    "Warm": "Positive",
    "Calm": "Neutral",
    "Joyful": "Celebratory",
    "Serious": "Neutral",
    "Tense": "Difficult",
    "Supportive": "Supportive",
    # Already-normalized / new-client codes
    "Positive": "Positive",
    "Neutral": "Neutral",
    "Difficult": "Difficult",
    "Celebratory": "Celebratory",
}
TIME_INVESTED_OPTIONS = [
    {"value": "<15", "label": "5 min"},
    {"value": "15_30", "label": "15 min"},
    {"value": "30_60", "label": "30 min"},
    {"value": "1_2_HOURS", "label": "1 hour"},
    {"value": "2_PLUS_HOURS", "label": "2+ hours"},
]
TIME_INVESTED_VALUES = {"<15", "15_30", "30_60", "1_2_HOURS", "2_PLUS_HOURS"}
TIME_INVESTED_ALIASES = {
    "5 min": "<15",
    "15 min": "15_30",
    "30 min": "30_60",
    "1 hour": "1_2_HOURS",
    "2+ hours": "2_PLUS_HOURS",
    "<15": "<15",
    "15_30": "15_30",
    "30_60": "30_60",
    "1_2_HOURS": "1_2_HOURS",
    "2_PLUS_HOURS": "2_PLUS_HOURS",
}
SPEND_CATEGORIES = [
    "Dining",
    "Travel",
    "Gift",
    "Event",
    "Support",
    "Experience",
    "Other",
]
SUPPORT_TYPES = {
    "Emotional",
    "Practical",
    "Financial",
    "Advice",
    "Encouragement",
    "Care",
    "Celebration",
    "Other",
}
SUPPORT_DIRECTIONS = ["Given", "Received", "Mutual"]
SUPPORT_IMPACTS = ["Small", "Meaningful", "Important", "Transformational"]
INVESTMENT_TYPES = {
    "Gift",
    "Support",
    "Education",
    "Travel",
    "Celebration",
    "Shared Goal",
    "Family Expense",
    "Contribution",
    "Other",
}
INVESTMENT_PURPOSES = {
    "Care",
    "Growth",
    "Support",
    "Celebration",
    "Responsibility",
    "Shared Future",
}
PERCEIVED_VALUES = ["Low", "Moderate", "High", "Exceptional"]
ADJUSTMENT_AREAS = {
    "More Time Together",
    "Better Communication",
    "More Presence",
    "More Support",
    "More Fun",
    "More Shared Experiences",
    "More Appreciation",
    "More Consistency",
}
RELATIONSHIP_FOCUSES = {
    "Partner",
    "Family",
    "Friend",
    "Parent",
    "Child",
}
PRIORITY_LEVELS = ["Low", "Medium", "High"]
CONFIDENCE_LEVELS = ["Not Sure", "Somewhat Sure", "Very Sure"]
