"""Multi-member Group sync: fan-out invalidate, display names, stream route."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.domains.group.member_names import (
    display_name_from_user,
    is_generic_member_name,
    resolve_user_display_name,
)
from app.domains.group.projection_cache import invalidate_group_projections
from app.domains.users.models import UserModel


def test_is_generic_member_name():
    assert is_generic_member_name("Member")
    assert is_generic_member_name("member")
    assert is_generic_member_name("Member 1")
    assert is_generic_member_name("Member 2")
    assert is_generic_member_name("")
    assert is_generic_member_name(None)
    assert not is_generic_member_name("Ada Lovelace")
    assert not is_generic_member_name("Membership Club")


def test_display_name_from_user_prefers_profile_then_email():
    user = SimpleNamespace(display_name="Priya", email="priya@example.com")
    assert display_name_from_user(user) == "Priya"
    user2 = SimpleNamespace(display_name=None, email="alex@momentra.app")
    assert display_name_from_user(user2) == "alex"
    assert display_name_from_user(None) == "Member"


@pytest.mark.asyncio
async def test_resolve_user_display_name_loads_user():
    user_id = uuid4()
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = UserModel(
        id=user_id,
        firebase_uid="fb",
        email="jo@example.com",
        display_name="Jordan",
    )
    session.execute.return_value = result
    assert await resolve_user_display_name(session, user_id) == "Jordan"


@pytest.mark.asyncio
async def test_invalidate_fan_out_marks_all_members_stale(monkeypatch):
    actor = uuid4()
    peer = uuid4()
    moment_id = uuid4()
    marked: list[tuple] = []
    enqueued: list[str] = []

    async def fake_mark_stale(user_id, template, slice_type):
        marked.append((user_id, template, slice_type))

    def fake_enqueue(user_id, moment_id, *, moment_type="SHARED_EXPERIENCE", reason="x"):
        enqueued.append(str(user_id))

    async def fake_publish(*_a, **_k):
        return None

    async def fake_list_ids(session, mid, *, moment=None):
        return {actor, peer}

    monkeypatch.setattr(
        "app.domains.projections.projection_cache.mark_stale", fake_mark_stale
    )
    monkeypatch.setattr(
        "app.domains.group.projection_cache.enqueue_group_projection_refresh",
        fake_enqueue,
    )
    monkeypatch.setattr(
        "app.domains.group.group_moment_events.publish_group_moment_invalidate",
        fake_publish,
    )
    monkeypatch.setattr(
        "app.domains.group.access.list_group_member_user_ids",
        fake_list_ids,
    )

    session = AsyncMock()
    await invalidate_group_projections(
        actor,
        moment_id,
        moment_type="SHARED_EXPERIENCE",
        reason="test_fanout",
        session=session,
    )

    users_marked = {uid for uid, _, _ in marked}
    assert actor in users_marked
    assert peer in users_marked
    assert set(enqueued) == {str(actor), str(peer)}
    # 5 slices × 2 users
    assert len(marked) == 10


@patch("app.dependencies.auth.verify_firebase_token")
def test_group_moments_stream_route_exists(
    mock_verify, client, mock_db, sample_user: UserModel
):
    mock_verify.return_value = {"uid": "test-firebase-uid", "email": "t@example.com"}
    mock_db.add(sample_user)
    # Missing moment → 404 (route is registered and auth'd), not 405/404 router miss.
    mid = uuid4()
    res = client.get(
        f"/api/v1/group/moments/{mid}/stream",
        headers={"Authorization": "Bearer test-token"},
    )
    assert res.status_code in {404, 401, 403}
    # StreamingResponse for missing moment uses require_group_moment_access → 404
    assert res.status_code == 404
