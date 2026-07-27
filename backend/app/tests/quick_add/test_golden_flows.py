"""Golden flow fixture presence + contract coverage (backend-first)."""
from __future__ import annotations

import json

from app.domains.quick_add_contract.hash import fixtures_root

GOLDEN = [
    "life_ops_expense.json",
    "future_contribution.json",
    "lifestyle_experience.json",
    "relationship_connection.json",
    "group_trip_expense.json",
    "purchase_contribution.json",
    "living_rent.json",
]


def test_golden_flow_suite_present():
    root = fixtures_root() / "golden_flow"
    for name in GOLDEN:
        path = root / name
        assert path.exists(), f"missing golden flow {name}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "flow_id" in data
        assert "steps" in data
        assert "create" in data["steps"]
        fixture_name = data["fixture"]
        assert (fixtures_root() / fixture_name).exists()


def test_golden_flows_cover_seven_references():
    ids = set()
    for name in GOLDEN:
        data = json.loads((fixtures_root() / "golden_flow" / name).read_text())
        ids.add(data["flow_id"])
    assert len(ids) == 7
