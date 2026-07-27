"""Business Operations analytics projector — deterministic in-memory bundle."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.domains.business.templates.business_operations.context import OpsContext


@dataclass
class OpsProjectionBundle:
    attention_items: list[dict]
    signal_items: list[dict]
    recommended_action: dict | None


def _change_percent(current: int, prior: int) -> float:
    if prior <= 0:
        return float(current * 100) if current > 0 else 0.0
    return round(((current - prior) / prior) * 100, 2)


def _event_window_count(activities: list[dict], action_type: str, start: datetime, end: datetime) -> int:
    count = 0
    for a in activities:
        if (a.get("action_type") or "") != action_type:
            continue
        raw = a.get("occurred_at")
        if not raw:
            continue
        try:
            occurred = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            continue
        if start <= occurred < end:
            count += 1
    return count


class OpsProjector:
    def refresh(self, ctx: OpsContext) -> OpsProjectionBundle:
        return OpsProjectionBundle(
            attention_items=self._build_attention(ctx),
            signal_items=self._build_signals(ctx),
            recommended_action=self._build_recommended_action(ctx),
        )

    def _build_attention(self, ctx: OpsContext) -> list[dict]:
        items: list[dict] = []
        if ctx.budget_usage_pct >= 100:
            items.append(
                {
                    "kind": "budget_over",
                    "label": "Budget fully used",
                    "count": 1,
                    "severity": "critical",
                    "description": f"Usage {ctx.budget_usage_pct:.0f}%",
                }
            )
        elif ctx.budget_usage_pct >= 90:
            items.append(
                {
                    "kind": "budget_threshold",
                    "label": "Budget threshold reached",
                    "count": 1,
                    "severity": "high",
                    "description": f"Usage {ctx.budget_usage_pct:.0f}%",
                }
            )
        if ctx.critical_issue_count > 0:
            items.append(
                {
                    "kind": "critical_issues",
                    "label": f"{ctx.critical_issue_count} critical issue"
                    f"{'s' if ctx.critical_issue_count != 1 else ''}",
                    "count": ctx.critical_issue_count,
                    "severity": "high",
                    "description": "Critical issues need review",
                }
            )
        elif ctx.open_issue_count > 0:
            items.append(
                {
                    "kind": "open_issues",
                    "label": f"{ctx.open_issue_count} open issue"
                    f"{'s' if ctx.open_issue_count != 1 else ''}",
                    "count": ctx.open_issue_count,
                    "severity": "medium",
                    "description": "Open operational issues",
                }
            )
        if ctx.overdue_approval_count > 0:
            items.append(
                {
                    "kind": "overdue_approvals",
                    "label": f"{ctx.overdue_approval_count} overdue approval"
                    f"{'s' if ctx.overdue_approval_count != 1 else ''}",
                    "count": ctx.overdue_approval_count,
                    "severity": "high",
                    "description": "Approvals past due date",
                }
            )
        elif ctx.pending_approvals > 0:
            items.append(
                {
                    "kind": "pending_approvals",
                    "label": f"{ctx.pending_approvals} pending approval"
                    f"{'s' if ctx.pending_approvals != 1 else ''}",
                    "count": ctx.pending_approvals,
                    "severity": "medium",
                    "description": "Approvals awaiting decision",
                }
            )
        return items

    def _build_signals(self, ctx: OpsContext) -> list[dict]:
        now = datetime.now(timezone.utc)
        current_start = now - timedelta(days=7)
        prior_start = now - timedelta(days=14)
        activities = list(ctx.activities or [])
        signals: list[dict] = []
        for action_type, label, impact in (
            ("SPEND_ENTRY", "Spend activity", "high"),
            ("ISSUE_RISK", "Issue activity", "high"),
            ("OPERATIONAL_IMPROVEMENT", "Improvements", "medium"),
            ("OPS_APPROVAL_REQUEST", "Approvals", "medium"),
            ("VENDOR_UPDATE", "Vendor updates", "low"),
        ):
            current = _event_window_count(activities, action_type, current_start, now)
            prior = _event_window_count(activities, action_type, prior_start, current_start)
            if current == 0 and prior == 0:
                continue
            change = _change_percent(current, prior)
            direction = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
            signals.append(
                {
                    "signal_type": action_type.lower(),
                    "title": f"{label} {direction}",
                    "summary": f"{current} in last 7 days vs {prior} prior week",
                    "change_percent": change,
                    "impact_level": impact,
                }
            )
        return signals[:3]

    def _build_recommended_action(self, ctx: OpsContext) -> dict | None:
        if ctx.critical_issue_count > 0 or ctx.open_issue_count > 0:
            return {
                "action_id": "issue_risk",
                "renderer_id": "ops.issue",
                "title": "Review open operational issues",
                "subtitle": f"{ctx.open_issue_count} open",
                "reason": "open_issues",
                "metadata": {"open_issue_count": ctx.open_issue_count},
            }
        if ctx.overdue_approval_count > 0 or ctx.pending_approvals > 0:
            return {
                "action_id": "ops_approval",
                "renderer_id": "ops.approval",
                "title": "Clear approval backlog",
                "subtitle": f"{ctx.pending_approvals} pending",
                "reason": "pending_approvals",
                "metadata": {"pending_approval_count": ctx.pending_approvals},
            }
        if ctx.budget_usage_pct >= 90:
            return {
                "action_id": "spend_entry",
                "renderer_id": "ops.spend_entry",
                "title": "Review budget usage",
                "subtitle": f"{ctx.budget_usage_pct:.0f}% used",
                "reason": "budget_threshold",
                "metadata": {"budget_usage_percent": ctx.budget_usage_pct},
            }
        return None


def refresh_ops_projections(ctx: OpsContext) -> OpsProjectionBundle:
    return OpsProjector().refresh(ctx)
