"""Unit tests for activity DTO auth flags + list filter helpers."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from app.domains.business.activity.engine import _auth_flags, _to_dto
from app.domains.business.activity.types import ActionType


def _event(action_type: str, *, created_by=None, is_voided=False):
    return SimpleNamespace(
        event_id=uuid4(),
        business_moment_id=uuid4(),
        user_id=uuid4(),
        moment_type_code="TEAM_OPERATIONS",
        action_type=action_type,
        title="t",
        subtitle=None,
        occurred_at=None,
        created_by=created_by or uuid4(),
        source="action_center",
        payload={},
        client_request_id=None,
        is_voided=is_voided,
    )


def test_auth_flags_from_registry_for_team_update():
    viewer = uuid4()
    event = _event(ActionType.TEAM_UPDATE.value, created_by=viewer)
    member = SimpleNamespace(
        can_edit_own_entries=True,
        can_edit_team_entries=False,
        can_delete_operations_records=False,
        role="MEMBER",
        is_team_lead=False,
        is_budget_owner=False,
    )
    editable, deletable, supported = _auth_flags(event, viewer_id=viewer, member=member)
    assert editable is True
    assert deletable is True
    assert supported == ["edit", "delete"]


def test_auth_flags_approval_request_not_editable():
    viewer = uuid4()
    event = _event(ActionType.APPROVAL_REQUEST.value, created_by=viewer)
    member = SimpleNamespace(
        can_edit_own_entries=True,
        can_edit_team_entries=True,
        can_delete_operations_records=True,
        role="OWNER",
        is_team_lead=True,
        is_budget_owner=True,
    )
    editable, deletable, supported = _auth_flags(event, viewer_id=viewer, member=member)
    assert editable is False
    assert deletable is False
    assert supported == []


def test_to_dto_includes_permission_fields():
    viewer = uuid4()
    event = _event(ActionType.ISSUE.value, created_by=viewer)
    event.occurred_at = __import__("datetime").datetime(2026, 7, 15, 12, 0, 0)
    member = SimpleNamespace(
        can_edit_own_entries=True,
        can_edit_team_entries=False,
        can_delete_operations_records=False,
        role="MEMBER",
        is_team_lead=False,
        is_budget_owner=False,
    )
    dto = _to_dto(event, viewer_id=viewer, member=member)
    assert dto["is_editable"] is True
    assert dto["is_deletable"] is True
    assert dto["supported_actions"] == ["edit", "delete"]
    assert dto["action_type"] == "ISSUE"
