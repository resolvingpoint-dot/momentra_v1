"""Pure transform: ProjectionContext → LifeProjection (Personal Life aggregate)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.domains.personal.catalog import moment_type_name, normalize_moment_type_code
from app.domains.personal.future_building.signals import derive_future_signals, life_dimension_boosts
from app.domains.personal.templates.lifestyle.signals import derive_lifestyle_signals, life_dimension_boosts as lifestyle_life_boosts
from app.domains.personal.templates.relationships.signals import (
    derive_relationships_signals,
    life_dimension_boosts as relationships_life_boosts,
)
from app.domains.personal.projection.context import ProjectionContext
from app.domains.personal.models import (
    PersonalFutureBuildingProfile,
    PersonalLifestyleProfile,
    PersonalRelationshipsProfile,
)

_TYPE_ORDER = ["LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS"]
_TYPE_COLORS = {
    "LIFE_OPERATIONS": "primary",
    "FUTURE_BUILDING": "secondary",
    "LIFESTYLE": "tertiary",
    "RELATIONSHIPS": "error",
}
_DIM_LABELS = {
    "STRESS": "Stress",
    "CAPACITY": "Capacity",
    "GROWTH": "Growth",
    "FULFILLMENT": "Fulfillment",
}


def _score(value: Any, default: int = 70) -> int:
    if value is None:
        return default
    return max(0, min(100, int(round(float(value)))))


def build_life_projection(ctx: ProjectionContext) -> dict[str, Any]:
    health = ctx.life_health
    agg = ctx.life_aggregate
    scores = ctx.runtime_scores_by_type

    life_score = _score(health.life_health_score if health else (agg.life_health_score if agg else None))
    delta_month = (
        int(round(float(health.monthly_delta_score)))
        if health and health.monthly_delta_score is not None
        else None
    )
    status_label = (
        health.health_status_label
        if health
        else ("Balanced" if life_score >= 70 else "Building")
    )
    insight_quote = (
        health.summary_text
        if health and health.summary_text
        else "Your life dimensions are weaving together through daily signals."
    )

    satellite_scores = [
        {
            "moment_type_code": code,
            "label": moment_type_name(code),
            "score": scores.get(code),
            "color_token": _TYPE_COLORS.get(code, "primary"),
        }
        for code in _TYPE_ORDER
        if code in scores or any(
            normalize_moment_type_code(m.moment_type or "") == code for m in ctx.active_moments
        )
    ]

    life_health = {
        "life_score": life_score,
        "status_label": status_label,
        "delta_month": delta_month,
        "insight_quote": insight_quote,
        "satellite_scores": satellite_scores,
    }

    dominant_code = (agg.dominant_emotion or "calm").lower() if agg else "calm"
    dominant_label = agg.dominant_emotion if agg and agg.dominant_emotion else "Calm"
    dominant_pct = _score(agg.dominant_emotion_pct if agg else 42, 42)

    emotional_trend = {
        "window_label": "Last 4 Weeks",
        "series": _emotional_trend_series(agg),
        "is_sparse": agg is None,
    }

    dominant_emotion = {
        "dominant_code": dominant_code,
        "dominant_label": dominant_label,
        "dominant_percent": dominant_pct,
        "breakdown": _emotion_breakdown(ctx),
        "footer_text": (
            agg.life_intelligence_summary
            if agg and agg.life_intelligence_summary
            else "Emotional tone follows recovery and connection patterns."
        ),
        "is_sparse": agg is None,
    }

    balance_model = {
        "subtitle": "How your life dimensions are balancing",
        "dimensions": _balance_dimensions(agg, _merged_dimension_boosts(ctx)),
    }

    connections = [
        {
            "from_type_code": c.source_moment_type_code,
            "from_label": moment_type_name(c.source_moment_type_code),
            "to_type_code": c.target_moment_type_code,
            "to_label": moment_type_name(c.target_moment_type_code),
            "summary": c.connection_summary,
            "sentiment": c.signal_label,
        }
        for c in ctx.life_connections[:6]
    ]

    drift_alert = None
    if ctx.drift_alerts:
        d = ctx.drift_alerts[0]
        drift_alert = {
            "title": d.drift_title,
            "body": d.drift_message,
            "cta_label": d.recommended_action or "Review balance",
        }

    leverage = None
    if agg and agg.leverage_area:
        leverage = {
            "title": f"Leverage: {agg.leverage_area}",
            "body": "Small shifts here can lift multiple life dimensions.",
            "cta_label": "Take action",
            "action_code": "RECOVERY",
            "expected_impact": [
                {
                    "dimension_code": "CAPACITY",
                    "label": "Capacity",
                    "delta": 8,
                }
            ],
        }

    happiness = {
        "top_drivers": [agg.happiness_driver] if agg and agg.happiness_driver else ["Recovery", "Connection"],
        "highest_return": [
            {"label": "REC", "height_fraction": 1.0},
            {"label": "PLAN", "height_fraction": 0.7},
            {"label": "MOOD", "height_fraction": 0.45},
        ],
        "lowest_return": [
            {"label": "SCROLL", "height_fraction": 0.35},
            {"label": "LATE", "height_fraction": 0.25},
        ],
        "footer_text": "Behaviors with the highest life return are showing up in your logs.",
    }

    life_rec = ctx.life_recommendations[0] if ctx.life_recommendations else None
    intelligence = {
        "preamble": "Life Intelligence",
        "insight_text": (
            agg.life_intelligence_summary
            if agg and agg.life_intelligence_summary
            else (
                life_rec.recommendation_description
                if life_rec
                else "Your system is learning how your moments connect."
            )
        ),
        "cta_label": life_rec.recommended_action if life_rec else "Reflect",
        "cta_action_code": "REFLECTION",
    }

    monthly_changes = [
        {
            "change_code": (m.dimension_code or m.change_label).lower().replace(" ", "_"),
            "label": m.change_label,
            "sublabel": m.moment_type_code or "All moments",
            "delta_percent": int(round(float(m.change_value_pct))),
            "direction": m.direction if m.direction in {"UP", "DOWN"} else "UP",
        }
        for m in ctx.monthly_changes[:4]
    ]

    journey = [
        {
            "period_label": e.journey_month.strftime("%b %Y"),
            "summary": e.journey_description or e.journey_title,
        }
        for e in ctx.journey_events[:6]
    ]

    future_signals_block = _future_signals_for_life(ctx)
    lifestyle_signals_block = _lifestyle_signals_for_life(ctx)

    return {
        "life_health": life_health,
        "emotional_trend": emotional_trend,
        "dominant_emotion": dominant_emotion,
        "balance_model": balance_model,
        "connections": connections,
        "drift_alert": drift_alert,
        "leverage": leverage,
        "happiness": happiness,
        "intelligence": intelligence,
        "monthly_changes": monthly_changes,
        "journey": journey,
        "future_signals": future_signals_block,
        "lifestyle_signals": lifestyle_signals_block,
        "quick_actions": [
            {"action_code": "RECOVERY", "label": "Log Recovery", "event_type": "RECOVERY", "color_token": "primary"},
            {"action_code": "MOOD", "label": "Log Mood", "event_type": "MOOD", "color_token": "tertiary"},
            {"action_code": "REFLECTION", "label": "Reflect", "event_type": "REFLECTION", "color_token": "secondary"},
        ],
        "footer_quote": insight_quote,
    }


def _emotional_trend_series(agg: Any | None) -> list[dict[str, Any]]:
    base_conn = _score(agg.relationship_health_score if agg else None, 65)
    base_joy = _score(agg.fulfillment_score if agg else None, 60)
    base_stress = 100 - _score(agg.stress_score if agg else None, 35)
    base_ful = _score(agg.fulfillment_score if agg else None, 62)
    labels = ["Wk 1", "Wk 2", "Wk 3", "Wk 4"]
    momentum = _score(agg.emotional_momentum_score if agg else 0, 0)
    series = []
    for i, label in enumerate(labels):
        drift = int(momentum * (i + 1) / 4)
        series.append(
            {
                "week_label": label,
                "connection": max(0, min(100, base_conn + drift)),
                "joy": max(0, min(100, base_joy + drift // 2)),
                "stress": max(0, min(100, base_stress - drift // 2)),
                "fulfillment": max(0, min(100, base_ful + drift // 3)),
            }
        )
    return series


def _emotion_breakdown(ctx: ProjectionContext) -> list[dict[str, Any]]:
    if ctx.emotional_dna:
        return [
            {
                "emotion_code": s.emotion_name.lower(),
                "label": s.emotion_name,
                "percent": _score(s.emotion_pct),
                "color_token": "primary" if i == 0 else "tertiary" if i == 1 else "error",
            }
            for i, s in enumerate(sorted(ctx.emotional_dna, key=lambda x: x.emotion_rank)[:4])
        ]
    return [
        {"emotion_code": "calm", "label": "Calm", "percent": 42, "color_token": "primary"},
        {"emotion_code": "relief", "label": "Relief", "percent": 33, "color_token": "tertiary"},
    ]


def _balance_dimensions(
    agg: Any | None,
    boosts: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    boosts = boosts or {}
    if agg is None:
        base_scores = {
            "STRESS": 70,
            "CAPACITY": 70,
            "GROWTH": 70,
            "FULFILLMENT": 70,
        }
    else:
        base_scores = {
            "STRESS": 100 - _score(agg.stress_score),
            "CAPACITY": _score(agg.capacity_score),
            "GROWTH": _score(agg.growth_dimension_score or agg.growth_score),
            "FULFILLMENT": _score(agg.fulfillment_dimension_score or agg.fulfillment_score),
        }

    capacity_adj = boosts.get("CAPACITY", 0)
    growth_adj = boosts.get("GROWTH", 0)
    fulfillment_adj = boosts.get("FULFILLMENT", 0)
    stress_adj = boosts.get("STRESS", 0)

    adjusted = {
        "STRESS": max(0, min(100, base_scores["STRESS"] + stress_adj)),
        "CAPACITY": max(0, min(100, base_scores["CAPACITY"] + capacity_adj)),
        "GROWTH": max(0, min(100, base_scores["GROWTH"] + growth_adj)),
        "FULFILLMENT": max(0, min(100, base_scores["FULFILLMENT"] + fulfillment_adj)),
    }

    drivers = {
        "STRESS": "Stress load",
        "CAPACITY": "Recovery capacity",
        "GROWTH": "Growth momentum",
        "FULFILLMENT": "Fulfillment",
    }
    dims = []
    for code in ("STRESS", "CAPACITY", "GROWTH", "FULFILLMENT"):
        score = adjusted[code]
        badge = "Strong" if score >= 75 else "Stable" if score >= 60 else "Watch"
        token = "primary" if score >= 75 else "tertiary" if score >= 60 else "error"
        dims.append(
            {
                "dimension_code": code,
                "label": _DIM_LABELS[code],
                "score": score,
                "badge_label": badge,
                "badge_color_token": token,
                "driver_text": drivers[code],
            }
        )
    return dims


def _merged_dimension_boosts(ctx: ProjectionContext) -> dict[str, int]:
    """Merge template signal boosts into shared Life dimension scores."""
    capacity = 0
    growth = 0
    fulfillment = 0
    stress = 0

    fb = _future_signals_for_life(ctx)
    if fb:
        growth += int((fb.get("growth_momentum", 0) - 50) * 0.15)
        fulfillment += int((fb.get("fulfillment", 0) - 50) * 0.1)

    ls = _lifestyle_signals_for_life(ctx)
    if ls:
        fulfillment += int((ls.get("fulfillment", 0) - 50) * 0.12)
        capacity += int((ls.get("vitality", 0) - 50) * 0.08)

    rs = _relationships_dimension_boosts_for_life(ctx)
    if rs:
        capacity += int((rs.get("resilience", 0) - 50) * 0.15)
        growth += int((rs.get("growth", 0) - 50) * 0.12)
        fulfillment += int((rs.get("fulfillment", 0) - 50) * 0.1)
        fulfillment += int((rs.get("belonging", 0) - 50) * 0.08)
        fulfillment += int((rs.get("connection", 0) - 50) * 0.08)
        stress -= int((rs.get("connection", 0) - 50) * 0.05)

    return {
        "CAPACITY": capacity,
        "GROWTH": growth,
        "FULFILLMENT": fulfillment,
        "STRESS": stress,
    }


def _future_signals_for_life(ctx: ProjectionContext) -> dict[str, Any] | None:
    mctx = ctx.moments_by_type.get("FUTURE_BUILDING")
    if mctx is None:
        return None
    profile = mctx.profile if isinstance(mctx.profile, PersonalFutureBuildingProfile) else None
    learning_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "LEARNING"
    )
    milestone_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "MILESTONE"
    )
    opportunity_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "OPPORTUNITY"
    )
    signals = derive_future_signals(
        runtime=mctx.runtime,
        metrics=mctx.metrics,
        profile=profile,
        timeline_count=mctx.timeline_count,
        learning_count=learning_count,
        milestone_count=milestone_count,
        opportunity_count=opportunity_count,
    )
    return life_dimension_boosts(signals)


def _lifestyle_signals_for_life(ctx: ProjectionContext) -> dict[str, Any] | None:
    mctx = ctx.moments_by_type.get("LIFESTYLE")
    if mctx is None:
        return None
    profile = mctx.profile if isinstance(mctx.profile, PersonalLifestyleProfile) else None
    experience_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "EXPERIENCE"
    )
    wellbeing_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "WELLBEING"
    )
    discovery_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "DISCOVERY"
    )
    expression_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() in {"EXPRESSION", "CREATIVE"}
    )
    signals = derive_lifestyle_signals(
        runtime=mctx.runtime,
        metrics=mctx.metrics,
        profile=profile,
        timeline_count=mctx.timeline_count,
        experience_count=experience_count,
        wellbeing_count=wellbeing_count,
        discovery_count=discovery_count,
        expression_count=expression_count,
    )
    return lifestyle_life_boosts(signals)


def _relationships_dimension_boosts_for_life(ctx: ProjectionContext) -> dict[str, Any] | None:
    mctx = ctx.moments_by_type.get("RELATIONSHIPS")
    if mctx is None:
        return None
    profile = (
        mctx.profile if isinstance(mctx.profile, PersonalRelationshipsProfile) else None
    )
    connection_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "CONNECTION"
    )
    support_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "SUPPORT"
    )
    experience_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "SHARED_EXPERIENCE"
    )
    investment_count = sum(
        1 for t in mctx.timeline if (t.event_type or "").upper() == "RELATIONSHIP_INVESTMENT"
    )
    adjust_count = sum(
        1
        for t in mctx.timeline
        if (t.event_type or "").upper() in {"ADJUST", "RELATIONSHIP_ADJUST"}
    )
    signals = derive_relationships_signals(
        runtime=mctx.runtime,
        metrics=mctx.metrics,
        profile=profile,
        timeline_count=mctx.timeline_count,
        connection_count=connection_count,
        support_count=support_count,
        experience_count=experience_count,
        investment_count=investment_count,
        adjust_count=adjust_count,
    )
    return relationships_life_boosts(signals)
