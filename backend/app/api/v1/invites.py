"""Invite endpoints (mobile contract).

Cross-cutting invite surface:

- ``POST /moments/{moment_id}/email-invites``  -> create an email invite
- ``GET  /moments/{moment_id}/email-invites``  -> list invites
- ``GET  /moments/{moment_id}/share-invite``   -> shareable link
- ``GET  /moments/{moment_id}/invite-draft``   -> copy-ready draft (+ optional participant)
- ``POST /moments/{moment_id}/invite-draft/refresh`` -> revoke + remint
- ``POST /moments/{moment_id}/invite-channel`` -> record share channel
- ``POST /invites/{token}/accept``             -> accept a signed invite token
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.invites import schemas as s
from app.domains.invites.service import InviteService

router = APIRouter(tags=["invites"])


def _service(db: AsyncSession) -> InviteService:
    return InviteService(db)


@router.post("/moments/{moment_id}/email-invites", status_code=status.HTTP_201_CREATED)
async def create_email_invite(
    moment_id: UUID,
    body: s.EmailInviteCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_email_invite(
        user_id,
        moment_id,
        body.email,
        participant_id=body.participant_id,
    )


@router.get("/moments/{moment_id}/email-invites")
async def list_email_invites(
    moment_id: UUID,
    status: str = Query("pending"),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _service(db).list_email_invites(user_id, moment_id, status)


@router.get("/moments/{moment_id}/share-invite")
async def get_share_invite(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).share_invite(user_id, moment_id)


@router.get("/moments/{moment_id}/invite-draft")
async def get_invite_draft(
    moment_id: UUID,
    participant_id: str | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).invite_draft(
        user_id, moment_id, participant_id=participant_id
    )


@router.post("/moments/{moment_id}/invite-draft/refresh")
async def refresh_invite_draft(
    moment_id: UUID,
    body: s.InviteRefreshRequest | None = None,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    participant_id = body.participant_id if body else None
    return await _service(db).refresh_invite_draft(
        user_id, moment_id, participant_id=participant_id
    )


@router.post("/moments/{moment_id}/invite-channel")
async def record_invite_channel(
    moment_id: UUID,
    body: s.InviteChannelRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).record_channel(
        user_id,
        moment_id,
        channel=body.channel,
        participant_id=body.participant_id,
        invite_id=body.invite_id,
    )


@router.post("/invites/{token}/accept")
async def accept_invite(
    token: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).accept(user_id, token)
