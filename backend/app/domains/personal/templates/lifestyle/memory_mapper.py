"""Lifestyle memory projection mapper."""
from __future__ import annotations

from typing import Any

from app.domains.personal.templates.lifestyle.constants import MOMENT_TYPE_CODE
from app.domains.personal.templates.lifestyle.projection_builder import (
    LifestyleProjectionContext,
)
from app.domains.personal.templates.pattern_evidence import gate_and_dedupe_patterns

_LS = MOMENT_TYPE_CODE


def build_lifestyle_memory(ctx: LifestyleProjectionContext) -> dict[str, Any]:
    profile = ctx.profile
    signals = ctx.signals
    identity_title = profile.lifestyle_identity if profile else "Experience Curator"
    confidence = signals.wellbeing if signals else 70

    identity_snapshot = {
        "title": identity_title,
        "trend_label": "Living with intention",
        "confidence_percent": confidence,
        "body": (
            profile.primary_lifestyle_opportunity
            if profile and profile.primary_lifestyle_opportunity
            else "You are shaping a lifestyle through experiences, wellbeing, and creative expression."
        ),
        "image_url": None,
        "tag_label": profile.lifestyle_style if profile else "Balanced Living",
    }

    pattern_confidence = min(95, 55 + ctx.experience_count * 5)
    core_pattern = {
        "pattern_confidence_percent": pattern_confidence,
        "nodes": [
            {"node_id": "health", "icon": "favorite", "label": "Health", "subtitle": "Body & energy"},
            {"node_id": "joy", "icon": "celebration", "label": "Joy", "subtitle": "Experiences"},
            {"node_id": "balance", "icon": "balance", "label": "Balance", "subtitle": "Rhythm"},
        ],
    }

    best_drivers = [
        {"rank": 1, "label": "Experiences", "impact_percent": signals.social if signals else 88, "impact_description": "Highest fulfillment driver"},
        {"rank": 2, "label": "Wellbeing", "impact_percent": signals.wellbeing if signals else 82, "impact_description": "Sustains daily energy"},
        {"rank": 3, "label": "Routine", "impact_percent": signals.routine if signals else 75, "impact_description": "Creates consistency"},
    ]

    lowest_drivers = [
        {"rank": 1, "label": "Neglected Recovery", "impact_percent": max(20, 100 - (signals.energy if signals else 66)), "impact_description": "Energy dips without rest"},
        {"rank": 2, "label": "Passive Spending", "impact_percent": max(15, 100 - (signals.balance if signals else 69)), "impact_description": "Low-return lifestyle spend"},
    ]

    roi_analysis = {
        "title": "Experiences",
        "roi_label": f"{min(12.0, 6.0 + ctx.experience_count * 0.5):.1f}x Lifestyle Return",
        "bars": [
            {"behavior_code": "exp", "label": "EXP", "height_fraction": 1.0},
            {"behavior_code": "well", "label": "WELL", "height_fraction": 0.78},
            {"behavior_code": "create", "label": "CREATE", "height_fraction": 0.55},
        ],
    }

    emotional_dna = {
        "dominant_label": "CURATOR",
        "segments": [
            {"segment_id": "joy", "label": "Joy", "percent": 42, "color_token": "primary"},
            {"segment_id": "calm", "label": "Calm", "percent": 33, "color_token": "tertiary"},
            {"segment_id": "energy", "label": "Energy", "percent": 25, "color_token": "secondary"},
        ],
        "insight_body": "Your emotional tone blends joyful experiences with restorative calm.",
    }

    behavioral_patterns = gate_and_dedupe_patterns(
        [
            {
                "pattern_id": "weekend_experiences",
                "icon": "weekend",
                "title": "Weekend Experience Pattern",
                "subtitle": "Memorable experiences cluster on weekends",
                "confidence_percent": min(90, 50 + ctx.experience_count * 8),
            },
            {
                "pattern_id": "wellbeing_mornings",
                "icon": "wb_sunny",
                "title": "Morning Wellbeing Anchor",
                "subtitle": "Wellbeing logs favor morning routines",
                "confidence_percent": min(85, 45 + ctx.wellbeing_count * 6),
            },
        ],
        evidence_counts={
            "weekend_experiences": ctx.experience_count,
            "wellbeing_mornings": ctx.wellbeing_count,
        },
    )

    evolution_timeline = [
        {"phase_id": "exploring", "label": "Exploring", "is_active": False},
        {"phase_id": "curating", "label": "Curating", "is_active": True},
        {"phase_id": "thriving", "label": "Thriving", "is_active": False},
    ]

    ai_interpretation = {
        "quote": "Momentra sees your lifestyle as an intentional system — experiences and wellbeing reinforce each other.",
    }

    next_growth_edge = {
        "title": "Increase Experience Intentionality",
        "body": "More deliberate experiences will lift fulfillment faster than passive consumption.",
        "cta_label": "Log Experience",
        "priority": "HIGH",
        "roi_multiplier": 8.6,
    }

    return {
        "moment_type_code": _LS,
        "identity_snapshot": identity_snapshot,
        "core_pattern": core_pattern,
        "best_drivers": best_drivers,
        "lowest_drivers": lowest_drivers,
        "roi_analysis": roi_analysis,
        "emotional_dna": emotional_dna,
        "behavioral_patterns": behavioral_patterns,
        "evolution_timeline": evolution_timeline,
        "ai_interpretation": ai_interpretation,
        "next_growth_edge": next_growth_edge,
    }


def build_lifestyle_memory_aggregate(ctx: LifestyleProjectionContext) -> dict[str, Any]:
    projection = build_lifestyle_memory(ctx)
    signals = ctx.signals
    profile = ctx.profile
    potential = profile.lifestyle_potential if profile else "MODERATE"
    focus_percent = signals.routine if signals else 70
    return {
        "section_label": "Lifestyle Memory",
        "status_label": "ACTIVE",
        "synthesis_title": projection["identity_snapshot"]["title"],
        "synthesis_body": projection["identity_snapshot"]["body"],
        "system_state": profile.current_lifestyle_state if profile else "Curating",
        "days_analyzed": max(1, ctx.timeline_count),
        "confidence_percent": signals.wellbeing if signals else 70,
        "confidence_title": "Pattern Confidence",
        "confidence_body": projection["ai_interpretation"]["quote"],
        "identity_label": projection["identity_snapshot"]["title"],
        "style_label": profile.lifestyle_style if profile else "Balanced",
        "neural_growth_title": "Lifestyle DNA Map",
        "neural_growth_subtitle": "How your lifestyle patterns are wiring in",
        "breakthrough_title": f"{potential} Vitality Window",
        "breakthrough_body": (
            profile.primary_lifestyle_opportunity
            if profile and profile.primary_lifestyle_opportunity
            else "Your next lifestyle lift is forming through consistent experiences."
        ),
        "breakthrough_active": potential == "HIGH",
        "focus_title": "Rhythm Optimization",
        "focus_percent": focus_percent,
        "focus_body": "Daily rhythms are the highest-leverage driver of lifestyle vitality.",
        "metrics": projection,
    }
