from __future__ import annotations

from pydantic import BaseModel

from app.domains.module_states.schemas import ContextSchema
from app.domains.preferences.schemas import UserPreferenceSchema
from app.domains.users.schemas import UserResponse


class SummaryCountsSchema(BaseModel):
    my_money_moments: int = 0
    group_moments: int = 0
    business_moments: int = 0
    circle_participants: int = 0
    memories: int = 0


class ModuleEntrySchema(BaseModel):
    state: str = "EMPTY"


class BootstrapResponse(BaseModel):
    user: UserResponse
    preferences: UserPreferenceSchema
    contexts: list[ContextSchema]
    modules: dict[str, ModuleEntrySchema]
    summary_counts: SummaryCountsSchema
    reference_data_version: int = 1
    template_version: int = 1
    ui_schema_version: int = 1
    quick_add_version: int = 1
    setup_version: int = 1
    metadata_version: int = 1
    server_time: str
