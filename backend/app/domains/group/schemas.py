"""Group domain read schemas (one per table, from_attributes).

Generated from the SQLAlchemy models -- returned by the service layer so that
services never expose ORM models.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GroupActivityEditsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    edit_id: UUID
    moment_id: UUID
    entity_name: str
    entity_id: UUID
    edit_status: str
    edited_by: UUID
    edited_at: datetime
    activity_id: UUID | None = None
    edit_payload_json: Any | None = None
    edit_reason: str | None = None


class GroupAiInsightsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    insight_id: UUID
    moment_id: UUID
    insight_type: str
    insight_title: str
    insight_text: str
    generated_at: datetime
    display_context: str
    insight_layer: str
    insight_body: str
    is_active: bool
    created_at: datetime
    confidence_score: Decimal | None = None
    source_snapshot_date: date | None = None
    related_life_space_id: UUID | None = None
    confidence_level: str | None = None
    supporting_metrics_json: Any | None = None
    display_order: int | None = None
    updated_at: datetime | None = None


class GroupAttachmentsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attachment_id: UUID
    moment_id: UUID
    entity_name: str
    entity_id: UUID
    file_url: str
    file_type: str
    uploaded_by: UUID
    uploaded_at: datetime
    is_deleted: bool
    is_gallery_item: bool
    event_id: UUID | None = None
    attachment_context: str | None = None
    thumbnail_url: str | None = None
    gallery_group: str | None = None
    asset_category: str | None = None


class GroupAttendanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attendance_id: UUID
    moment_id: UUID
    member_id: UUID
    attendance_type: str
    status: str
    created_at: datetime
    attendance_date: date | None = None
    notes: str | None = None
    updated_at: datetime | None = None


class GroupChangeHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    change_id: UUID
    moment_id: UUID
    entity_name: str
    entity_id: UUID
    change_type: str
    changed_by: UUID
    changed_at: datetime
    rollback_supported: bool
    field_name: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    change_category: str | None = None
    source_widget: str | None = None
    edit_batch_id: UUID | None = None
    edit_reason: str | None = None
    source_activity_id: UUID | None = None


class GroupContributionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contribution_id: UUID
    moment_id: UUID
    contributor_member_id: UUID
    category: str
    amount: Decimal
    contribution_date: date
    status: str
    created_at: datetime
    payment_method: str | None = None
    reference_number: str | None = None
    notes: str | None = None
    updated_at: datetime | None = None
    budget_plan_id: UUID | None = None
    budget_split_id: UUID | None = None
    target_contribution_amount: Decimal | None = None


class GroupDecisionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    decision_id: UUID
    moment_id: UUID
    decision_type: str
    title: str
    status: str
    created_by: UUID
    created_at: datetime
    owner_id: UUID | None = None
    result: str | None = None
    decision_date: datetime | None = None
    source_ref_table: str | None = None
    source_ref_id: UUID | None = None
    updated_at: datetime | None = None


class GroupExpenseSplitsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    split_id: UUID
    expense_id: UUID
    member_id: UUID
    split_method: str
    split_amount: Decimal
    settlement_status: str
    created_at: datetime
    split_percentage: Decimal | None = None


class GroupExpensesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expense_id: UUID
    moment_id: UUID
    module_context: str
    category: str
    expense_name: str
    amount: Decimal
    expense_date: date
    paid_by_member_id: UUID
    status: str
    created_at: datetime
    notes: str | None = None
    updated_at: datetime | None = None
    budget_plan_id: UUID | None = None
    budget_category_id: UUID | None = None
    budget_variance_amount: Decimal | None = None


class GroupFieldValueConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    config_value_id: UUID
    moment_type: str
    moment_profile: str
    module_code: str
    field_name: str
    value_code: str
    value_label: str
    display_order: int
    is_top_category: bool
    is_active: bool
    created_at: datetime
    value_group: str | None = None
    value_subgroup: str | None = None


class GroupHealthSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    health_snapshot_id: UUID
    moment_id: UUID
    snapshot_date: date
    health_score: Decimal
    health_status: str
    created_at: datetime
    people_score: Decimal | None = None
    money_score: Decimal | None = None
    activity_score: Decimal | None = None
    health_delta: Decimal | None = None
    health_delta_period: str | None = None
    health_driver_breakdown_json: Any | None = None
    budget_health_score: Decimal | None = None
    dimension_breakdown_json: Any | None = None


class GroupJourneyMetricsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_id: UUID
    moment_id: UUID
    metric_date: date
    stage_name: str
    created_at: datetime
    days_in_stage: int | None = None
    completion_percentage: Decimal | None = None
    milestone_count: int | None = None


class GroupLifeDimensionScoresSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dimension_score_id: UUID
    life_snapshot_id: UUID
    dimension_code: str
    dimension_name: str
    score: Decimal
    created_at: datetime
    status: str | None = None
    trend_delta: Decimal | None = None
    explanation: str | None = None


class GroupLifeDriverEffectsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_effect_id: UUID
    life_snapshot_id: UUID
    source_moment_type: str
    target_moment_type: str
    effect_label: str
    impact_pct: Decimal
    explanation: str
    confidence_level: str
    rank_no: int
    created_at: datetime
    recommended_action: str | None = None
    supporting_metrics_json: Any | None = None


class GroupLifeMasterSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    master_snapshot_id: UUID
    user_id: UUID
    life_space_id: UUID
    snapshot_date: date
    group_life_score: Decimal
    created_at: datetime
    participation_score: Decimal | None = None
    contribution_score: Decimal | None = None
    coordination_score: Decimal | None = None
    progress_score: Decimal | None = None
    community_score: Decimal | None = None
    active_group_moments_count: int | None = None
    active_members_count: int | None = None
    open_group_actions_count: int | None = None
    group_risk_count: int | None = None
    dominant_group_driver: str | None = None
    dominant_group_risk: str | None = None
    highest_group_leverage: str | None = None
    source_snapshot_ids_json: Any | None = None


class GroupLifeMomentLinksSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_link_id: UUID
    life_space_id: UUID
    moment_id: UUID
    moment_type: str
    is_active: bool
    included_weight: Decimal
    linked_at: datetime


class GroupLifeSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_snapshot_id: UUID
    life_space_id: UUID
    snapshot_date: date
    group_life_score: Decimal
    health_status: str
    created_at: datetime
    dominant_driver: str | None = None
    dominant_risk: str | None = None
    highest_leverage: str | None = None
    trend_delta: Decimal | None = None


class GroupLifeSpacesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_space_id: UUID
    user_id: UUID
    space_name: str
    space_status: str
    created_at: datetime
    updated_at: datetime | None = None


class GroupLiveFeedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feed_id: UUID
    moment_id: UUID
    event_id: UUID
    feed_category: str
    title: str
    can_view: bool
    can_edit: bool
    visibility: str
    is_hidden: bool
    created_at: datetime
    can_delete: bool
    is_editable: bool
    summary: str | None = None
    category_chip: str | None = None
    timeline_display_json: Any | None = None
    source_widget: str | None = None
    created_by: UUID | None = None
    entity_name: str | None = None
    entity_id: UUID | None = None
    edit_route: str | None = None


class GroupMemoryEntriesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    memory_id: UUID
    moment_id: UUID
    memory_type: str
    category: str
    title: str
    memory_date: date
    created_at: datetime
    is_gallery_item: bool
    description: str | None = None
    source_event_id: UUID | None = None
    created_by: UUID | None = None
    memory_category: str | None = None
    media_count: int | None = None
    visibility: str | None = None
    highlight_score: Decimal | None = None
    budget_plan_id: UUID | None = None


class GroupMemoryPatternsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pattern_id: UUID
    moment_id: UUID
    moment_type: str
    pattern_type: str
    pattern_category: str
    insight_title: str
    confidence_score: Decimal
    status: str
    created_at: datetime
    insight_text: str | None = None
    supporting_event_ids_json: Any | None = None
    updated_at: datetime | None = None
    lesson_text: str | None = None
    identity_label: str | None = None
    pattern_strength: Decimal | None = None
    trend_direction: str | None = None
    supporting_metrics_json: Any | None = None


class GroupMemorySnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: UUID
    moment_id: UUID
    snapshot_date: date
    memory_count: int
    milestone_count: int
    created_at: datetime
    what_changed_json: Any | None = None
    budget_reflection_json: Any | None = None
    identity_label: str | None = None


class GroupMomentMembersSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: UUID
    moment_id: UUID
    display_name: str
    role_code: str
    status: str
    created_at: datetime
    joined_at: datetime | None = None
    left_at: datetime | None = None
    user_id: UUID | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    invite_token: UUID | None = None
    invite_sent_at: datetime | None = None
    avatar_url: str | None = None


class GroupMomentProfilesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: UUID
    moment_type: str
    profile_code: str
    profile_name: str
    display_order: int
    is_active: bool
    created_at: datetime
    profile_description: str | None = None


class GroupMomentResourcesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resource_id: UUID
    moment_id: UUID
    resource_type: str
    resource_name: str
    status: str
    is_memory_asset: bool
    created_by: UUID
    created_at: datetime
    description: str | None = None
    owner_id: UUID | None = None
    attachment_id: UUID | None = None
    resource_url: str | None = None
    updated_at: datetime | None = None


class GroupMomentRolesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_code: str
    moment_type: str
    role_name: str
    permission_json: Any
    display_order: int
    is_default: bool
    is_active: bool
    created_at: datetime
    role_description: str | None = None


class GroupMomentStageHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stage_history_id: UUID
    moment_id: UUID
    new_stage: str
    changed_by: UUID
    changed_at: datetime
    is_current: bool
    old_stage: str | None = None
    change_reason: str | None = None
    source_event_id: UUID | None = None


class GroupMomentWorkItemsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    work_item_id: UUID
    moment_id: UUID
    work_item_type: str
    title: str
    status: str
    source_quick_add: str
    is_milestone: bool
    created_by: UUID
    created_at: datetime
    category: str | None = None
    description: str | None = None
    owner_id: UUID | None = None
    priority: str | None = None
    due_date: date | None = None
    event_date: datetime | None = None
    progress_pct: Decimal | None = None
    updated_at: datetime | None = None


class GroupMomentsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    moment_id: UUID
    moment_type: str
    moment_profile: str
    moment_name: str
    status: str
    stage: str
    currency_code: str
    created_by: UUID
    created_at: datetime
    is_life_included: bool
    activated_at: datetime | None = None
    updated_at: datetime | None = None
    experience_subtype: str | None = None
    planning_mode: str | None = None
    activation_status: str | None = None
    planned_activation_date: date | None = None
    group_life_space_id: UUID | None = None


class GroupPeopleImpactScoresSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    impact_id: UUID
    moment_id: UUID
    member_id: UUID
    impact_type: str
    impact_score: Decimal
    rank_no: int
    created_at: datetime
    badge_label: str | None = None
    supporting_metrics_json: Any | None = None
    activity_score: Decimal | None = None
    helpfulness_score: Decimal | None = None
    contribution_score: Decimal | None = None


class GroupPollOptionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    option_id: UUID
    poll_id: UUID
    option_text: str
    sort_order: int
    is_active: bool
    created_at: datetime


class GroupPollVotesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vote_id: UUID
    poll_id: UUID
    option_id: UUID
    voter_member_id: UUID
    voted_at: datetime
    rank_order: int | None = None


class GroupPollsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    poll_id: UUID
    moment_id: UUID
    category: str
    question: str
    poll_type: str
    is_anonymous: bool
    allow_multiple_votes: bool
    status: str
    created_by: UUID
    created_at: datetime
    end_date: date | None = None
    updated_at: datetime | None = None


class GroupPulseSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: UUID
    moment_id: UUID
    snapshot_date: date
    completion_percentage: Decimal
    participation_percentage: Decimal
    funding_percentage: Decimal
    active_members: int
    active_tasks: int
    open_items: int
    pulse_score: Decimal
    created_at: datetime
    hero_snapshot_json: Any | None = None
    health_driver_json: Any | None = None
    progress_context_json: Any | None = None
    budget_snapshot_json: Any | None = None
    participation_json: Any | None = None
    timeline_preview_json: Any | None = None
    insights_json: Any | None = None
    extended_metrics_json: Any | None = None
    attention_items_json: Any | None = None
    next_best_action_json: Any | None = None


class GroupQuickAddConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    config_id: UUID
    moment_type: str
    moment_profile: str
    module_code: str
    module_label: str
    display_order: int
    is_enabled: bool
    is_visible: bool
    is_required: bool
    created_at: datetime
    quick_add_category: str | None = None
    moment_type_support: str | None = None


class GroupQuickAddEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: UUID
    moment_id: UUID
    module_code: str
    event_ref_table: str
    event_ref_id: UUID
    event_action: str
    created_by: UUID
    event_time: datetime
    event_payload_json: Any | None = None


class GroupRecommendationsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: UUID
    moment_id: UUID
    recommendation_type: str
    recommendation_category: str
    title: str
    priority: str
    status: str
    generated_at: datetime
    description: str | None = None
    recommendation_score: Decimal | None = None
    actioned_at: datetime | None = None
    expected_impact_json: Any | None = None
    impact_score: Decimal | None = None
    confidence_level: str | None = None
    action_deeplink: str | None = None
    related_life_space_id: UUID | None = None
    action_label: str | None = None
    action_deep_link: str | None = None


class GroupSignalsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    signal_id: UUID
    moment_id: UUID
    signal_type: str
    signal_category: str
    signal_title: str
    priority: str
    is_active: bool
    generated_at: datetime
    signal_description: str | None = None
    signal_score: Decimal | None = None
    expires_at: datetime | None = None
    severity: str | None = None
    signal_status: str | None = None
    display_order: int | None = None
    action_ref: UUID | None = None
    source_widget: str | None = None
    related_budget_plan_id: UUID | None = None


class GroupUpdatesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    update_id: UUID
    moment_id: UUID
    category: str
    title: str
    description: str
    visibility: str
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime | None = None
