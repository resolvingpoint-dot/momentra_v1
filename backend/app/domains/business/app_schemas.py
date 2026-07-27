"""Pydantic schemas for the Business mobile contract.

The Android (`apk_copy`) and iOS (`ios_copy`) Business models are near-identical,
so each response is a single shape both decode. Every field has a default so
``model_dump(mode="json")`` always emits the full key set — in particular the
non-optional nested ``avatar_requirements`` / ``cover_requirements`` objects and
the required list fields (benefits / dimension_cards / cards / modules /
patterns) that both strict decoders require.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Image requirements (required nested object on every screen)
# --------------------------------------------------------------------------- #
class BusinessImageRequirements(BaseModel):
    min_width: int = 400
    min_height: int = 400
    target_width: int = 1200
    target_height: int = 1200
    max_bytes: int = 5_000_000
    aspect_ratio: str = "1:1"
    allowed_content_types: list[str] = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "image/webp"]
    )


def _avatar_requirements() -> BusinessImageRequirements:
    return BusinessImageRequirements(aspect_ratio="1:1", target_width=1024, target_height=1024)


def _cover_requirements() -> BusinessImageRequirements:
    return BusinessImageRequirements(
        aspect_ratio="16:9", target_width=1600, target_height=900, max_bytes=8_000_000
    )


# --------------------------------------------------------------------------- #
# Shared building blocks
# --------------------------------------------------------------------------- #
class BusinessMomentTypeCard(BaseModel):
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    create_tagline: str | None = None
    badge_label: str | None = None
    icon_name: str | None = None
    accent_main: str | None = None
    accent_soft_tint: str | None = None
    card_layout: str | None = None
    display_order: int = 0
    linked_moment_id: str | None = None
    linked_moment_status: str | None = None
    # Personal parity: true when linked status is ACTIVE / PAUSED / COMPLETED.
    is_active: bool = False
    cover_image_url: str | None = None
    action_label: str = "Explore"
    action_style: str = "filled"


class BusinessBenefitItem(BaseModel):
    item_code: str
    title: str
    description: str
    icon_name: str
    image_url: str | None = None


class BusinessIntelligencePreview(BaseModel):
    badge: str
    title: str
    subtitle: str
    tags: list[str] = Field(default_factory=list)
    illustration_url: str | None = None


class BusinessInfoCardItem(BaseModel):
    item_code: str
    title: str
    description: str
    icon_name: str


class BusinessFooterBand(BaseModel):
    title: str
    subtitle: str
    cta_label: str
    illustration_url: str | None = None


class BusinessFeedPreviewItem(BaseModel):
    item_code: str
    title: str
    description: str
    badge_label: str
    accent_main: str | None = None


class BusinessStepItem(BaseModel):
    item_code: str
    title: str
    description: str | None = None
    icon_name: str | None = None
    display_order: int = 0
    is_active: bool = False
    step_label: str | None = None
    is_goal: bool = False


class BusinessInsightExample(BaseModel):
    item_code: str
    title: str
    description: str
    accent_main: str | None = None


class BusinessEmptyStateItem(BaseModel):
    item_code: str
    item_kind: str
    title: str
    description: str | None = None
    icon_name: str | None = None
    accent_main: str | None = None
    accent_soft_tint: str | None = None
    badge_label: str | None = None
    card_layout: str | None = None
    display_order: int = 0


class BusinessCreateOptionCard(BaseModel):
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    create_tagline: str | None = None
    description: str | None = None
    icon_name: str | None = None
    accent_main: str | None = None
    accent_soft_tint: str | None = None
    badge_label: str | None = None
    cover_image_url: str | None = None
    card_layout: str | None = None
    display_order: int = 0
    linked_moment_id: str | None = None
    linked_moment_status: str | None = None
    # Personal parity: true when linked status is ACTIVE / PAUSED / COMPLETED.
    is_active: bool = False
    is_selected: bool = False
    is_available: bool = True
    implementation_status: str = "active"


# --------------------------------------------------------------------------- #
# Screen responses
# --------------------------------------------------------------------------- #
class BusinessPulseResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    avatar_image_url: str | None = None
    avatar_editable: bool = True
    avatar_requirements: BusinessImageRequirements = Field(default_factory=_avatar_requirements)
    cover_requirements: BusinessImageRequirements = Field(default_factory=_cover_requirements)
    hero_badge: str = "Your business, in focus"
    hero_title: str = "Run your business with clarity"
    hero_title_accent: str | None = None
    hero_subtitle: str = "See every dimension of your company in one calm place."
    hero_illustration_url: str | None = None
    cta_label: str = "Create your first moment"
    trust_line: str | None = None
    secondary_cta_label: str = "See how it works"
    dimensions_section_title: str = "The dimensions you'll track"
    dimensions_section_subtitle: str | None = None
    explore_moments_label: str | None = None
    intelligence_preview: BusinessIntelligencePreview | None = None
    benefits_section_title: str = "Why founders use Momentra"
    benefits: list[BusinessBenefitItem] = Field(default_factory=list)
    dimension_cards: list[BusinessMomentTypeCard] = Field(default_factory=list)


class BusinessMomentsHomeResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    avatar_image_url: str | None = None
    avatar_editable: bool = True
    avatar_requirements: BusinessImageRequirements = Field(default_factory=_avatar_requirements)
    cover_requirements: BusinessImageRequirements = Field(default_factory=_cover_requirements)
    hero_title: str = "Your business moments"
    hero_subtitle: str = "Everything you're operating, in one place."
    cta_label: str = "Create a business moment"
    info_card_title: str | None = None
    info_card_items: list[BusinessInfoCardItem] = Field(default_factory=list)
    info_card_footnote: str | None = None
    footer_band: BusinessFooterBand | None = None
    cards: list[BusinessMomentTypeCard] = Field(default_factory=list)


class BusinessLiveResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    avatar_image_url: str | None = None
    avatar_editable: bool = True
    avatar_requirements: BusinessImageRequirements = Field(default_factory=_avatar_requirements)
    cover_requirements: BusinessImageRequirements = Field(default_factory=_cover_requirements)
    status_label: str = "Nothing live yet"
    page_title: str | None = None
    hero_badge: str | None = None
    hero_title: str = "Your live command center"
    hero_subtitle: str = "Activate a moment to see it come alive here."
    hero_body: str | None = None
    hero_illustration_url: str | None = None
    cta_label: str = "Create a business moment"
    preview_section_title: str | None = None
    preview_modules: list[BusinessEmptyStateItem] = Field(default_factory=list)
    feed_section_title: str | None = None
    feed_section_badge: str | None = None
    feed_preview: list[BusinessFeedPreviewItem] = Field(default_factory=list)
    how_it_works_title: str | None = None
    how_it_works: list[BusinessStepItem] = Field(default_factory=list)
    bottom_cta_title: str | None = None
    bottom_cta_subtitle: str | None = None
    bottom_cta_label: str | None = None
    modules: list[BusinessEmptyStateItem] = Field(default_factory=list)


class BusinessMemoryResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    avatar_image_url: str | None = None
    avatar_editable: bool = True
    avatar_requirements: BusinessImageRequirements = Field(default_factory=_avatar_requirements)
    cover_requirements: BusinessImageRequirements = Field(default_factory=_cover_requirements)
    hero_badge: str = "Your business story"
    hero_title: str = "Every decision, remembered"
    hero_title_accent: str | None = None
    hero_subtitle: str = "The milestones and lessons of your company, kept forever."
    section_title: str = "Your timeline"
    section_subtitle: str | None = None
    cta_label: str = "Create a business moment"
    footer_text: str = "Momentra remembers so you can focus on what's next."
    illustration_url: str | None = None
    illustration_alt: str | None = None
    timeline_title: str | None = None
    timeline_steps: list[BusinessStepItem] = Field(default_factory=list)
    insights_section_title: str | None = None
    insight_examples: list[BusinessInsightExample] = Field(default_factory=list)
    patterns: list[BusinessEmptyStateItem] = Field(default_factory=list)


class BusinessCreateOptionsResponse(BaseModel):
    is_empty: bool = True
    active_moment_count: int = 0
    avatar_image_url: str | None = None
    avatar_editable: bool = True
    avatar_requirements: BusinessImageRequirements = Field(default_factory=_avatar_requirements)
    cover_requirements: BusinessImageRequirements = Field(default_factory=_cover_requirements)
    hero_title: str = "Create a business moment"
    hero_subtitle: str = "Choose the dimension you want to build."
    hero_hint: str | None = None
    cta_label: str = "Continue"
    secondary_cta_label: str | None = None
    selection_chip_prefix: str | None = None
    journey_section_title: str | None = None
    journey_steps: list[BusinessStepItem] = Field(default_factory=list)
    cards: list[BusinessCreateOptionCard] = Field(default_factory=list)
    preview_text: str | None = None


class BusinessMomentResponse(BaseModel):
    moment_id: str
    moment_type_id: str
    moment_type_code: str | None = None
    moment_name: str
    moment_description: str | None = None
    status: str = "DRAFT"
    cover_image_url: str | None = None
    workspace_id: str | None = None


class BusinessWorkspaceSummary(BaseModel):
    id: str
    name: str
    logo: str | None = None
    role: str = "MEMBER"
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"
    industry: str | None = None
    status: str = "ACTIVE"


class BusinessModuleTile(BaseModel):
    key: str
    label: str
    status: str = "coming_soon"
    description: str | None = None


class BusinessDashboardSummary(BaseModel):
    open_moments: int = 0
    pending_approvals: int = 0
    member_count: int = 0
    revenue_today: int | None = None
    cash_balance: int | None = None


class BusinessSessionBootstrapResponse(BaseModel):
    pulse: BusinessPulseResponse = Field(default_factory=BusinessPulseResponse)
    moments_home: BusinessMomentsHomeResponse = Field(default_factory=BusinessMomentsHomeResponse)
    # Group parity: full visible moment inventory for the switcher (workspace-scoped).
    moments: list[BusinessMomentResponse] = Field(default_factory=list)
    selected_workspace: BusinessWorkspaceSummary | None = None
    workspaces: list[BusinessWorkspaceSummary] = Field(default_factory=list)
    module_tiles: list[BusinessModuleTile] = Field(default_factory=list)
    dashboard: BusinessDashboardSummary = Field(default_factory=BusinessDashboardSummary)


class BusinessSessionResponse(BaseModel):
    """Stable session chrome — rare invalidation."""

    selected_workspace: BusinessWorkspaceSummary | None = None
    workspaces: list[BusinessWorkspaceSummary] = Field(default_factory=list)
    module_tiles: list[BusinessModuleTile] = Field(default_factory=list)


class BusinessWorkspaceOverviewResponse(BaseModel):
    """Volatile company home snapshot — short TTL / soft revalidate."""

    workspace_id: str
    dashboard: BusinessDashboardSummary = Field(default_factory=BusinessDashboardSummary)
    recent_moments: list[BusinessMomentResponse] = Field(default_factory=list)


class BusinessWorkspaceMomentsResponse(BaseModel):
    """Workspace moment inventory."""

    workspace_id: str
    moments_home: BusinessMomentsHomeResponse = Field(default_factory=BusinessMomentsHomeResponse)
    moments: list[BusinessMomentResponse] = Field(default_factory=list)
    pulse: BusinessPulseResponse = Field(default_factory=BusinessPulseResponse)


class BusinessWorkspaceCreateRequest(BaseModel):
    name: str
    currency_code: str = "INR"
    timezone: str = "Asia/Kolkata"
    industry: str | None = None
    logo_url: str | None = None


class BusinessWorkspaceUpdateRequest(BaseModel):
    name: str | None = None
    logo_url: str | None = None
    industry: str | None = None
    currency_code: str | None = None
    timezone: str | None = None
    status: str | None = None


class BusinessWorkspaceSelectRequest(BaseModel):
    workspace_id: str


class BusinessWorkspaceInviteRequest(BaseModel):
    email: str
    role: str = "MEMBER"


class BusinessWorkspaceAcceptInviteRequest(BaseModel):
    token: str


# --------------------------------------------------------------------------- #
# Requests + upload
# --------------------------------------------------------------------------- #
class BusinessMomentCreateRequest(BaseModel):
    moment_type_code: str
    moment_name: str | None = None
    title: str | None = None
    template_id: str | None = None
    template_version: str | int | None = "1"
    workspace_id: str | None = None


class BusinessMomentUpdateRequest(BaseModel):
    moment_name: str | None = None
    status: str | None = None


class BusinessImageUploadUrlRequest(BaseModel):
    filename: str
    content_type: str
    byte_size: int = 0


class BusinessImageUploadUrlResponse(BaseModel):
    upload_url: str
    storage_path: str
    token: str | None = None


class BusinessImageConfirmRequest(BaseModel):
    storage_path: str
