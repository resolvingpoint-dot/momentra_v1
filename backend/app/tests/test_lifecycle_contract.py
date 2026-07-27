"""Unit tests for cross-context lifecycle contract helpers."""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import StateTransitionError
from app.domains.moment_engine.lifecycle_contract import (
    LIFECYCLE_TRANSITION_INVALID,
    build_lifecycle_response,
    pick_replacement_moment,
)
from app.domains.moment_engine.state import assert_transition, can_transition


def _m(status: str, *, moment_type: str = "SHARED_EXPERIENCE"):
    return SimpleNamespace(
        id=uuid4(),
        status=status,
        moment_type=moment_type,
        updated_at=datetime.now(timezone.utc),
        setup_state="ACTIVE",
        title="t",
        context_type="GROUP",
    )


def test_paused_can_complete():
    assert can_transition("PAUSED", "COMPLETED")
    assert_transition("PAUSED", "COMPLETED")


def test_invalid_transition_code():
    with pytest.raises(StateTransitionError) as ei:
        assert_transition("ARCHIVED", "ACTIVE")
    assert ei.value.code == LIFECYCLE_TRANSITION_INVALID


def test_pick_replacement_prefers_active_and_skips_archived():
    archived = _m("ARCHIVED")
    paused = _m("PAUSED")
    active = _m("ACTIVE")
    mid, mtype = pick_replacement_moment(
        [archived, paused, active],
        exclude_id=None,
    )
    assert mid == str(active.id)
    assert mtype == "SHARED_EXPERIENCE"


def test_pick_replacement_excludes_id():
    a = _m("ACTIVE", moment_type="A")
    b = _m("ACTIVE", moment_type="B")
    mid, mtype = pick_replacement_moment([a, b], exclude_id=a.id)
    assert mid == str(b.id)
    assert mtype == "B"


def test_build_lifecycle_response_includes_replacement():
    moment = _m("ARCHIVED")
    moment.id = uuid4()
    payload = build_lifecycle_response(
        moment=moment,  # type: ignore[arg-type]
        context_type="GROUP",
        previous_status="ACTIVE",
        module_state="SETUP",
        replacement_moment_id="repl",
        replacement_moment_type_code="SHARED_PURCHASE",
    )
    assert payload["status"] == "ARCHIVED"
    assert payload["replacement_moment_id"] == "repl"
    assert payload["context_type"] == "GROUP"
    assert payload["previous_status"] == "ACTIVE"
