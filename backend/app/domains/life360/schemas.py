"""Life360 domain read schemas (one per table, from_attributes).

Generated from the SQLAlchemy models -- returned by the service layer so that
services never expose ORM models.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AiSignalsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    signal_id: UUID
    moment_id: UUID
    signal_scope: str
    signal_type: str
    signal_title: str
    signal_message: str
    severity: str
    signal_status: str
    generated_at: datetime
    source_table: str | None = None
    source_record_id: UUID | None = None
    confidence_score: Decimal | None = None
    recommended_action: str | None = None
    target_screen: str | None = None
    expires_at: datetime | None = None


class BudgetMasterCategoriesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: UUID
    category_code: str
    category_name: str
    display_order: int
    is_active: bool
    created_at: datetime
    icon_name: str | None = None


class CommunityCoordinationDetailsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    community_id: UUID
    moment_id: UUID
    community_type: str
    community_status: str
    created_at: datetime
    member_base_count: int | None = None
    coordination_mode: str | None = None
    primary_owner_id: UUID | None = None
    updated_at: datetime | None = None


class ExperienceBudgetTemplatesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    template_id: UUID
    experience_subtype: str
    category_id: UUID
    suggested_percentage: Decimal
    display_order: int
    is_default: bool
    created_at: datetime


class Life360SnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life360_snapshot_id: UUID
    user_id: UUID
    snapshot_date: date
    snapshot_month: date
    life_alignment_score: Decimal
    source_personal_snapshot_id: UUID | None = None
    source_group_snapshot_id: UUID | None = None
    source_business_snapshot_id: UUID | None = None
    personal_score: Decimal | None = None
    group_score: Decimal | None = None
    business_score: Decimal | None = None
    life_phase: str | None = None
    money_score: Decimal | None = None
    relationship_score: Decimal | None = None
    execution_score: Decimal | None = None
    growth_score: Decimal | None = None
    personal_energy_pct: Decimal | None = None
    group_energy_pct: Decimal | None = None
    business_energy_pct: Decimal | None = None
    momentum_score: Decimal | None = None
    momentum_status: str | None = None
    strongest_driver: str | None = None
    biggest_tension: str | None = None
    money_status: str | None = None
    relationship_status: str | None = None
    execution_status: str | None = None
    growth_status: str | None = None
    reflection_summary: str | None = None
    active_dimensions_count: int | None = None
    signal_confidence_score: Decimal | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SharedExperienceBudgetAllocationsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    allocation_id: UUID
    budget_plan_id: UUID
    category_id: UUID
    final_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    created_at: datetime
    recommended_percentage: Decimal | None = None
    recommended_amount: Decimal | None = None
    final_percentage: Decimal | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class SharedExperienceBudgetPlansSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    budget_plan_id: UUID
    moment_id: UUID
    planned_total_budget: Decimal
    final_total_budget: Decimal
    participant_count: int
    split_method: str
    status: str
    created_by: UUID
    created_at: datetime
    funding_readiness_pct: Decimal | None = None
    updated_at: datetime | None = None


class SharedExperienceBudgetSplitsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    split_id: UUID
    budget_plan_id: UUID
    member_id: UUID
    planned_share_amount: Decimal
    committed_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    split_status: str
    created_at: datetime
    updated_at: datetime | None = None


class SharedExperienceDetailsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    experience_detail_id: UUID
    moment_id: UUID
    experience_profile: str
    planning_style: str
    money_tracking_mode: str
    created_at: datetime
    budget_enabled: bool
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    expected_participants: int | None = None
    description: str | None = None
    updated_at: datetime | None = None
    default_budget_plan_id: UUID | None = None


class SharedExperienceMemoryHighlightsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    highlight_id: UUID
    moment_id: UUID
    highlight_type: str
    title: str
    importance_score: Decimal
    created_at: datetime
    description: str | None = None
    source_event_id: UUID | None = None
    updated_at: datetime | None = None


class SharedExperiencePlanningItemsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: UUID
    moment_id: UUID
    item_type: str
    category: str
    title: str
    status: str
    created_by: UUID
    created_at: datetime
    owner_member_id: UUID | None = None
    due_date: date | None = None
    estimated_cost: Decimal | None = None
    actual_cost: Decimal | None = None
    provider_name: str | None = None
    booking_reference: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None
    budget_plan_id: UUID | None = None
    budget_category_id: UUID | None = None


class SharedExperienceSettlementsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    settlement_id: UUID
    moment_id: UUID
    payer_member_id: UUID
    receiver_member_id: UUID
    settlement_amount: Decimal
    settlement_status: str
    created_at: datetime
    settled_at: datetime | None = None
    source_expense_ids_json: Any | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class SharedGoalDetailsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    goal_id: UUID
    moment_id: UUID
    goal_type: str
    goal_status: str
    progress_pct: Decimal
    created_at: datetime
    target_amount: Decimal | None = None
    target_date: date | None = None
    goal_owner_id: UUID | None = None
    updated_at: datetime | None = None


class SharedLivingAssetsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID
    moment_id: UUID
    category: str
    asset_name: str
    is_shared_asset: bool
    status: str
    created_at: datetime
    owner_member_id: UUID | None = None
    purchase_date: date | None = None
    estimated_value: Decimal | None = None
    location_in_home: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class SharedLivingDetailsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    living_detail_id: UUID
    moment_id: UUID
    living_type: str
    living_name: str
    management_style: str
    created_at: datetime
    location: str | None = None
    move_in_date: date | None = None
    monthly_budget: Decimal | None = None
    expected_residents: int | None = None
    description: str | None = None
    updated_at: datetime | None = None


class SharedLivingHomePersonalitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    personality_id: UUID
    moment_id: UUID
    traits_json: Any
    primary_trait: str
    confidence_score: Decimal
    snapshot_date: date
    created_at: datetime
    description: str | None = None
    updated_at: datetime | None = None


class SharedLivingMaintenanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    maintenance_id: UUID
    moment_id: UUID
    category: str
    issue_title: str
    reported_by_member_id: UUID
    priority: str
    status: str
    created_at: datetime
    description: str | None = None
    assigned_to_member_id: UUID | None = None
    target_resolution_date: date | None = None
    fixed_at: datetime | None = None
    estimated_cost: Decimal | None = None
    notes: str | None = None
    updated_at: datetime | None = None
    linked_expense_id: UUID | None = None


class SharedLivingResidentDynamicsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dynamics_id: UUID
    moment_id: UUID
    resident_member_id: UUID
    activity_score: Decimal
    period_start: date
    period_end: date
    created_at: datetime
    helpfulness_score: Decimal | None = None
    contribution_score: Decimal | None = None
    summary_label: str | None = None
    updated_at: datetime | None = None


class SharedLivingResidentsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resident_id: UUID
    moment_id: UUID
    member_id: UUID
    resident_type: str
    status: str
    created_at: datetime
    move_in_date: date | None = None
    move_out_date: date | None = None
    expected_monthly_contribution: Decimal | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class SharedLivingRulesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: UUID
    moment_id: UUID
    category: str
    rule_title: str
    rule_description: str
    applies_to: str
    effective_date: date
    status: str
    created_by: UUID
    created_at: datetime
    review_date: date | None = None
    updated_at: datetime | None = None


class SharedLivingTasksSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: UUID
    moment_id: UUID
    category: str
    task_name: str
    frequency: str
    status: str
    created_at: datetime
    assigned_to_member_id: UUID | None = None
    due_date: date | None = None
    priority: str | None = None
    completed_at: datetime | None = None
    notes: str | None = None
    updated_at: datetime | None = None
    next_due_date: date | None = None


class SharedPurchaseContributorsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contributor_id: UUID
    moment_id: UUID
    member_id: UUID
    contributor_type: str
    status: str
    created_at: datetime
    expected_amount: Decimal | None = None
    invited_at: datetime | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class SharedPurchaseDeliverySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    delivery_id: UUID
    moment_id: UUID
    delivery_category: str
    status: str
    created_at: datetime
    delivery_date: date | None = None
    received_by_member_id: UUID | None = None
    proof_attachment_id: UUID | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class SharedPurchaseDetailsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    purchase_detail_id: UUID
    moment_id: UUID
    purchase_type: str
    purchase_name: str
    target_amount: Decimal
    funding_style: str
    created_at: datetime
    target_date: date | None = None
    purchase_link: str | None = None
    description: str | None = None
    expected_contributors: int | None = None
    updated_at: datetime | None = None


class SharedPurchaseItemsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: UUID
    moment_id: UUID
    category: str
    item_name: str
    status: str
    created_by: UUID
    created_at: datetime
    target_price: Decimal | None = None
    quantity: int | None = None
    purchase_link: str | None = None
    priority: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class SharedPurchaseOwnershipSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ownership_id: UUID
    moment_id: UUID
    owner_member_id: UUID
    ownership_type: str
    status: str
    created_at: datetime
    ownership_percentage: Decimal | None = None
    usage_rights: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class SharedPurchaseOwnershipInsightsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    insight_id: UUID
    moment_id: UUID
    insight_type: str | None = None
    title: str | None = None
    description: str | None = None
    confidence_score: Decimal | None = None
    created_at: datetime | None = None


class SharedPurchaseVendorsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vendor_id: UUID
    moment_id: UUID
    vendor_category: str
    vendor_name: str
    status: str
    created_at: datetime
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    quoted_price: Decimal | None = None
    vendor_link: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None
