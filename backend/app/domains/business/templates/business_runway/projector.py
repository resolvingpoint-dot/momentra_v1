"""Business Runway analytics projector — deterministic in-memory bundle (no SQL writes)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.domains.business.templates.business_runway.context import RunwayContext


@dataclass
class RunwayProjectionBundle:
    attention_items: list[dict]
    signal_items: list[dict]
    recommended_action: dict | None
    trend_items: list[dict]


def _change_percent(current: int, prior: int) -> float:
    if prior <= 0:
        return float(current * 100) if current > 0 else 0.0
    return round(((current - prior) / prior) * 100, 2)


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _event_window_count(activities: list[dict], action_type: str, start: datetime, end: datetime) -> int:
    count = 0
    start_utc = _as_utc(start)
    end_utc = _as_utc(end)
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
        if start_utc <= _as_utc(occurred) < end_utc:
            count += 1
    return count


class RunwayProjector:
    def refresh(self, ctx: RunwayContext) -> RunwayProjectionBundle:
        return RunwayProjectionBundle(
            attention_items=self._build_attention(ctx),
            signal_items=self._build_signals(ctx),
            recommended_action=self._build_recommended_action(ctx),
            trend_items=self._build_trends(ctx),
        )

    def _build_attention(self, ctx: RunwayContext) -> list[dict]:
        items: list[dict] = []
        threshold = float(ctx.alert_threshold_months or 6)
        if ctx.runway_months is not None and ctx.runway_months < threshold:
            items.append(
                {
                    "kind": "low_runway",
                    "label": f"{ctx.runway_months:.1f} months runway",
                    "count": 1,
                    "severity": "critical" if ctx.runway_months < 1 else "high",
                    "description": f"Below alert threshold of {threshold:.0f} months",
                }
            )
        if ctx.risk_count > 0:
            items.append(
                {
                    "kind": "runway_risks",
                    "label": f"{ctx.risk_count} open risk{'s' if ctx.risk_count != 1 else ''}",
                    "count": ctx.risk_count,
                    "severity": "high" if ctx.risk_count >= 3 else "medium",
                    "description": "Runway risks need review",
                }
            )
        if ctx.collection_rate_percent is not None and ctx.collection_rate_percent < 70:
            items.append(
                {
                    "kind": "collection_rate",
                    "label": f"Collection rate {ctx.collection_rate_percent}%",
                    "count": 1,
                    "severity": "medium",
                    "description": "Collection below target",
                }
            )
        return items

    def _build_signals(self, ctx: RunwayContext) -> list[dict]:
        now = datetime.now(timezone.utc)
        current_start = now - timedelta(days=7)
        prior_start = now - timedelta(days=14)
        activities = list(ctx.activities or [])
        signals: list[dict] = []
        for action_type, label, impact in (
            ("CASH_INFLOW", "Cash inflows", "medium"),
            ("EXPENSE_BURN", "Expense burn", "high"),
            ("FINANCIAL_UPDATE", "Financial updates", "low"),
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

    def _build_recommended_action(self, ctx: RunwayContext) -> dict | None:
        if ctx.risk_count > 0:
            return {
                "action_id": "runway_risk",
                "label": "Review runway risks",
                "reason": "open_risks",
                "cta_label": "Take Action",
                "target_screen": "action_center",
                "priority": "high",
            }
        threshold = float(ctx.alert_threshold_months or 6)
        if ctx.runway_months is not None and ctx.runway_months < threshold:
            return {
                "action_id": "financial_update",
                "label": "Update financial forecast",
                "reason": "low_runway",
                "cta_label": "Take Action",
                "target_screen": "action_center",
                "priority": "high",
            }
        if ctx.cash_available_minor > 0:
            return {
                "action_id": "cash_inflow",
                "label": "Log a cash inflow",
                "reason": "keep_runway_current",
                "cta_label": "Take Action",
                "target_screen": "action_center",
                "priority": "medium",
            }
        return None

    def _build_trends(self, ctx: RunwayContext) -> list[dict]:
        activities = list(ctx.activities or [])
        now = datetime.now(timezone.utc)
        current_start = now - timedelta(days=7)
        trends: list[dict] = []
        for action_type, label in (
            ("CASH_INFLOW", "Inflows"),
            ("EXPENSE_BURN", "Burn"),
            ("FINANCIAL_UPDATE", "Updates"),
        ):
            count = _event_window_count(activities, action_type, current_start, now)
            if count == 0:
                continue
            trends.append(
                {
                    "trend_code": action_type.lower(),
                    "label": label,
                    "count": count,
                    "window_days": 7,
                }
            )
        return trends


def refresh_runway_projections(ctx: RunwayContext) -> RunwayProjectionBundle:
    return RunwayProjector().refresh(ctx)
