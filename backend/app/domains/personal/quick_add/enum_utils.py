"""Normalize client quick-add values to DB enum defaults."""
from __future__ import annotations

from typing import Any


def normalize_choice(
    value: Any,
    valid: set[str],
    default: str,
    *,
    aliases: dict[str, str] | None = None,
) -> str:
    if value is None or str(value).strip() == "":
        return default
    raw = str(value).strip()
    if aliases:
        mapped = aliases.get(raw.upper()) or aliases.get(raw.lower()) or aliases.get(raw)
        if mapped:
            raw = mapped
    if raw in valid:
        return raw
    upper = raw.upper()
    for candidate in valid:
        if candidate.upper() == upper:
            return candidate
    title = raw.replace("_", " ").title()
    for candidate in valid:
        if candidate.lower() == title.lower():
            return candidate
    return default


def as_note(*parts: Any) -> str | None:
    text = " · ".join(str(p).strip() for p in parts if p and str(p).strip())
    return text or None


def as_list(value: Any, *, default: list[str] | None = None) -> list[str]:
    if value is None:
        return list(default or [])
    if isinstance(value, list):
        return [str(v).strip() for v in value if v and str(v).strip()]
    text = str(value).strip()
    return [text] if text else list(default or [])
