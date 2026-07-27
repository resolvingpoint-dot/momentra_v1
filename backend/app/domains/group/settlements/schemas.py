"""Pydantic models for Settlement Engine v1."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SettlementStatus = Literal["OPEN", "SETTLED", "WAIVED"]
SplitStyle = Literal["EQUAL", "EXACT", "PERCENTAGE", "SHARES"]


class MemberBalance(BaseModel):
    member_id: str
    display_name: str
    paid_minor: int = 0
    owed_minor: int = 0
    net_minor: int = 0
    currency_code: str = "INR"


class TransferSuggestion(BaseModel):
    from_member_id: str
    to_member_id: str
    from_display_name: str
    to_display_name: str
    amount_minor: int
    currency_code: str = "INR"
    reason: str = "to stabilize balance"


class SettlementPreview(BaseModel):
    moment_id: str
    currency_code: str = "INR"
    total_expenses_minor: int = 0
    member_balances: list[MemberBalance] = Field(default_factory=list)
    suggestions: list[TransferSuggestion] = Field(default_factory=list)
    harmony_label: str = "In harmony"
    balance_insight: str = ""
    status: str = "preview"


class SettlementRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    moment_id: str
    from_member_id: str
    to_member_id: str
    amount_minor: int
    currency_code: str = "INR"
    status: SettlementStatus = "OPEN"
    description: str | None = None
    client_request_id: str | None = None
    created_at: str
    updated_at: str
    settled_at: str | None = None
    deleted: bool = False


class SettlementCreateRequest(BaseModel):
    from_member_id: str
    to_member_id: str
    amount_minor: int = Field(gt=0)
    currency_code: str = "INR"
    description: str | None = None
    client_request_id: str | None = None


class SettlementPatchRequest(BaseModel):
    from_member_id: str | None = None
    to_member_id: str | None = None
    amount_minor: int | None = Field(default=None, gt=0)
    currency_code: str | None = None
    description: str | None = None
    status: SettlementStatus | None = None


class SettlementListResponse(BaseModel):
    moment_id: str
    currency_code: str = "INR"
    settlements: list[SettlementRecord] = Field(default_factory=list)


class MarkSettledResponse(BaseModel):
    settlement: SettlementRecord
    idempotent: bool = False
