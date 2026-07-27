from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.domains.life360.life360_service import Life360Service
from app.domains.life360.models import Life360Snapshots
from app.workers import procedures as procs


def test_user_snapshot_procs_run_life360_last() -> None:
    assert procs.USER_SNAPSHOT_PROCS[0] == "sp_refresh_personal_life_health"
    assert procs.USER_SNAPSHOT_PROCS[1] == "sp_refresh_personal_life_dimensions"
    assert procs.USER_SNAPSHOT_PROCS[2] == "sp_refresh_personal_life_snapshot"
    assert procs.USER_SNAPSHOT_PROCS[-1] == "sp_refresh_life360_snapshots"


def test_life360_full_state_requires_confidence_at_least_25() -> None:
    low = Life360Snapshots(
        user_id=uuid4(),
        snapshot_date=__import__("datetime").date.today(),
        snapshot_month=__import__("datetime").date.today(),
        life_alignment_score=Decimal("70"),
        signal_confidence_score=Decimal("24.99"),
    )
    high = Life360Snapshots(
        user_id=uuid4(),
        snapshot_date=__import__("datetime").date.today(),
        snapshot_month=__import__("datetime").date.today(),
        life_alignment_score=Decimal("70"),
        signal_confidence_score=Decimal("50"),
    )
    assert Life360Service._is_full_state(low) is False
    assert Life360Service._is_full_state(high) is True
    assert Life360Service._is_full_state(None) is False


@pytest.mark.asyncio
async def test_life360_home_reports_domain_signal_counts() -> None:
    user_id = uuid4()
    snapshot = Life360Snapshots(
        user_id=user_id,
        snapshot_date=__import__("datetime").date.today(),
        snapshot_month=__import__("datetime").date.today(),
        life_alignment_score=Decimal("72"),
        signal_confidence_score=Decimal("50"),
        personal_score=Decimal("68"),
        group_score=None,
        business_score=Decimal("74"),
    )
    session = AsyncMock()
    service = Life360Service(session)
    service.snapshots_repo.list = AsyncMock(return_value=[snapshot])

    home = await service.home(user_id)

    assert home["state"] == "FULL"
    assert home["counts"] == {
        "personal_signals": 1,
        "group_signals": 0,
        "business_signals": 1,
    }


@pytest.mark.asyncio
async def test_life360_home_empty_without_snapshot() -> None:
    user_id = uuid4()
    session = AsyncMock()
    service = Life360Service(session)
    service.snapshots_repo.list = AsyncMock(return_value=[])

    home = await service.home(user_id)

    assert home["state"] == "EMPTY"
    assert home["counts"] == {
        "personal_signals": 0,
        "group_signals": 0,
        "business_signals": 0,
    }


@pytest.mark.asyncio
@patch("app.workers.tasks.analytics.procs.refresh_life360_snapshot", new_callable=AsyncMock)
@patch("app.workers.tasks.analytics.procs.refresh_analytics", new_callable=AsyncMock)
async def test_analytics_refresh_recomputes_life360_for_group(
    mock_refresh_analytics: AsyncMock,
    mock_refresh_life360: AsyncMock,
) -> None:
    from app.workers.tasks.analytics import _refresh

    user_id = uuid4()
    moment_id = uuid4()
    mock_refresh_analytics.return_value = "sp_refresh_group_analytics"

    result = await _refresh("group", moment_id, user_id)

    mock_refresh_analytics.assert_awaited_once()
    mock_refresh_life360.assert_awaited_once()
    assert result["life360_refreshed"] is True


@pytest.mark.asyncio
@patch("app.workers.tasks.analytics.procs.refresh_life360_snapshot", new_callable=AsyncMock)
@patch("app.workers.tasks.analytics.procs.refresh_analytics", new_callable=AsyncMock)
async def test_analytics_refresh_skips_life360_for_personal(
    mock_refresh_analytics: AsyncMock,
    mock_refresh_life360: AsyncMock,
) -> None:
    from app.workers.tasks.analytics import _refresh

    user_id = uuid4()
    moment_id = uuid4()
    mock_refresh_analytics.return_value = "sp_run_personal_ai_refresh"

    result = await _refresh("personal", moment_id, user_id)

    mock_refresh_analytics.assert_awaited_once()
    mock_refresh_life360.assert_not_awaited()
    assert result["life360_refreshed"] is False


@patch("app.dependencies.auth.verify_firebase_token")
def test_life360_home_endpoint_uses_snapshot_state(
    mock_verify,
    client,
    mock_db,
    sample_user,
) -> None:
    mock_verify.return_value = {
        "uid": "test123",
        "email": "test@example.com",
        "name": "Test User",
    }
    mock_db.add(sample_user)

    with patch.object(
        Life360Service,
        "home",
        new=AsyncMock(
            return_value={
                "state": "FULL",
                "counts": {
                    "personal_signals": 1,
                    "group_signals": 0,
                    "business_signals": 0,
                },
            }
        ),
    ):
        resp = client.get(
            "/api/v1/life360/home",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["module"] == "LIFE360"
    assert data["state"] == "FULL"
    assert data["counts"]["personal_signals"] == 1
