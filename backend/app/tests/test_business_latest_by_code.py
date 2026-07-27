"""Unit tests for BusinessAppService._latest_by_code + card is_active preference."""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.domains.business.app_service import BusinessAppService, _SWITCHER_ACTIVE_STATUSES


def _moment(
    *,
    moment_type: str,
    status: str,
    title: str = "m",
    updated_at: datetime | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        moment_type=moment_type,
        status=status,
        title=title,
        description=None,
        updated_at=updated_at,
        created_at=updated_at,
    )


def _svc() -> BusinessAppService:
    # Avoid __init__ (needs DB session + domain registry); only exercise helpers.
    return object.__new__(BusinessAppService)


def test_latest_by_code_prefers_active_over_newer_draft():
    """DRAFT listed first must not beat ACTIVE of the same type."""
    svc = _svc()
    moments = [
        _moment(moment_type="TEAM_OPERATIONS", status="DRAFT", title="newer draft"),
        _moment(moment_type="TEAM_OPERATIONS", status="ACTIVE", title="older active"),
        _moment(moment_type="BUSINESS_RUNWAY", status="ACTIVE", title="runway"),
    ]
    latest = svc._latest_by_code(moments)  # type: ignore[arg-type]
    assert latest["TEAM_OPERATIONS"].status == "ACTIVE"
    assert latest["TEAM_OPERATIONS"].title == "older active"
    assert latest["BUSINESS_RUNWAY"].status == "ACTIVE"


def test_latest_by_code_prefers_paused_over_setup():
    svc = _svc()
    moments = [
        _moment(moment_type="BUSINESS_OPERATIONS", status="SETUP"),
        _moment(moment_type="BUSINESS_OPERATIONS", status="PAUSED"),
    ]
    latest = svc._latest_by_code(moments)  # type: ignore[arg-type]
    assert latest["BUSINESS_OPERATIONS"].status == "PAUSED"


def test_latest_by_code_keeps_newest_among_same_rank():
    svc = _svc()
    older = datetime(2026, 1, 1, tzinfo=timezone.utc)
    newer = datetime(2026, 6, 1, tzinfo=timezone.utc)
    moments = [
        _moment(
            moment_type="TEAM_OPERATIONS",
            status="ACTIVE",
            title="older active",
            updated_at=older,
        ),
        _moment(
            moment_type="TEAM_OPERATIONS",
            status="ACTIVE",
            title="newest active",
            updated_at=newer,
        ),
    ]
    latest = svc._latest_by_code(moments)  # type: ignore[arg-type]
    assert latest["TEAM_OPERATIONS"].title == "newest active"


def test_dimension_cards_is_active_prefers_active_not_draft():
    svc = _svc()
    moments = [
        _moment(moment_type="TEAM_OPERATIONS", status="DRAFT", title="draft"),
        _moment(moment_type="TEAM_OPERATIONS", status="ACTIVE", title="active team"),
        _moment(moment_type="BUSINESS_RUNWAY", status="ACTIVE", title="runway"),
        _moment(moment_type="BUSINESS_OPERATIONS", status="ACTIVE", title="ops"),
    ]
    latest = svc._latest_by_code(moments)  # type: ignore[arg-type]
    cards = svc._dimension_cards(latest)
    by_code = {c.moment_type_code: c for c in cards}
    assert by_code["TEAM_OPERATIONS"].is_active is True
    assert by_code["TEAM_OPERATIONS"].linked_moment_status == "ACTIVE"
    assert by_code["BUSINESS_RUNWAY"].is_active is True
    assert by_code["BUSINESS_OPERATIONS"].is_active is True
    assert set(_SWITCHER_ACTIVE_STATUSES) == {"ACTIVE", "PAUSED", "COMPLETED"}


def test_map_moment_inventory_includes_all_visible():
    svc = _svc()
    moments = [
        _moment(moment_type="TEAM_OPERATIONS", status="ACTIVE", title="team"),
        _moment(moment_type="BUSINESS_RUNWAY", status="ACTIVE", title="runway"),
        _moment(moment_type="BUSINESS_OPERATIONS", status="ACTIVE", title="ops"),
        _moment(moment_type="TEAM_OPERATIONS", status="DRAFT", title="draft"),
    ]
    mapped = [svc._map_moment(m) for m in moments]  # type: ignore[arg-type]
    assert len(mapped) == 4
    active_codes = {
        m.moment_type_code for m in mapped if (m.status or "").upper() == "ACTIVE"
    }
    assert active_codes == {
        "TEAM_OPERATIONS",
        "BUSINESS_RUNWAY",
        "BUSINESS_OPERATIONS",
    }
