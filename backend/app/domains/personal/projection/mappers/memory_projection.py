"""Pure transform: ProjectionContext → MemoryProjection (Personal Intelligence)."""
from __future__ import annotations

from typing import Any

from app.domains.personal.catalog import moment_type_name, normalize_moment_type_code
from app.domains.personal.projection.context import ProjectionContext

_TYPE_ORDER = ["LIFE_OPERATIONS", "FUTURE_BUILDING", "LIFESTYLE", "RELATIONSHIPS"]


def _pick_identity(ctx: ProjectionContext) -> Any | None:
    for code in _TYPE_ORDER:
        for row in ctx.identity_snapshots:
            if row.moment_type_code == code:
                return row
    return ctx.identity_snapshots[0] if ctx.identity_snapshots else None


def _trend_label(row: Any) -> str:
    if row.confidence_trend_pct is None:
        return "Building stability"
    pct = float(row.confidence_trend_pct)
    if pct > 0:
        return f"↑ {abs(int(pct))}% stronger than 3 months ago"
    if pct < 0:
        return f"↓ {abs(int(pct))}% vs 3 months ago"
    return "Holding steady"


def build_memory_projection(
    ctx: ProjectionContext, moment_type_code: str | None = None
) -> dict[str, Any]:
    code = normalize_moment_type_code(moment_type_code or "LIFE_OPERATIONS")
    identity_row = _pick_identity(ctx)

    identity_snapshot = {
        "title": identity_row.identity_title if identity_row else "Structured Stabilizer",
        "trend_label": _trend_label(identity_row) if identity_row else "Building patterns",
        "confidence_percent": int(float(identity_row.confidence_pct)) if identity_row else 70,
        "body": (
            identity_row.identity_summary
            if identity_row and identity_row.identity_summary
            else "You are building balance through recovery and intentional choices."
        ),
        "image_url": None,
    }

    pattern_row = ctx.memory_patterns[0] if ctx.memory_patterns else None
    core_pattern = {
        "pattern_confidence_percent": int(float(pattern_row.pattern_confidence_pct or pattern_row.confidence_score))
        if pattern_row
        else 75,
        "nodes": [
            {
                "node_id": "recovery",
                "icon": "eco",
                "label": "Recovery",
                "subtitle": "Rebuild energy",
            },
            {
                "node_id": "stress",
                "icon": "psychology_alt",
                "label": "Lower Stress",
                "subtitle": "Calm mind",
            },
            {
                "node_id": "decisions",
                "icon": "verified",
                "label": "Better Decisions",
                "subtitle": "Make wiser choices",
            },
        ],
    }

    positive = [
        d
        for d in ctx.driver_rankings
        if d.driver_category in {"POSITIVE", "CAPACITY_DRIVER", "GROWTH_DRIVER"}
    ]
    negative = [d for d in ctx.driver_rankings if d.driver_category == "NEGATIVE"]
    highest_return = [d for d in ctx.driver_rankings if d.driver_category == "HIGHEST_RETURN"]

    best_drivers = [
        {
            "rank": d.driver_rank,
            "label": d.driver_name,
            "impact_percent": int(float(d.impact_pct or 0)),
            "impact_description": d.impact_description,
        }
        for d in sorted(positive, key=lambda x: x.driver_rank)[:3]
    ]
    if not best_drivers:
        best_drivers = [
            {"rank": 1, "label": "Recovery", "impact_percent": 85, "impact_description": "Creates stability"},
            {"rank": 2, "label": "Planning", "impact_percent": 72, "impact_description": "Calmer decisions"},
        ]

    lowest_drivers = [
        {
            "rank": d.driver_rank,
            "label": d.driver_name,
            "impact_percent": int(float(d.impact_pct or 0)),
            "impact_description": d.impact_description,
        }
        for d in sorted(negative, key=lambda x: x.driver_rank)[:3]
    ]

    return_behaviors = highest_return[0] if highest_return else None
    highest_return_behaviors = {
        "title": return_behaviors.driver_name if return_behaviors else "Recovery Block",
        "roi_label": f"{float(return_behaviors.return_multiplier or 8.7):.1f}x Stability Return"
        if return_behaviors and return_behaviors.return_multiplier
        else "8.7x Stability Return",
        "bars": [
            {"behavior_code": "rec", "label": "REC", "height_fraction": 1.0},
            {"behavior_code": "plan", "label": "PLAN", "height_fraction": 0.65},
            {"behavior_code": "mood", "label": "MOOD", "height_fraction": 0.45},
            {"behavior_code": "rest", "label": "REST", "height_fraction": 0.3},
        ],
    }

    segments = sorted(ctx.emotional_dna, key=lambda x: x.emotion_rank)[:4]
    dominant = segments[0].emotion_name if segments else "Calm"
    emotional_dna = {
        "dominant_label": dominant,
        "segments": [
            {
                "segment_id": s.emotion_name.lower(),
                "label": s.emotion_name,
                "percent": int(float(s.emotion_pct)),
                "color_token": "primary" if i == 0 else "tertiary" if i == 1 else "error",
            }
            for i, s in enumerate(segments)
        ]
        or [
            {"segment_id": "calm", "label": "Calm", "percent": 42, "color_token": "primary"},
            {"segment_id": "relief", "label": "Relief", "percent": 33, "color_token": "tertiary"},
        ],
        "insight_body": (
            segments[0].dna_summary
            if segments and segments[0].dna_summary
            else "Your stability is anchored in recovery and intentional pacing."
        ),
    }

    behavioral_patterns = [
        {
            "pattern_id": str(p.memory_pattern_id),
            "icon": "event_available",
            "title": p.pattern_title,
            "subtitle": p.pattern_description,
            "confidence_percent": int(float(p.confidence_score)),
        }
        for p in ctx.memory_patterns[:5]
    ]

    evolution = ctx.evolution_snapshots[0] if ctx.evolution_snapshots else None
    if evolution:
        evolution_timeline = [
            {"phase_id": "previous", "label": evolution.previous_stage, "is_active": False},
            {"phase_id": "current", "label": evolution.current_stage, "is_active": True},
        ]
        if evolution.emerging_stage:
            evolution_timeline.append(
                {"phase_id": "emerging", "label": evolution.emerging_stage, "is_active": False}
            )
    else:
        evolution_timeline = [
            {"phase_id": "stable", "label": "Stable", "is_active": True},
            {"phase_id": "structured", "label": "Structured", "is_active": False},
            {"phase_id": "thriving", "label": "Thriving", "is_active": False},
        ]

    mem_rec = ctx.memory_recommendations[0] if ctx.memory_recommendations else None
    ai_interpretation = {
        "quote": mem_rec.recommendation_description
        if mem_rec
        else "Neural analysis suggests recovery activity is effectively dampening pressure trends."
    }

    growth_rec = mem_rec or (ctx.memory_recommendations[1] if len(ctx.memory_recommendations) > 1 else None)
    next_growth_edge = {
        "title": growth_rec.recommendation_title if growth_rec else "Protect Recovery",
        "body": growth_rec.recommendation_description
        if growth_rec
        else "Log one recovery block this week to stabilize capacity.",
        "cta_label": growth_rec.recommended_action if growth_rec else "Log Recovery",
    }

    return {
        "moment_type_code": code,
        "identity_snapshot": identity_snapshot,
        "core_pattern": core_pattern,
        "best_drivers": best_drivers,
        "lowest_drivers": lowest_drivers,
        "highest_return_behaviors": highest_return_behaviors,
        "emotional_dna": emotional_dna,
        "behavioral_patterns": behavioral_patterns,
        "evolution_timeline": evolution_timeline,
        "ai_interpretation": ai_interpretation,
        "next_growth_edge": next_growth_edge,
    }
