"""Business module API router (mobile contract).

Router -> :class:`BusinessAppService` -> repositories. Endpoints match the exact
paths, verbs and response shapes the Android (`apk_copy`) and iOS (`ios_copy`)
clients call. Registered *before* the legacy operations-CRUD ``business.router``
in ``main.py`` so overlapping paths (e.g. ``POST /business/moments``) resolve to
these app-contract handlers.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.business import app_schemas as s
from app.domains.business.active_service import BusinessActiveService
from app.domains.business.app_service import BusinessAppService
from app.domains.business.setup import schemas as setup_schemas

router = APIRouter(prefix="/business", tags=["business"])


def _service(db: AsyncSession) -> BusinessAppService:
    return BusinessAppService(db)


# --------------------------------------------------------------------------- #
# Landing surfaces
# --------------------------------------------------------------------------- #
@router.get("/pulse")
async def get_pulse(
    force_refresh: bool = Query(False),
    workspace_id: UUID | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).pulse(user_id, workspace_id=workspace_id)


@router.get("/session/bootstrap")
async def session_bootstrap(
    force_refresh: bool = Query(False),
    workspace_id: UUID | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).session_bootstrap(user_id, workspace_id=workspace_id)


@router.get("/session")
async def get_session(
    workspace_id: UUID | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_session(user_id, workspace_id=workspace_id)


@router.get("/workspaces/{workspace_id}/overview")
async def workspace_overview(
    workspace_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_workspace_overview(user_id, workspace_id)


@router.get("/workspaces/{workspace_id}/moments")
async def workspace_moments(
    workspace_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_workspace_moments(user_id, workspace_id)


@router.get("/moments/home")
async def moments_home(
    workspace_id: UUID | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).moments_home(user_id, workspace_id=workspace_id)


@router.get("/live")
async def get_live(
    workspace_id: UUID | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).live(user_id, workspace_id=workspace_id)


@router.get("/memory")
async def get_memory(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Contribution memory aggregate (Redis SWR) — same contract as business_active."""
    return await BusinessActiveService(db).get_memory(user_id)


@router.get("/create/options")
async def create_options(
    workspace_id: UUID | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_options(user_id, workspace_id=workspace_id)


# --------------------------------------------------------------------------- #
# Company workspaces
# --------------------------------------------------------------------------- #
@router.post("/workspaces", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    body: s.BusinessWorkspaceCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.business.workspace_service import BusinessWorkspaceService

    result = await BusinessWorkspaceService(db).create_workspace(
        user_id,
        name=body.name,
        currency_code=body.currency_code,
        timezone_name=body.timezone,
        industry=body.industry,
        logo_url=body.logo_url,
    )
    await db.commit()
    return result


@router.patch("/workspaces/{workspace_id}")
async def update_workspace(
    workspace_id: UUID,
    body: s.BusinessWorkspaceUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.business.workspace_service import BusinessWorkspaceService

    result = await BusinessWorkspaceService(db).update_workspace(
        user_id,
        workspace_id,
        name=body.name,
        logo_url=body.logo_url,
        industry=body.industry,
        currency_code=body.currency_code,
        timezone_name=body.timezone,
        status=body.status,
    )
    await db.commit()
    return result


@router.post("/workspaces/select")
async def select_workspace(
    body: s.BusinessWorkspaceSelectRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.business.workspace_service import BusinessWorkspaceService

    result = await BusinessWorkspaceService(db).select_workspace(
        user_id, UUID(body.workspace_id)
    )
    await db.commit()
    return result


@router.get("/workspaces/{workspace_id}/members")
async def list_workspace_members(
    workspace_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.business.workspace_service import BusinessWorkspaceService

    members = await BusinessWorkspaceService(db).list_members(user_id, workspace_id)
    return {"members": members}


@router.post("/workspaces/{workspace_id}/invites", status_code=status.HTTP_201_CREATED)
async def invite_workspace_member(
    workspace_id: UUID,
    body: s.BusinessWorkspaceInviteRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.business.workspace_service import BusinessWorkspaceService
    from app.domains.invites.platform_service import (
        PlatformInviteService,
        opaque_creates_enabled,
    )

    # Prefer opaque company invites when enabled; keep email-bound legacy path as dual-write.
    if opaque_creates_enabled():
        opaque = await PlatformInviteService(db).create_company_invite(
            user_id,
            workspace_id,
            role_code=body.role,
            max_uses=1,
        )
        await db.commit()
        return {
            "invitation_id": opaque["invite_id"],
            "workspace_id": str(workspace_id),
            "invitee_email": body.email,
            "role": (body.role or "MEMBER").upper(),
            "token": opaque["code"],
            "invite_link": opaque["invite_url"],
            "qr_payload": opaque["qr_payload"],
            "status": "PENDING",
            "code": opaque["code"],
            "expires_at": opaque["expires_at"],
            "max_uses": opaque["max_uses"],
        }

    result = await BusinessWorkspaceService(db).invite_member(
        user_id, workspace_id, email=body.email, role=body.role
    )
    await db.commit()
    return result


@router.post(
    "/workspaces/{workspace_id}/invites/opaque",
    status_code=status.HTTP_201_CREATED,
)
async def create_opaque_company_invite(
    workspace_id: UUID,
    body: dict = Body(default_factory=dict),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.invites.platform_service import PlatformInviteService

    result = await PlatformInviteService(db).create_company_invite(
        user_id,
        workspace_id,
        role_code=str(body.get("role_code") or "MEMBER"),
        expires_in_days=body.get("expires_in_days"),
        max_uses=int(body.get("max_uses") or 1),
    )
    await db.commit()
    return result


@router.get("/workspaces/{workspace_id}/invites")
async def list_workspace_invites(
    workspace_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.invites.platform_service import PlatformInviteService

    items = await PlatformInviteService(db).list_workspace_invites(user_id, workspace_id)
    return {"invites": items}


@router.get("/company-invites/{code}")
async def preview_company_invite(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Public preview — no auth required."""
    from app.domains.invites.platform_service import PlatformInviteService

    return await PlatformInviteService(db).preview(code)


@router.post("/company-invites/{code}/accept")
async def accept_company_invite_opaque(
    code: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.invites.platform_service import PlatformInviteService

    result = await PlatformInviteService(db).accept(user_id, code)
    await db.commit()
    return result


@router.post("/company-invites/{code}/decline")
async def decline_company_invite_opaque(
    code: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.invites.platform_service import PlatformInviteService

    result = await PlatformInviteService(db).decline(user_id, code)
    await db.commit()
    return result


@router.post("/company-invites/by-id/{invite_id}/revoke")
async def revoke_company_invite_opaque(
    invite_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.invites.platform_service import PlatformInviteService

    result = await PlatformInviteService(db).revoke(user_id, invite_id)
    await db.commit()
    return result


@router.post("/workspaces/invites/accept")
async def accept_workspace_invite(
    body: s.BusinessWorkspaceAcceptInviteRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.domains.business.workspace_service import BusinessWorkspaceService
    from app.domains.invites import codes as invite_codes
    from app.domains.invites.platform_service import (
        PlatformInviteService,
        legacy_workspace_token_accept_enabled,
    )

    token = (body.token or "").strip()
    if invite_codes.is_opaque_code_shape(token):
        result = await PlatformInviteService(db).accept(user_id, token)
        await db.commit()
        return result

    if not legacy_workspace_token_accept_enabled():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Invitation not found or already used.")

    result = await BusinessWorkspaceService(db).accept_invite(user_id, body.token)
    await db.commit()
    return result


# --------------------------------------------------------------------------- #
# Moment create / setup / manage / cover
# --------------------------------------------------------------------------- #
@router.post("/moments", status_code=status.HTTP_201_CREATED)
async def create_moment(
    body: s.BusinessMomentCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    ws_id = UUID(body.workspace_id) if body.workspace_id else None
    return await _service(db).create_moment(
        user_id,
        body.moment_type_code,
        body.moment_name,
        title=body.title,
        template_id=body.template_id,
        template_version=body.template_version,
        workspace_id=ws_id,
    )


@router.get("/moments/{moment_id}/setup")
async def get_setup(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_setup_state(user_id, moment_id)


@router.put("/moments/{moment_id}/setup/draft")
async def save_setup_draft(
    moment_id: UUID,
    body: setup_schemas.SetupDraftSaveRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).save_setup_draft(
        user_id,
        moment_id,
        body.model_dump(mode="json"),
    )


@router.post("/moments/{moment_id}/setup/preview")
async def preview_setup(
    moment_id: UUID,
    body: setup_schemas.SetupPreviewRequest | None = Body(default=None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    payload = body.model_dump(mode="json") if body is not None else {}
    return await _service(db).preview_setup(user_id, moment_id, payload)


@router.post("/moments/{moment_id}/setup/activate")
async def activate_setup(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).activate_setup(user_id, moment_id)


@router.post("/moments/{moment_id}/setup/invites/draft")
async def setup_invite_draft(
    moment_id: UUID,
    body: setup_schemas.BusinessSetupInviteDraftRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_invite_draft(
        user_id,
        moment_id,
        local_id=body.local_id,
        channel=body.channel,
        role=body.role,
    )


@router.post("/moments/{moment_id}/cover/upload-url")
async def cover_upload_url(
    moment_id: UUID,
    body: s.BusinessImageUploadUrlRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).cover_upload_url(user_id, moment_id, body.content_type)


@router.patch("/moments/{moment_id}/cover")
async def cover_confirm(
    moment_id: UUID,
    body: s.BusinessImageConfirmRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).cover_confirm(user_id, moment_id, body.storage_path)


@router.patch("/moments/{moment_id}")
async def patch_moment(
    moment_id: UUID,
    body: s.BusinessMomentUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).patch_moment(user_id, moment_id, body)


@router.post("/moments/{moment_id}/complete")
async def complete_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).complete_moment(user_id, moment_id)


@router.post("/moments/{moment_id}/archive")
async def archive_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).archive_moment(user_id, moment_id)


@router.post("/moments/{moment_id}/leave")
async def leave_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Member exits a Business moment (owner must archive or delete)."""
    return await _service(db).leave_moment(user_id, moment_id)
