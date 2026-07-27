"""Future Building memory projection mapper — template-specific content."""
from __future__ import annotations

from typing import Any

from app.domains.personal.templates.future_building.projection_builder import (
    FutureBuildingProjectionContext,
)

_FB = "FUTURE_BUILDING"


def build_future_building_memory(ctx: FutureBuildingProjectionContext) -> dict[str, Any]:
    profile = ctx.profile
    signals = ctx.signals
    identity_title = profile.future_identity if profile else "Consistent Builder"
    confidence = signals.confidence if signals else 70

    identity_snapshot = {
        "title": identity_title,
        "trend_label": "Building systematic growth",
        "confidence_percent": confidence,
        "body": (
            profile.primary_opportunity_label
            if profile and profile.primary_opportunity_label
            else "You are building your future through learning, execution, and intentional investment."
        ),
        "image_url": None,
        "tag_label": profile.future_theme if profile else "Systematic Growth Architecture",
    }

    pattern_confidence = min(95, 55 + ctx.learning_count * 5)
    core_pattern = {
        "pattern_confidence_percent": pattern_confidence,
        "nodes": [
            {"node_id": "learning", "icon": "school", "label": "Learning", "subtitle": "Expand capability"},
            {"node_id": "confidence", "icon": "verified", "label": "Confidence", "subtitle": "Trust the path"},
            {"node_id": "progress", "icon": "trending_up", "label": "Progress", "subtitle": "Move forward"},
        ],
    }

    best_drivers = [
        {"rank": 1, "label": "Learning", "impact_percent": signals.consistency if signals else 94, "impact_description": "Highest leverage growth driver"},
        {"rank": 2, "label": "Execution", "impact_percent": signals.discipline if signals else 82, "impact_description": "Turns plans into outcomes"},
        {"rank": 3, "label": "Milestones", "impact_percent": signals.growth if signals else 75, "impact_description": "Marks meaningful progress"},
    ]

    lowest_drivers = [
        {"rank": 1, "label": "Inconsistent Learning", "impact_percent": max(20, 100 - (signals.consistency if signals else 66)), "impact_description": "Gaps slow compounding"},
        {"rank": 2, "label": "Unfinished Projects", "impact_percent": max(15, 100 - (signals.discipline if signals else 69)), "impact_description": "Scope drift reduces returns"},
    ]

    highest_return_behaviors = {
        "title": "Learning Sessions",
        "roi_label": f"{min(12.0, 6.0 + ctx.learning_count * 0.5):.1f}x Future Return",
        "bars": [
            {"behavior_code": "learn", "label": "LEARN", "height_fraction": 1.0},
            {"behavior_code": "exec", "label": "EXEC", "height_fraction": 0.75},
            {"behavior_code": "invest", "label": "INV", "height_fraction": 0.55},
        ],
    }

    emotional_dna = {
        "dominant_label": "BUILDER",
        "segments": [
            {"segment_id": "confidence", "label": "Confidence", "percent": 45, "color_token": "primary"},
            {"segment_id": "hope", "label": "Hope", "percent": 32, "color_token": "tertiary"},
            {"segment_id": "achievement", "label": "Achievement", "percent": 23, "color_token": "secondary"},
        ],
        "insight_body": "Your emotional tone is anchored in builder confidence and forward hope.",
    }

    behavioral_patterns = [
        {
            "pattern_id": "tuesday_learning",
            "icon": "event_available",
            "title": "Tuesday Learning Pattern",
            "subtitle": "Learning sessions cluster mid-week",
            "confidence_percent": min(90, 50 + ctx.learning_count * 8),
        },
        {
            "pattern_id": "morning_momentum",
            "icon": "wb_sunny",
            "title": "Morning Momentum Accelerator",
            "subtitle": "Progress logs favor morning blocks",
            "confidence_percent": min(85, 45 + ctx.progress_count * 6),
        },
    ]

    evolution_timeline = [
        {"phase_id": "exploring", "label": "Exploring", "is_active": False},
        {"phase_id": "building", "label": "Building", "is_active": True},
        {"phase_id": "accelerating", "label": "Accelerating", "is_active": False},
    ]

    ai_interpretation = {
        "quote": "Momentra sees your future building as a compounding system — learning and execution are reinforcing each other.",
    }

    next_growth_edge = {
        "title": "Increase Learning Frequency",
        "body": "More consistent learning sessions will raise future readiness faster than sporadic bursts.",
        "cta_label": "Log Learning",
        "priority": "HIGH",
        "roi_multiplier": 9.3,
    }

    return {
        "moment_type_code": _FB,
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


def build_future_building_memory_aggregate(ctx: FutureBuildingProjectionContext) -> dict[str, Any]:
    """Wrapper for GET /memory aggregate block."""
    projection = build_future_building_memory(ctx)
    signals = ctx.signals
    profile = ctx.profile
    breakthrough = profile.breakthrough_potential if profile else "MODERATE"
    focus_percent = signals.discipline if signals else 70
    return {
        "section_label": "Future Building Memory",
        "status_label": "ACTIVE",
        "synthesis_title": projection["identity_snapshot"]["title"],
        "synthesis_body": projection["identity_snapshot"]["body"],
        "system_state": profile.current_momentum_state if profile else "Building",
        "days_analyzed": max(1, ctx.timeline_count),
        "confidence_percent": signals.confidence if signals else 70,
        "confidence_title": "Pattern Confidence",
        "confidence_body": projection["ai_interpretation"]["quote"],
        "identity_label": projection["identity_snapshot"]["title"],
        "direction_label": profile.future_theme if profile else "Future Growth",
        "neural_growth_title": "Neural Growth Map",
        "neural_growth_subtitle": "How your future-building patterns are wiring in",
        "breakthrough_title": f"{breakthrough} Breakthrough Window",
        "breakthrough_body": (
            profile.primary_opportunity_label
            if profile and profile.primary_opportunity_label
            else "Your next compounding window is forming through consistent execution."
        ),
        "breakthrough_active": breakthrough == "HIGH",
        "focus_title": "Focus Optimization",
        "focus_percent": focus_percent,
        "focus_body": "Daily focus blocks are the highest-leverage driver of future momentum.",
        "metrics": projection,
    }
