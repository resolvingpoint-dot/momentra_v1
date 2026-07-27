"""Derive Ops pulse signals from activity windows (fallback when projector absent)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.domains.business.templates.business_operations.context import OpsContext


def derive_signals(ctx: OpsContext) -> list[dict]:
    now = datetime.now(timezone.utc)
    week = now - timedelta(days=7)
    counts: dict[str, int] = {}
    for a in ctx.activities or []:
        at = a.get("action_type") or ""
        raw = a.get("occurred_at")
        if not raw:
            continue
        try:
            occurred = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            continue
        if occurred >= week:
            counts[at] = counts.get(at, 0) + 1

    signals = []
    if counts.get("SPEND_ENTRY"):
        signals.append(
            {
                "signal_type": "spend_entry",
                "title": "Spend activity",
                "summary": f"{counts['SPEND_ENTRY']} spend entries in 7 days",
                "change_percent": None,
                "severity": "medium",
            }
        )
    if counts.get("ISSUE_RISK"):
        signals.append(
            {
                "signal_type": "issue_risk",
                "title": "Issue activity",
                "summary": f"{counts['ISSUE_RISK']} issues in 7 days",
                "change_percent": None,
                "severity": "high",
            }
        )
    if ctx.budget_usage_pct >= 90:
        signals.append(
            {
                "signal_type": "budget_usage",
                "title": "Budget usage elevated",
                "summary": f"{ctx.budget_usage_pct:.0f}% of budget used",
                "change_percent": None,
                "severity": "high",
            }
        )
    return signals[:3]
