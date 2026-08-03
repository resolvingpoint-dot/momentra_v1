from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.storage import build_storage_path, build_upload_url, public_url_for
from app.dependencies.auth import get_current_user
from app.domains.personal.preferences_service import PersonalPreferencesService
from app.domains.personal.schemas import (
    PersonalUserPreferencesSchema,
    PersonalUserPreferencesUpdateSchema,
)
from app.domains.users.account_service import AccountDeletionService
from app.domains.users.schemas import (
    ImageConfirmRequest,
    ImageUploadUrlRequest,
    ImageUploadUrlResponse,
    UserProfileUpdateRequest,
    UserResponse,
)
from app.domains.users.service import UserService

router = APIRouter(prefix="/me", tags=["me"])


async def _require_user(auth_user: dict, db: AsyncSession):
    user = await UserService(db).get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if getattr(user, "deleted_at", None) is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account has been deleted"
        )
    return user


@router.get("")
async def get_me(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _require_user(auth_user, db)
    return UserResponse.model_validate(user).model_dump(mode="json")


@router.patch("")
async def update_me(
    body: UserProfileUpdateRequest,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _require_user(auth_user, db)
    service = UserService(db)
    updated = await service.update_profile(user, display_name=body.display_name)
    return UserResponse.model_validate(updated).model_dump(mode="json")


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    user = await _require_user(auth_user, db)
    await AccountDeletionService(db).soft_delete(user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/preferences")
async def get_me_preferences(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _require_user(auth_user, db)
    from app.domains.preferences.service import UserPreferenceService

    app_pref = await UserPreferenceService(db).get_or_create(user.id)
    service = PersonalPreferencesService(db)
    pref = await service.get_or_create(
        user.id,
        default_currency_code=app_pref.default_currency_code,
        timezone_name=app_pref.timezone,
    )
    await db.commit()
    return PersonalUserPreferencesSchema.model_validate(pref).model_dump(mode="json")


@router.patch("/preferences")
async def update_me_preferences(
    body: PersonalUserPreferencesUpdateSchema,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _require_user(auth_user, db)
    service = PersonalPreferencesService(db)
    try:
        pref = await service.update(user.id, body)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    await db.commit()

    from app.domains.app_bootstrap.service import AppBootstrapService

    await AppBootstrapService(db).invalidate_cache(user.id)
    return PersonalUserPreferencesSchema.model_validate(pref).model_dump(mode="json")


@router.post("/avatar/upload-url")
async def avatar_upload_url(
    body: ImageUploadUrlRequest,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.core.storage import assert_attachment_upload

    user = await _require_user(auth_user, db)
    try:
        assert_attachment_upload(
            content_type=body.content_type,
            byte_size=body.byte_size,
            purpose="avatar",
        )
        storage_path = build_storage_path(f"avatars/{user.id}", body.content_type)
        upload_url = build_upload_url(storage_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return ImageUploadUrlResponse(
        upload_url=upload_url,
        storage_path=storage_path,
        token=None,
    ).model_dump(mode="json")


@router.patch("/avatar")
async def confirm_avatar(
    body: ImageConfirmRequest,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.core.storage import assert_storage_path_under

    user = await _require_user(auth_user, db)
    try:
        path = assert_storage_path_under(body.storage_path, f"avatars/{user.id}")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    service = UserService(db)
    updated = await service.update_profile(
        user, photo_url=public_url_for(path)
    )
    return UserResponse.model_validate(updated).model_dump(mode="json")


@router.post("/device-tokens")
async def register_device_token(
    body: dict[str, Any],
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Register or refresh an FCM token for push notifications."""
    from datetime import datetime, timezone

    from sqlalchemy import select

    from app.domains.users.models import UserDeviceToken

    user = await _require_user(auth_user, db)
    token = str(body.get("fcm_token") or body.get("token") or "").strip()
    platform = str(body.get("platform") or "android").strip().lower()
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="fcm_token required")
    if platform not in {"android", "ios", "web"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid platform")

    result = await db.execute(
        select(UserDeviceToken).where(
            UserDeviceToken.user_id == user.id,
            UserDeviceToken.fcm_token == token,
        )
    )
    row = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if row is None:
        row = UserDeviceToken(
            user_id=user.id,
            platform=platform,
            fcm_token=token,
            app_version=str(body.get("app_version") or "") or None,
            last_seen_at=now,
        )
        db.add(row)
    else:
        row.platform = platform
        row.app_version = str(body.get("app_version") or "") or row.app_version
        row.last_seen_at = now
        row.updated_at = now
    await db.commit()
    return {"ok": True, "platform": platform}


@router.delete("/device-tokens")
async def unregister_device_token(
    body: dict[str, Any],
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from sqlalchemy import delete

    from app.domains.users.models import UserDeviceToken

    user = await _require_user(auth_user, db)
    token = str(body.get("fcm_token") or body.get("token") or "").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="fcm_token required")
    await db.execute(
        delete(UserDeviceToken).where(
            UserDeviceToken.user_id == user.id,
            UserDeviceToken.fcm_token == token,
        )
    )
    await db.commit()
    return {"ok": True}
