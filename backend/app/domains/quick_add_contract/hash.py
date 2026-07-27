"""Registry hash + load reference actions from shared fixtures."""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[4]
_FIXTURE_PATH = _REPO_ROOT / "fixtures" / "quick_add" / "contract_v1_reference_actions.json"


def fixtures_root() -> Path:
    return _REPO_ROOT / "fixtures" / "quick_add"


@lru_cache(maxsize=1)
def load_reference_actions() -> list[dict[str, Any]]:
    raw = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    actions = raw.get("reference_actions") or []
    if not isinstance(actions, list) or len(actions) != 7:
        raise RuntimeError(f"Expected 7 reference actions in {_FIXTURE_PATH}")
    return actions


def canonical_action_blob(action: dict[str, Any]) -> str:
    """Stable JSON for hashing — sorted keys, no whitespace variance."""
    keys = (
        "key",
        "moment_type_code",
        "action_id",
        "renderer_id",
        "endpoint",
        "edit_endpoint",
        "delete_endpoint",
        "handler_id",
        "payload_builder_id",
        "capabilities",
        "output_events",
        "affected_projections",
        "platforms",
        "contract_version",
    )
    slim = {k: action.get(k) for k in keys}
    return json.dumps(slim, sort_keys=True, separators=(",", ":"))


def compute_registry_hash(actions: list[dict[str, Any]] | None = None) -> str:
    rows = actions if actions is not None else load_reference_actions()
    joined = "\n".join(canonical_action_blob(a) for a in sorted(rows, key=lambda x: x["key"]))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
