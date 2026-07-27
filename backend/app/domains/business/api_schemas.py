"""Request / response DTOs for the Business API.

Request models validate the caller-supplied fields (enum values mirror the DB
CHECK constraints so invalid input fails with 422 before hitting the database).
Response composites bundle several generated read schemas for aggregate
endpoints (workspace config, analytics, memory overview).
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domains.business.schemas import (
    BusinessAttentionItemsSchema,
    BusinessHealthDriverScoresSchema,
    BusinessMemoryLearningsSchema,
    BusinessMemoryPatternsSchema,
    BusinessMemorySnapshotsSchema,
    BusinessMomentGovernanceSchema,
    BusinessMomentMetricsSchema,
    BusinessMomentSetupSchema,
    BusinessMomentStructureSchema,
    BusinessRecommendedActionsSchema,
    BusinessSignalInsightsSchema,
    BusinessSuccessMemorySchema,
    BusinessWisdomSchema,
)

# --------------------------------------------------------------------------- #
# Enum literals (mirror DB CHECK constraints)
# --------------------------------------------------------------------------- #
MomentType = Literal[
    "team_operations", "business_runway", "business_operations", "project_operations",
    "event_operations", "department_operations", "vendor_operations", "custom_operational_moment",
]
MemberRole = Literal[
    "Team Member", "Team Lead", "Budget Owner", "Approver", "Observer", "Runway Owner",
    "Finance Lead", "Operations Lead", "Financial Contributor", "Viewer", "Operations Owner",
    "Budget Controller", "Contributor",
]
MemberStatus = Literal["configured", "invited", "active", "removed"]
InviteMethod = Literal["email", "mobile", "username", "qr"]
Priority = Literal["low", "medium", "high", "critical"]
RunwayExpensePriority = Literal["low", "medium", "high"]
LifecycleTarget = Literal["configured", "active", "completed", "archived"]
Decision = Literal["approved", "rejected"]

OpsApprovalType = Literal[
    "expense_approval", "vendor_approval", "budget_change", "policy_exception", "operational_request",
]
TeamPriority = Literal["normal", "urgent"]

SpendCategory = Literal[
    "purchase", "vendor_payment", "staff_cost", "utility_bill", "maintenance",
    "marketing_spend", "inventory_refill", "service_charge", "travel_expense", "other",
]
InflowType = Literal[
    "revenue_collected", "investor_funding", "owner_contribution", "bank_loan",
    "government_grant", "customer_advance", "other",
]
ExpenseCategory = Literal[
    "salaries", "marketing", "technology", "operations", "vendor", "inventory", "taxes", "other",
]

RiskType = Literal[
    "funding_delay", "revenue_drop", "cost_increase", "customer_loss", "loan_risk",
    "vendor_dependency", "other",
]
RiskImpact = Literal["lt_1_month", "1_3_months", "3_6_months", "6_plus_months"]
AffectedMetric = Literal["cash_available", "revenue", "monthly_burn", "runway_threshold"]
IssueImpact = Literal["none_yet", "minor", "moderate", "major"]

JobType = Literal[
    "pulse_refresh", "moments_refresh", "life_refresh", "memory_refresh",
    "activity_refresh", "workspace_refresh", "business_360_refresh",
]

TeamSize = Literal["just_me", "2_5", "6_15", "16_50", "50_plus"]
WorkStyle = Literal["planned", "mixed", "fast_response"]
SetupVisibility = Literal["team_only", "leadership", "organization"]
CoordinationStyle = Literal["independent", "cross_functional", "leadership_driven", "shared_ownership"]
MonitoringLevel = Literal["basic", "standard", "high_visibility"]
OperationalVisibility = Literal["private", "leadership", "organization"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------- #
# Moments / projects / departments
# --------------------------------------------------------------------------- #
class BusinessMomentCreateRequest(_Strict):
    moment_type: MomentType
    moment_name: str = Field(min_length=1, max_length=255)
    workspace_id: UUID | None = None
    owner_name: str = Field(default="Owner", max_length=255)
    owner_role: MemberRole = "Operations Owner"


class BusinessMomentNamedCreateRequest(_Strict):
    """Create request for the project/department convenience endpoints."""

    moment_name: str = Field(min_length=1, max_length=255)
    workspace_id: UUID | None = None
    owner_name: str = Field(default="Owner", max_length=255)


# --------------------------------------------------------------------------- #
# Workspace configuration
# --------------------------------------------------------------------------- #
class WorkspaceSetupRequest(_Strict):
    purpose: str = Field(min_length=1, max_length=100)
    team_size: TeamSize
    work_style: WorkStyle
    visibility: SetupVisibility
    budget_enabled: bool = False
    currency: str = Field(default="INR", max_length=10)
    custom_purpose: str | None = Field(default=None, max_length=255)
    monthly_budget: Decimal | None = Field(default=None, ge=0)


class WorkspaceStructureRequest(_Strict):
    roles_supported: dict[str, Any]
    approver_role: str = Field(min_length=1, max_length=100)
    approval_threshold: Decimal = Field(ge=0)
    escalation_contact_role: str = Field(min_length=1, max_length=100)
    coordination_style: CoordinationStyle
    monitoring_level: MonitoringLevel
    approval_threshold_label: str | None = Field(default=None, max_length=100)
    custom_approver_user_id: UUID | None = None
    custom_escalation_user_id: UUID | None = None


class WorkspaceGovernanceRequest(_Strict):
    operational_visibility: OperationalVisibility
    send_invites_on_activation: bool = True
    notify_approvals: bool = True
    notify_spending_activity: bool = True
    notify_issues_risks: bool = True
    notify_team_updates: bool = True
    approval_enabled: bool = False
    activation_ready: bool = False
    runway_approval_required: bool = False
    operations_approval_required: bool = False


# --------------------------------------------------------------------------- #
# Members / invitations
# --------------------------------------------------------------------------- #
class MemberAddRequest(_Strict):
    name: str = Field(min_length=1, max_length=255)
    role: MemberRole
    member_status: MemberStatus = "configured"
    email: str | None = Field(default=None, max_length=255)
    mobile: str | None = Field(default=None, max_length=50)
    username: str | None = Field(default=None, max_length=100)
    is_team_lead: bool = False
    is_budget_owner: bool = False


class MemberUpdateRequest(_Strict):
    name: str | None = Field(default=None, max_length=255)
    role: MemberRole | None = None
    member_status: MemberStatus | None = None
    is_team_lead: bool | None = None
    is_budget_owner: bool | None = None
    can_edit_team_entries: bool | None = None
    can_add_runway_transactions: bool | None = None
    can_approve_operations_requests: bool | None = None


class InvitationCreateRequest(_Strict):
    invite_method: InviteMethod
    invite_target: str = Field(min_length=1, max_length=255)
    member_id: UUID | None = None
    send_on_activation: bool = True


# --------------------------------------------------------------------------- #
# Approvals
# --------------------------------------------------------------------------- #
class OperationsApprovalCreateRequest(_Strict):
    request_type: OpsApprovalType
    request_title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    priority: Priority = "medium"
    amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)
    linked_spend_entry_id: UUID | None = None


class TeamApprovalCreateRequest(_Strict):
    request_title: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(ge=0)
    approval_type: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1)
    approver_id: UUID
    priority: TeamPriority = "normal"


class ApprovalDecisionRequest(_Strict):
    decision: Decision
    note: str | None = None


# --------------------------------------------------------------------------- #
# Risks
# --------------------------------------------------------------------------- #
class RunwayRiskCreateRequest(_Strict):
    risk_title: str = Field(min_length=1, max_length=255)
    risk_type: RiskType
    severity: Priority
    expected_impact: RiskImpact
    owner_id: UUID | None = None
    target_resolution_date: date | None = None
    description: str | None = None
    affected_metric: AffectedMetric | None = None


class TeamIssueCreateRequest(_Strict):
    issue_title: str = Field(min_length=1, max_length=255)
    issue_type: str = Field(min_length=1, max_length=100)
    severity: Priority
    current_impact: IssueImpact
    owner_id: UUID | None = None
    target_resolution_date: datetime | None = None
    description: str | None = None


# --------------------------------------------------------------------------- #
# Transactions
# --------------------------------------------------------------------------- #
class SpendCreateRequest(_Strict):
    spend_name: str = Field(min_length=1, max_length=255)
    budget_category_id: UUID
    spend_category: SpendCategory
    currency: str = Field(min_length=1, max_length=10)
    amount: Decimal = Field(gt=0)
    spend_date: date
    exchange_rate_to_operating_currency: Decimal = Field(default=Decimal(1), gt=0)
    amount_in_operating_currency: Decimal | None = Field(default=None, ge=0)
    priority: Priority = "medium"
    approval_required: bool = False
    vendor_name: str | None = Field(default=None, max_length=255)
    description: str | None = None


class CashInflowCreateRequest(_Strict):
    inflow_type: InflowType
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=1, max_length=10)
    inflow_date: date
    exchange_rate_to_operating_currency: Decimal = Field(default=Decimal(1), gt=0)
    amount_in_operating_currency: Decimal | None = Field(default=None, ge=0)
    reference: str | None = Field(default=None, max_length=255)
    description: str | None = None


class ExpenseBurnCreateRequest(_Strict):
    expense_category: ExpenseCategory
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=1, max_length=10)
    expense_date: date
    exchange_rate_to_operating_currency: Decimal = Field(default=Decimal(1), gt=0)
    amount_in_operating_currency: Decimal | None = Field(default=None, ge=0)
    priority: RunwayExpensePriority = "medium"
    approval_required: bool = False
    vendor_name: str | None = Field(default=None, max_length=255)
    description: str | None = None


# --------------------------------------------------------------------------- #
# Quick add / state engine
# --------------------------------------------------------------------------- #
class QuickAddDraftCreateRequest(_Strict):
    tab_type: str = Field(min_length=1, max_length=50)
    draft_payload: dict[str, Any]


class OrchestrationJobCreateRequest(_Strict):
    job_type: JobType
    orchestration_scope: str | None = Field(default=None, max_length=50)
    priority: str = Field(default="medium", max_length=30)


# --------------------------------------------------------------------------- #
# Aggregate response composites
# --------------------------------------------------------------------------- #
class BusinessWorkspaceResponse(BaseModel):
    setup: BusinessMomentSetupSchema | None = None
    structure: BusinessMomentStructureSchema | None = None
    governance: BusinessMomentGovernanceSchema | None = None


class BusinessAnalyticsResponse(BaseModel):
    metrics: BusinessMomentMetricsSchema | None = None
    signals: list[BusinessSignalInsightsSchema] = []
    recommended_actions: list[BusinessRecommendedActionsSchema] = []
    health_drivers: list[BusinessHealthDriverScoresSchema] = []
    attention_items: list[BusinessAttentionItemsSchema] = []


class BusinessMemoryOverviewResponse(BaseModel):
    learnings: list[BusinessMemoryLearningsSchema] = []
    patterns: list[BusinessMemoryPatternsSchema] = []
    snapshots: list[BusinessMemorySnapshotsSchema] = []
    successes: list[BusinessSuccessMemorySchema] = []
    wisdom: list[BusinessWisdomSchema] = []
