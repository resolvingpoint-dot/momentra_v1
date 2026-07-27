"""Pydantic response/request models matching the mobile Personal contract.

These mirror the Android (`*Dto`) and iOS (`*Response`) shapes exactly. Every
field has a default so ``model_dump`` always emits a full object — Kotlin's
kotlinx.serialization requires all non-defaulted keys to be present, so the
backend must never omit a required field even in the empty state.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Moments / moment types
# --------------------------------------------------------------------------- #
class PersonalMomentResponse(BaseModel):
    moment_id: str
    moment_type_id: str
    moment_type_code: str | None = None
    moment_name: str = "Untitled"
    moment_description: str | None = None
    status: str = "DRAFT"
    current_runtime_state: str | None = None
    activated_at: str | None = None


class PersonalMomentTypeResponse(BaseModel):
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    theme_color: str | None = None
    icon_name: str | None = None
    display_order: int = 0


class PersonalMomentCreateRequest(BaseModel):
    moment_type_code: str
    moment_name: str | None = None


class PersonalMomentUpdateRequest(BaseModel):
    moment_name: str | None = None
    moment_description: str | None = None
    status: str | None = None


# --------------------------------------------------------------------------- #
# Create options
# --------------------------------------------------------------------------- #
class PersonalCreateOptionCard(BaseModel):
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    create_tagline: str | None = None
    create_badge_label: str | None = None
    is_create_featured: bool = False
    theme_color: str | None = None
    icon_name: str | None = None
    display_order: int = 0
    linked_moment_id: str | None = None
    linked_moment_status: str | None = None
    has_draft: bool = False
    action_label: str = "Begin Journey"
    background_image_url: str | None = None


class PersonalCreateOptionsResponse(BaseModel):
    hero_badge_label: str = "Recommended First Moment"
    hero_subtitle: str = "Choose the system that will guide this part of your life."
    featured_hero_image_url: str = ""
    cta_label: str = "Begin Journey"
    section_title: str = "Other Moment Types"
    footer_badge: str = "Intentional Design"
    footer_quote: str = (
        "Every moment you create is a step toward your personal operating "
        "system's harmony."
    )
    cards: list[PersonalCreateOptionCard] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Pulse
# --------------------------------------------------------------------------- #
class PersonalPulseResponse(BaseModel):
    overall_rhythm_state: str = "EMPTY"
    active_moment_count: int = 0
    is_empty: bool = True
    hero_image_url: str = ""
    hero_title: str | None = None
    hero_subtitle: str | None = None
    journey_title: str | None = None
    journey_subtitle: str | None = None
    cta_label: str | None = None
    life_operations: dict[str, Any] | None = None
    future_building: dict[str, Any] | None = None
    lifestyle: dict[str, Any] | None = None
    emotional_security: dict[str, Any] | None = None


# --------------------------------------------------------------------------- #
# Moments home
# --------------------------------------------------------------------------- #
class PersonalMomentHomeCard(BaseModel):
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    card_category_label: str | None = None
    theme_color: str | None = None
    icon_name: str | None = None
    display_order: int = 0
    linked_moment_id: str | None = None
    linked_moment_status: str | None = None
    moment_name: str | None = None
    current_runtime_state: str | None = None
    is_active: bool = False
    rhythm_state: str | None = None
    state_chip_label: str | None = None
    summary_text: str | None = None
    cover_image_url: str | None = None
    system_tag: str | None = None
    action_label: str | None = None


class PersonalMomentsHomeResponse(BaseModel):
    active_moment_count: int = 0
    is_empty: bool = True
    subtitle: str = "Your personal operating system starts with a single moment."
    cards: list[PersonalMomentHomeCard] = Field(default_factory=list)
    hero_title: str | None = None
    hero_subtitle: str | None = None
    build_space_title: str | None = None
    build_space_body: str | None = None
    life_operations_detail: dict[str, Any] | None = None
    future_building_detail: dict[str, Any] | None = None
    lifestyle_detail: dict[str, Any] | None = None
    emotional_security_detail: dict[str, Any] | None = None


class PersonalSessionBootstrapResponse(BaseModel):
    pulse: PersonalPulseResponse
    moments_home: PersonalMomentsHomeResponse


class PersonalTypeHint(BaseModel):
    moment_type_code: str
    linked_moment_id: str | None = None
    linked_moment_status: str | None = None
    has_draft: bool = False
    is_active: bool = False


class PersonalSessionResponse(BaseModel):
    """Stable session chrome — counts and per-type draft/active hints."""

    is_empty: bool = True
    active_moment_count: int = 0
    has_draft: bool = False
    type_hints: list[PersonalTypeHint] = Field(default_factory=list)


class PersonalInventoryResponse(BaseModel):
    """Frequent inventory refresh — pulse + moments_home cards (no heavy details)."""

    pulse: PersonalPulseResponse
    moments_home: PersonalMomentsHomeResponse


# --------------------------------------------------------------------------- #
# Memory
# --------------------------------------------------------------------------- #
class PersonalMemoryResponse(BaseModel):
    pattern_insight_count: int = 0
    is_empty: bool = True
    hero_badge: str = "PATTERN INTELLIGENCE"
    hero_title: str = "Your Memory Is Forming"
    hero_subtitle: str = (
        "Capture a few moments and Momentra begins to surface your patterns."
    )
    section_title: str = "Insight Categories"
    section_subtitle: str = "Insights unlock as you capture more of your life."
    category_cards: list[dict[str, Any]] = Field(default_factory=list)
    featured_insights: list[dict[str, Any]] = Field(default_factory=list)
    cta_title: str = "Keep Building Your Memory"
    cta_label: str = "Capture a Moment"
    show_cta: bool = False
    hero_image_url: str = ""
    avatar_image_url: str | None = None
    intelligence_modules: list[dict[str, Any]] = Field(default_factory=list)
    maturation_percent: int | None = None
    maturation_label: str | None = None
    formation_title: str | None = None
    formation_body: str | None = None
    section_sync_badge: str | None = None
    life_operations: dict[str, Any] | None = None
    future_building: dict[str, Any] | None = None
    lifestyle: dict[str, Any] | None = None
    emotional_security: dict[str, Any] | None = None


class PersonalMemorySummaryResponse(BaseModel):
    pattern_insight_count: int = 0


# --------------------------------------------------------------------------- #
# Life
# --------------------------------------------------------------------------- #
class PersonalLifeResponse(BaseModel):
    active_moment_count: int = 0
    is_empty: bool = True
    date_range_label: str | None = None
    metrics: dict[str, Any] | None = None


class PersonalLifeOpsActivitySummary(BaseModel):
    total_logs: int = 0
    this_month: int = 0
    total_amount_minor: int = 0


class PersonalLifeOpsActivityResponse(BaseModel):
    moment_id: str
    summary: PersonalLifeOpsActivitySummary = Field(
        default_factory=PersonalLifeOpsActivitySummary
    )
    items: list[dict[str, Any]] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Live
# --------------------------------------------------------------------------- #
class PersonalLiveResponse(BaseModel):
    active_moment_count: int = 0
    is_empty: bool = True
    hero_title: str = "Live Capture"
    hero_subtitle: str = "Log what's happening as your day unfolds."
    action_cards: list[dict[str, Any]] = Field(default_factory=list)
    education_title: str = "How live capture works"
    education_body: str = (
        "Every quick entry feeds your pulse, memory and life dashboards."
    )
    quick_add_enabled: bool = True
    quick_add_title: str = "Quick Add"
    quick_add_subtitle: str = "Capture a moment in seconds."
    avatar_image_url: str | None = None
    life_operations: dict[str, Any] | None = None
    future_building: dict[str, Any] | None = None
    lifestyle: dict[str, Any] | None = None
    emotional_security: dict[str, Any] | None = None
    runtime_modules: list[dict[str, Any]] = Field(default_factory=list)
    cta_label: str | None = None
    core_visual_url: str | None = None
    active_node_label: str | None = None


# --------------------------------------------------------------------------- #
# Quick add
# --------------------------------------------------------------------------- #
class PersonalQuickAddMomentOption(BaseModel):
    moment_id: str
    moment_name: str
    moment_type_code: str


class PersonalQuickAddOptionsResponse(BaseModel):
    moments: list[PersonalQuickAddMomentOption] = Field(default_factory=list)
    tabs: list[dict[str, Any]] = Field(default_factory=list)
    categories: list[dict[str, Any]] = Field(default_factory=list)
    accounts: list[dict[str, Any]] = Field(default_factory=list)
    entries_today_count: int = 0
    metadata: dict[str, Any] | None = None


class PersonalQuickAddEventResponse(BaseModel):
    quick_add_event_id: str
    event_type: str
    event_title: str
    moment_id: str


class PersonalQuickAddDetailResponse(BaseModel):
    quick_add_event_id: str
    moment_id: str
    event_type: str
    event_title: str
    event_summary: str | None = None
    captured_at: str
    recovery: dict[str, Any] | None = None
    reflection: dict[str, Any] | None = None
    rhythm: dict[str, Any] | None = None
    expense: dict[str, Any] | None = None
    commitment: dict[str, Any] | None = None


# --------------------------------------------------------------------------- #
# Accounts
# --------------------------------------------------------------------------- #
class PersonalAccountResponse(BaseModel):
    id: str
    account_id: str
    account_name: str
    account_type: str
    account_type_label: str = ""
    currency_code: str = "INR"
    current_balance: str = "0"
    current_balance_minor: int = 0
    opening_balance_minor: int = 0
    is_default: bool = False
    is_primary: bool = False
    is_archived: bool = False
    transaction_count: int = 0
    created_at: str | None = None
    updated_at: str | None = None


class PersonalAccountPatchRequest(BaseModel):
    account_name: str | None = None
    account_type: str | None = None
    currency_code: str | None = None
    current_balance_minor: int | None = None
    is_default: bool | None = None


class PersonalAccountCreateRequest(BaseModel):
    account_name: str
    account_type: str
    currency_code: str = "INR"
    opening_balance: str | None = None
    opening_balance_minor: int | None = None
    is_primary: bool = False


# --------------------------------------------------------------------------- #
# Master expense
# --------------------------------------------------------------------------- #
class PersonalMasterExpenseOptionsResponse(BaseModel):
    accounts: list[dict[str, Any]] = Field(default_factory=list)
    categories: list[dict[str, Any]] = Field(default_factory=list)
    feelings: list[dict[str, Any]] = Field(default_factory=list)
    scale_levels: list[dict[str, Any]] = Field(default_factory=list)
    shared_with: list[dict[str, Any]] = Field(default_factory=list)
    relationship_impacts: list[dict[str, Any]] = Field(default_factory=list)
    context_reasons: list[dict[str, Any]] = Field(default_factory=list)
    life_operations_moment_id: str | None = None
    lifestyle_moment_id: str | None = None
    emotional_security_moment_id: str | None = None


class PersonalMasterExpenseEventRef(BaseModel):
    quick_add_event_id: str
    moment_id: str
    moment_type_code: str
    event_type: str


class PersonalMasterExpenseResponse(BaseModel):
    id: str | None = None
    master_expense_id: str | None = None
    created_events: dict[str, str | None] = Field(default_factory=dict)
    impact_preview: dict[str, str] = Field(default_factory=dict)
    idempotent_replay: bool = False
    master_expense_group_id: str
    transaction_id: str
    account_id: str
    amount_minor: int
    events: list[PersonalMasterExpenseEventRef] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Setup
# --------------------------------------------------------------------------- #
class PersonalSetupOption(BaseModel):
    value: str
    label: str
    description: str | None = None
    bar_level: float | None = None
    accent: str | None = None


class PersonalSetupField(BaseModel):
    field_key: str
    label: str
    helper_text: str | None = None
    field_type: str
    options: list[PersonalSetupOption] | None = None
    required: bool = True
    icon_name: str | None = None


class PersonalSetupMission(BaseModel):
    badge_label: str
    title: str
    body: str


class PersonalSetupResponse(BaseModel):
    moment_id: str
    moment_type_code: str
    moment_name: str
    status: str = "DRAFT"
    title: str = "Set up your moment"
    subtitle: str = "A few questions to calibrate your system."
    background_image_url: str | None = None
    fields: list[PersonalSetupField] = Field(default_factory=list)
    mission: PersonalSetupMission | None = None
    saved_answers: dict[str, Any] | None = None
    cta_label: str | None = "Continue"
    footer_note: str | None = None


class PersonalSetupMeter(BaseModel):
    label: str
    pct: int


class PersonalSetupPreviewResponse(BaseModel):
    narrative: str = "Your system is ready to begin learning your rhythm."
    rhythm: PersonalSetupMeter = Field(
        default_factory=lambda: PersonalSetupMeter(label="Rhythm", pct=50)
    )
    pressure: PersonalSetupMeter = Field(
        default_factory=lambda: PersonalSetupMeter(label="Pressure", pct=40)
    )
    recovery: PersonalSetupMeter = Field(
        default_factory=lambda: PersonalSetupMeter(label="Recovery", pct=60)
    )
    runtime_priorities: list[str] = Field(default_factory=list)
    identity_chips: list[str] = Field(default_factory=list)
    future_building: dict[str, Any] | None = None
    lifestyle: dict[str, Any] | None = None
    emotional_security: dict[str, Any] | None = None


class PersonalSetupSubmitRequest(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Image upload (moment cover)
# --------------------------------------------------------------------------- #
class PersonalImageUploadUrlRequest(BaseModel):
    content_type: str
    byte_size: int


class PersonalImageUploadUrlResponse(BaseModel):
    upload_url: str
    storage_path: str
    token: str | None = None


class PersonalImageConfirmRequest(BaseModel):
    storage_path: str
