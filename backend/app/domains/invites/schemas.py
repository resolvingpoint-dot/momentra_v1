"""Invite contract schemas (mobile).

Mirror the Android DTOs: ``EmailInviteCreateDto`` / ``EmailInviteResponseDto`` /
``ShareInviteResponseDto`` / ``InviteAcceptResponseDto``. Field names are
snake_case to match the clients' ``@SerialName`` mappings.
"""
from __future__ import annotations

from pydantic import BaseModel


class EmailInviteCreateRequest(BaseModel):
    email: str
    participant_id: str | None = None
    channel: str | None = "email"


class EmailInviteResponse(BaseModel):
    id: str
    moment_id: str
    invitee_email: str
    status: str = "pending"
    expires_at: str
    created_at: str
    sent: bool = False
    invite_link: str | None = None
    email_subject: str | None = None
    email_body: str | None = None
    send_error: str | None = None


class ShareInviteResponse(BaseModel):
    invite_url: str
    trip_name: str
    expires_at: str
    share_message: str | None = None


class InviteDraftResponse(BaseModel):
    invite_link: str
    invite_code: str
    qr_payload: str
    email_subject: str
    email_body: str
    whatsapp_text: str
    sms_text: str
    experience_name: str | None = None
    expires_at: str | None = None
    invite_id: str | None = None
    participant_id: str | None = None
    status: str | None = None


class InviteRefreshRequest(BaseModel):
    participant_id: str | None = None


class InviteChannelRequest(BaseModel):
    channel: str
    participant_id: str | None = None
    invite_id: str | None = None


class InviteAcceptResponse(BaseModel):
    moment_id: str
    moment_name: str
    moment_type: str | None = None
    already_member: bool = False
    participant_id: str | None = None
