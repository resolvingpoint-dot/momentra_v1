"""Pure transform: ProjectionContext → MomentProjection."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.life_operations.activity_mapper import (
    map_timeline_to_recent_item,
    money_events_by_quick_add,
)
from app.domains.personal.projection.context import MomentContext, ProjectionContext

_TYPE_LABELS = {
    "LIFE_OPERATIONS": "Life Operations",
    "FUTURE_BUILDING": "Future Building",
    "LIFESTYLE": "Lifestyle",
    "RELATIONSHIPS": "Relationships",
}

_ICON_BY_HIGHLIGHT = {
    "recovery": "recovery",
    "pressure": "pressure",
    "stability": "stability",
    "momentum": "momentum",
}


def _int_score(value: Any, default: int = 70) -> int:
    if value is None:
        return default
    return max(0, min(100, int(round(float(value)))))


def _metric_value(metrics: list, code: str, default: int) -> int:
    upper = code.upper()
    for m in metrics:
        if (m.metric_code or "").upper() == upper and m.metric_value is not None:
            return _int_score(m.metric_value, default)
    return default


def _status_band(score: int) -> str:
    if score >= 80:
        return "THRIVING"
    if score >= 65:
        return "STABLE"
    return "BUILDING"


def _recovery_count(timeline: list) -> int:
    return sum(
        1
        for t in timeline
        if (t.event_type or "").upper() in {"RECOVERY", "MOOD", "REFLECTION"}
    )


def build_moment_projection(
    ctx: ProjectionContext, moment_type_code: str
) -> dict[str, Any] | None:
    code = normalize_moment_type_code(moment_type_code)
    mctx = ctx.moments_by_type.get(code)
    if mctx is None:
        return None

    runtime = mctx.runtime
    ops_index = _int_score(runtime.primary_score if runtime else None, 70)
    recovery = _metric_value(mctx.metrics, "RECOVERY_SCORE", ops_index)
    status = _status_band(ops_index)
    band_label = runtime.runtime_state_label if runtime else "Stable"
    insight = (
        runtime.runtime_summary
        if runtime and runtime.runtime_summary
        else "Your daily rhythm is building through recovery, discipline, and awareness."
    )

    activated = mctx.moment.updated_at
    days_active = 1
    if activated:
        when = activated
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        days_active = max(1, (datetime.now(timezone.utc) - when).days + 1)

    recovery_events = _recovery_count(mctx.timeline)
    adjustments = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() in {"ADJUST", "COMMITMENT"}
    )
    pressure_reduced = max(0, min(40, recovery_events * 4))

    journey_hero = {
        "journey_score": ops_index,
        "status_band": status,
        "phases": [
            {"phase_id": "stable", "label": "Stable", "is_active": status == "STABLE"},
            {"phase_id": "structured", "label": "Structured", "is_active": status == "BUILDING"},
            {"phase_id": "thriving", "label": "Thriving", "is_active": status == "THRIVING"},
        ],
        "insight_body": insight,
        "days_active": days_active,
        "recovery_events": recovery_events,
        "adjustments_made": adjustments,
        "pressure_reduced_percent": pressure_reduced,
    }

    money_by_qa = money_events_by_quick_add(mctx.money_events)
    journey_timeline = [
        map_timeline_to_recent_item(
            item, money=money_by_qa.get(item.quick_add_event_id), catalog=ctx.catalog
        )
        for item in mctx.timeline[:12]
    ]

    money_journey = _build_money_journey(mctx, ctx.catalog)

    best_moments = [
        {
            "card_id": str(h.moment_highlight_id),
            "title": h.highlight_title,
            "period_label": h.impact_label or h.highlight_type,
            "impact_lines": [h.impact_label] if h.impact_label else [],
            "icon": _ICON_BY_HIGHLIGHT.get(
                (h.highlight_type or "").lower(), "momentum"
            ),
        }
        for h in mctx.highlights[:6]
    ]
    if not best_moments and mctx.timeline:
        best_moments = [
            {
                "card_id": str(mctx.timeline[0].timeline_id),
                "title": "Recent activity",
                "period_label": "This week",
                "impact_lines": ["Signals logged"],
                "icon": "momentum",
            }
        ]

    turning_points = [
        {
            "turning_point_id": str(tp.turning_point_id),
            "title": tp.turning_point_title,
            "subtitle": tp.turning_point_description or tp.turning_point_type,
            "icon": (tp.turning_point_type or "milestone").lower(),
        }
        for tp in mctx.turning_points[:6]
    ]

    return {
        "moment_type_code": code,
        "journey_hero": journey_hero,
        "journey_timeline": journey_timeline,
        "money_journey": money_journey,
        "best_moments": best_moments,
        "turning_points": turning_points,
    }


def _build_money_journey(mctx: MomentContext, catalog: Any) -> dict[str, Any]:
    from app.domains.personal.life_operations.pulse_mapper import _money_minor

    now = datetime.now(timezone.utc).date()
    months: list[tuple[str, datetime.date]] = []
    for i in range(5, -1, -1):
        d = now.replace(day=1) - timedelta(days=30 * i)
        months.append((d.strftime("%b"), d.replace(day=1)))

    by_month: dict[str, int] = defaultdict(int)
    category_totals: dict[str, int] = defaultdict(int)
    for ev in mctx.money_events:
        if (ev.direction or "").upper() != "DEBIT":
            continue
        minor = _money_minor(ev)
        if ev.event_date:
            key = ev.event_date.strftime("%Y-%m")
            by_month[key] += minor
        cat = (ev.category_code or "other").lower()
        category_totals[cat] += minor

    series = []
    for cat, total in sorted(category_totals.items(), key=lambda x: -x[1])[:3]:
        points = []
        for label, month_start in months:
            key = month_start.strftime("%Y-%m")
            points.append(
                {
                    "date": month_start.isoformat(),
                    "value_minor": by_month.get(key, 0) // max(1, len(category_totals)),
                }
            )
        series.append(
            {
                "category_id": cat,
                "category_name": cat.replace("_", " ").title(),
                "points": points,
            }
        )

    total_spend = sum(by_month.values())
    month_vals = list(by_month.items())
    highest = max(month_vals, key=lambda x: x[1], default=("—", 0))
    lowest = min(month_vals, key=lambda x: x[1], default=("—", 0)) if month_vals else ("—", 0)

    return {
        "title": "Essential Spend Journey",
        "period_label": "Last 6 Months",
        "series": series,
        "total_spend_minor": total_spend,
        "highest_month": {"label": highest[0], "amount_minor": highest[1]},
        "lowest_month": {"label": lowest[0], "amount_minor": lowest[1]},
    }
