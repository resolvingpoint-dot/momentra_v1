"""P0.7 projection_hint on Business activity mutations."""
from __future__ import annotations

from app.domains.business.activity.projection_hint import (
    build_projection_hint,
    wrap_mutation_response,
)


def test_wrap_mutation_response_shape():
    activity = {
        "event_id": "e1",
        "business_moment_id": "m1",
        "action_type": "LOG_ISSUE",
        "title": "Blocked",
        "occurred_at": "2026-01-01T00:00:00Z",
        "client_request_id": "c1",
    }
    wrapped = wrap_mutation_response(activity, op="create")
    assert "activity" in wrapped
    assert "projection_hint" in wrapped
    hint = wrapped["projection_hint"]
    assert hint["op"] == "create"
    assert hint["activity_event"]["event_id"] == "e1"
    assert hint["counters"]["activity_delta"] == 1
    assert hint["counters"]["open_issues_delta"] == 1


def test_delete_hint_negative_delta():
    hint = build_projection_hint(
        {"event_id": "e1", "action_type": "LOG_ISSUE", "title": "x"},
        op="delete",
    )
    assert hint["counters"]["activity_delta"] == -1
    assert hint["pulse"]["recent_activity_prepend"] is None
