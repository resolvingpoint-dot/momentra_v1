"""Activity timeline for Business Runway template."""
from __future__ import annotations

from app.domains.business.templates.business_runway.context import RunwayContext


def build_activity(ctx: RunwayContext) -> dict:
    return {
        "moment_id": str(ctx.moment_id),
        "moment_type": ctx.moment_type,
        "activity_count": ctx.activity_count,
        "items": [
            {
                "event_id": str(a.get("event_id") or ""),
                "action_type": a.get("action_type", ""),
                "title": a.get("title", ""),
                "subtitle": a.get("subtitle"),
                "occurred_at": str(a.get("occurred_at") or ""),
            }
            for a in ctx.activities
            if not a.get("is_voided")
        ],
    }
