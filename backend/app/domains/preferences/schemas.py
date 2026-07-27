from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

VALID_CONTEXTS = {"MY_MONEY", "GROUP", "BUSINESS", "CIRCLE"}


class UserPreferenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    selected_context: str = "MY_MONEY"
    default_currency_code: str = "INR"
    locale: str = "en-IN"
    country_code: str = "IN"
    timezone: str = "Asia/Kolkata"
    created_at: datetime
    updated_at: datetime


class PreferenceUpdateSchema(BaseModel):
    selected_context: str | None = None
    default_currency_code: str | None = None
    locale: str | None = None
    country_code: str | None = None
    timezone: str | None = None

    @field_validator("selected_context")
    @classmethod
    def validate_context(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_CONTEXTS:
            raise ValueError(f"Invalid context: {v}. Must be one of {VALID_CONTEXTS}")
        return v

    @model_validator(mode="after")
    def at_least_one_field(self) -> PreferenceUpdateSchema:
        if not any(
            [
                self.selected_context is not None,
                self.default_currency_code is not None,
                self.locale is not None,
                self.country_code is not None,
                self.timezone is not None,
            ]
        ):
            raise ValueError("At least one preference field must be provided")
        return self
