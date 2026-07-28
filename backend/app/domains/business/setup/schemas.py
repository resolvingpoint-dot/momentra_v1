"""Business setup schemas (shared setup engine)."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SetupProgress(BaseModel):
    current_step: int = 1
    completed_steps: list[int] = Field(default_factory=list)


class MemberDraft(BaseModel):
    """Canonical Team Operations member draft (answers.members[])."""

    local_id: str
    user_id: str | None = None
    name: str = ""
    email: str | None = None
    phone: str | None = None
    role: str = "MEMBER"
    permission_profile: str = "TEAM_MEMBER_V1"
    permission_version: int = 1
    invite_method: str = "EMAIL"
    invite_status: str = "DRAFT"
    is_approver: bool = False
    is_budget_owner: bool = False


class MembershipRecord(BaseModel):
    user_id: str
    role: str = "OWNER"
    status: str = "ACTIVE"
    invitation_status: str = "ACCEPTED"


class BusinessMomentCreateRequest(BaseModel):
    moment_type_code: str
    moment_name: str | None = None
    title: str | None = None
    template_id: str | None = None
    template_version: str | int | None = "1"


class SetupDraftSaveRequest(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)
    progress: SetupProgress | None = None
    template_id: str | None = None
    template_version: str | int | None = None
    setup_version: str | int | None = None


class SetupPreviewRequest(BaseModel):
    answers: dict[str, Any] | None = None
    template_id: str | None = None
    template_version: str | int | None = None
    setup_version: str | int | None = None


class SetupSummaryBlock(BaseModel):
    block_id: str
    title: str
    body: str | None = None
    items: list[dict[str, Any]] = Field(default_factory=list)


class SetupPreviewResponse(BaseModel):
    template_id: str | None = None
    moment_type_code: str | None = None
    summary_blocks: list[SetupSummaryBlock] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_errors: list[str] = Field(default_factory=list)
    activation_ready: bool = False
    derived_preview: dict[str, Any] | None = None


class SetupStateResponse(BaseModel):
    moment_id: str
    moment_type_code: str
    status: str
    template_id: str
    template_version: str = "1"
    setup_version: str = "1"
    answers: dict[str, Any] = Field(default_factory=dict)
    progress: SetupProgress = Field(default_factory=SetupProgress)
    preview: SetupPreviewResponse | None = None
    membership: list[MembershipRecord] = Field(default_factory=list)
    updated_at: str | None = None


class ActivateResponse(BaseModel):
    moment_id: str
    moment_type_code: str
    status: str = "ACTIVE"
    activated_at: str | None = None
    membership: list[MembershipRecord] = Field(default_factory=list)
    projection_status: str = "REFRESHING"


class BusinessSetupInviteDraftRequest(BaseModel):
    local_id: str
    channel: str = "EMAIL"


class BusinessSetupInviteDraftResponse(BaseModel):
    invite_id: str
    local_id: str
    channel: str
    invite_link: str
    invite_code: str
    qr_payload: str
    email_subject: str | None = None
    email_body: str | None = None
    whatsapp_text: str | None = None
    sms_text: str | None = None
    expires_at: str | None = None
