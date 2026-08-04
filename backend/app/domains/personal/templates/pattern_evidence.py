"""Shared gating/dedupe helper for memory-mapper `behavioral_patterns` lists.

Template memory mappers (Future Building, Relationships, Lifestyle, ...) surface
a small set of named behavioral patterns (e.g. "Tuesday Learning Pattern"). Each
pattern must only be shown when the underlying signal it claims actually has
evidence in the user's logged activity — never as a static placeholder — and a
`pattern_id` must never appear twice in the same response.
"""
from __future__ import annotations

from typing import Any


def gate_and_dedupe_patterns(
    patterns: list[dict[str, Any]],
    evidence_counts: dict[str, int],
) -> list[dict[str, Any]]:
    """Keep only patterns backed by evidence, deduped by `pattern_id`.

    ``evidence_counts`` maps each pattern's `pattern_id` to the count of
    underlying signal events supporting it. A pattern is dropped when its
    count is missing or non-positive, and repeated `pattern_id`s collapse to
    the first occurrence.
    """
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for pattern in patterns:
        pattern_id = pattern.get("pattern_id")
        if not pattern_id or pattern_id in seen:
            continue
        if evidence_counts.get(pattern_id, 0) <= 0:
            continue
        seen.add(pattern_id)
        result.append(pattern)
    return result
