from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.storage import build_storage_path, build_upload_url, public_url_for
from app.dependencies.auth import get_current_user
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
