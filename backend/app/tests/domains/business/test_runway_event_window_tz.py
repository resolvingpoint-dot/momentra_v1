"""Regression: Runway signal windows tolerate naive vs aware occurred_at."""
from datetime import datetime, timedelta, timezone

from app.domains.business.templates.business_runway.projector import _event_window_count


def test_event_window_count_mixed_tz_naive_and_aware():
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    activities = [
        {
            "action_type": "cash_in",
            "occurred_at": (now - timedelta(days=1)).replace(tzinfo=None).isoformat(),
        },
        {
            "action_type": "cash_in",
            "occurred_at": (now - timedelta(days=2)).isoformat().replace("+00:00", "Z"),
        },
        {
            "action_type": "cash_out",
            "occurred_at": (now - timedelta(days=1)).isoformat(),
        },
    ]
    assert _event_window_count(activities, "cash_in", start, now) == 2
    assert _event_window_count(activities, "cash_out", start, now) == 1
