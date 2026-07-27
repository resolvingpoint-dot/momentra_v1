"""Tests for Quick Add Registry Validator + registry hash lock."""
from __future__ import annotations

import json
from pathlib import Path

from app.domains.quick_add_contract.hash import compute_registry_hash, fixtures_root, load_reference_actions
from app.domains.quick_add_contract.inventory import (
    BACKEND_HANDLER_IDS,
    BACKEND_PAYLOAD_BUILDER_IDS,
    BACKEND_RENDERER_IDS,
)
from app.domains.quick_add_contract.validator import QuickAddRegistryValidator, validate_reference_registry

LOCKFILE = fixtures_root() / "registry_hash.lock"


def test_reference_actions_count():
    assert len(load_reference_actions()) == 7


def test_registry_validator_passes_with_inventory():
    result = validate_reference_registry(
        renderer_ids=BACKEND_RENDERER_IDS,
        payload_builder_ids=BACKEND_PAYLOAD_BUILDER_IDS,
        handler_ids=BACKEND_HANDLER_IDS,
    )
    result.raise_if_failed()
    assert result.ok
    assert len(result.registry_hash) == 64


def test_registry_validator_fails_missing_handler():
    result = QuickAddRegistryValidator(
        handler_exists=lambda _i: False,
    ).validate()
    assert not result.ok
    assert any(i.code == "handler_missing" for i in result.issues)


def test_registry_hash_lockfile():
    current = compute_registry_hash()
    if not LOCKFILE.exists():
        LOCKFILE.write_text(current + "\n", encoding="utf-8")
    expected = LOCKFILE.read_text(encoding="utf-8").strip()
    assert current == expected, (
        f"Registry hash drift. Update fixtures/quick_add/registry_hash.lock only with intentional contract changes.\n"
        f"expected={expected}\ngot={current}"
    )


def test_edit_delete_capabilities_require_endpoints():
    actions = load_reference_actions()
    for action in actions:
        caps = action["capabilities"]
        if caps.get("edit"):
            assert action.get("edit_endpoint")
        if caps.get("delete"):
            assert action.get("delete_endpoint")


def test_contract_lockfile_shape():
    path = fixtures_root() / "contract_v1_reference_actions.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["contract_version"] == "v1"
    keys = {a["key"] for a in raw["reference_actions"]}
    assert keys == {
        "LIFE_OPERATIONS:EXPENSE",
        "FUTURE_BUILDING:CONTRIBUTION",
        "LIFESTYLE:EXPERIENCE",
        "RELATIONSHIPS:CONNECTION",
        "SHARED_EXPERIENCE:EXPENSE",
        "SHARED_PURCHASE:CONTRIBUTOR",
        "SHARED_LIVING:EXPENSE",
    }
    by_key = {a["key"]: a for a in raw["reference_actions"]}
    assert by_key["LIFE_OPERATIONS:EXPENSE"]["contract_version"] == "v2"
    assert by_key["SHARED_EXPERIENCE:EXPENSE"]["contract_version"] == "v2"
    assert by_key["SHARED_LIVING:EXPENSE"]["contract_version"] == "v1"
