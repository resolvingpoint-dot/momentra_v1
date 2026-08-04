"""Pydantic schemas for the Group mobile contract.

Each response is the **union** of the fields the Android (`apk_copy`) and iOS
(`ios_copy`) clients decode for a given path, so one payload satisfies both.
Every field carries a default (scalars) or ``default_factory`` (collections) so
``model_dump(mode="json")`` always emits the full key set and neither client's
strict decoder trips on a missing key.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Shared building blocks
# --------------------------------------------------------------------------- #
class GroupMomentTypeCard(BaseModel):
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    create_tagline: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    accent_main: str | None = None
    accent_soft_tint: str | None = None
    card_layout: str | None = None
    display_order: int = 0
    linked_moment_id: str | None = None
    linked_moment_status: str | None = None
    cover_image_url: str | None = None
    action_label: str = "Begin"


class GroupEmptyStateItem(BaseModel):
    item_code: str
    item_kind: str
    title: str
    description: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    accent_main: str | None = None
    accent_soft_tint: str | None = None
    badge_label: str | None = None
    card_layout: str | None = None
    display_order: int = 0


class GroupScreenAsset(BaseModel):
    asset_role: str
    image_url: str
    alt_text: str | None = None
    display_order: int = 0


class GroupCreateOptionCard(BaseModel):
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    create_tagline: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    accent_main: str | None = None
    accent_soft_tint: str | None = None
    card_layout: str | None = None
    display_order: int = 0


# --------------------------------------------------------------------------- #
# Empty-state / landing surfaces
# --------------------------------------------------------------------------- #
class GroupPulseResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    hero_title: str = "Better together"
    hero_subtitle: str = "Plan, spend and remember with the people who matter."
    hero_image_url: str | None = None
    cta_label: str = "Start a group moment"
    type_section_title: str = "What will you build together?"
    type_section_subtitle: str = "Pick a starting point — you can invite people next."
    type_cards: list[GroupMomentTypeCard] = Field(default_factory=list)
    why_groups: list[GroupEmptyStateItem] = Field(default_factory=list)
    magic_intro: str = "How Momentra keeps your group in sync"
    magic_steps: list[GroupEmptyStateItem] = Field(default_factory=list)


class GroupMomentsHomeResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    hero_title: str = "Your group moments"
    hero_subtitle: str = "Everything you are building together, in one place."
    cta_label: str = "Create a group moment"
    cta_subtitle: str = "Start something new with your people."
    type_cards: list[GroupMomentTypeCard] = Field(default_factory=list)
    how_it_works: list[GroupEmptyStateItem] = Field(default_factory=list)


class GroupLiveEmptyResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    hero_title: str = "Live together"
    hero_subtitle: str = "See what everyone is doing, as it happens."
    hero_image_url: str | None = None
    section_title: str = "What comes alive here"
    section_subtitle: str = "Activate a moment to light up the live board."
    pillars: list[GroupEmptyStateItem] = Field(default_factory=list)
    empty_title: str = "Nothing live yet"
    empty_subtitle: str = "Create and activate a group moment to get started."
    cta_label: str = "Create a group moment"


class GroupMemoryResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    hero_title: str = "Memories you make together"
    hero_subtitle: str = "The story of your group, kept forever."
    section_title: str = "Your shared timeline"
    polaroids: list[GroupScreenAsset] = Field(default_factory=list)
    insights: list[GroupEmptyStateItem] = Field(default_factory=list)
    empty_title: str = "No memories yet"
    empty_subtitle: str = "Finish a group moment and it will live here."
    cta_label: str = "Create a group moment"


class GroupCreateOptionsResponse(BaseModel):
    hero_title: str = "Create a group moment"
    hero_subtitle: str = "Choose what you want to build together."
    hero_image_url: str | None = None
    cta_label: str = "Continue"
    preview_text: str | None = None
    cards: list[GroupCreateOptionCard] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Life (health) surface
# --------------------------------------------------------------------------- #
class GroupLifeSatelliteScore(BaseModel):
    moment_type_code: str
    label: str
    score: int | None = None
    color_token: str


class GroupLifeHealthHero(BaseModel):
    life_score: int
    status_label: str
    delta_month: int | None = None
    insight_quote: str
    satellite_scores: list[GroupLifeSatelliteScore] = Field(default_factory=list)


class GroupLifeBalanceDimension(BaseModel):
    dimension_code: str
    label: str
    score: int
    badge_label: str
    badge_color_token: str


class GroupLifeBalanceModel(BaseModel):
    subtitle: str
    dimensions: list[GroupLifeBalanceDimension] = Field(default_factory=list)


class GroupLifeDriver(BaseModel):
    source_type_code: str
    title: str
    relation: str
    icon: str
    accent_token: str
    impact_percent: int
    body: str
    action: str
    priority: str


class GroupLifeDriftAlert(BaseModel):
    title: str
    body: str
    impact_label: str
    impact_body: str


class GroupLifeLeverage(BaseModel):
    title: str
    impact_lines: list[str] = Field(default_factory=list)
    impact_score: int
    confidence_label: str


class GroupLifeEvolutionPoint(BaseModel):
    label: str
    value: int


class GroupLifeEvolutionSeries(BaseModel):
    dimension_code: str
    label: str
    delta_percent: int
    color_token: str
    points: list[GroupLifeEvolutionPoint] = Field(default_factory=list)


class GroupLifeMonthlyChange(BaseModel):
    change_code: str
    label: str
    delta_percent: int
    color_token: str


class GroupLifeJourneyItem(BaseModel):
    event_key: str
    title: str
    subtitle: str | None = None
    icon: str
    accent_token: str
    is_current: bool = False


class GroupLifeIntelligence(BaseModel):
    insight_text: str
    confidence_label: str
    dimension_pills: list[str] = Field(default_factory=list)


class GroupLifeQuickAction(BaseModel):
    action_code: str
    label: str
    moment_type_code: str
    color_token: str


class GroupLifeMetrics(BaseModel):
    life_health: GroupLifeHealthHero
    balance_model: GroupLifeBalanceModel
    drivers: list[GroupLifeDriver] = Field(default_factory=list)
    drift_alert: GroupLifeDriftAlert | None = None
    leverage: GroupLifeLeverage | None = None
    evolution: list[GroupLifeEvolutionSeries] = Field(default_factory=list)
    monthly_changes: list[GroupLifeMonthlyChange] = Field(default_factory=list)
    journey: list[GroupLifeJourneyItem] = Field(default_factory=list)
    intelligence: GroupLifeIntelligence
    quick_actions: list[GroupLifeQuickAction] = Field(default_factory=list)


class GroupLifeResponse(BaseModel):
    active_moment_count: int = 0
    is_empty: bool = True
    date_range_label: str | None = None
    metrics: GroupLifeMetrics | None = None


class GroupActiveLifeResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    metrics: GroupLifeMetrics | None = None


# --------------------------------------------------------------------------- #
# Moment CRUD
# --------------------------------------------------------------------------- #
class GroupMomentCreateRequest(BaseModel):
    moment_type_code: str
    moment_name: str | None = None


class GroupMomentUpdateRequest(BaseModel):
    moment_name: str | None = None
    status: str | None = None


class GroupDraftMomentResponse(BaseModel):
    moment_id: str
    moment_type_code: str
    moment_name: str
    cover_image_url: str | None = None
    orchestration_state: str | None = None


class GroupMomentManageResponse(BaseModel):
    moment_id: str
    moment_type_code: str
    moment_name: str
    cover_image_url: str | None = None
    orchestration_state: str | None = None
    lifecycle_status: str | None = None
    status: str = "DRAFT"
    is_archived: bool = False


class GroupMomentTemplate(BaseModel):
    id: str
    moment_type: str
    title: str
    subtitle: str
    icon: str
    image_url: str = ""
    layout: str = "standard"
    sort_order: int = 0
    default_name: str = ""


# --------------------------------------------------------------------------- #
# Session bootstrap (Android nested + iOS flat union)
# --------------------------------------------------------------------------- #
class GroupMomentListItem(BaseModel):
    id: str
    name: str
    cover_image_url: str | None = None
    moment_type: str | None = None
    category: str = "trips"
    status_label: str = "Draft"
    status_tone: str = "neutral"
    subtitle: str | None = None
    orchestration_state: str | None = None
    readiness_score: float | None = None
    lifecycle_status: str | None = None
    is_owned: bool = True
    trip_live_meta: dict | None = None
    updated_at: str = ""


class GroupLiveParticipant(BaseModel):
    user_id: str
    display_name: str
    photo_url: str | None = None


class GroupLiveOverview(BaseModel):
    sync_energy_percent: float = 0.0
    active_moment_count: int = 0
    total_group_moment_count: int = 0
    participants: list[GroupLiveParticipant] = Field(default_factory=list)
    live_cards: list[GroupMomentListItem] = Field(default_factory=list)


class GroupSessionResponse(BaseModel):
    """Stable session chrome — changes rarely (draft/focus/counts)."""

    is_empty: bool = True
    active_moment_count: int = 0
    focus_moment_id: str | None = None
    active_moment_id: str | None = None
    moment_type: str | None = None
    draft_moment_id: str | None = None
    draft_moment_type: str | None = None
    has_draft: bool = False
    linked_moment_status: str | None = None


class GroupInventoryResponse(BaseModel):
    """Frequent inventory refresh — moments, pulse cards, live overview."""

    pulse: GroupPulseResponse
    moments: list[GroupMomentListItem] = Field(default_factory=list)
    live_overview: GroupLiveOverview = Field(default_factory=GroupLiveOverview)


class GroupSessionBootstrapResponse(BaseModel):
    # Android nested shape
    pulse: GroupPulseResponse
    moments: list[GroupMomentListItem] = Field(default_factory=list)
    live_overview: GroupLiveOverview = Field(default_factory=GroupLiveOverview)
    focus_moment_id: str | None = None
    focus_trip_pulse: dict | None = None
    focus_purchase_pulse: dict | None = None
    focus_living_pulse: dict | None = None
    # iOS flat shape
    is_empty: bool = True
    active_moment_count: int = 0
    active_moment_id: str | None = None
    moment_type: str | None = None
    moment_profile: str | None = None
    setup_step: str | None = None
    create_options: list[GroupCreateOptionCard] | None = None
    pulse_data: dict | None = None
    moments_data: list[dict] | None = None
    memory_data: dict | None = None
    # Phase 2 resume
    draft_moment_id: str | None = None
    draft_moment_type: str | None = None
    has_draft: bool = False
    linked_moment_status: str | None = None


# --------------------------------------------------------------------------- #
# Setup flow (both path variants)
# --------------------------------------------------------------------------- #
class GroupSetupProfile(BaseModel):
    profile_id: str
    moment_type: str
    profile_code: str
    profile_name: str
    profile_description: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    display_order: int = 0


class GroupSetupBasicsResponse(BaseModel):
    moment_id: str
    moment_type_code: str
    moment_name: str
    lifecycle_status: str = "SETUP"
    cover_image_url: str | None = None
    orchestration_state: str | None = None


class GroupSetupPeopleResponse(BaseModel):
    moment_id: str
    moment_type_code: str = ""
    moment_name: str = ""
    status: str = "SETUP"
    cover_image_url: str | None = None
    orchestration_state: str | None = None


class GroupSetupReviewItem(BaseModel):
    label: str
    value: str
    icon_name: str | None = None


class GroupMemberEntry(BaseModel):
    name: str
    email: str
    role: str | None = None


class GroupSetupReviewResponse(BaseModel):
    moment_id: str
    moment_name: str = ""
    profile_name: str = ""
    summary_items: list[GroupSetupReviewItem] = Field(default_factory=list)
    insight_text: str | None = None
    # iOS extras
    moment_type: str = ""
    moment_profile: str = ""
    basics: dict = Field(default_factory=dict)
    people: list[GroupMemberEntry] = Field(default_factory=list)
    coordination: dict | None = None


class GroupSetupActivateResponse(BaseModel):
    moment_id: str
    lifecycle_status: str = "ACTIVE"
    activated_at: str = ""
    # iOS GroupDraftMomentResponse extras
    moment_type_code: str = ""
    moment_name: str = ""
    cover_image_url: str | None = None
    orchestration_state: str | None = None


# --------------------------------------------------------------------------- #
# Life-ops activity
# --------------------------------------------------------------------------- #
class GroupLifeOpsActivitySummary(BaseModel):
    total_logs: int = 0
    this_month: int = 0


class GroupLifeOpsActivityItem(BaseModel):
    id: str
    event_type: str
    category_label: str
    detail_line: str
    relative_time: str
    captured_at: str
    icon: str | None = None
    actor_name: str | None = None
    can_edit: bool = False


class GroupLifeOpsActivityResponse(BaseModel):
    moment_id: str
    summary: GroupLifeOpsActivitySummary = Field(default_factory=GroupLifeOpsActivitySummary)
    items: list[GroupLifeOpsActivityItem] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# iOS active surface
# --------------------------------------------------------------------------- #
class GroupPulseDataResponse(BaseModel):
    moment_id: str
    moment_type: str = ""
    moment_profile: str = ""
    moment_name: str = ""
    health_score: float = 0.0
    health_status: str = "Getting started"
    people_score: float = 0.0
    money_score: float = 0.0
    activity_score: float = 0.0
    completion_percentage: float = 0.0
    participation_percentage: float = 0.0
    funding_percentage: float = 0.0
    active_members: int = 0
    active_tasks: int = 0
    open_items: int = 0


class GroupMemoryDataContainer(BaseModel):
    highlights: list[dict] = Field(default_factory=list)
    patterns: list[dict] = Field(default_factory=list)
    insights: list[dict] = Field(default_factory=list)


class GroupLifeDataResponse(BaseModel):
    overall_health_score: float = 0.0
    balance_model_scores: list[dict] = Field(default_factory=list)
    life_journey_events: list[dict] = Field(default_factory=list)
    ai_insights: list[dict] = Field(default_factory=list)


class GroupQuickAddConfigResponse(BaseModel):
    moment_id: str
    moment_type: str = ""
    moment_profile: str = ""
    categories: list[dict] = Field(default_factory=list)
