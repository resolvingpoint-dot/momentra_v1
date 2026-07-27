"""Relationships template constants."""
from __future__ import annotations

MOMENT_TYPE_CODE = "RELATIONSHIPS"
TEMPLATE_ID = "relationships"
TEMPLATE_VERSION = 1

RELATIONSHIPS_ACTIVITY_EVENTS = frozenset({
    "CONNECTION",
    "SUPPORT",
    "SHARED_EXPERIENCE",
    "RELATIONSHIP_INVESTMENT",
    "ADJUST",
    "RELATIONSHIP_ADJUST",
})
