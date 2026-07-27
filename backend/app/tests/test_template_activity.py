"""Tests for template activity API, soft delete, FB setup contract, and invalidation."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalQuickAddEvents,
)
from app.domains.projections.invalidation import invalidate_for_quick_add
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


@patch("app.dependencies.auth.verify_firebase_token")
def test_template_activity_lifestyle_requires_moment(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/personal/templates/LIFESTYLE/activity?moment_id=00000000-0000-0000-0000-000000000099",
        headers=AUTH,
    )
    assert resp.status_code in {404, 403}


@patch("app.dependencies.auth.verify_firebase_token")
def test_fb_setup_get_includes_six_fields(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    create = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "FUTURE_BUILDING", "moment_name": "My Future"},
        headers=AUTH,
    )
    assert create.status_code == 201
    moment_id = create.json()["moment_id"]

    resp = client.get(f"/api/v1/personal/moments/{moment_id}/setup", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    keys = {f["field_key"] for f in data["fields"]}
    assert "building_focus" in keys
    assert "current_state" in keys
    assert "values" in keys
    assert "friction_sources" in keys
    assert "momentum_drivers" in keys
    assert "future_feeling" in keys
    assert data["moment_type_code"] == "FUTURE_BUILDING"


@patch("app.dependencies.auth.verify_firebase_token")
def test_fb_setup_draft_resume(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    create = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "FUTURE_BUILDING", "moment_name": "Draft Future"},
        headers=AUTH,
    )
    moment_id = create.json()["moment_id"]

    draft = client.put(
        f"/api/v1/personal/moments/{moment_id}/setup/draft",
        json={"answers": {
            "building_focus": "CAREER_GROWTH",
            "current_state": "JUST_STARTING",
            "values": ["GROWTH"],
            "friction_sources": ["TIME"],
            "momentum_drivers": ["LEARNING"],
            "future_feeling": "HOPEFUL",
        }},
        headers=AUTH,
    )
    assert draft.status_code == 200
    saved = draft.json().get("saved_answers") or {}
    assert saved.get("building_focus") == "CAREER_GROWTH"

    resumed = client.get(f"/api/v1/personal/moments/{moment_id}/setup", headers=AUTH)
    assert resumed.status_code == 200
    resumed_saved = resumed.json().get("saved_answers") or {}
    assert resumed_saved.get("building_focus") == "CAREER_GROWTH"


@pytest.mark.asyncio
async def test_invalidate_fb_contribution_refreshes_moments():
    user_id = UUID("00000000-0000-0000-0000-000000000001")
    with patch(
        "app.domains.projections.invalidation.refresh_slices_async",
        new_callable=AsyncMock,
    ) as refresh:
        await invalidate_for_quick_add(user_id, "FUTURE_BUILDING", "CONTRIBUTION")
        refresh.assert_awaited_once()
        _args, kwargs = refresh.await_args
        assert "moments" in _args[2]
        assert kwargs.get("include_personal_life") is True


def test_series_helpers_zero_fill():
    from app.domains.personal.templates.future_building.series_helpers import (
        build_trends_30d,
        daily_counts,
    )

    assert daily_counts([], frozenset({"LEARNING"}), days=30) == [0] * 30
    trends = build_trends_30d([])
    assert len(trends["learning"]) == 30
    assert trends["learning"][0] == {"date": trends["learning"][0]["date"], "value": 0}
    assert len(trends["execution"]) == 30
    assert len(trends["progress"]) == 30


def test_series_helpers_counts_events():
    from datetime import datetime, timezone

    from app.domains.personal.templates.future_building.series_helpers import (
        build_trends_30d,
    )

    class _Row:
        def __init__(self, event_type: str, when: datetime):
            self.event_type = event_type
            self.event_occurred_at = when

    today = datetime.now(timezone.utc)
    timeline = [
        _Row("LEARNING", today),
        _Row("CONTRIBUTION", today),
        _Row("MILESTONE", today),
    ]
    trends = build_trends_30d(timeline)  # type: ignore[arg-type]
    assert trends["learning"][-1]["value"] == 1
    assert trends["execution"][-1]["value"] == 1
    assert trends["progress"][-1]["value"] == 1
