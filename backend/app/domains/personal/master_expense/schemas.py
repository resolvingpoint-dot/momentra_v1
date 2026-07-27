"""Master expense request/response schemas and static option catalogs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


def option(value: str, label: str) -> dict[str, str]:
    return {"value": value, "label": label}


MASTER_EXPENSE_FEELINGS = [
    option("VERY_BAD", "Very Bad"),
    option("BAD", "Bad"),
    option("NEUTRAL", "Neutral"),
    option("GOOD", "Good"),
    option("GREAT", "Great"),
]

MASTER_EXPENSE_SCALE_LEVELS = [
    option("LOW", "Low"),
    option("MEDIUM", "Medium"),
    option("HIGH", "High"),
]

MASTER_EXPENSE_SHARED_WITH = [
    option("SPOUSE", "Spouse"),
    option("PARENTS", "Parents"),
    option("FAMILY", "Family"),
    option("FRIENDS", "Friends"),
    option("CUSTOM", "Custom"),
]

MASTER_EXPENSE_RELATIONSHIP_IMPACTS = [
    option("STRENGTHENED_CONNECTION", "Strengthened Connection"),
    option("CELEBRATION_TOGETHER", "Celebration Together"),
    option("SUPPORT_GIVEN", "Support Given"),
]

MASTER_EXPENSE_CONTEXT_REASONS = [
    option("CELEBRATION", "Celebration"),
    option("DAILY_NEED", "Daily Need"),
    option("GIFT", "Gift"),
    option("TRAVEL", "Travel"),
    option("OTHER", "Other"),
]

# Honest impact copy: describes fan-out targets / refresh outcomes only — never invented ₹ impact.
IMPACT_COPY = {
    "life_operations_active": "Will refresh Life Ops Pulse & Activity",
    "lifestyle_active": "Will refresh Lifestyle Pulse & Moments",
    "relationships_active": "Will refresh Relationships Pulse & Moments",
    "relationships_skipped": "Skipped (not shared)",
}


def build_impact_preview(
    *,
    life_operations: bool,
    lifestyle: bool,
    relationships: bool,
) -> dict[str, str]:
    """Derive impact labels from actual fan-out targets (no fabricated totals)."""
    return {
        "life_operations": (
            IMPACT_COPY["life_operations_active"] if life_operations else "Not logged"
        ),
        "lifestyle": IMPACT_COPY["lifestyle_active"] if lifestyle else "Not logged",
        "relationships": (
            IMPACT_COPY["relationships_active"]
            if relationships
            else IMPACT_COPY["relationships_skipped"]
        ),
        "templates_touched": str(
            int(life_operations) + int(lifestyle) + int(relationships)
        ),
        "will_refresh": "Pulse & Activity on touched templates",
    }


class MasterExpenseExperienceInput(BaseModel):
    feeling: str | None = None
    meaningfulness: str | None = None
    memorability: str | None = None


class MasterExpenseSharedInput(BaseModel):
    is_shared: bool = False
    shared_with: list[str] = Field(default_factory=list)
    relationship_impact: list[str] = Field(default_factory=list)


class MasterExpenseContextInput(BaseModel):
    reason: str | None = None


class MasterExpenseCreateRequest(BaseModel):
    client_request_id: str | None = None
    title: str
    amount_minor: int
    currency_code: str
    account_id: str
    category_code: str
    subcategory_code: str | None = None
    occurred_at: str | None = None
    experience: MasterExpenseExperienceInput | None = None
    shared: MasterExpenseSharedInput | None = None
    context: MasterExpenseContextInput | None = None
    notes: str | None = None


class MasterExpenseCreatedEvents(BaseModel):
    life_operations: str | None = None
    lifestyle: str | None = None
    relationships: str | None = None


class MasterExpenseCreateResponse(BaseModel):
    id: str
    master_expense_id: str
    created_events: MasterExpenseCreatedEvents
    impact_preview: dict[str, str]
    idempotent_replay: bool = False
    # Legacy mobile contract fields
    master_expense_group_id: str
    transaction_id: str
    account_id: str
    amount_minor: int
    events: list[dict[str, Any]] = Field(default_factory=list)
