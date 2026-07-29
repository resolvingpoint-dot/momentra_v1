"""Contract schemas for shared-purchase & shared-living read surfaces (mobile).

Mirror the Android DTOs in ``GroupSharedPurchaseDto`` / ``GroupSharedLivingDto``
(+ ``GroupPurchaseQuickAddDto`` / living quick-add). Reuse the ``TripLiveHub*`` and
operations/memory hub building blocks from :mod:`trip_schemas`. Only the client's
required (no-default) fields are declared; optional client fields are omitted and
default on the client, and list fields default to empty.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.domains.group import trip_schemas as ts


class QuickAddOption(BaseModel):
    id: str
    label: str
    icon: str | None = None


class InviteQuickAddContext(BaseModel):
    supports_link: bool = True
    supports_qr: bool = True
    supports_whatsapp: bool = True
    supports_sms: bool = True
    supports_email: bool = True
    share_message: str


# ----- shared-purchase ---------------------------------------------------- #
class PurchaseSelector(BaseModel):
    moment_id: str
    moment_name: str
    profile_label: str


class PurchaseLiveHub(BaseModel):
    moment_id: str
    participants: list[dict] = Field(default_factory=list)
    selector: PurchaseSelector
    other_active_purchases: list[PurchaseSelector] = Field(default_factory=list)
    header: ts.TripLiveHubHeader
    hero: ts.TripLiveHubHero
    journey_steps: list[ts.TripLiveHubJourneyStep] = Field(default_factory=list)
    quick_add_modules: list[ts.TripLiveHubQuickAddModule] = Field(default_factory=list)
    suggested_actions: list[ts.TripLiveHubPrimaryAction] = Field(default_factory=list)
    activity_items: list[ts.TripLiveHubActivityItem] = Field(default_factory=list)
    activity_preview_items: list[ts.TripLiveHubActivityItem] = Field(default_factory=list)
    show_activity_preview: bool = False
    insight: ts.TripLiveHubInsight
    lifecycle_status: str | None = None
    orchestration_state: str | None = None


class PurchasePulseStats(BaseModel):
    contributors_joined: int = 0
    plan_items: int = 0
    vendors: int = 0
    open_polls: int = 0
    total_expenses_minor: int = 0
    contributions_minor: int = 0
    ownership_status: str = "Unassigned"
    items_finalized: int = 0
    target_amount_minor: int = 0
    remaining_amount_minor: int = 0
    updated_at_display: dict = Field(default_factory=lambda: {"label": "", "minutes_ago": 0})


class PurchasePulse(BaseModel):
    moment_id: str
    moment_name: str
    profile_badge: str
    stage_badge: str
    status_badge: str
    funding_percent: float = 0.0
    funded_amount_minor: int = 0
    target_amount_minor: int = 0
    amount_remaining_minor: int = 0
    currency_code: str = "INR"
    readiness_score: float = 0.0
    readiness_title: str
    readiness_narrative: str
    contributor_count: int = 0
    experience_health_percent: float = 0.0
    participation_percent: float = 0.0
    participation_breakdown: dict = Field(default_factory=lambda: {"active": 0, "pending": 0, "inactive": 0})
    participant_avatars: list[str] = Field(default_factory=list)
    health_dimensions: list[dict] = Field(default_factory=list)
    attention_items: list[dict] = Field(default_factory=list)
    insights: list[dict] = Field(default_factory=list)
    next_best_action: dict | None = None
    dashboard_card: dict | None = None
    metric_tiles: list[dict] = Field(default_factory=list)
    recent_activity: list[dict] = Field(default_factory=list)
    health_trend: dict = Field(default_factory=lambda: {"label": "", "value": 0, "direction": "up"})
    settlement_widget: dict | None = None
    settlement_preview: dict | None = None
    stats: PurchasePulseStats


class PurchaseNextBestAction(BaseModel):
    title: str
    subtitle: str
    action: str


class PurchaseMomentsView(BaseModel):
    moment_id: str
    moment_name: str
    profile_badge: str
    stage_badge: str
    status_badge: str
    funding_percent: float = 0.0
    funded_amount_minor: int = 0
    contributor_count: int = 0
    state_tiles: list[dict] = Field(default_factory=list)
    next_best_action: PurchaseNextBestAction
    health_scores: list[dict] = Field(default_factory=list)
    journey_steps: list[ts.TripLiveHubJourneyStep] = Field(default_factory=list)
    memory_hero_title: str
    memory_hero_subtitle: str
    operations_hub: ts.GroupMomentsOperationsHub
    memory_hub: ts.GroupMomentsMemoryHub


class PurchaseQuickAddHubHero(BaseModel):
    title: str
    subtitle: str


class PurchaseQuickAddHub(BaseModel):
    moment_id: str
    moment_name: str
    context_chips: list[str] = Field(default_factory=list)
    hero: PurchaseQuickAddHubHero
    sections: list[dict] = Field(default_factory=list)
    suggested_first_actions: list[dict] = Field(default_factory=list)


class PurchaseContextBase(BaseModel):
    moment_id: str
    trip_name: str
    status_line: str
    context_chips: list[str] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)
    members: list[dict] = Field(default_factory=list)
    payers: list[dict] = Field(default_factory=list)
    default_paid_by_participant_id: str | None = None


class PurchaseVendorContext(PurchaseContextBase):
    vendor_types: list[QuickAddOption] = Field(default_factory=list)


class PurchaseUpdateContext(PurchaseContextBase):
    update_types: list[QuickAddOption] = Field(default_factory=list)
    visibility_options: list[QuickAddOption] = Field(default_factory=list)


class PurchaseOwnershipContext(PurchaseContextBase):
    usage_rights_options: list[QuickAddOption] = Field(default_factory=list)
    existing_allocations: list[dict] = Field(default_factory=list)
    total_allocated_pct: str = "0"


class PurchaseDeliveryContext(PurchaseContextBase):
    event_types: list[QuickAddOption] = Field(default_factory=list)
    statuses: list[QuickAddOption] = Field(default_factory=list)


# ----- shared-living ------------------------------------------------------ #
class LivingSelector(BaseModel):
    moment_id: str
    moment_name: str
    profile_label: str


class LivingLiveHub(BaseModel):
    moment_id: str
    participants: list[dict] = Field(default_factory=list)
    selector: LivingSelector
    other_active_homes: list[LivingSelector] = Field(default_factory=list)
    header: ts.TripLiveHubHeader
    hero: ts.TripLiveHubHero
    journey_steps: list[ts.TripLiveHubJourneyStep] = Field(default_factory=list)
    quick_add_modules: list[ts.TripLiveHubQuickAddModule] = Field(default_factory=list)
    suggested_actions: list[ts.TripLiveHubPrimaryAction] = Field(default_factory=list)
    activity_items: list[ts.TripLiveHubActivityItem] = Field(default_factory=list)
    activity_preview_items: list[ts.TripLiveHubActivityItem] = Field(default_factory=list)
    show_activity_preview: bool = False
    insight: ts.TripLiveHubInsight
    lifecycle_status: str | None = None
    orchestration_state: str | None = None
    context_chips: list[str] = Field(default_factory=list)


class LivingPulseStats(BaseModel):
    residents_joined: int = 0
    expenses_logged: int = 0
    total_expenses_minor: int = 0
    contributions_minor: int = 0
    open_polls: int = 0
    tasks_open: int = 0
    rules_count: int = 0
    assets_count: int = 0


class LivingPulse(BaseModel):
    moment_id: str
    moment_name: str
    profile_badge: str
    stage_badge: str
    status_badge: str
    health_percent: float = 0.0
    expenses_total_minor: int = 0
    contributions_total_minor: int = 0
    outstanding_minor: int = 0
    currency_code: str = "INR"
    readiness_score: float = 0.0
    readiness_title: str
    readiness_narrative: str
    resident_count: int = 0
    experience_health_percent: float = 0.0
    participation_percent: float = 0.0
    participation_breakdown: dict = Field(default_factory=lambda: {"active": 0, "pending": 0, "inactive": 0})
    participant_avatars: list[str] = Field(default_factory=list)
    health_dimensions: list[dict] = Field(default_factory=list)
    attention_items: list[dict] = Field(default_factory=list)
    insights: list[dict] = Field(default_factory=list)
    next_best_action: dict | None = None
    dashboard_card: dict | None = None
    metric_tiles: list[dict] = Field(default_factory=list)
    recent_activity: list[dict] = Field(default_factory=list)
    health_trend: dict = Field(default_factory=lambda: {"label": "", "value": 0, "direction": "up"})
    operations_progress: dict | None = None
    settlement_widget: dict | None = None
    settlement_preview: dict | None = None
    stats: LivingPulseStats


class LivingNextBestAction(BaseModel):
    title: str
    subtitle: str
    action: str


class LivingMomentsView(BaseModel):
    moment_id: str
    moment_name: str
    profile_badge: str
    stage_badge: str
    status_badge: str
    health_percent: float = 0.0
    expenses_total_minor: int = 0
    resident_count: int = 0
    state_tiles: list[dict] = Field(default_factory=list)
    next_best_action: LivingNextBestAction
    health_scores: list[dict] = Field(default_factory=list)
    journey_steps: list[ts.TripLiveHubJourneyStep] = Field(default_factory=list)
    memory_hero_title: str
    memory_hero_subtitle: str
    operations_hub: ts.GroupMomentsOperationsHub
    memory_hub: ts.GroupMomentsMemoryHub


class LivingQuickAddHubHero(BaseModel):
    title: str
    subtitle: str


class LivingQuickAddHub(BaseModel):
    moment_id: str
    living_name: str
    profile_label: str
    stage_label: str
    context_chips: list[str] = Field(default_factory=list)
    hero: LivingQuickAddHubHero
    suggested_actions: list[dict] = Field(default_factory=list)
    sections: list[dict] = Field(default_factory=list)


class LivingContextBase(BaseModel):
    moment_id: str
    living_name: str
    status_line: str
    context_chips: list[str] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)
    members: list[dict] = Field(default_factory=list)
    payers: list[dict] = Field(default_factory=list)
    default_paid_by_participant_id: str | None = None


class LivingResidentContext(LivingContextBase):
    relationship_types: list[QuickAddOption] = Field(default_factory=list)
    resident_roles: list[QuickAddOption] = Field(default_factory=list)
    statuses: list[QuickAddOption] = Field(default_factory=list)
    guests: list[dict] = Field(default_factory=list)
    invite: InviteQuickAddContext


class LivingExpenseContext(LivingContextBase):
    expense_categories: list[QuickAddOption] = Field(default_factory=list)
    currencies: list[QuickAddOption] = Field(default_factory=list)
    split_types: list[QuickAddOption] = Field(default_factory=list)
    guests: list[dict] = Field(default_factory=list)


class LivingContributionContext(LivingContextBase):
    contribution_categories: list[QuickAddOption] = Field(default_factory=list)
    payment_methods: list[QuickAddOption] = Field(default_factory=list)
    contribution_statuses: list[QuickAddOption] = Field(default_factory=list)


class LivingTaskContext(LivingContextBase):
    task_categories: list[QuickAddOption] = Field(default_factory=list)
    frequencies: list[QuickAddOption] = Field(default_factory=list)
    priorities: list[QuickAddOption] = Field(default_factory=list)


class LivingRuleContext(LivingContextBase):
    rule_types: list[QuickAddOption] = Field(default_factory=list)
    visibility_options: list[QuickAddOption] = Field(default_factory=list)


class LivingAssetContext(LivingContextBase):
    asset_types: list[QuickAddOption] = Field(default_factory=list)


class LivingMaintenanceContext(LivingContextBase):
    maintenance_types: list[QuickAddOption] = Field(default_factory=list)


class LivingUpdateContext(LivingContextBase):
    update_types: list[QuickAddOption] = Field(default_factory=list)
    visibility_options: list[QuickAddOption] = Field(default_factory=list)


class LivingPollContext(LivingContextBase):
    poll_categories: list[QuickAddOption] = Field(default_factory=list)
    poll_types: list[QuickAddOption] = Field(default_factory=list)
    max_options: int = 6
    min_options: int = 2
    supports_anonymous: bool = True
    supports_expiry: bool = True


class LivingMemoryContext(LivingContextBase):
    memory_categories: list[QuickAddOption] = Field(default_factory=list)
    memory_formats: list[QuickAddOption] = Field(default_factory=list)
