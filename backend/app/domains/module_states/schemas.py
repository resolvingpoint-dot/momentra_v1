from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ModuleStateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    module_key: str
    state: str = "EMPTY"
    reason: str | None = None
    payload: dict | None = None
    created_at: datetime
    updated_at: datetime


class ContextSchema(BaseModel):
    key: str
    label: str
    state: str = "EMPTY"
