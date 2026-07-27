"""Personal module API router (mobile contract).

Router -> :class:`PersonalAppService` -> repositories. Endpoints match the exact
paths, verbs and response shapes the Android (`apk_copy`) and iOS (`ios_copy`)
clients call. Where the two apps use different paths for the same action, both
are registered against one handler (see quick-add and life-activity aliases).

Static sub-paths (``/moments/home`` etc.) are declared before the
``/moments/{moment_id}`` routes so they are not captured by the UUID converter.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.personal import app_schemas as s
from app.domains.personal.app_service import PersonalAppService
from app.domains.personal.template_projection_service import TemplateProjectionService

router = APIRouter(prefix="/personal", tags=["personal"])


def _service(db: AsyncSession) -> PersonalAppService:
    return PersonalAppService(db)


def _templates(db: AsyncSession) -> TemplateProjectionService:
    return TemplateProjectionService(db)


# --------------------------------------------------------------------------- #
# Pulse / session bootstrap
# --------------------------------------------------------------------------- #
@router.get("/pulse")
async def get_pulse(
    moment_type_code: str | None = Query(None),
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return (await _service(db).pulse(
        user_id, force_refresh=force_refresh, moment_type_code=moment_type_code
    )).model_dump(mode="json")


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
    moment_type_code: str | None = Query(None),
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).session_bootstrap(
        user_id, force_refresh=force_refresh, moment_type_code=moment_type_code
    )


# --------------------------------------------------------------------------- #
# Moment types / home / create options
# --------------------------------------------------------------------------- #
@router.get("/moment-types")
async def list_moment_types(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _service(db).list_moment_types()


@router.get("/moments/home")
async def moments_home(
    moment_type_code: str | None = Query(None),
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return (
        await _service(db).moments_home(
            user_id, force_refresh=force_refresh, moment_type_code=moment_type_code
        )
    ).model_dump(mode="json")


@router.get("/create/options")
async def create_options(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_options(user_id)


# --------------------------------------------------------------------------- #
# Template tab projections (reference vertical pattern)
# --------------------------------------------------------------------------- #
@router.get("/templates/{moment_type}/moments")
async def template_moments(
    moment_type: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _templates(db).moments(user_id, moment_type)


@router.get("/templates/{moment_type}/moments/{moment_id}")
async def template_moment_detail(
    moment_type: str,
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _templates(db).moment_detail(user_id, moment_type, moment_id)


@router.patch("/templates/{moment_type}/moments/{moment_id}")
async def template_moment_patch(
    moment_type: str,
    moment_id: UUID,
    body: s.PersonalMomentUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _templates(db).patch_moment(user_id, moment_type, moment_id, body)


@router.post("/templates/{moment_type}/moments/{moment_id}/archive")
async def template_moment_archive(
    moment_type: str,
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _templates(db).archive_moment(user_id, moment_type, moment_id)


@router.post("/templates/{moment_type}/moments/{moment_id}/complete")
async def template_moment_complete(
    moment_type: str,
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _templates(db).complete_moment(user_id, moment_type, moment_id)


@router.get("/templates/{moment_type}/pulse")
async def template_pulse(
    moment_type: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _templates(db).pulse(user_id, moment_type)


@router.get("/templates/{moment_type}/life")
async def template_life(
    moment_type: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _templates(db).life(user_id, moment_type)


@router.get("/templates/{moment_type}/memory")
async def template_memory(
    moment_type: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _templates(db).memory(user_id, moment_type)


@router.get("/templates/{moment_type}/activity")
async def template_activity_list(
    moment_type: str,
    moment_id: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).template_activity_list(
        user_id,
        moment_type,
        moment_id=moment_id,
        cursor=cursor,
        limit=limit,
    )


@router.get("/templates/{moment_type}/activity/{event_id}")
async def template_activity_get(
    moment_type: str,
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).template_activity_get(
        user_id, moment_type, event_id
    )


@router.patch("/templates/{moment_type}/activity/{event_id}")
async def template_activity_patch(
    moment_type: str,
    event_id: str,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).template_activity_patch(
        user_id, moment_type, event_id, body
    )


@router.delete(
    "/templates/{moment_type}/activity/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def template_activity_delete(
    moment_type: str,
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    await _service(db).template_activity_delete(user_id, moment_type, event_id)


# --------------------------------------------------------------------------- #
# Life / memory (legacy stubs)
# --------------------------------------------------------------------------- #
@router.get("/life/activity")
@router.get("/life-operations/activity")
async def life_activity(
    moment_id: str | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).life_activity(user_id, moment_id)


@router.get("/life")
async def get_life(
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).life(user_id, force_refresh=force_refresh)


@router.get("/memory/summary")
async def memory_summary(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).memory_summary(user_id)


@router.get("/memory")
async def get_memory(
    moment_type_code: str | None = Query(None),
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).memory(
        user_id, force_refresh=force_refresh, moment_type_code=moment_type_code
    )


# --------------------------------------------------------------------------- #
# Live capture surface
# --------------------------------------------------------------------------- #
@router.get("/live/quick-add/options")
async def quick_add_options(
    moment_id: str | None = Query(None),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).quick_add_options(user_id, moment_id=moment_id)


@router.get("/live/quick-add/events/{event_id}")
async def quick_add_event_detail_alias(
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).quick_add_detail(user_id, event_id)


@router.patch("/live/quick-add/events/{event_id}")
async def quick_add_event_patch_alias(
    event_id: str,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).quick_add_patch(user_id, event_id, body)


@router.get("/live/quick-add/{event_id}")
async def quick_add_event_detail(
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).quick_add_detail(user_id, event_id)


@router.patch("/live/quick-add/{event_id}")
async def quick_add_event_patch(
    event_id: str,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).quick_add_patch(user_id, event_id, body)


@router.delete("/live/quick-add/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def quick_add_event_delete(
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    await _service(db).quick_add_delete(user_id, event_id)


@router.post("/live/quick-add", status_code=status.HTTP_201_CREATED)
async def quick_add_submit(
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).quick_add_submit(user_id, body)


@router.get("/live")
async def get_live(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).live(user_id)


# --------------------------------------------------------------------------- #
# Accounts
# --------------------------------------------------------------------------- #
@router.get("/accounts")
async def list_accounts(
    include_archived: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _service(db).list_accounts(user_id, include_archived=include_archived)


@router.get("/accounts/{account_id}")
async def get_account(
    account_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_account(user_id, account_id)


@router.post("/accounts", status_code=status.HTTP_201_CREATED)
async def create_account(
    body: s.PersonalAccountCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_account(user_id, body)


@router.patch("/accounts/{account_id}")
async def patch_account(
    account_id: UUID,
    body: s.PersonalAccountPatchRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).patch_account(user_id, account_id, body)


@router.post("/accounts/{account_id}/archive")
async def archive_account(
    account_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).archive_account(user_id, account_id)


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    await _service(db).delete_account(user_id, account_id)
    return None


# --------------------------------------------------------------------------- #
# Master expense
# --------------------------------------------------------------------------- #
@router.get("/master-expense/options")
async def master_expense_options(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).master_expense_options(user_id)


@router.post("/master-expense", status_code=status.HTTP_201_CREATED)
async def master_expense_submit(
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).master_expense_submit(user_id, body)


# --------------------------------------------------------------------------- #
# Moments CRUD  (static sub-paths above already registered)
# --------------------------------------------------------------------------- #
@router.get("/moments")
async def list_moments(
    status_filter: str | None = Query(None, alias="status"),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _service(db).list_moments(user_id, status_filter=status_filter)


@router.post("/moments", status_code=status.HTTP_201_CREATED)
async def create_moment(
    body: s.PersonalMomentCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_moment(
        user_id, body.moment_type_code, body.moment_name
    )


@router.post("/moments/{moment_id}/cover/upload-url")
async def moment_cover_upload_url(
    moment_id: UUID,
    body: s.PersonalImageUploadUrlRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).cover_upload_url(user_id, moment_id, body.content_type)


@router.patch("/moments/{moment_id}/cover")
async def moment_cover_confirm(
    moment_id: UUID,
    body: s.PersonalImageConfirmRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    return await _service(db).cover_confirm(user_id, moment_id, body.storage_path)


@router.put("/moments/{moment_id}/setup/draft")
async def moment_setup_draft(
    moment_id: UUID,
    body: s.PersonalSetupSubmitRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_draft(user_id, moment_id, body.answers)


@router.post("/moments/{moment_id}/setup/preview")
async def moment_setup_preview(
    moment_id: UUID,
    body: s.PersonalSetupSubmitRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_preview(user_id, moment_id, body.answers)


@router.get("/moments/{moment_id}/setup")
async def moment_setup_get(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_get(user_id, moment_id)


@router.post("/moments/{moment_id}/setup")
async def moment_setup_commit(
    moment_id: UUID,
    body: s.PersonalSetupSubmitRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).setup_commit(user_id, moment_id, body.answers)


@router.get("/moments/{moment_id}")
async def get_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_moment(user_id, moment_id)


@router.patch("/moments/{moment_id}")
async def patch_moment(
    moment_id: UUID,
    body: s.PersonalMomentUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).patch_moment(user_id, moment_id, body)
