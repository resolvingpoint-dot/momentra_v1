"""Pydantic schemas for Business activity engine."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateActivityRequest(BaseModel):
    action_type: str
    title: str
    subtitle: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    client_request_id: str | None = None
    source: str = "quick_add"


class PatchActivityRequest(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    payload: dict[str, Any] | None = None


class ActivityDTO(BaseModel):
    event_id: UUID
    business_moment_id: UUID
    user_id: UUID
    moment_type_code: str
    action_type: str
    title: str
    subtitle: str | None = None
    occurred_at: datetime
    created_by: UUID
    source: str = "quick_add"
    payload: dict[str, Any] = Field(default_factory=dict)
    client_request_id: str | None = None
    is_voided: bool = False
    typed_row_id: UUID | None = None
    idempotent_replay: bool = False
    # Server-owned authorization — clients must not infer from registries.
    is_editable: bool = False
    is_deletable: bool = False
    supported_actions: list[str] = Field(default_factory=list)


class ActivityListResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int


ActivitySort = Literal["newest", "oldest"]
ActivityStatus = Literal["all", "active", "voided"]
