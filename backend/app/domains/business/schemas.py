"""Business domain read schemas (one per table, from_attributes).

Generated from the SQLAlchemy models -- returned by the service layer so that
services never expose ORM models.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BusinessActivityCenterItemsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_center_item_id: UUID
    moment_id: UUID
    occurred_at: datetime
    created_at: datetime
    source_table: str | None = None
    source_record_id: UUID | None = None
    activity_type: str | None = None
    activity_title: str | None = None
    activity_summary: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    actor_user_id: UUID | None = None
    actor_name: str | None = None
    activity_status: str | None = None
    permission_badge: str | None = None


class BusinessActivityPermissionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    permission_id: UUID
    moment_id: UUID
    source_table: str
    source_record_id: UUID
    role_name: str
    granted_at: datetime
    can_view: bool | None = None
    can_edit: bool | None = None
    can_delete: bool | None = None
    can_approve: bool | None = None
    permission_reason: str | None = None


class BusinessActivitySourceMappingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mapping_id: UUID
    source_table: str
    title_field: str
    description_field: str | None = None
    status_field: str | None = None
    date_field: str | None = None
    amount_field: str | None = None
    active_flag: bool | None = None


class BusinessAttachmentFilesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file_id: UUID
    moment_id: UUID
    source_table: str
    source_record_id: UUID
    file_name: str
    file_type: str
    file_size_bytes: int
    storage_path: str
    uploaded_by: UUID
    uploaded_at: datetime


class BusinessAttentionItemsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attention_id: UUID
    moment_id: UUID
    attention_type: str
    severity: str
    title: str
    status: str
    created_at: datetime
    description: str | None = None
    due_date: datetime | None = None
    source_table: str | None = None
    source_record_id: UUID | None = None
    generated_by: str | None = None
    resolved_at: datetime | None = None


class BusinessAuditHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    audit_id: UUID
    moment_id: UUID
    source_table: str
    source_record_id: UUID
    field_name: str
    new_value: str
    change_type: str
    changed_by: UUID
    changed_by_name: str
    changed_at: datetime
    old_value: str | None = None
    change_reason: str | None = None


class BusinessDriverFormulaRegistrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_formula_id: UUID
    moment_type: str
    driver_code: str
    driver_name: str
    driver_weight: Decimal
    source_table: str
    formula_description: str
    source_column: str | None = None
    active_flag: bool | None = None
    created_at: datetime | None = None


class BusinessHealthDriverScoresSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score_id: UUID
    moment_id: UUID
    driver_code: str
    driver_name: str
    driver_score: Decimal
    driver_status: str
    calculated_at: datetime
    score_delta: Decimal | None = None
    trend_direction: str | None = None
    source_table: str | None = None
    source_record_id: UUID | None = None


class BusinessLifeConnectionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    connection_id: UUID
    workspace_id: UUID
    generated_at: datetime
    source_dimension: str | None = None
    source_label: str | None = None
    source_change: Decimal | None = None
    influence_type: str | None = None
    influence_strength: str | None = None
    target_dimension: str | None = None
    target_label: str | None = None
    target_change: Decimal | None = None
    confidence_score: Decimal | None = None


class BusinessLifeDimensionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dimension_id: UUID
    workspace_id: UUID
    dimension_type: str
    dimension_name: str
    dimension_score: Decimal
    generated_at: datetime
    dimension_status: str | None = None
    trend_direction: str | None = None
    trend_delta: Decimal | None = None
    active_moment_count: int | None = None


class BusinessLifeInsightsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    life_insight_id: UUID
    workspace_id: UUID
    insight_type: str
    insight_title: str
    insight_body: str
    generated_at: datetime
    insight_score: Decimal | None = None
    priority: str | None = None
    source_dimension: str | None = None
    insight_status: str | None = None


class BusinessLifeSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: UUID
    workspace_id: UUID
    life_score: Decimal
    life_status: str
    generated_at: datetime
    people_score: Decimal | None = None
    finance_score: Decimal | None = None
    operations_score: Decimal | None = None
    vendor_score: Decimal | None = None
    growth_score: Decimal | None = None
    active_moment_count: int | None = None
    strongest_dimension: str | None = None
    weakest_dimension: str | None = None
    leverage_dimension: str | None = None
    drift_detected: bool | None = None
    life_score_delta: Decimal | None = None
    included_moment_types: Any | None = None


class BusinessLiveFeedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feed_id: UUID
    moment_id: UUID
    source_table: str
    source_record_id: UUID
    event_type: str
    actor_user_id: UUID
    actor_name: str
    headline: str
    event_timestamp: datetime
    visibility: str
    is_deleted: bool
    activity_center_visible: bool
    detail_message: str | None = None
    amount: Decimal | None = None
    priority: str | None = None
    edit_mode: str | None = None
    permission_badge: str | None = None


class BusinessMemoryLearningsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    learning_id: UUID
    workspace_id: UUID
    created_at: datetime
    moment_id: UUID | None = None
    learning_type: str | None = None
    learning_title: str | None = None
    learning_summary: str | None = None
    confidence_score: Decimal | None = None
    derived_from_count: int | None = None
    learning_status: str | None = None


class BusinessMemoryPatternsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pattern_id: UUID
    moment_id: UUID
    pattern_type: str
    pattern_title: str
    observation_text: str
    first_observed_at: datetime
    last_observed_at: datetime
    pattern_status: str
    created_at: datetime
    display_priority: int
    source_metric: str | None = None
    confidence_level: Decimal | None = None
    workspace_id: UUID | None = None
    pattern_strength: Decimal | None = None


class BusinessMemorySnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: UUID
    workspace_id: UUID
    memory_score: Decimal
    memory_status: str
    generated_at: datetime
    learning_count: int | None = None
    playbook_count: int | None = None
    risk_count: int | None = None
    strongest_learning_id: UUID | None = None
    strongest_wisdom_id: UUID | None = None
    memory_score_delta: Decimal | None = None
    success_count: int | None = None
    wisdom_count: int | None = None


class BusinessMomentGovernanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    governance_id: UUID
    moment_id: UUID
    send_invites_on_activation: bool
    operational_visibility: str
    notify_approvals: bool
    notify_spending_activity: bool
    notify_issues_risks: bool
    notify_team_updates: bool
    approval_enabled: bool
    activation_ready: bool
    created_at: datetime
    updated_at: datetime
    runway_approval_required: bool
    operations_approval_required: bool
    activation_ready_reason: str | None = None
    activated_by: UUID | None = None
    activated_at: datetime | None = None
    runway_visibility_roles: Any | None = None
    runway_alert_roles: Any | None = None
    runway_alert_conditions: Any | None = None
    runway_approval_rules: Any | None = None
    operations_visibility_roles: Any | None = None
    operations_alert_roles: Any | None = None
    operations_alert_conditions: Any | None = None
    operations_approval_rules: Any | None = None
    operations_monitoring_level: str | None = None


class BusinessMomentHighlightsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    highlight_id: UUID
    moment_id: UUID
    highlight_type: str
    highlight_title: str
    created_at: datetime
    highlight_summary: str | None = None
    source_table: str | None = None
    source_record_id: UUID | None = None
    impact_level: str | None = None
    highlight_status: str | None = None


class BusinessMomentInvitationsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invite_id: UUID
    moment_id: UUID
    invite_method: str
    invite_status: str
    invite_target: str
    send_on_activation: bool
    created_at: datetime
    updated_at: datetime
    member_id: UUID | None = None
    qr_token: str | None = None
    sent_at: datetime | None = None
    accepted_at: datetime | None = None
    expires_at: datetime | None = None


class BusinessMomentMembersSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: UUID
    moment_id: UUID
    name: str
    role: str
    member_status: str
    is_team_lead: bool
    is_budget_owner: bool
    can_edit_own_entries: bool
    can_edit_team_entries: bool
    can_edit_expense_entries: bool
    added_by: UUID
    created_at: datetime
    updated_at: datetime
    can_add_runway_transactions: bool
    can_edit_financial_entries: bool
    can_manage_runway_settings: bool
    can_approve_runway_changes: bool
    can_add_operations_records: bool
    can_edit_operations_records: bool
    can_edit_own_operations_records: bool
    can_approve_operations_requests: bool
    can_delete_operations_records: bool
    can_manage_operations_settings: bool
    user_id: UUID | None = None
    email: str | None = None
    mobile: str | None = None
    username: str | None = None


class BusinessMomentMetricsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_id: UUID
    moment_id: UUID
    members_count: int
    activities_count: int
    pending_approvals: int
    open_risks: int
    spend_amount: Decimal
    last_updated_at: datetime
    cash_available: Decimal
    estimated_runway_months: Decimal
    cash_inflow_count: int
    expense_count: int
    risk_count: int
    decision_count: int
    net_burn: Decimal
    budget_category_count: int
    operations_budget_used_total: Decimal
    operations_active_issue_count: int
    operations_approval_count: int
    operations_improvement_count: int
    recent_wins_count: int
    timeline_count: int
    last_activity_at: datetime | None = None
    operating_currency: str | None = None
    last_operations_activity_at: datetime | None = None
    latest_spend_title: str | None = None
    latest_issue_title: str | None = None
    latest_approval_status: str | None = None
    latest_improvement_title: str | None = None
    operations_operating_currency: str | None = None
    progress_score: Decimal | None = None
    progress_status: str | None = None
    continue_cta_label: str | None = None


class BusinessMomentSetupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    setup_id: UUID
    moment_id: UUID
    purpose: str
    team_size: str
    budget_enabled: bool
    currency: str
    work_style: str
    visibility: str
    team_owner_user_id: UUID
    created_at: datetime
    updated_at: datetime
    custom_purpose: str | None = None
    monthly_budget: Decimal | None = None


class BusinessMomentStructureSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    structure_id: UUID
    moment_id: UUID
    roles_supported: Any
    approver_role: str
    approval_threshold: Decimal
    escalation_contact_role: str
    coordination_style: str
    monitoring_level: str
    created_at: datetime
    updated_at: datetime
    custom_approver_user_id: UUID | None = None
    approval_threshold_label: str | None = None
    custom_escalation_user_id: UUID | None = None


class BusinessMomentsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    moment_id: UUID
    workspace_id: UUID
    moment_type: str
    moment_name: str
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    activated_at: datetime | None = None


class BusinessNotificationsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: UUID
    moment_id: UUID
    recipient_user_id: UUID
    notification_type: str
    source_table: str
    source_record_id: UUID
    title: str
    message: str
    priority: str
    delivery_channel: str
    notification_status: str
    created_at: datetime
    read_at: datetime | None = None
    expires_at: datetime | None = None


class BusinessOperationsBudgetCategoriesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    budget_category_id: UUID
    moment_id: UUID
    category_name: str
    allocated_budget: Decimal
    currency: str
    category_status: str
    created_at: datetime
    updated_at: datetime
    custom_category_name: str | None = None
    archived_at: datetime | None = None
    alert_threshold_percent: Decimal | None = None


class BusinessOperationsGovernanceRulesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operations_governance_id: UUID
    moment_id: UUID
    visibility_roles: Any
    alert_conditions: Any
    alert_recipient_roles: Any
    approval_required: bool
    monitoring_level: str
    created_at: datetime
    updated_at: datetime
    approval_rules: Any | None = None


class BusinessOperationsSetupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operations_setup_id: UUID
    moment_id: UUID
    operations_type: str
    operating_model: str
    operational_owner_role: str
    operating_currency: str
    monthly_operating_budget: Decimal
    created_at: datetime
    updated_at: datetime


class BusinessOperationsSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operations_snapshot_id: UUID
    moment_id: UUID
    snapshot_date: date
    monthly_budget: Decimal
    allocated_budget: Decimal
    budget_used: Decimal
    budget_remaining: Decimal
    budget_alert_count: int
    vendor_activity_count: int
    open_approval_count: int
    active_issue_count: int
    critical_issue_count: int
    improvement_count: int
    operations_health_status: str
    operating_currency: str
    generated_at: datetime


class BusinessOperationsStructureSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operations_structure_id: UUID
    moment_id: UUID
    vendor_dependency: str
    approval_model: str
    issue_sensitivity: str
    performance_review_cycle: str
    created_at: datetime
    updated_at: datetime
    kpi_tracking: Any | None = None


class BusinessOrchestrationJobsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    moment_id: UUID
    job_type: str
    job_status: str
    attempts: int
    queued_at: datetime
    source_table: str | None = None
    source_record_id: UUID | None = None
    error_message: str | None = None
    completed_at: datetime | None = None
    workspace_id: UUID | None = None
    orchestration_scope: str | None = None
    priority: str | None = None


class BusinessPlaybooksSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    playbook_id: UUID
    workspace_id: UUID
    created_at: datetime
    moment_id: UUID | None = None
    playbook_title: str | None = None
    playbook_summary: str | None = None
    success_rate: Decimal | None = None
    confidence_score: Decimal | None = None
    playbook_status: str | None = None


class BusinessProgressSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    progress_id: UUID
    moment_id: UUID
    metric_code: str
    metric_name: str
    metric_score: Decimal
    snapshot_date: date
    generated_at: datetime
    metric_delta: Decimal | None = None
    metric_status: str | None = None


class BusinessPulseSnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: UUID
    moment_id: UUID
    snapshot_date: date
    activities_count: int
    completed_activities: int
    in_progress_activities: int
    planned_activities: int
    pending_approvals: int
    open_risks: int
    critical_risks: int
    monthly_spend: Decimal
    generated_at: datetime
    health_score: Decimal
    health_status: str
    cash_available: Decimal
    estimated_runway_months: Decimal
    cash_inflow_total: Decimal
    expense_burn_total: Decimal
    net_burn: Decimal
    runway_alert_count: int
    runway_risk_count: int
    active_issue_count: int
    open_approval_count: int
    budget_alert_count: int
    improvement_count: int
    budget_used_total: Decimal
    budget_remaining_total: Decimal
    vendor_activity_count: int
    health_driver_count: int
    attention_count: int
    signal_count: int
    top_spend_category: str | None = None
    health_reason: str | None = None
    operating_currency: str | None = None
    operations_health_status: str | None = None
    operations_operating_currency: str | None = None
    pulse_category: str | None = None
    pulse_description: str | None = None
    next_best_action_id: UUID | None = None


class BusinessQuickAddDraftsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    draft_id: UUID
    moment_id: UUID
    user_id: UUID
    tab_type: str
    draft_payload: Any
    draft_status: str
    updated_at: datetime


class BusinessRecommendedActionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action_id: UUID
    moment_id: UUID
    action_title: str
    action_reason: str
    priority: str
    cta_label: str
    created_at: datetime
    target_screen: str | None = None
    target_payload: Any | None = None
    expected_health_impact: Decimal | None = None
    source_rule: str | None = None
    status: str | None = None
    completed_at: datetime | None = None


class BusinessRiskMemorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    risk_memory_id: UUID
    workspace_id: UUID
    created_at: datetime
    moment_id: UUID | None = None
    risk_title: str | None = None
    risk_summary: str | None = None
    observed_count: int | None = None
    severity: str | None = None


class BusinessRunwayGovernanceRulesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    governance_rule_id: UUID
    moment_id: UUID
    visibility_roles: Any
    alert_recipient_roles: Any
    alert_conditions: Any
    approval_required: bool
    created_at: datetime
    updated_at: datetime
    approval_rules: Any | None = None


class BusinessRunwaySetupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    runway_setup_id: UUID
    moment_id: UUID
    business_stage: str
    cash_available: Decimal
    monthly_burn: Decimal
    monthly_revenue: Decimal
    operating_currency: str
    estimated_runway_months: Decimal
    runway_goal: str
    created_at: datetime
    updated_at: datetime
    runway_owner_id: UUID | None = None


class BusinessRunwaySnapshotsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: UUID
    moment_id: UUID
    snapshot_date: date
    cash_available: Decimal
    total_cash_inflow: Decimal
    total_expense_burn: Decimal
    net_burn: Decimal
    estimated_runway_months: Decimal
    open_risks: int
    decision_count: int
    operating_currency: str
    generated_at: datetime


class BusinessRunwayStructureSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    structure_id: UUID
    moment_id: UUID
    burn_categories: Any
    revenue_model: str
    alert_threshold_months: Decimal
    funding_structure: str
    runway_philosophy: str
    monitoring_level: str
    created_at: datetime
    updated_at: datetime
    hiring_intent: str | None = None


class BusinessSignalInsightsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    signal_id: UUID
    moment_id: UUID
    signal_type: str
    signal_title: str
    signal_summary: str
    impact_level: str
    generated_at: datetime
    change_percent: Decimal | None = None
    lookback_days: int | None = None
    source_table: str | None = None
    source_record_id: UUID | None = None
    expires_at: datetime | None = None
    signal_status: str | None = None


class BusinessSuccessMemorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success_id: UUID
    workspace_id: UUID
    created_at: datetime
    moment_id: UUID | None = None
    success_title: str | None = None
    success_summary: str | None = None
    action_taken: str | None = None
    impact_score: Decimal | None = None


class BusinessTransactionPermissionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    permission_id: UUID
    moment_id: UUID
    source_table: str
    source_record_id: UUID
    role_name: str
    can_view: bool
    can_edit: bool
    can_delete: bool
    permission_reason: str
    granted_at: datetime
    active_flag: bool
    can_approve: bool


class BusinessVendorDirectorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vendor_id: UUID
    workspace_id: UUID
    vendor_name: str
    vendor_status: str
    total_spend: Decimal
    created_at: datetime
    vendor_category: str | None = None
    last_transaction_at: datetime | None = None


class BusinessWisdomSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    wisdom_id: UUID
    workspace_id: UUID
    wisdom_text: str
    created_at: datetime
    moment_id: UUID | None = None
    confidence_score: Decimal | None = None


class OperationsApprovalRequestsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operations_approval_id: UUID
    moment_id: UUID
    request_type: str
    request_title: str
    priority: str
    description: str
    approval_status: str
    requested_by: UUID
    created_at: datetime
    updated_at: datetime
    amount: Decimal | None = None
    currency: str | None = None
    linked_spend_entry_id: UUID | None = None
    approver_id: UUID | None = None
    decision_note: str | None = None
    decided_by: UUID | None = None
    decided_at: datetime | None = None
    archived_at: datetime | None = None


class OperationsImprovementsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    improvement_id: UUID
    moment_id: UUID
    improvement_type: str
    improvement_title: str
    impact_area: str
    expected_impact: str
    effective_date: date
    follow_up_required: bool
    improvement_status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    owner_id: UUID | None = None
    description: str | None = None
    follow_up_owner_id: UUID | None = None
    follow_up_date: date | None = None
    completed_at: datetime | None = None
    archived_at: datetime | None = None


class OperationsIssuesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    operations_issue_id: UUID
    moment_id: UUID
    issue_category: str
    issue_title: str
    severity: str
    impact_area: str
    issue_status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    owner_id: UUID | None = None
    target_resolution_date: date | None = None
    description: str | None = None
    resolved_at: datetime | None = None
    archived_at: datetime | None = None


class OperationsSpendEntriesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    spend_entry_id: UUID
    moment_id: UUID
    spend_name: str
    budget_category_id: UUID
    spend_category: str
    currency: str
    amount: Decimal
    exchange_rate_to_operating_currency: Decimal
    amount_in_operating_currency: Decimal
    spend_date: date
    priority: str
    approval_required: bool
    approval_status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    vendor_name: str | None = None
    description: str | None = None
    archived_at: datetime | None = None


class OperationsVendorUpdatesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vendor_update_id: UUID
    moment_id: UUID
    vendor_event_type: str
    vendor_name: str
    vendor_category: str
    vendor_status: str
    impact_level: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    archived_at: datetime | None = None


class RunwayCashInflowsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cash_inflow_id: UUID
    moment_id: UUID
    inflow_type: str
    amount: Decimal
    currency: str
    exchange_rate_to_operating_currency: Decimal
    amount_in_operating_currency: Decimal
    inflow_date: date
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    reference: str | None = None
    description: str | None = None
    archived_at: datetime | None = None


class RunwayExpenseBurnsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expense_id: UUID
    moment_id: UUID
    expense_category: str
    amount: Decimal
    currency: str
    exchange_rate_to_operating_currency: Decimal
    amount_in_operating_currency: Decimal
    expense_date: date
    approval_required: bool
    approval_status: str
    priority: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    vendor_name: str | None = None
    description: str | None = None
    archived_at: datetime | None = None


class RunwayFinancialUpdatesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    financial_update_id: UUID
    moment_id: UUID
    update_type: str
    current_value: Decimal
    new_value: Decimal
    reason: str
    approval_required: bool
    approval_status: str
    applied_status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    currency: str | None = None
    exchange_rate_to_operating_currency: Decimal | None = None
    new_value_in_operating_currency: Decimal | None = None
    applied_at: datetime | None = None
    archived_at: datetime | None = None


class RunwayRisksSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    risk_id: UUID
    moment_id: UUID
    risk_title: str
    risk_type: str
    severity: str
    expected_impact: str
    risk_status: str
    adjustment_required: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    owner_id: UUID | None = None
    target_resolution_date: date | None = None
    description: str | None = None
    affected_metric: str | None = None
    current_value: Decimal | None = None
    new_value: Decimal | None = None
    resolved_at: datetime | None = None
    archived_at: datetime | None = None


class RunwayStrategicDecisionsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    decision_id: UUID
    moment_id: UUID
    decision_type: str
    decision_title: str
    expected_impact: str
    decision_status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    decision_owner_id: UUID | None = None
    description: str | None = None
    archived_at: datetime | None = None


class TeamActivitiesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_id: UUID
    moment_id: UUID
    activity_title: str
    category: str
    activity_status: str
    has_spend: bool
    priority: str
    created_by: UUID
    recorded_at: datetime
    updated_at: datetime
    description: str | None = None
    activity_owner_id: UUID | None = None
    amount: Decimal | None = None
    vendor_name: str | None = None
    receipt_file_id: UUID | None = None
    archived_at: datetime | None = None


class TeamApprovalRequestsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    approval_id: UUID
    moment_id: UUID
    request_title: str
    amount: Decimal
    approval_type: str
    reason: str
    priority: str
    requested_by: UUID
    approver_id: UUID
    approval_status: str
    created_at: datetime
    updated_at: datetime
    converted_to_spend: bool
    needed_by: datetime | None = None
    decision_note: str | None = None
    decided_by: UUID | None = None
    decided_at: datetime | None = None
    archived_at: datetime | None = None
    converted_activity_id: UUID | None = None
    converted_at: datetime | None = None


class TeamIssueRisksSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    issue_id: UUID
    moment_id: UUID
    issue_title: str
    issue_type: str
    severity: str
    current_impact: str
    resolution_status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    owner_id: UUID | None = None
    target_resolution_date: datetime | None = None
    description: str | None = None
    resolved_at: datetime | None = None
    archived_at: datetime | None = None


class TeamUpdatesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    update_id: UUID
    moment_id: UUID
    update_type: str
    update_title: str
    visibility: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    people_involved: Any | None = None
    description: str | None = None
    archived_at: datetime | None = None
