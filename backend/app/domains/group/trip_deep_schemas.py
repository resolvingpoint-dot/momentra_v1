"""Contract schemas for the trips *deep* modules (mobile).

Mirror the Android DTOs in ``GroupLiveWorkspaceDto`` / ``GroupTripCorpusDto`` /
``GroupTripSettlementDto`` / ``GroupTripApprovalDto`` / ``GroupTripPlanDto`` /
``GroupContributionDto`` / ``GroupExpenseDto`` / ``GroupTripQuickAddDto`` /
``TripCreationDto``. Only the client's required fields are declared; optional
fields are omitted (defaulted on the client) and lists default to empty.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.domains.group import trip_schemas as ts
from app.domains.group.read_schemas import QuickAddOption


# ----- live-workspace ----------------------------------------------------- #
class LiveWorkspaceHeader(BaseModel):
    moment_name: str
    status_line: str
    stage_label: str
    cover_image_url: str | None = None


class LiveWorkspaceHero(BaseModel):
    title: str
    subtitle: str


class LiveWorkspaceAttendance(BaseModel):
    confirmed_count: int = 0
    avatar_urls: list[str] = Field(default_factory=list)
    overflow_count: int = 0


class TripLiveWorkspace(BaseModel):
    moment_id: str
    header: LiveWorkspaceHeader
    hero: LiveWorkspaceHero
    filter_chips: list[dict] = Field(default_factory=list)
    feed_items: list[dict] = Field(default_factory=list)
    attendance: LiveWorkspaceAttendance = Field(default_factory=LiveWorkspaceAttendance)
    change_history: list[dict] = Field(default_factory=list)
    quick_add_modules: list[ts.TripLiveHubQuickAddModule] = Field(default_factory=list)


# ----- corpus ------------------------------------------------------------- #
class TripCorpusSummary(BaseModel):
    moment_id: str
    trip_name: str
    currency_code: str = "INR"
    corpus_balance_minor: int = 0
    total_deposits_minor: int = 0
    total_disbursements_minor: int = 0
    custodian_user_id: str | None = None
    custodian_display_name: str | None = None
    ledger: list[dict] = Field(default_factory=list)
    members: list[dict] = Field(default_factory=list)


# ----- settlements -------------------------------------------------------- #
class TripSettlementContext(BaseModel):
    moment_id: str
    trip_name: str
    status_line: str
    balance_sync_percent: float = 100.0
    balance_insight: str
    harmony_label: str
    pending_balances: list[dict] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)
    guests: list[dict] = Field(default_factory=list)


# ----- approvals ---------------------------------------------------------- #
class TripApprovalDecisionDetail(BaseModel):
    id: str
    slug: str
    title: str
    member_votes: list[dict] = Field(default_factory=list)
    current_user_vote_status: str | None = None


class TripApprovalPollCard(BaseModel):
    id: str
    question: str
    status: str
    options: list[dict] = Field(default_factory=list)
    total_votes: int = 0


class TripApprovalContext(BaseModel):
    moment_id: str
    trip_name: str
    status_line: str
    sync_insight: str
    selected_decision_slug: str
    queue: list[dict] = Field(default_factory=list)
    featured_decision: TripApprovalDecisionDetail | None = None
    polls: list[TripApprovalPollCard] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)


# ----- plans -------------------------------------------------------------- #
class TripPlanContext(BaseModel):
    moment_id: str
    trip_name: str
    status_line: str
    selected_category: str
    categories: list[dict] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)
    ai_insight: str


class GroupTripPlanResponse(BaseModel):
    id: str
    moment_id: str
    category: str
    title: str
    details: dict[str, Any] = Field(default_factory=dict)
    needs_coordination: bool = False
    participant_user_ids: list[str] = Field(default_factory=list)


# ----- contributions ------------------------------------------------------ #
class TripContributionContext(BaseModel):
    moment_id: str
    trip_name: str
    currency_code: str = "INR"
    funding_target_minor: int | None = None
    pools: list[dict] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)
    ai_insight: str
    status_line: str


class GroupContributionResponse(BaseModel):
    id: str
    moment_id: str
    contributor_user_id: str
    amount_minor: int
    currency_code: str = "INR"
    title: str | None = None
    allocation_category: str | None = None


# ----- expenses ----------------------------------------------------------- #
class GroupExpenseResponse(BaseModel):
    id: str
    moment_id: str
    paid_by_user_id: str
    paid_by_participant_id: str | None = None
    amount_minor: int
    currency_code: str = "INR"
    title: str | None = None
    description: str
    category: str | None = None
    category_code: str | None = None
    subcategory_code: str | None = None
    split_type: str = "equal"
    split_style: str | None = None
    expense_date: str
    occurred_at: str | None = None
    participant_ids: list[str] = Field(default_factory=list)
    split_details: Any | None = None
    notes: str | None = None
    client_request_id: str | None = None
    is_settled: bool = False
    shares: list[dict] = Field(default_factory=list)


# ----- quick-add contexts ------------------------------------------------- #
class TripContextBase(BaseModel):
    moment_id: str
    trip_name: str
    status_line: str
    context_chips: list[str] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)


class ParticipantQuickAddContext(TripContextBase):
    relationship_types: list[QuickAddOption] = Field(default_factory=list)
    statuses: list[QuickAddOption] = Field(default_factory=list)
    guests: list[dict] = Field(default_factory=list)
    invite: "InviteQuickAddContextOut"


class InviteQuickAddContextOut(BaseModel):
    supports_link: bool = True
    supports_qr: bool = True
    supports_whatsapp: bool = True
    supports_sms: bool = True
    supports_email: bool = True
    share_message: str


class BookingQuickAddContext(TripContextBase):
    booking_types: list[QuickAddOption] = Field(default_factory=list)
    booking_statuses: list[QuickAddOption] = Field(default_factory=list)


class PlanningItemQuickAddContext(TripContextBase):
    planning_categories: list[QuickAddOption] = Field(default_factory=list)
    planning_statuses: list[QuickAddOption] = Field(default_factory=list)


class ExpenseQuickAddContext(TripContextBase):
    category_sections: list[dict] = Field(default_factory=list)
    expense_categories: list[dict] = Field(default_factory=list)
    currencies: list[QuickAddOption] = Field(default_factory=list)
    split_types: list[QuickAddOption] = Field(default_factory=list)
    guests: list[dict] = Field(default_factory=list)
    # Payers for expense "Paid by" dropdown: id is user_id when linked, else member/guest id.
    payers: list[dict] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)
    default_currency_code: str = "INR"
    allow_multi_currency: bool = True
    default_paid_by_participant_id: str | None = None
    members: list[dict] = Field(default_factory=list)


class MemoryQuickAddContext(TripContextBase):
    memory_categories: list[QuickAddOption] = Field(default_factory=list)
    memory_formats: list[QuickAddOption] = Field(default_factory=list)
    upload_requirements: dict[str, Any] = Field(default_factory=dict)


class PollQuickAddContext(TripContextBase):
    poll_types: list[QuickAddOption] = Field(default_factory=list)
    category_tags: list[QuickAddOption] = Field(default_factory=list)
    max_options: int = 6
    min_options: int = 2
    supports_anonymous: bool = True
    supports_expiry: bool = True


class AttendanceQuickAddContext(TripContextBase):
    attendance_types: list[QuickAddOption] = Field(default_factory=list)
    statuses: list[QuickAddOption] = Field(default_factory=list)


class BudgetQuickAddContext(TripContextBase):
    templates: list[QuickAddOption] = Field(default_factory=list)
    categories: list[QuickAddOption] = Field(default_factory=list)
    participant_count: int = 1
    existing_plan_id: str | None = None
    default_currency_code: str = "INR"


class BudgetAllocationItem(BaseModel):
    category_code: str
    amount_minor: int = 0
    percent: float | None = None


class BudgetPlanResponse(BaseModel):
    id: str
    moment_id: str
    template_id: str
    total_amount_minor: int = 0
    currency_code: str = "INR"
    allocations: list[BudgetAllocationItem] = Field(default_factory=list)
    split_method: str = "EQUAL"
    participant_count: int = 1
    contribution_per_person_minor: int | None = None
    notes: str | None = None
    created_at: str | None = None


class VendorQuickAddContext(TripContextBase):
    vendor_types: list[QuickAddOption] = Field(default_factory=list)


class UpdateQuickAddContext(TripContextBase):
    update_types: list[QuickAddOption] = Field(default_factory=list)
    visibility_options: list[QuickAddOption] = Field(default_factory=list)


# ----- quick-add create responses ----------------------------------------- #
class BookingResponse(BaseModel):
    id: str
    moment_id: str
    booking_type: str
    provider: str | None = None
    booking_status: str = "planned"
    amount_minor: int = 0
    description: str | None = None


class VendorResponse(BaseModel):
    id: str
    moment_id: str
    vendor_name: str
    vendor_type: str | None = None
    contact: str | None = None
    notes: str | None = None


class UpdateResponse(BaseModel):
    id: str
    moment_id: str
    title: str
    body: str | None = None
    update_type: str | None = None
    visibility: str | None = None


class AttendanceResponse(BaseModel):
    id: str
    moment_id: str
    member_id: str
    attendance_type: str
    status: str = "CONFIRMED"
    notes: str | None = None


class GroupMomentGuestResponse(BaseModel):
    id: str
    moment_id: str
    full_name: str
    phone: str | None = None
    email: str | None = None
    relationship_type: str
    assigned_role: str | None = None
    status: str = "invited"
    created_at: str


class AttachmentUploadUrlResponse(BaseModel):
    upload_url: str
    storage_path: str
    token: str | None = None


class AttachmentConfirmResponse(BaseModel):
    storage_path: str


# ----- trip-creation-options ---------------------------------------------- #
class TripOptionItem(BaseModel):
    id: str
    label: str
    icon: str


class TripCreationOptions(BaseModel):
    hero_image_url: str
    vibes: list[TripOptionItem] = Field(default_factory=list)
    budget_moods: list[TripOptionItem] = Field(default_factory=list)


ParticipantQuickAddContext.model_rebuild()
