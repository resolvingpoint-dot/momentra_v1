"""Schemas for opaque platform invites."""
from __future__ import annotations

from pydantic import BaseModel, Field


class OpaqueCompanyInviteCreateRequest(BaseModel):
    role_code: str = "MEMBER"
    expires_in_days: int | None = None
    max_uses: int = 1


class OpaqueCompanyInviteCreateResponse(BaseModel):
    invite_id: str
    code: str
    invite_url: str
    expires_at: str
    role_code: str
    max_uses: int
    qr_payload: str | None = None


class CompanyInvitePreviewResponse(BaseModel):
    invite_type: str = "COMPANY"
    company: dict
    inviter: dict
    role: dict
    expires_at: str | None = None
    status: str
    requires_authentication: bool = True
    result_code: str | None = None


class CompanyInviteAcceptResponse(BaseModel):
    result: str
    workspace_id: str | None = None
    company_id: str | None = None
    membership: dict | None = None
    selected_workspace: dict | None = None
    selected_company: dict | None = None
    session: dict | None = None


class PlatformInviteListItem(BaseModel):
    invite_id: str
    code_suffix: str
    invite_type: str
    role_code: str | None = None
    status: str
    created_at: str
    expires_at: str
    max_uses: int
    use_count: int
    invite_url: str | None = None


class OpaqueGroupInviteCreateRequest(BaseModel):
    expires_in_days: int | None = None
    max_uses: int = 50
    role_code: str = "PARTICIPANT"
    metadata: dict = Field(default_factory=dict)
