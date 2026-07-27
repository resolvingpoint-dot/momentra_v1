from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    firebase_uid: str
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    photo_url: str | None = None
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime


class UserResponse(BaseModel):
    """Public user shape consumed by the mobile clients (``UserResponse``)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str | None = None
    display_name: str | None = None
    photo_url: str | None = None
    is_active: bool = True
    created_at: datetime


class TokenResponse(BaseModel):
    """Access/refresh token pair (``TokenResponse``)."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class FirebaseExchangeRequest(BaseModel):
    id_token: str | None = None
    device_info: str | None = None


class FirebaseExchangeResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserProfileUpdateRequest(BaseModel):
    display_name: str | None = None


class ImageUploadUrlRequest(BaseModel):
    content_type: str
    byte_size: int


class ImageUploadUrlResponse(BaseModel):
    upload_url: str
    storage_path: str
    token: str | None = None


class ImageConfirmRequest(BaseModel):
    storage_path: str
