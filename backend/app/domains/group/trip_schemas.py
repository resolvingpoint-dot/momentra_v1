"""Contract schemas for the Group *trips* read surfaces (mobile).

Mirror the Android DTOs in ``TripLiveHubDto`` / ``GroupTripPulseDto`` /
``TripMomentsViewDto`` / ``GroupMomentsOperationsHubDto`` / ``GroupMemoryHubDto``.
Only the client's required (no-default) fields must be populated; list fields
default to empty and optional nested objects to ``None``. These power the trips
live-hub / pulse / moments-view screens as schema-valid empty/seeded shapes.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ----- live-hub building blocks ------------------------------------------- #
class TripLiveHubHeader(BaseModel):
    moment_name: str
    status_badge: str
    profile_badge: str
    settings_available: bool = True


class TripLiveHubHero(BaseModel):
    cover_image_url: str | None = None
    title: str
    subtitle: str


class TripLiveHubActivationBanner(BaseModel):
    title: str
    message: str


class TripLiveHubExperienceProfile(BaseModel):
    title: str
    description: str
    capability_chips: list[str] = Field(default_factory=list)
    profile_icon: str | None = None


class TripLiveHubSnapshot(BaseModel):
    id: str
    label: str
    value: str


class TripLiveHubJourneyStep(BaseModel):
    id: str
    label: str
    state: str


class TripLiveHubCreationEvent(BaseModel):
    title: str
    subtitle: str
    icon: str = "auto_awesome"


class TripLiveHubQuickAddModule(BaseModel):
    module_code: str
    label: str
    icon: str


class TripLiveHubPrimaryAction(BaseModel):
    id: str
    title: str
    subtitle: str
    icon: str
    action: str


class TripLiveHubActivityItem(BaseModel):
    id: str
    activity_type: str
    title: str
    subtitle: str
    icon: str
    occurred_at: str


class TripLiveHubInsight(BaseModel):
    title: str
    message: str


class TripLiveHubResponse(BaseModel):
    moment_id: str
    participants: list[dict] = Field(default_factory=list)
    readiness_score: float = 0.0
    header: TripLiveHubHeader
    hero: TripLiveHubHero
    activation_banner: TripLiveHubActivationBanner | None = None
    experience_profile: TripLiveHubExperienceProfile
    snapshots: list[TripLiveHubSnapshot] = Field(default_factory=list)
    journey_steps: list[TripLiveHubJourneyStep] = Field(default_factory=list)
    creation_event: TripLiveHubCreationEvent
    quick_add_modules: list[TripLiveHubQuickAddModule] = Field(default_factory=list)
    primary_actions: list[TripLiveHubPrimaryAction] = Field(default_factory=list)
    activity_items: list[TripLiveHubActivityItem] = Field(default_factory=list)
    activity_empty_message: str | None = None
    insight: TripLiveHubInsight
    lifecycle_status: str | None = None
    orchestration_state: str | None = None
    can_open_live_workspace: bool = False


# ----- pulse -------------------------------------------------------------- #
class TripPulseStats(BaseModel):
    participants_joined: int = 0
    members_joined: int = 0
    guests_joined: int = 0
    participants_expected: int | None = None
    active_plan_items: int = 0
    confirmed_bookings: int = 0
    total_expenses_minor: int = 0
    total_expenses_currency: str = "INR"
    total_budget_minor: int = 0
    contributions_minor: int = 0
    contributions_currency: str = "INR"
    corpus_balance_minor: int = 0
    open_polls: int = 0
    memories_count: int = 0
    memory_contributor_avatars: list[str] = Field(default_factory=list)
    updated_at_display: dict = Field(default_factory=lambda: {"label": "", "minutes_ago": 0})


class TripPulseResponse(BaseModel):
    moment_id: str
    trip_name: str
    cover_image_url: str | None = None
    profile_badge: str
    stage_badge: str
    status_badge: str
    readiness_score: float = 0.0
    readiness_title: str
    readiness_narrative: str
    stats: TripPulseStats
    attention_items: list[dict] = Field(default_factory=list)
    experience_signals: list[dict] = Field(default_factory=list)
    focus_options: list[dict] = Field(default_factory=list)
    experience_health_percent: float = 0.0
    participation_percent: float = 0.0
    participant_avatars: list[str] = Field(default_factory=list)
    participation_breakdown: dict = Field(default_factory=lambda: {"active": 0, "pending": 0, "inactive": 0})
    days_remaining: int | None = None
    health_trend: dict = Field(default_factory=lambda: {"label": "", "value": 0, "direction": "up"})
    next_best_action: dict | None = None
    dashboard_card: dict | None = None
    health_dimensions: list[dict] = Field(default_factory=list)
    insights: list[dict] = Field(default_factory=list)
    open_live_label: str = "Open Live Workspace"
    quick_add_label: str = "Quick Add"


# ----- operations hub ----------------------------------------------------- #
class GroupMomentsStatTile(BaseModel):
    label: str
    value: str
    highlight: bool = False


class GroupMomentsCoreSummary(BaseModel):
    eyebrow: str
    eyebrow_icon: str = "palette"
    moment_name: str
    stage_badge: str
    stat_tiles: list[GroupMomentsStatTile] = Field(default_factory=list)


class GroupMomentsPeopleRoles(BaseModel):
    primary: dict | None = None
    role_counts: list[dict] = Field(default_factory=list)
    view_all_action: str = "members"


class GroupMomentsMoneyColumn(BaseModel):
    label: str
    value: str
    highlight: bool = False


class GroupMomentsMoneyStatus(BaseModel):
    progress_label: str
    progress_percent: float
    columns: list[GroupMomentsMoneyColumn] = Field(default_factory=list)


class GroupMomentsCurrentState(BaseModel):
    stage_label: str
    focus_items: list[dict] = Field(default_factory=list)
    cta_label: str = ""
    cta_action: str = "hub"
    hero_icon: str = "flight_takeoff"


class GroupMomentsOperationsHub(BaseModel):
    core_summary: GroupMomentsCoreSummary
    people_roles: GroupMomentsPeopleRoles = Field(default_factory=GroupMomentsPeopleRoles)
    money_status: GroupMomentsMoneyStatus
    activity_ops: list[dict] = Field(default_factory=list)
    assets: list[dict] = Field(default_factory=list)
    decisions: list[dict] = Field(default_factory=list)
    current_state: GroupMomentsCurrentState


# ----- memory hub --------------------------------------------------------- #
class GroupMemoryHero(BaseModel):
    moment_name: str
    cover_image_url: str | None = None
    chips: list[dict] = Field(default_factory=list)
    hero_icon: str = "auto_awesome"


class GroupMomentsMemoryHub(BaseModel):
    hero: GroupMemoryHero
    timeline: list[dict] = Field(default_factory=list)
    milestone_wall: list[dict] = Field(default_factory=list)
    people_impact: list[dict] = Field(default_factory=list)
    gallery: list[dict] = Field(default_factory=list)
    lessons_pattern: str = ""
    group_identity: str = ""
    highlights: list[dict] = Field(default_factory=list)
    intelligence: dict = Field(default_factory=lambda: {"metrics": [], "insight": ""})
    budget_reflection: dict | None = None


# ----- moments-view ------------------------------------------------------- #
class TripMomentsMemoryHero(BaseModel):
    eyebrow: str
    title: str
    subtitle: str
    cover_image_url: str | None = None
    primary_cta_label: str = "Open Live Workspace"
    secondary_cta_label: str = "Add Memory"


class TripMomentsViewResponse(BaseModel):
    moment_id: str
    trip_name: str
    stage_badge: str
    status_badge: str
    experience_chips: list[dict] = Field(default_factory=list)
    memory_hero: TripMomentsMemoryHero
    milestones: list[dict] = Field(default_factory=list)
    learned_patterns: list[dict] = Field(default_factory=list)
    captured_memories: list[dict] = Field(default_factory=list)
    group_dynamics: list[dict] = Field(default_factory=list)
    memory_feed: list[dict] = Field(default_factory=list)
    focus_options: list[dict] = Field(default_factory=list)
    operations_hub: GroupMomentsOperationsHub
    memory_hub: GroupMomentsMemoryHub


# ----- memory create ------------------------------------------------------ #
class GroupMomentMemoryCreateRequest(BaseModel):
    title: str
    note: str | None = None
    media_storage_paths: list[str] = Field(default_factory=list)
    memory_format: str | None = None
    memory_category: str | None = None


class GroupMomentMemoryResponse(BaseModel):
    id: str
    moment_id: str
    created_by_user_id: str
    created_by_name: str
    title: str
    note: str | None = None
    created_at: str
