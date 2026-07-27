from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.pagination import PageParams
from app.dependencies.auth import get_current_user
from app.domains.moments.schemas import (
    MomentCreateSchema,
    MomentSchema,
    MomentUpdateSchema,
)
from app.domains.moments.service import MomentService
from app.domains.users.service import UserService

router = APIRouter(prefix="/moments", tags=["moments"])


async def _resolve_user(db: AsyncSession, auth_user: dict[str, Any]):
    user = await UserService(db).get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("")
async def create_moment(
    body: MomentCreateSchema,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _resolve_user(db, auth_user)
    moment = await MomentService(db).create_moment(
        user_id=user.id,
        context_type=body.context_type,
        moment_type=body.moment_type,
        title=body.title,
        description=body.description,
    )
    return MomentSchema.model_validate(moment).model_dump(mode="json")


@router.get("/home")
async def moments_home(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _resolve_user(db, auth_user)
    params = PageParams(page=page, per_page=per_page)
    result = await MomentService(db).home_paginated(user.id, params)
    return result.model_dump(mode="json")


@router.get("/{moment_id}")
async def get_moment(
    moment_id: UUID,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _resolve_user(db, auth_user)
    moment = await MomentService(db).get_moment(user.id, moment_id)
    if moment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
        )
    return MomentSchema.model_validate(moment).model_dump(mode="json")


@router.patch("/{moment_id}")
async def update_moment(
    moment_id: UUID,
    body: MomentUpdateSchema,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _resolve_user(db, auth_user)
    moment = await MomentService(db).update_moment(
        user.id,
        moment_id,
        title=body.title,
        description=body.description,
        moment_type=body.moment_type,
    )
    return MomentSchema.model_validate(moment).model_dump(mode="json")


@router.delete("/{moment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_moment(
    moment_id: UUID,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    user = await _resolve_user(db, auth_user)
    await MomentService(db).delete_moment(user.id, moment_id)


@router.post("/{moment_id}/activate")
async def activate_moment(
    moment_id: UUID,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _resolve_user(db, auth_user)
    moment = await MomentService(db).activate_moment(user.id, moment_id)
    return MomentSchema.model_validate(moment).model_dump(mode="json")


@router.post("/{moment_id}/complete")
async def complete_moment(
    moment_id: UUID,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _resolve_user(db, auth_user)
    moment = await MomentService(db).complete_moment(user.id, moment_id)
    return MomentSchema.model_validate(moment).model_dump(mode="json")


@router.post("/{moment_id}/archive")
async def archive_moment(
    moment_id: UUID,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await _resolve_user(db, auth_user)
    moment = await MomentService(db).archive_moment(user.id, moment_id)
    return MomentSchema.model_validate(moment).model_dump(mode="json")
