"""Correlation / request ID validation for observability headers."""
from __future__ import annotations

import re
import uuid

# UUID or opaque token: alphanumeric, underscore, hyphen; 8–128 chars.
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")


def mint_id() -> str:
    return str(uuid.uuid4())


def sanitize_observability_id(value: str | None) -> str | None:
    """Return a safe ID or None if missing/invalid (caller mints replacement)."""
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if len(cleaned) > 128:
        return None
    if _SAFE_ID_RE.fullmatch(cleaned):
        return cleaned
    return None


def resolve_request_id(header_value: str | None) -> str:
    return sanitize_observability_id(header_value) or mint_id()


def resolve_correlation_id(header_value: str | None, *, fallback: str) -> str:
    return sanitize_observability_id(header_value) or fallback
