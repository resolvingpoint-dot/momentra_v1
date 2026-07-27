from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.service import Page
from app.dependencies.auth import get_current_user, get_current_user_id
from app.domains.app_bootstrap.empty_state_config import EMPTY_STATE_OVERRIDES
from app.domains.business.api_schemas import (
    ApprovalDecisionRequest,
    BusinessAnalyticsResponse,
    BusinessMemoryOverviewResponse,
    BusinessMomentNamedCreateRequest,
    BusinessWorkspaceResponse,
    CashInflowCreateRequest,
    ExpenseBurnCreateRequest,
    InvitationCreateRequest,
    MemberAddRequest,
    MemberUpdateRequest,
    OperationsApprovalCreateRequest,
    OrchestrationJobCreateRequest,
    QuickAddDraftCreateRequest,
    RunwayRiskCreateRequest,
    SpendCreateRequest,
    TeamApprovalCreateRequest,
    TeamIssueCreateRequest,
    WorkspaceGovernanceRequest,
    WorkspaceSetupRequest,
    WorkspaceStructureRequest,
)
from app.domains.business.schemas import (
    BusinessActivityCenterItemsSchema,
    BusinessLiveFeedSchema,
    BusinessMomentGovernanceSchema,
    BusinessMomentInvitationsSchema,
    BusinessMomentMembersSchema,
    BusinessMomentSetupSchema,
    BusinessMomentStructureSchema,
    BusinessMomentsSchema,
    BusinessNotificationsSchema,
    BusinessOrchestrationJobsSchema,
    BusinessPulseSnapshotsSchema,
    BusinessQuickAddDraftsSchema,
    OperationsApprovalRequestsSchema,
    OperationsSpendEntriesSchema,
    RunwayCashInflowsSchema,
    RunwayExpenseBurnsSchema,
    RunwayRisksSchema,
    TeamApprovalRequestsSchema,
    TeamIssueRisksSchema,
)
from app.domains.business.services import (
    BusinessActivityFeedModule,
    BusinessAnalyticsModule,
    BusinessApprovalsModule,
    BusinessDepartmentsModule,
    BusinessMembersModule,
    BusinessMemoryModule,
    BusinessMomentsModule,
    BusinessNotificationsModule,
    BusinessProjectsModule,
    BusinessPulseModule,
    BusinessQuickAddModule,
    BusinessRisksModule,
    BusinessStateEngineModule,
    BusinessTransactionsModule,
    BusinessWorkspaceModule,
)
from app.domains.moments.service import MomentService
from app.domains.module_states.service import ModuleStateService
from app.domains.users.service import UserService

router = APIRouter(prefix="/business", tags=["business"])


# --------------------------------------------------------------------------- #
# Home / bootstrap
# --------------------------------------------------------------------------- #
@router.get("/home", summary="Business context home / empty-state bootstrap")
async def business_home(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_service = UserService(db)
    user = await user_service.get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    count = await MomentService(db).count_by_context_type(user.id, "BUSINESS")
    ms = await ModuleStateService(db).get_state(user.id, "BUSINESS")
    return {
        "context": "BUSINESS",
        "state": ms.state if ms else "EMPTY",
        "counts": {"moments": count},
        "empty_state_override": EMPTY_STATE_OVERRIDES.get("BUSINESS"),
    }


# --------------------------------------------------------------------------- #
# Moments
# --------------------------------------------------------------------------- #
@router.get("/moments", response_model=Page[BusinessMomentsSchema], summary="List business moments the caller belongs to")
async def list_moments(
    status_filter: str | None = Query(default=None, alias="status"),
    moment_type: str | None = Query(default=None),
    workspace_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessMomentsSchema]:
    return await BusinessMomentsModule(db).list_moments(
        user_id, status=status_filter, moment_type=moment_type, workspace_id=workspace_id, page=page, per_page=per_page
    )


# NOTE: ``POST /business/moments`` is served by the mobile-contract router
# (``business_app``), which is registered first in ``main.py`` and wins the path.
# The typed create handler is intentionally not defined here to avoid a shadowed
# (unreachable) route and a duplicate OpenAPI operation.


@router.get("/moments/{moment_id}", response_model=BusinessMomentsSchema, summary="Get a business moment")
async def get_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> BusinessMomentsSchema:
    return await BusinessMomentsModule(db).get_moment(user_id, moment_id)


# --------------------------------------------------------------------------- #
# State engine — lifecycle + orchestration jobs
# --------------------------------------------------------------------------- #
@router.post("/moments/{moment_id}/configure", response_model=BusinessMomentsSchema, summary="Mark moment as configured")
async def configure_moment(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> BusinessMomentsSchema:
    return await BusinessStateEngineModule(db).configure(user_id, moment_id)


@router.post("/moments/{moment_id}/activate", response_model=BusinessMomentsSchema, summary="Activate moment")
async def activate_moment(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> BusinessMomentsSchema:
    return await BusinessStateEngineModule(db).activate(user_id, moment_id)


@router.post("/moments/{moment_id}/complete", response_model=BusinessMomentsSchema, summary="Complete moment")
async def complete_moment(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> BusinessMomentsSchema:
    return await BusinessStateEngineModule(db).complete(user_id, moment_id)


@router.post("/moments/{moment_id}/archive", response_model=BusinessMomentsSchema, summary="Archive moment")
async def archive_moment(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> BusinessMomentsSchema:
    return await BusinessStateEngineModule(db).archive(user_id, moment_id)


@router.get("/moments/{moment_id}/jobs", response_model=Page[BusinessOrchestrationJobsSchema], summary="List orchestration jobs")
async def list_jobs(
    moment_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessOrchestrationJobsSchema]:
    return await BusinessStateEngineModule(db).list_jobs(user_id, moment_id, status=status_filter, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/jobs", response_model=BusinessOrchestrationJobsSchema, status_code=status.HTTP_201_CREATED, summary="Enqueue an orchestration job")
async def enqueue_job(
    moment_id: UUID,
    body: OrchestrationJobCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> BusinessOrchestrationJobsSchema:
    return await BusinessStateEngineModule(db).enqueue_job(
        user_id, moment_id, job_type=body.job_type, orchestration_scope=body.orchestration_scope, priority=body.priority
    )


# --------------------------------------------------------------------------- #
# Workspace configuration
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/workspace", response_model=BusinessWorkspaceResponse, summary="Get workspace configuration")
async def get_workspace(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> BusinessWorkspaceResponse:
    return await BusinessWorkspaceModule(db).get_workspace(user_id, moment_id)


@router.put("/moments/{moment_id}/workspace/setup", response_model=BusinessMomentSetupSchema, summary="Create/replace workspace setup")
async def upsert_workspace_setup(
    moment_id: UUID, body: WorkspaceSetupRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentSetupSchema:
    return await BusinessWorkspaceModule(db).upsert_setup(user_id, moment_id, body.model_dump())


@router.put("/moments/{moment_id}/workspace/structure", response_model=BusinessMomentStructureSchema, summary="Create/replace workspace structure")
async def upsert_workspace_structure(
    moment_id: UUID, body: WorkspaceStructureRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentStructureSchema:
    return await BusinessWorkspaceModule(db).upsert_structure(user_id, moment_id, body.model_dump())


@router.put("/moments/{moment_id}/workspace/governance", response_model=BusinessMomentGovernanceSchema, summary="Create/replace workspace governance")
async def upsert_workspace_governance(
    moment_id: UUID, body: WorkspaceGovernanceRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentGovernanceSchema:
    return await BusinessWorkspaceModule(db).upsert_governance(user_id, moment_id, body.model_dump())


# --------------------------------------------------------------------------- #
# Members + invitations
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/members", response_model=Page[BusinessMomentMembersSchema], summary="List moment members")
async def list_members(
    moment_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessMomentMembersSchema]:
    return await BusinessMembersModule(db).list_members(user_id, moment_id, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/members", response_model=BusinessMomentMembersSchema, status_code=status.HTTP_201_CREATED, summary="Add a member")
async def add_member(
    moment_id: UUID, body: MemberAddRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentMembersSchema:
    return await BusinessMembersModule(db).add_member(user_id, moment_id, body.model_dump())


@router.patch("/moments/{moment_id}/members/{member_id}", response_model=BusinessMomentMembersSchema, summary="Update a member")
async def update_member(
    moment_id: UUID, member_id: UUID, body: MemberUpdateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentMembersSchema:
    return await BusinessMembersModule(db).update_member(user_id, moment_id, member_id, body.model_dump(exclude_unset=True))


@router.delete("/moments/{moment_id}/members/{member_id}", response_model=BusinessMomentMembersSchema, summary="Remove a member")
async def remove_member(
    moment_id: UUID, member_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentMembersSchema:
    return await BusinessMembersModule(db).remove_member(user_id, moment_id, member_id)


@router.get("/moments/{moment_id}/invitations", response_model=Page[BusinessMomentInvitationsSchema], summary="List invitations")
async def list_invitations(
    moment_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessMomentInvitationsSchema]:
    return await BusinessMembersModule(db).list_invitations(user_id, moment_id, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/invitations", response_model=BusinessMomentInvitationsSchema, status_code=status.HTTP_201_CREATED, summary="Create an invitation")
async def create_invitation(
    moment_id: UUID, body: InvitationCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentInvitationsSchema:
    return await BusinessMembersModule(db).create_invitation(
        user_id, moment_id, invite_method=body.invite_method, invite_target=body.invite_target,
        member_id=body.member_id, send_on_activation=body.send_on_activation,
    )


@router.post("/moments/{moment_id}/invitations/{invite_id}/accept", response_model=BusinessMomentInvitationsSchema, summary="Accept an invitation")
async def accept_invitation(
    moment_id: UUID, invite_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentInvitationsSchema:
    return await BusinessMembersModule(db).accept_invitation(user_id, moment_id, invite_id)


@router.post("/moments/{moment_id}/invitations/{invite_id}/cancel", response_model=BusinessMomentInvitationsSchema, summary="Cancel an invitation")
async def cancel_invitation(
    moment_id: UUID, invite_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentInvitationsSchema:
    return await BusinessMembersModule(db).cancel_invitation(user_id, moment_id, invite_id)


# --------------------------------------------------------------------------- #
# Departments + projects (type-filtered moments)
# --------------------------------------------------------------------------- #
@router.get("/departments", response_model=Page[BusinessMomentsSchema], summary="List department moments")
async def list_departments(
    status_filter: str | None = Query(default=None, alias="status"),
    workspace_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessMomentsSchema]:
    return await BusinessDepartmentsModule(db).list_departments(user_id, status=status_filter, workspace_id=workspace_id, page=page, per_page=per_page)


@router.post("/departments", response_model=BusinessMomentsSchema, status_code=status.HTTP_201_CREATED, summary="Create a department moment")
async def create_department(
    body: BusinessMomentNamedCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentsSchema:
    return await BusinessDepartmentsModule(db).create_department(user_id, moment_name=body.moment_name, workspace_id=body.workspace_id, owner_name=body.owner_name)


@router.get("/projects", response_model=Page[BusinessMomentsSchema], summary="List project moments")
async def list_projects(
    status_filter: str | None = Query(default=None, alias="status"),
    workspace_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessMomentsSchema]:
    return await BusinessProjectsModule(db).list_projects(user_id, status=status_filter, workspace_id=workspace_id, page=page, per_page=per_page)


@router.post("/projects", response_model=BusinessMomentsSchema, status_code=status.HTTP_201_CREATED, summary="Create a project moment")
async def create_project(
    body: BusinessMomentNamedCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMomentsSchema:
    return await BusinessProjectsModule(db).create_project(user_id, moment_name=body.moment_name, workspace_id=body.workspace_id, owner_name=body.owner_name)


# --------------------------------------------------------------------------- #
# Approvals
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/approvals/operations", response_model=Page[OperationsApprovalRequestsSchema], summary="List operations approvals")
async def list_operations_approvals(
    moment_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[OperationsApprovalRequestsSchema]:
    return await BusinessApprovalsModule(db).list_operations_approvals(user_id, moment_id, status=status_filter, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/approvals/operations", response_model=OperationsApprovalRequestsSchema, status_code=status.HTTP_201_CREATED, summary="Create an operations approval request")
async def create_operations_approval(
    moment_id: UUID, body: OperationsApprovalCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> OperationsApprovalRequestsSchema:
    return await BusinessApprovalsModule(db).create_operations_approval(
        user_id, moment_id, request_type=body.request_type, request_title=body.request_title, description=body.description,
        priority=body.priority, amount=body.amount, currency=body.currency, linked_spend_entry_id=body.linked_spend_entry_id,
    )


@router.post("/moments/{moment_id}/approvals/operations/{approval_id}/decide", response_model=OperationsApprovalRequestsSchema, summary="Approve/reject an operations request")
async def decide_operations_approval(
    moment_id: UUID, approval_id: UUID, body: ApprovalDecisionRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> OperationsApprovalRequestsSchema:
    return await BusinessApprovalsModule(db).decide_operations_approval(user_id, moment_id, approval_id, body.decision, body.note)


@router.get("/moments/{moment_id}/approvals/team", response_model=Page[TeamApprovalRequestsSchema], summary="List team approvals")
async def list_team_approvals(
    moment_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[TeamApprovalRequestsSchema]:
    return await BusinessApprovalsModule(db).list_team_approvals(user_id, moment_id, status=status_filter, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/approvals/team", response_model=TeamApprovalRequestsSchema, status_code=status.HTTP_201_CREATED, summary="Create a team approval request")
async def create_team_approval(
    moment_id: UUID, body: TeamApprovalCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> TeamApprovalRequestsSchema:
    return await BusinessApprovalsModule(db).create_team_approval(
        user_id, moment_id, request_title=body.request_title, amount=body.amount, approval_type=body.approval_type,
        reason=body.reason, approver_id=body.approver_id, priority=body.priority,
    )


@router.post("/moments/{moment_id}/approvals/team/{approval_id}/decide", response_model=TeamApprovalRequestsSchema, summary="Approve/reject a team request")
async def decide_team_approval(
    moment_id: UUID, approval_id: UUID, body: ApprovalDecisionRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> TeamApprovalRequestsSchema:
    return await BusinessApprovalsModule(db).decide_team_approval(user_id, moment_id, approval_id, body.decision, body.note)


# --------------------------------------------------------------------------- #
# Risks
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/risks/runway", response_model=Page[RunwayRisksSchema], summary="List runway risks")
async def list_runway_risks(
    moment_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[RunwayRisksSchema]:
    return await BusinessRisksModule(db).list_runway_risks(user_id, moment_id, status=status_filter, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/risks/runway", response_model=RunwayRisksSchema, status_code=status.HTTP_201_CREATED, summary="Record a runway risk")
async def create_runway_risk(
    moment_id: UUID, body: RunwayRiskCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> RunwayRisksSchema:
    return await BusinessRisksModule(db).create_runway_risk(user_id, moment_id, body.model_dump(exclude_none=True))


@router.post("/moments/{moment_id}/risks/runway/{risk_id}/resolve", response_model=RunwayRisksSchema, summary="Resolve a runway risk")
async def resolve_runway_risk(
    moment_id: UUID, risk_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> RunwayRisksSchema:
    return await BusinessRisksModule(db).resolve_runway_risk(user_id, moment_id, risk_id)


@router.get("/moments/{moment_id}/risks/team", response_model=Page[TeamIssueRisksSchema], summary="List team issues/risks")
async def list_team_issues(
    moment_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[TeamIssueRisksSchema]:
    return await BusinessRisksModule(db).list_team_issues(user_id, moment_id, status=status_filter, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/risks/team", response_model=TeamIssueRisksSchema, status_code=status.HTTP_201_CREATED, summary="Record a team issue/risk")
async def create_team_issue(
    moment_id: UUID, body: TeamIssueCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> TeamIssueRisksSchema:
    return await BusinessRisksModule(db).create_team_issue(user_id, moment_id, body.model_dump(exclude_none=True))


@router.post("/moments/{moment_id}/risks/team/{issue_id}/resolve", response_model=TeamIssueRisksSchema, summary="Resolve a team issue/risk")
async def resolve_team_issue(
    moment_id: UUID, issue_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> TeamIssueRisksSchema:
    return await BusinessRisksModule(db).resolve_team_issue(user_id, moment_id, issue_id)


# --------------------------------------------------------------------------- #
# Transactions
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/transactions/spend", response_model=Page[OperationsSpendEntriesSchema], summary="List operations spend entries")
async def list_spend(
    moment_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[OperationsSpendEntriesSchema]:
    return await BusinessTransactionsModule(db).list_spend(user_id, moment_id, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/transactions/spend", response_model=OperationsSpendEntriesSchema, status_code=status.HTTP_201_CREATED, summary="Record a spend entry")
async def create_spend(
    moment_id: UUID, body: SpendCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> OperationsSpendEntriesSchema:
    return await BusinessTransactionsModule(db).create_spend(user_id, moment_id, body.model_dump())


@router.get("/moments/{moment_id}/transactions/inflows", response_model=Page[RunwayCashInflowsSchema], summary="List cash inflows")
async def list_inflows(
    moment_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[RunwayCashInflowsSchema]:
    return await BusinessTransactionsModule(db).list_inflows(user_id, moment_id, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/transactions/inflows", response_model=RunwayCashInflowsSchema, status_code=status.HTTP_201_CREATED, summary="Record a cash inflow")
async def create_inflow(
    moment_id: UUID, body: CashInflowCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> RunwayCashInflowsSchema:
    return await BusinessTransactionsModule(db).create_inflow(user_id, moment_id, body.model_dump())


@router.get("/moments/{moment_id}/transactions/burns", response_model=Page[RunwayExpenseBurnsSchema], summary="List expense burns")
async def list_burns(
    moment_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[RunwayExpenseBurnsSchema]:
    return await BusinessTransactionsModule(db).list_burns(user_id, moment_id, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/transactions/burns", response_model=RunwayExpenseBurnsSchema, status_code=status.HTTP_201_CREATED, summary="Record an expense burn")
async def create_burn(
    moment_id: UUID, body: ExpenseBurnCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> RunwayExpenseBurnsSchema:
    return await BusinessTransactionsModule(db).create_burn(user_id, moment_id, body.model_dump())


# --------------------------------------------------------------------------- #
# Quick add
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/quick-add", response_model=Page[BusinessQuickAddDraftsSchema], summary="List my quick-add drafts")
async def list_quick_add(
    moment_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessQuickAddDraftsSchema]:
    return await BusinessQuickAddModule(db).list_drafts(user_id, moment_id, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/quick-add", response_model=BusinessQuickAddDraftsSchema, status_code=status.HTTP_201_CREATED, summary="Create a quick-add draft")
async def create_quick_add(
    moment_id: UUID, body: QuickAddDraftCreateRequest, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessQuickAddDraftsSchema:
    return await BusinessQuickAddModule(db).create_draft(user_id, moment_id, tab_type=body.tab_type, draft_payload=body.draft_payload)


@router.post("/moments/{moment_id}/quick-add/{draft_id}/submit", response_model=BusinessQuickAddDraftsSchema, summary="Submit a quick-add draft")
async def submit_quick_add(
    moment_id: UUID, draft_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessQuickAddDraftsSchema:
    return await BusinessQuickAddModule(db).submit_draft(user_id, moment_id, draft_id)


@router.post("/moments/{moment_id}/quick-add/{draft_id}/discard", response_model=BusinessQuickAddDraftsSchema, summary="Discard a quick-add draft")
async def discard_quick_add(
    moment_id: UUID, draft_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessQuickAddDraftsSchema:
    return await BusinessQuickAddModule(db).discard_draft(user_id, moment_id, draft_id)


# --------------------------------------------------------------------------- #
# Notifications
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/notifications", response_model=Page[BusinessNotificationsSchema], summary="List my notifications")
async def list_notifications(
    moment_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessNotificationsSchema]:
    return await BusinessNotificationsModule(db).list_notifications(user_id, moment_id, status=status_filter, page=page, per_page=per_page)


@router.post("/moments/{moment_id}/notifications/{notification_id}/read", response_model=BusinessNotificationsSchema, summary="Mark a notification read")
async def mark_notification_read(
    moment_id: UUID, notification_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessNotificationsSchema:
    return await BusinessNotificationsModule(db).mark_read(user_id, moment_id, notification_id)


@router.post("/moments/{moment_id}/notifications/read-all", summary="Mark all my notifications read")
async def mark_all_notifications_read(
    moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> dict[str, int]:
    updated = await BusinessNotificationsModule(db).mark_all_read(user_id, moment_id)
    return {"updated": updated}


# --------------------------------------------------------------------------- #
# Activity feed
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/activity", response_model=Page[BusinessLiveFeedSchema], summary="List the live activity feed")
async def list_activity_feed(
    moment_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessLiveFeedSchema]:
    return await BusinessActivityFeedModule(db).list_feed(user_id, moment_id, page=page, per_page=per_page)


@router.get("/moments/{moment_id}/activity-center", response_model=Page[BusinessActivityCenterItemsSchema], summary="List activity-center items")
async def list_activity_center(
    moment_id: UUID,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[BusinessActivityCenterItemsSchema]:
    return await BusinessActivityFeedModule(db).list_activity_center(user_id, moment_id, page=page, per_page=per_page)


# --------------------------------------------------------------------------- #
# Pulse / analytics / memory
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/pulse", response_model=list[BusinessPulseSnapshotsSchema], summary="Recent pulse snapshots")
async def get_pulse(
    moment_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[BusinessPulseSnapshotsSchema]:
    return await BusinessPulseModule(db).get_pulse(user_id, moment_id, limit=limit)


@router.get("/moments/{moment_id}/analytics", response_model=BusinessAnalyticsResponse, summary="Business analytics rollup")
async def get_analytics(
    moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessAnalyticsResponse:
    return await BusinessAnalyticsModule(db).analytics(user_id, moment_id)


@router.get("/moments/{moment_id}/memory", response_model=BusinessMemoryOverviewResponse, summary="Business memory overview")
async def get_memory(
    moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
) -> BusinessMemoryOverviewResponse:
    return await BusinessMemoryModule(db).memory_overview(user_id, moment_id)
