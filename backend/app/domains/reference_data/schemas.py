from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ReferenceItemSchema(BaseModel):
    code: str
    label: str
    icon: str = ""
    color: str = ""
    sort_order: int = 0
    is_active: bool = True
    taxonomy: str | None = None
    parent_code: str | None = None
    children: list["ReferenceItemSchema"] = Field(default_factory=list)

    model_config = {"extra": "ignore"}


class CurrencySchema(ReferenceItemSchema):
    symbol: str = ""
    minor_unit: int = 2
    locale_hint: str = "en-US"


class ReferenceDataBootstrapSchema(BaseModel):
    reference_data_version: int
    currencies: list[CurrencySchema]
    countries: list[ReferenceItemSchema]
    locales: list[ReferenceItemSchema]
    timezones: list[ReferenceItemSchema]
    languages: list[ReferenceItemSchema] = Field(default_factory=list)
    categories: dict[str, list[ReferenceItemSchema]]


class ReferenceDataOptionsSchema(BaseModel):
    reference_data_version: int
    data: dict[str, list[Any]]
