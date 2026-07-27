"""Normalizers for Business setup answers and template ids."""
from __future__ import annotations

from typing import Any

from app.domains.business.catalog import (
    BUSINESS_OPERATIONS,
    BUSINESS_RUNWAY,
    TEAM_OPERATIONS,
    normalize_moment_type_code,
)

# Canonical template_id values (web registry).
TEMPLATE_IDS: dict[str, str] = {
    TEAM_OPERATIONS: "team_ops",
    BUSINESS_RUNWAY: "business_runway",
    BUSINESS_OPERATIONS: "business_operations",
}

_TEMPLATE_ALIASES: dict[str, str] = {
    "team_ops": "team_ops",
    "team_operations": "team_ops",
    "TEAM_OPERATIONS": "team_ops",
    "business_runway": "business_runway",
    "BUSINESS_RUNWAY": "business_runway",
    "business-runway": "business_runway",
    "runway": "business_runway",
    "business_operations": "business_operations",
    "BUSINESS_OPERATIONS": "business_operations",
    "business-operations": "business_operations",
    "operations": "business_operations",
    "department_operations": "business_operations",
}

_FIELD_ALIASES: dict[str, str] = {
    "purpose": "team_purpose",
    "currency": "operating_currency_code",
    "currency_code": "operating_currency_code",
    "operating_currency": "operating_currency_code",
    "default_currency_code": "operating_currency_code",
    "cash_available_minor": "current_cash_minor",
}


def template_id_for_type(moment_type_code: str) -> str:
    canonical = normalize_moment_type_code(moment_type_code) or moment_type_code
    return TEMPLATE_IDS.get(canonical, canonical.lower())


def normalize_template_id(template_id: str | None, moment_type_code: str | None = None) -> str:
    if template_id:
        key = template_id.strip()
        if key in _TEMPLATE_ALIASES:
            return _TEMPLATE_ALIASES[key]
        lower = key.lower()
        if lower in _TEMPLATE_ALIASES:
            return _TEMPLATE_ALIASES[lower]
    if moment_type_code:
        return template_id_for_type(moment_type_code)
    return "team_ops"


def normalize_answers(answers: dict[str, Any] | None) -> dict[str, Any]:
    raw = dict(answers or {})
    out: dict[str, Any] = {}
    for key, value in raw.items():
        canonical = _FIELD_ALIASES.get(key, key)
        out[canonical] = value
    return out
