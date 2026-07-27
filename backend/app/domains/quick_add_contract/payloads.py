"""Payload builder interface helpers (validate / normalize / build / serialize)."""
from __future__ import annotations

from typing import Any, Mapping, Protocol

from app.domains.quick_add_contract.errors import QuickAddInvalidPayload
from app.domains.quick_add_contract.normalize import normalize_payload


class PayloadBuilder(Protocol):
    builder_id: str

    def validate(self, form: Mapping[str, Any]) -> None: ...

    def normalize(self, form: Mapping[str, Any]) -> dict[str, Any]: ...

    def build(self, form: Mapping[str, Any]) -> dict[str, Any]: ...

    def serialize(self, payload: Mapping[str, Any]) -> dict[str, Any]: ...


def require_fields(form: Mapping[str, Any], fields: list[str], *, builder_id: str) -> None:
    missing = [f for f in fields if form.get(f) in (None, "", [])]
    if missing:
        raise QuickAddInvalidPayload(
            f"{builder_id} missing required fields: {', '.join(missing)}",
        )


def pipeline_build(
    form: Mapping[str, Any],
    *,
    moment_type_code: str,
    action_id: str,
    required: list[str],
    builder_id: str,
) -> dict[str, Any]:
    """Canonical builder pipeline used by tests and adapters."""
    require_fields(form, required, builder_id=builder_id)
    normalized = normalize_payload(form, moment_type_code=moment_type_code, action_id=action_id)
    if "subcategory_code" in normalized or any(
        k in form for k in ("subcategory_code", "subcategory", "sub_category", "expense_subcategory")
    ):
        normalized["contract_version"] = "v2"
    else:
        normalized["contract_version"] = "v1"
    return normalized
