"""Contract schemas for the Group ``shared-*`` setup surface (mobile).

Mirror the Android DTOs in ``GroupSharedExperienceDto`` / ``GroupSharedPurchaseDto``
/ ``GroupSharedLivingDto``. Fields carry the same defaults as the client so a
partial server payload still deserializes; only the client's required
(non-nullable, no-default) fields must always be populated.

Phase 2 also exposes product-facing aliases (trip_name, destination, …) alongside
canonical keys, plus ``saved_answers`` / ``preview_blocks`` for the Setup Engine.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ----- shared building blocks --------------------------------------------- #
class SharedProfileOut(BaseModel):
    profile_id: str
    profile_code: str
    profile_name: str
    profile_description: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    display_order: int
    is_launchable: bool = True


class ProfilesListResponse(BaseModel):
    profiles: list[SharedProfileOut] = Field(default_factory=list)


class EnumOptionOut(BaseModel):
    code: str
    label: str
    description: str | None = None
    icon_name: str | None = None


class ModuleOptionOut(BaseModel):
    module_code: str
    module_label: str
    icon_name: str | None = None
    is_default: bool = False


class AudienceTagOptionOut(BaseModel):
    value_code: str
    value_label: str


class PendingEmailInviteOut(BaseModel):
    id: str
    email: str
    status: str = "pending"


class PreviewBlockOut(BaseModel):
    label: str
    value: str | None = None


# ----- shared-experience -------------------------------------------------- #
class ExperienceDraftCreateRequest(BaseModel):
    experience_profile: str


class DraftCreateResponse(BaseModel):
    moment_id: str
    moment_type_code: str
    lifecycle_status: str = "draft"


class ExperienceSetupState(BaseModel):
    moment_id: str
    moment_type_code: str = "SHARED_EXPERIENCE"
    lifecycle_status: str | None = None
    status: str | None = None
    experience_profile: str | None = None
    experience_type: str | None = None
    profile_name: str | None = None
    moment_name: str
    experience_name: str | None = None
    trip_name: str | None = None
    location: str | None = None
    destination: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    expected_participants: int | None = None
    participants: int | None = None
    audience_tags: list[str] = Field(default_factory=list)
    money_tracking_mode: str = "NO_MONEY"
    split_style: str | None = None
    planning_style: str = "SIMPLE"
    trip_style: str | None = None
    currency_code: str = "INR"
    budget_currency: str | None = None
    allow_multi_currency: bool = True
    estimated_budget: Any | None = None
    enabled_modules: list[str] = Field(default_factory=list)
    default_modules: list[str] = Field(default_factory=list)
    cover_image_url: str | None = None
    profiles: list[SharedProfileOut] = Field(default_factory=list)
    coordination_modules: list[ModuleOptionOut] = Field(default_factory=list)
    audience_tag_options: list[AudienceTagOptionOut] = Field(default_factory=list)
    money_tracking_modes: list[EnumOptionOut] = Field(default_factory=list)
    planning_styles: list[EnumOptionOut] = Field(default_factory=list)
    pending_email_invites: list[PendingEmailInviteOut] = Field(default_factory=list)
    saved_answers: dict[str, Any] | None = None
    fields: list[Any] = Field(default_factory=list)
    title: str | None = None
    subtitle: str | None = None
    background_image_url: str | None = None
    mission: dict[str, Any] | None = None
    cta_label: str | None = None
    footer_note: str | None = None


class ExperiencePreview(BaseModel):
    moment_id: str
    moment_name: str
    experience_name: str | None = None
    trip_name: str | None = None
    profile_name: str
    profile_code: str
    experience_type: str | None = None
    location: str | None = None
    destination: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    expected_participants: int | None = None
    participants: int | None = None
    money_tracking_mode: str
    money_tracking_label: str
    split_style: str | None = None
    planning_style: str
    planning_style_label: str
    trip_style: str | None = None
    currency_code: str = "INR"
    budget_currency: str | None = None
    allow_multi_currency: bool = True
    estimated_budget: Any | None = None
    enabled_modules: list[str] = Field(default_factory=list)
    audience_tags: list[str] = Field(default_factory=list)
    cover_image_url: str | None = None
    insight_text: str
    narrative: str | None = None
    preview_blocks: list[PreviewBlockOut] = Field(default_factory=list)
    identity_chips: list[str] = Field(default_factory=list)
    runtime_priorities: list[str] = Field(default_factory=list)
    pending_invite_count: int = 0
    rhythm: dict[str, Any] | None = None
    pressure: dict[str, Any] | None = None
    recovery: dict[str, Any] | None = None


class ActivateResponse(BaseModel):
    moment_id: str
    lifecycle_status: str
    orchestration_state: str | None = None
    activated_at: str


# ----- shared-purchase ---------------------------------------------------- #
class PurchaseDraftCreateRequest(BaseModel):
    purchase_profile: str


class PurchaseSetupState(BaseModel):
    moment_id: str
    moment_type_code: str = "SHARED_PURCHASE"
    lifecycle_status: str | None = None
    status: str | None = None
    purchase_profile: str | None = None
    profile_name: str | None = None
    moment_name: str
    purchase_name: str | None = None
    currency_code: str = "INR"
    allow_multi_currency: bool = True
    target_amount_minor: int | None = None
    expected_amount: Any | None = None
    target_date: str | None = None
    decision_deadline: str | None = None
    purchase_link: str | None = None
    description: str | None = None
    item_or_goal: str | None = None
    expected_contributors: int | None = None
    contributors: int | None = None
    funding_style: str = "SUGGESTED"
    payment_plan: str | None = None
    ownership_style: str | None = None
    enabled_modules: list[str] = Field(default_factory=list)
    default_modules: list[str] = Field(default_factory=list)
    cover_image_url: str | None = None
    profiles: list[SharedProfileOut] = Field(default_factory=list)
    purchase_modules: list[ModuleOptionOut] = Field(default_factory=list)
    funding_styles: list[EnumOptionOut] = Field(default_factory=list)
    pending_email_invites: list[PendingEmailInviteOut] = Field(default_factory=list)
    step3_insight: str | None = None
    step4_insight: str | None = None
    saved_answers: dict[str, Any] | None = None
    fields: list[Any] = Field(default_factory=list)
    title: str | None = None
    subtitle: str | None = None
    background_image_url: str | None = None
    mission: dict[str, Any] | None = None
    cta_label: str | None = None
    footer_note: str | None = None


class PurchasePreview(BaseModel):
    moment_id: str
    moment_name: str
    purchase_name: str | None = None
    profile_name: str
    profile_code: str
    currency_code: str = "INR"
    target_amount_minor: int | None = None
    expected_amount: Any | None = None
    target_date: str | None = None
    decision_deadline: str | None = None
    expected_contributors: int | None = None
    contributors: int | None = None
    funding_style: str
    funding_style_label: str
    payment_plan: str | None = None
    ownership_style: str | None = None
    item_or_goal: str | None = None
    enabled_modules: list[str] = Field(default_factory=list)
    cover_image_url: str | None = None
    insight_text: str
    narrative: str | None = None
    preview_blocks: list[PreviewBlockOut] = Field(default_factory=list)
    identity_chips: list[str] = Field(default_factory=list)
    runtime_priorities: list[str] = Field(default_factory=list)
    pending_invite_count: int = 0
    member_count: int = 0
    rhythm: dict[str, Any] | None = None
    pressure: dict[str, Any] | None = None
    recovery: dict[str, Any] | None = None


# ----- shared-living ------------------------------------------------------ #
class LivingDraftCreateRequest(BaseModel):
    living_type: str


class LivingSetupState(BaseModel):
    moment_id: str
    moment_type_code: str = "SHARED_LIVING"
    lifecycle_status: str | None = None
    status: str | None = None
    living_type: str | None = None
    profile_name: str | None = None
    living_name: str
    home_name: str | None = None
    location: str | None = None
    move_in_date: str | None = None
    monthly_budget: str | None = None
    currency_code: str = "INR"
    allow_multi_currency: bool = True
    management: str = "SHARED"
    rent_split_style: str | None = None
    chores_style: str | None = None
    expected_residents: int | None = None
    members: int | None = None
    description: str | None = None
    rules_or_notes: str | None = None
    cover_image_url: str | None = None
    profiles: list[SharedProfileOut] = Field(default_factory=list)
    management_styles: list[EnumOptionOut] = Field(default_factory=list)
    pending_email_invites: list[PendingEmailInviteOut] = Field(default_factory=list)
    enabled_modules: list[str] = Field(default_factory=list)
    default_modules: list[str] = Field(default_factory=list)
    step3_insight: str | None = None
    step4_insight: str | None = None
    saved_answers: dict[str, Any] | None = None
    fields: list[Any] = Field(default_factory=list)
    title: str | None = None
    subtitle: str | None = None
    background_image_url: str | None = None
    mission: dict[str, Any] | None = None
    cta_label: str | None = None
    footer_note: str | None = None


class LivingPreview(BaseModel):
    moment_id: str
    living_name: str
    home_name: str | None = None
    profile_name: str
    profile_code: str
    living_type: str | None = None
    location: str | None = None
    move_in_date: str | None = None
    monthly_budget: str | None = None
    currency_code: str = "INR"
    allow_multi_currency: bool = True
    management: str = "SHARED"
    management_label: str
    rent_split_style: str | None = None
    chores_style: str | None = None
    expected_residents: int | None = None
    members: int | None = None
    rules_or_notes: str | None = None
    cover_image_url: str | None = None
    insight_text: str
    narrative: str | None = None
    preview_blocks: list[PreviewBlockOut] = Field(default_factory=list)
    identity_chips: list[str] = Field(default_factory=list)
    runtime_priorities: list[str] = Field(default_factory=list)
    pending_invite_count: int = 0
    member_count: int = 0
    rhythm: dict[str, Any] | None = None
    pressure: dict[str, Any] | None = None
    recovery: dict[str, Any] | None = None
