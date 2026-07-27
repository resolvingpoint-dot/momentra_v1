"""Typed Quick Add contract errors."""
from __future__ import annotations


class QuickAddContractError(Exception):
    code: str = "quick_add_contract_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code
        self.message = message

    def to_detail(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


class QuickAddActionNotSupported(QuickAddContractError):
    code = "quick_add_action_not_supported"


class QuickAddInvalidPayload(QuickAddContractError):
    code = "quick_add_invalid_payload"


class QuickAddInvalidCurrency(QuickAddContractError):
    code = "invalid_currency"


class QuickAddInvalidAmount(QuickAddContractError):
    code = "invalid_amount"


class QuickAddInvalidMember(QuickAddContractError):
    code = "invalid_member"


class QuickAddDuplicateRequest(QuickAddContractError):
    code = "duplicate_request"
