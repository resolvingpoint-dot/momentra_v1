"""Unit tests for behavioral-pattern evidence gating + dedupe (ACGmNh-c)."""
from __future__ import annotations

from app.domains.personal.templates.pattern_evidence import gate_and_dedupe_patterns


def test_drops_patterns_without_evidence():
    patterns = [
        {"pattern_id": "tuesday_learning", "title": "Tuesday Learning Pattern"},
        {"pattern_id": "morning_momentum", "title": "Morning Momentum Accelerator"},
    ]
    result = gate_and_dedupe_patterns(
        patterns,
        evidence_counts={"tuesday_learning": 3, "morning_momentum": 0},
    )
    assert [p["pattern_id"] for p in result] == ["tuesday_learning"]


def test_keeps_all_patterns_with_evidence():
    patterns = [
        {"pattern_id": "weekend_connections", "title": "Weekend Connection Pattern"},
        {"pattern_id": "support_after_stress", "title": "Support Response Pattern"},
    ]
    result = gate_and_dedupe_patterns(
        patterns,
        evidence_counts={"weekend_connections": 4, "support_after_stress": 2},
    )
    assert len(result) == 2


def test_dedupes_by_pattern_id_keeping_first_occurrence():
    patterns = [
        {"pattern_id": "weekend_experiences", "title": "First"},
        {"pattern_id": "weekend_experiences", "title": "Duplicate"},
    ]
    result = gate_and_dedupe_patterns(
        patterns,
        evidence_counts={"weekend_experiences": 5},
    )
    assert len(result) == 1
    assert result[0]["title"] == "First"


def test_missing_pattern_id_is_dropped():
    patterns = [{"title": "No id"}]
    result = gate_and_dedupe_patterns(patterns, evidence_counts={})
    assert result == []


def test_empty_input_returns_empty_list():
    assert gate_and_dedupe_patterns([], evidence_counts={}) == []
