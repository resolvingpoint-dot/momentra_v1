"""Personal domain read schemas (one per table, from_attributes).

Generated from the SQLAlchemy models -- returned by the service layer so that
services never expose ORM models.
"""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class PersonalAccountsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: UUID
    user_id: UUID
    account_name: str
    account_type: str
    currency_code: str
    current_balance: Decimal
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    opening_balance: Decimal | None = None


class PersonalActivityTimelineSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timeline_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    moment_type_code: str
    event_type: str
    display_title: str
    event_occurred_at: datetime
    is_editable: bool
    is_voided: bool
    created_at: datetime
    updated_at: datetime
    display_subtitle: str | None = None
    display_amount: Decimal | None = None
    impact_labels_json: Any | None = None


class PersonalAiInterpretationRunsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: UUID
    user_id: UUID
    run_type: str
    input_payload: Any
    status: str
    created_at: datetime
    moment_id: UUID | None = None
    moment_type_code: str | None = None
    output_payload: Any | None = None
    records_created_json: Any | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class PersonalCategoriesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: UUID
    moment_type_code: str
    category_group: str
    category_code: str
    category_name: str
    is_money_category: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user_id: UUID | None = None
    display_order: int | None = None


class PersonalEventEditsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    edit_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    edited_table_name: str
    edited_record_id: UUID
    before_payload: Any
    after_payload: Any
    requires_recalculation: bool
    created_at: datetime
    changed_fields: list[str] | None = None
    edit_reason: str | None = None
    recalculated_at: datetime | None = None


class PersonalEventVoidsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    void_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    voided_table_name: str
    voided_record_id: UUID
    void_payload: Any
    reversal_allowed: bool
    requires_recalculation: bool
    created_at: datetime
    void_reason: str | None = None
    undo_expires_at: datetime | None = None
    restored_at: datetime | None = None
    recalculated_at: datetime | None = None


class PersonalFutureBuildingProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    future_profile_id: UUID
    moment_id: UUID
    user_id: UUID
    future_theme: str
    current_momentum_state: str
    future_values: list[str]
    friction_sources: list[str]
    momentum_drivers: list[str]
    future_confidence: str
    future_identity: str
    created_at: datetime
    updated_at: datetime
    largest_friction_label: str | None = None
    primary_opportunity_label: str | None = None
    breakthrough_potential: str | None = None


class PersonalFutureLearningEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    learning_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    learning_type: str
    relevance_level: str
    readiness_signal_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    application_status: str | None = None
    note: str | None = None
    capability_score_delta: Decimal | None = None
    confidence_boost_score: Decimal | None = None


class PersonalFutureMilestoneEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    milestone_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    milestone_nature: str
    impact_level: str
    breakthrough_signal_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    outcome_value: str | None = None
    celebration_level: str | None = None
    note: str | None = None
    achievement_score_delta: Decimal | None = None
    future_return_signal: str | None = None


class PersonalFutureOpportunityEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    opportunity_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    opportunity_source: str
    potential_level: str
    opportunity_status: str
    acceleration_signal_flag: bool
    best_opportunity_candidate_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    note: str | None = None
    opportunity_score_delta: Decimal | None = None


class PersonalFuturePivotEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pivot_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    adjustment_type: str
    pivot_reason: str
    confidence_level: str
    future_horizon_update_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    note: str | None = None
    direction_shift_score: Decimal | None = None
    adaptability_score_delta: Decimal | None = None


class PersonalFutureProgressEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    progress_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    progress_type: str
    progress_level: str
    velocity_signal_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    money_invested_amount: Decimal | None = None
    time_invested_bucket: str | None = None
    effort_level: str | None = None
    note: str | None = None
    momentum_score_delta: Decimal | None = None
    investment_weight_score: Decimal | None = None


class PersonalInsightsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    insight_id: UUID
    user_id: UUID
    insight_scope: str
    insight_type: str
    insight_title: str
    insight_text: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    moment_id: UUID | None = None
    moment_type_code: str | None = None
    severity_level: str | None = None
    recommended_action: str | None = None
    source_metric_json: Any | None = None


class PersonalLifeAdjustEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    adjust_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    adjustment_areas: list[str]
    created_at: datetime
    updated_at: datetime
    pressure_signal: str | None = None
    recovery_signal: str | None = None
    focus_signal: str | None = None
    momentum_signal: str | None = None
    note: str | None = None
    runtime_shift_score: Decimal | None = None
    recommended_runtime_priority: str | None = None


class PersonalLifeAggregateSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_aggregate_snapshot_id: UUID
    user_id: UUID
    snapshot_date: date
    snapshot_month: date
    life_health_score: Decimal
    stability_score: Decimal
    growth_score: Decimal
    fulfillment_score: Decimal
    relationship_health_score: Decimal
    stress_score: Decimal
    capacity_score: Decimal
    growth_dimension_score: Decimal
    fulfillment_dimension_score: Decimal
    is_current: bool
    created_at: datetime
    updated_at: datetime
    dominant_emotion: str | None = None
    dominant_emotion_pct: Decimal | None = None
    emotional_momentum_score: Decimal | None = None
    drift_score: Decimal | None = None
    drift_status: str | None = None
    leverage_score: Decimal | None = None
    leverage_area: str | None = None
    happiness_driver: str | None = None
    happiness_driver_score: Decimal | None = None
    life_stage: str | None = None
    life_intelligence_summary: str | None = None


class PersonalLifeAttentionEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attention_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    attention_category: str
    intensity_level: str
    status: str
    created_at: datetime
    updated_at: datetime
    note: str | None = None
    pressure_weight: Decimal | None = None
    focus_load_score: Decimal | None = None


class PersonalLifeConnectionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_connection_id: UUID
    user_id: UUID
    source_moment_type_code: str
    target_moment_type_code: str
    connection_title: str
    connection_summary: str
    signal_label: str
    snapshot_month: date
    is_current: bool
    created_at: datetime
    connection_strength_pct: Decimal | None = None


class PersonalLifeDimensionScoresSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_dimension_score_id: UUID
    user_id: UUID
    dimension_code: str
    dimension_label: str
    dimension_score: Decimal
    status_label: str
    snapshot_month: date
    is_current: bool
    created_at: datetime
    driver_summary: str | None = None
    trend_direction: str | None = None


class PersonalLifeDriftAlertsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_drift_alert_id: UUID
    user_id: UUID
    drift_title: str
    drift_message: str
    severity_level: str
    is_active: bool
    created_at: datetime
    rising_dimension_code: str | None = None
    falling_dimension_code: str | None = None
    recommended_action: str | None = None


class PersonalLifeHealthSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_health_snapshot_id: UUID
    user_id: UUID
    life_health_score: Decimal
    health_status_label: str
    snapshot_month: date
    is_current: bool
    created_at: datetime
    monthly_delta_score: Decimal | None = None
    summary_text: str | None = None


class PersonalLifeJourneyEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_journey_event_id: UUID
    user_id: UUID
    journey_month: date
    journey_title: str
    created_at: datetime
    journey_description: str | None = None
    source_moment_type_code: str | None = None
    source_dimension_code: str | None = None
    importance_score: Decimal | None = None


class PersonalLifeMonthlyChangesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_monthly_change_id: UUID
    user_id: UUID
    change_label: str
    change_value_pct: Decimal
    direction: str
    snapshot_month: date
    created_at: datetime
    moment_type_code: str | None = None
    dimension_code: str | None = None


class PersonalLifeMoodEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mood_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    mood_state: str
    created_at: datetime
    updated_at: datetime
    reflection_text: str | None = None
    mood_tags: list[str] | None = None
    mood_score: Decimal | None = None
    pressure_context_flag: bool | None = None


class PersonalLifeOperationsProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_profile_id: UUID
    moment_id: UUID
    user_id: UUID
    current_life_state: str
    desired_directions: list[str]
    pressure_sources: list[str]
    recovery_supports: list[str]
    runtime_identity: str
    initial_runtime_focus: str
    created_at: datetime
    updated_at: datetime
    recovery_integrity_score: Decimal | None = None
    pressure_load_level: str | None = None


class PersonalLifeRecoveryEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recovery_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    recovery_type: str
    energy_impact: str
    created_at: datetime
    updated_at: datetime
    duration_bucket: str | None = None
    note: str | None = None
    recovery_score: Decimal | None = None
    anchor_candidate_flag: bool | None = None


class PersonalLifestyleAdjustEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lifestyle_adjust_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    adjustment_area: str
    priority_level: str
    confidence_level: str
    event_date: date
    created_at: datetime
    updated_at: datetime
    note: str | None = None
    lifestyle_gap_score: Decimal | None = None
    change_readiness_score: Decimal | None = None
    recommended_action_label: str | None = None


class PersonalLifestyleDiscoveryEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    discovery_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    discovery_type: str
    impact_level: str
    curiosity_level: str
    curiosity_driver_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    money_invested_amount: Decimal | None = None
    note: str | None = None
    exploration_score_delta: Decimal | None = None
    expansion_signal_score: Decimal | None = None


class PersonalLifestyleExperienceEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    experience_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    experience_type: str
    experience_quality: str
    energy_impact: str
    best_day_candidate_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    people_context: str | None = None
    location_context: str | None = None
    cost_amount: Decimal | None = None
    spend_category: str | None = None
    value_received: str | None = None
    note: str | None = None
    fulfillment_score_delta: Decimal | None = None
    lifestyle_roi_score: Decimal | None = None


class PersonalLifestyleExpressionEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expression_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    creation_type: str
    satisfaction_level: str
    inspiration_source_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    time_invested_bucket: str | None = None
    money_invested_amount: Decimal | None = None
    note: str | None = None
    creativity_score_delta: Decimal | None = None
    expression_energy_score: Decimal | None = None


class PersonalLifestyleProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lifestyle_profile_id: UUID
    moment_id: UUID
    user_id: UUID
    lifestyle_style: str
    current_lifestyle_state: str
    desired_lifestyle_vectors: list[str]
    neglected_lifestyle_areas: list[str]
    best_day_drivers: list[str]
    lifestyle_enrichment_factors: list[str]
    lifestyle_identity: str
    lifestyle_energy: str
    created_at: datetime
    updated_at: datetime
    primary_lifestyle_gap: str | None = None
    primary_lifestyle_opportunity: str | None = None
    lifestyle_potential: str | None = None


class PersonalLifestyleWellbeingEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wellbeing_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    wellbeing_areas: list[str]
    wellbeing_state: str
    balance_driver_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    contributors: list[str] | None = None
    note: str | None = None
    wellbeing_score_delta: Decimal | None = None
    energy_signal_score: Decimal | None = None


class PersonalLivePrioritiesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    live_priority_id: UUID
    moment_id: UUID
    user_id: UUID
    moment_type_code: str
    priority_title: str
    recommended_action_label: str
    is_current: bool
    created_at: datetime
    updated_at: datetime
    priority_reason: str | None = None
    expected_impact_json: Any | None = None
    recent_activity_json: Any | None = None
    quick_actions_json: Any | None = None


class PersonalMemoryDriverRankingsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_ranking_id: UUID
    user_id: UUID
    moment_id: UUID
    moment_type_code: str
    driver_category: str
    driver_rank: int
    driver_name: str
    snapshot_month: date
    is_current: bool
    created_at: datetime
    updated_at: datetime
    impact_pct: Decimal | None = None
    impact_description: str | None = None
    return_multiplier: Decimal | None = None


class PersonalMemoryEmotionalDnaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    emotional_dna_id: UUID
    user_id: UUID
    emotion_name: str
    emotion_pct: Decimal
    emotion_rank: int
    snapshot_month: date
    is_current: bool
    created_at: datetime
    updated_at: datetime
    moment_id: UUID | None = None
    moment_type_code: str | None = None
    dna_summary: str | None = None


class PersonalMemoryEvolutionSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evolution_snapshot_id: UUID
    user_id: UUID
    moment_id: UUID
    moment_type_code: str
    previous_stage: str
    current_stage: str
    transition_date: date
    snapshot_month: date
    is_current: bool
    created_at: datetime
    updated_at: datetime
    emerging_stage: str | None = None
    evolution_confidence_pct: Decimal | None = None


class PersonalMemoryIdentitySnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    identity_snapshot_id: UUID
    user_id: UUID
    moment_id: UUID
    moment_type_code: str
    identity_title: str
    confidence_pct: Decimal
    snapshot_month: date
    is_current: bool
    created_at: datetime
    updated_at: datetime
    confidence_trend_pct: Decimal | None = None
    identity_summary: str | None = None
    identity_visual_type: str | None = None


class PersonalMemoryPatternsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    memory_pattern_id: UUID
    moment_id: UUID
    user_id: UUID
    moment_type_code: str
    pattern_type: str
    pattern_title: str
    pattern_description: str
    confidence_score: Decimal
    supporting_event_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    contribution_breakdown_json: Any | None = None
    pattern_confidence_pct: Decimal | None = None
    pattern_explanation: str | None = None


class PersonalMetricSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_snapshot_id: UUID
    user_id: UUID
    moment_id: UUID
    moment_type_code: str
    metric_code: str
    metric_label: str
    metric_value: Decimal
    measurement_period: str
    snapshot_date: date
    created_at: datetime
    metric_delta: Decimal | None = None
    trend_direction: str | None = None


class PersonalMomentHighlightsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    moment_highlight_id: UUID
    user_id: UUID
    moment_id: UUID
    moment_type_code: str
    highlight_title: str
    highlight_type: str
    occurred_at: datetime
    is_current: bool
    created_at: datetime
    source_event_id: UUID | None = None
    source_event_type: str | None = None
    impact_label: str | None = None
    impact_score: Decimal | None = None
    amount: Decimal | None = None


class PersonalMomentProfilesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: UUID
    moment_id: UUID
    user_id: UUID
    identity_label: str
    identity_description: str
    primary_focus_label: str
    setup_payload: Any
    is_current: bool
    created_at: datetime
    updated_at: datetime
    energy_label: str | None = None
    primary_gap_label: str | None = None
    primary_opportunity_label: str | None = None
    horizon_current_label: str | None = None
    horizon_target_label: str | None = None
    horizon_gap_label: str | None = None
    horizon_potential_label: str | None = None


class PersonalMomentTurningPointsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    turning_point_id: UUID
    user_id: UUID
    moment_id: UUID
    moment_type_code: str
    turning_point_title: str
    turning_point_type: str
    detected_at: datetime
    is_current: bool
    created_at: datetime
    source_event_id: UUID | None = None
    source_event_type: str | None = None
    turning_point_description: str | None = None
    impact_score: Decimal | None = None
    occurred_at: datetime | None = None


class PersonalMomentTypesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    moment_type_id: UUID
    moment_type_code: str
    moment_type_name: str
    description: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PersonalMomentsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    moment_id: UUID
    user_id: UUID
    moment_type_id: UUID
    moment_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    activated_at: datetime | None = None
    archived_at: datetime | None = None
    current_identity_label: str | None = None
    current_state_label: str | None = None
    last_activity_at: datetime | None = None


class PersonalMoneyEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    money_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    moment_type_code: str
    source_event_type: str
    linked_event_id: UUID
    money_event_type: str
    amount: Decimal
    currency_code: str
    category_code: str
    subcategory_code: str | None = None
    direction: str
    event_date: date
    is_voided: bool
    created_at: datetime
    updated_at: datetime
    account_id: UUID | None = None
    impact_label: str | None = None
    value_received_label: str | None = None
    financial_pressure_score: Decimal | None = None
    investment_score: Decimal | None = None
    roi_signal_score: Decimal | None = None


class PersonalNotificationQueueSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: UUID
    user_id: UUID
    notification_type: str
    title: str
    body: str
    priority_level: str
    scheduled_for: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    moment_id: UUID | None = None
    moment_type_code: str | None = None
    deep_link_target: str | None = None
    sent_at: datetime | None = None
    metadata_json: Any | None = None


class PersonalPulseSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pulse_snapshot_id: UUID
    user_id: UUID
    pulse_title: str
    primary_metric_label: str
    primary_metric_value: Decimal
    snapshot_date: date
    created_at: datetime
    moment_id: UUID | None = None
    moment_type_code: str | None = None
    pulse_summary: str | None = None
    secondary_metrics: Any | None = None
    emerging_signal_label: str | None = None
    opportunity_label: str | None = None


class PersonalQuickAddEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    moment_type_code: str
    quick_add_tab_code: str
    event_type: str
    event_occurred_at: datetime
    raw_payload: Any
    is_voided: bool
    created_at: datetime
    updated_at: datetime


class PersonalRecommendationsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: UUID
    user_id: UUID
    recommendation_type: str
    recommendation_title: str
    recommendation_description: str
    recommended_action: str
    confidence_score: Decimal
    priority_score: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    recommendation_scope: str
    moment_id: UUID | None = None
    moment_type_code: str | None = None
    expected_impact_json: Any | None = None
    source_signal_id: UUID | None = None
    source_pattern_id: UUID | None = None
    acted_at: datetime | None = None
    dismissed_at: datetime | None = None
    expires_at: datetime | None = None
    growth_edge_multiplier: Decimal | None = None
    growth_edge_confidence_pct: Decimal | None = None
    life_impact_json: Any | None = None


class PersonalRelationshipAdjustEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    relationship_adjust_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    relationship_focus: str
    adjustment_area: str
    priority_level: str
    confidence_level: str
    event_date: date
    created_at: datetime
    updated_at: datetime
    desired_outcome: str | None = None
    note: str | None = None
    connection_gap_score: Decimal | None = None
    relationship_readiness_score: Decimal | None = None
    recommended_connection_action: str | None = None


class PersonalRelationshipConnectionEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    connection_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    connection_type: str
    relationship_type: str
    connection_quality: str
    presence_signal_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    emotional_tone: str | None = None
    time_invested_bucket: str | None = None
    note: str | None = None
    connection_score_delta: Decimal | None = None
    trust_score_delta: Decimal | None = None


class PersonalRelationshipExperienceEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    relationship_experience_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    experience_type: str
    relationship_type: str
    value_received: str
    meaningful_moment_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    cost_amount: Decimal | None = None
    spend_category: str | None = None
    note: str | None = None
    connection_score_delta: Decimal | None = None
    relationship_roi_score: Decimal | None = None


class PersonalRelationshipInvestmentEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    investment_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    investment_type: str
    relationship_type: str
    amount: Decimal
    investment_purpose: str
    perceived_value: str
    financial_support_flag: bool
    event_date: date
    created_at: datetime
    updated_at: datetime
    note: str | None = None
    investment_score_delta: Decimal | None = None
    connection_roi_score: Decimal | None = None


class PersonalRelationshipSupportEventsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    support_event_id: UUID
    quick_add_event_id: UUID
    moment_id: UUID
    user_id: UUID
    support_type: str
    relationship_type: str
    support_direction: str
    impact_level: str
    event_date: date
    created_at: datetime
    updated_at: datetime
    note: str | None = None
    support_score_delta: Decimal | None = None
    resilience_score_delta: Decimal | None = None
    support_balance_side: str | None = None


class PersonalRelationshipsProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    relationship_profile_id: UUID
    moment_id: UUID
    user_id: UUID
    relationship_focus: str
    current_relationship_state: str
    desired_connection_types: list[str]
    neglected_relationship_areas: list[str]
    relationship_strength_factors: list[str]
    relationship_investment_areas: list[str]
    relationship_identity: str
    relationship_energy: str
    created_at: datetime
    updated_at: datetime
    primary_relationship_gap: str | None = None
    primary_relationship_opportunity: str | None = None
    relationship_potential: str | None = None


class PersonalRuntimeSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    runtime_snapshot_id: UUID
    moment_id: UUID
    user_id: UUID
    moment_type_code: str
    runtime_state_label: str
    primary_score: Decimal
    trend_direction: str
    snapshot_date: date
    created_at: datetime
    runtime_summary: str | None = None
    secondary_score: Decimal | None = None
    risk_or_gap_label: str | None = None


class PersonalSignalsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    signal_id: UUID
    user_id: UUID
    moment_id: UUID
    moment_type_code: str
    signal_type: str
    signal_title: str
    signal_description: str
    signal_score: Decimal
    severity_level: str
    source_event_count: int
    signal_window: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    trend_direction: str | None = None
    source_metric_code: str | None = None
    source_metric_delta: Decimal | None = None
    source_payload: Any | None = None
    expires_at: datetime | None = None


class PersonalUserPreferencesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preference_id: UUID
    user_id: UUID
    default_currency_code: str
    timezone_name: str
    notification_enabled: bool
    quick_add_reminder_enabled: bool
    daily_summary_enabled: bool
    privacy_mode_enabled: bool
    created_at: datetime
    updated_at: datetime
    week_start_day: str | None = None
    default_account_id: UUID | None = None
    preferred_summary_time: time | None = None


class PersonalUserPreferencesUpdateSchema(BaseModel):
    """Partial update for personal settings (week start, notifications, privacy)."""

    week_start_day: str | None = None
    notification_enabled: bool | None = None
    quick_add_reminder_enabled: bool | None = None
    daily_summary_enabled: bool | None = None
    privacy_mode_enabled: bool | None = None
    preferred_summary_time: time | None = None
    default_account_id: UUID | None = None
    default_currency_code: str | None = None
    timezone_name: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> PersonalUserPreferencesUpdateSchema:
        if not any(
            [
                self.week_start_day is not None,
                self.notification_enabled is not None,
                self.quick_add_reminder_enabled is not None,
                self.daily_summary_enabled is not None,
                self.privacy_mode_enabled is not None,
                "preferred_summary_time" in self.model_fields_set,
                "default_account_id" in self.model_fields_set,
                self.default_currency_code is not None,
                self.timezone_name is not None,
            ]
        ):
            raise ValueError("At least one preference field must be provided")
        return self


class BootstrapPersonalPreferencesSchema(BaseModel):
    """Slim personal prefs embedded on app bootstrap."""

    preference_id: str
    user_id: str
    week_start_day: str = "MONDAY"
    notification_enabled: bool = True
    quick_add_reminder_enabled: bool = False
    daily_summary_enabled: bool = False
    privacy_mode_enabled: bool = False
    preferred_summary_time: str | None = None
    default_account_id: str | None = None
