"""Group module API router (mobile contract).

Router -> :class:`GroupAppService` -> repositories. Endpoints match the exact
paths, verbs and response shapes the Android (`apk_copy`) and iOS (`ios_copy`)
clients call. Where the two apps use different paths for the same action, both
are registered against one handler (setup people/review/activate).

Registered *before* the legacy membership-CRUD ``group.router`` in
``main.py`` so overlapping paths (e.g. ``POST /group/moments``) resolve to these
app-contract handlers.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.group import app_schemas as s
from app.domains.group.app_service import GroupAppService

router = APIRouter(prefix="/group", tags=["group"])


def _service(db: AsyncSession) -> GroupAppService:
    return GroupAppService(db)


# --------------------------------------------------------------------------- #
# Landing surfaces
# --------------------------------------------------------------------------- #
@router.get("/pulse")
async def get_pulse(
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).pulse(user_id)


@router.get("/session")
async def get_session(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_session(user_id)


@router.get("/inventory")
async def get_inventory(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_inventory(user_id)


@router.get("/session/bootstrap")
async def session_bootstrap(
    focus_moment_id: str | None = Query(None),
    include_focus_pulse: bool = Query(False),
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).session_bootstrap(user_id)


@router.get("/moments/home")
async def moments_home(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).moments_home(user_id)


@router.get("/live")
async def get_live(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).live_empty(user_id)


@router.get("/memory")
async def get_memory(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).memory(user_id)


@router.get("/create/options")
async def create_options(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_options(user_id)


@router.get("/life")
async def get_life(
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).life(user_id)


@router.get("/activity")
async def life_activity(
    moment_id: str | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).life_activity(user_id, moment_id)


@router.get("/moment-templates")
async def list_templates(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _service(db).list_templates()


# --------------------------------------------------------------------------- #
# Moment create / manage
# --------------------------------------------------------------------------- #
@router.post("/moments", status_code=status.HTTP_201_CREATED)
async def create_moment(
    body: s.GroupMomentCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_moment(user_id, body.moment_type_code, body.moment_name)


@router.patch("/moments/{moment_id}")
async def patch_moment(
    moment_id: UUID,
    body: s.GroupMomentUpdateRequest,
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
    """Complete an app Group moment (shared moments table). Shadows legacy group_moments route."""
    return await _service(db).complete_moment(user_id, moment_id)


@router.post("/moments/{moment_id}/archive")
async def archive_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Archive an app Group moment. Shadows legacy group_moments route."""
    return await _service(db).archive_moment(user_id, moment_id)


@router.post("/moments/{moment_id}/delete")
async def delete_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Permanently delete a Group moment (ops purged, analytics retained)."""
    return await _service(db).delete_moment(user_id, moment_id)


@router.post("/moments/{moment_id}/leave")
async def leave_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Member exits a Group moment (owner must archive or delete)."""
    return await _service(db).leave_moment(user_id, moment_id)


# --------------------------------------------------------------------------- #
# Setup flow (both app path variants)
# --------------------------------------------------------------------------- #
@router.get("/setup/{moment_type}/profiles")
async def setup_profiles(
    moment_type: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _service(db).setup_profiles(moment_type)


@router.post("/setup/{moment_type}/basics")
async def setup_basics(
    moment_type: str,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_basics(user_id, moment_type, body)


# Android: moment id is part of the path
@router.post("/setup/{moment_type}/moments/{moment_id}/people")
async def setup_people_android(
    moment_type: str,
    moment_id: UUID,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_people(user_id, moment_type, moment_id, body)


# iOS: no moment id — resolve the caller's latest draft of this type
@router.post("/setup/{moment_type}/people")
async def setup_people_ios(
    moment_type: str,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_people(user_id, moment_type, None, body)


@router.get("/setup/moments/{moment_id}/review")
async def setup_review_android(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_review(user_id, moment_id)


@router.get("/setup/review/{moment_id}")
async def setup_review_ios(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_review(user_id, moment_id)


@router.post("/setup/moments/{moment_id}/activate")
async def setup_activate_android(
    moment_id: UUID,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_activate(user_id, moment_id)


@router.post("/setup/activate/{moment_id}")
async def setup_activate_ios(
    moment_id: UUID,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_activate(user_id, moment_id)


# --------------------------------------------------------------------------- #
# iOS active surface
# --------------------------------------------------------------------------- #
@router.get("/active/pulse/{moment_id}")
async def active_pulse(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).active_pulse(
        user_id, moment_id, force_refresh=force_refresh
    )


@router.get("/active/moments/{moment_id}")
async def active_moments(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).active_moments(
        user_id, moment_id, force_refresh=force_refresh
    )


@router.get("/active/memory/{moment_id}")
async def active_memory(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).active_memory(
        user_id, moment_id, force_refresh=force_refresh
    )


@router.get("/active/life")
async def active_life(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).active_life(user_id)


@router.get("/quickadd/{moment_id}")
async def quick_add_config(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).quick_add_config(user_id, moment_id)
