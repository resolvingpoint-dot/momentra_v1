"""Activity / timeline view for Team Operations template."""
from __future__ import annotations

from app.domains.business.templates.team_operations.context import TeamOpsContext


def build_activity(ctx: TeamOpsContext) -> dict:
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
                "is_voided": a.get("is_voided", False),
            }
            for a in ctx.activities
            if not a.get("is_voided")
        ],
    }
