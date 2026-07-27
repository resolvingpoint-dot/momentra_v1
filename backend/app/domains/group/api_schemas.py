"""Request/response DTOs for the Group module router.

Input contracts + composite responses for rich OpenAPI. Read payloads reuse the
generated per-table schemas; the service returns only schemas (never models).
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domains.group.schemas import (
    GroupAiInsightsSchema,
    GroupHealthSnapshotsSchema,
    GroupMemoryEntriesSchema,
    GroupMemoryPatternsSchema,
    GroupMemorySnapshotsSchema,
    GroupPeopleImpactScoresSchema,
    GroupPollOptionsSchema,
    GroupPollsSchema,
    GroupRecommendationsSchema,
)

SplitMethod = Literal["EQUAL", "CUSTOM_AMOUNT", "CUSTOM_PERCENTAGE", "ORGANIZER_PAID"]
PollType = Literal["SINGLE_CHOICE", "MULTIPLE_CHOICE", "YES_NO", "RANKING"]
TaskFrequency = Literal["ONE_TIME", "DAILY", "WEEKLY", "MONTHLY", "CUSTOM"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ------------------------------ moments ------------------------------------ #
class GroupMomentCreateRequest(_Strict):
    moment_type: str = Field(min_length=1, max_length=50)
    moment_profile: str = Field(min_length=1, max_length=100)
    moment_name: str = Field(min_length=1, max_length=200)
    currency_code: str = Field(default="INR", max_length=10)
    experience_subtype: str | None = Field(default=None, max_length=100)
    organizer_display_name: str = Field(default="Organizer", max_length=200)


# ------------------------------ members / invitations ---------------------- #
class GroupInviteRequest(_Strict):
    display_name: str = Field(min_length=1, max_length=200)
    role_code: str = Field(min_length=1, max_length=100)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=30)


class GroupInviteAcceptRequest(_Strict):
    """Secret minted at invite time — required to claim an INVITED seat."""

    invite_token: UUID


# ------------------------------ expenses ----------------------------------- #
class GroupExpenseSplitInput(_Strict):
    member_id: UUID
    split_method: SplitMethod = "EQUAL"
    split_amount: Decimal = Field(ge=0)
    split_percentage: Decimal | None = Field(default=None, ge=0, le=100)


class GroupExpenseCreateRequest(_Strict):
    module_context: str = Field(min_length=1, max_length=50)
    category: str = Field(min_length=1, max_length=100)
    expense_name: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0)
    expense_date: date
    paid_by_member_id: UUID | None = None
    notes: str | None = None
    splits: list[GroupExpenseSplitInput] = []


# ------------------------------ purchases ---------------------------------- #
class GroupPurchaseItemCreateRequest(_Strict):
    category: str = Field(min_length=1, max_length=100)
    item_name: str = Field(min_length=1, max_length=200)
    target_price: Decimal | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=1, ge=1)
    priority: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    purchase_link: str | None = None
    notes: str | None = None


# ------------------------------ shared living ------------------------------ #
class GroupLivingTaskCreateRequest(_Strict):
    category: str = Field(min_length=1, max_length=100)
    task_name: str = Field(min_length=1, max_length=200)
    frequency: TaskFrequency = "ONE_TIME"
    assigned_to_member_id: UUID | None = None
    due_date: date | None = None
    priority: Literal["LOW", "MEDIUM", "HIGH"] | None = None
    notes: str | None = None


# ------------------------------ events (work items) ------------------------ #
class GroupEventCreateRequest(_Strict):
    title: str = Field(min_length=1, max_length=250)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = None
    event_date: datetime | None = None
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] | None = None
    owner_id: UUID | None = None
    source_quick_add: str = Field(default="EVENTS", max_length=100)


# ------------------------------ polls -------------------------------------- #
class GroupPollOptionInput(_Strict):
    option_text: str = Field(min_length=1, max_length=250)
    sort_order: int | None = Field(default=None, ge=1)


class GroupPollCreateRequest(_Strict):
    category: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=300)
    poll_type: PollType = "SINGLE_CHOICE"
    is_anonymous: bool = False
    allow_multiple_votes: bool = False
    end_date: date | None = None
    options: list[GroupPollOptionInput] = Field(min_length=2)


class GroupPollVoteRequest(_Strict):
    option_id: UUID


class GroupPollDetail(BaseModel):
    poll: GroupPollsSchema
    options: list[GroupPollOptionsSchema] = []
    tally: dict[str, int] = {}


# ------------------------------ quick add ---------------------------------- #
class GroupQuickAddRequest(_Strict):
    module_code: str = Field(min_length=1, max_length=100)
    event_ref_table: str = Field(min_length=1, max_length=150)
    event_ref_id: UUID
    event_action: Literal["CREATED", "EDITED", "DELETED"] = "CREATED"
    event_payload_json: dict[str, Any] | None = None


# ------------------------------ memory / analytics ------------------------- #
class GroupMemoryOverviewResponse(BaseModel):
    entries: list[GroupMemoryEntriesSchema] = []
    patterns: list[GroupMemoryPatternsSchema] = []
    snapshots: list[GroupMemorySnapshotsSchema] = []


class GroupAnalyticsCounts(BaseModel):
    members: int = 0
    active_members: int = 0
    expenses: int = 0
    open_events: int = 0
    open_polls: int = 0
    memories: int = 0


class GroupAnalyticsResponse(BaseModel):
    counts: GroupAnalyticsCounts
    insights: list[GroupAiInsightsSchema] = []
    recommendations: list[GroupRecommendationsSchema] = []
    health: list[GroupHealthSnapshotsSchema] = []
    people_impact: list[GroupPeopleImpactScoresSchema] = []
