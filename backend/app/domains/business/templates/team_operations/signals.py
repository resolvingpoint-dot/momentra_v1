"""Sparse signals for Team Operations template."""
from __future__ import annotations

from app.domains.business.templates.team_operations.context import TeamOpsContext


def derive_signals(ctx: TeamOpsContext) -> list[dict]:
    signals: list[dict] = []
    open_issues = int(getattr(ctx, "open_issues", 0) or 0)
    pending_approvals = int(getattr(ctx, "pending_approvals", 0) or 0)
    escalation_count = int(getattr(ctx, "escalation_count", 0) or 0)
    if open_issues > 0:
        signals.append({
            "signal_type": "open_issues",
            "label": f"{open_issues} open issue{'s' if open_issues != 1 else ''}",
            "severity": "medium" if open_issues < 3 else "high",
        })
    if pending_approvals > 0:
        signals.append({
            "signal_type": "pending_approvals",
            "label": f"{pending_approvals} pending approval{'s' if pending_approvals != 1 else ''}",
            "severity": "low",
        })
    if escalation_count > 0:
        signals.append({
            "signal_type": "escalations",
            "label": f"{escalation_count} active escalation{'s' if escalation_count != 1 else ''}",
            "severity": "high",
        })
    return signals
