"""Relationships memory projection mapper."""
from __future__ import annotations

from typing import Any

from app.domains.personal.templates.relationships.constants import MOMENT_TYPE_CODE
from app.domains.personal.templates.relationships.projection_builder import (
    RelationshipsProjectionContext,
)
from app.domains.personal.templates.pattern_evidence import gate_and_dedupe_patterns

_RS = MOMENT_TYPE_CODE


def build_relationships_memory(ctx: RelationshipsProjectionContext) -> dict[str, Any]:
    profile = ctx.profile
    signals = ctx.signals
    identity_title = profile.relationship_identity if profile else "Connection Builder"
    confidence = signals.relationship_health if signals else 70

    identity_snapshot = {
        "title": identity_title,
        "trend_label": "Investing with intention",
        "confidence_percent": confidence,
        "body": (
            profile.primary_relationship_opportunity
            if profile and profile.primary_relationship_opportunity
            else "You are shaping relationships through connection, support, and shared experiences."
        ),
        "image_url": None,
        "tag_label": profile.relationship_focus if profile else "Family",
    }

    pattern_confidence = min(95, 55 + ctx.connection_count * 5)
    core_pattern = {
        "pattern_confidence_percent": pattern_confidence,
        "nodes": [
            {"node_id": "connection", "icon": "group", "label": "Connection", "subtitle": "Presence & trust"},
            {"node_id": "support", "icon": "favorite", "label": "Support", "subtitle": "Care given & received"},
            {"node_id": "growth", "icon": "trending_up", "label": "Growth", "subtitle": "Repair & reflection"},
        ],
    }

    best_drivers = [
        {"rank": 1, "label": "Connection", "impact_percent": signals.connection if signals else 88, "impact_description": "Highest bond driver"},
        {"rank": 2, "label": "Support", "impact_percent": signals.support if signals else 82, "impact_description": "Builds trust and resilience"},
        {"rank": 3, "label": "Shared Time", "impact_percent": signals.quality_time if signals else 75, "impact_description": "Deepens fulfillment"},
    ]

    lowest_drivers = [
        {"rank": 1, "label": "Neglected Check-ins", "impact_percent": max(20, 100 - (signals.communication if signals else 66)), "impact_description": "Gaps widen without contact"},
        {"rank": 2, "label": "Unresolved Tension", "impact_percent": max(15, 100 - (signals.growth if signals else 69)), "impact_description": "Conflict left unprocessed"},
    ]

    roi_analysis = {
        "title": "Connection",
        "roi_label": f"{min(12.0, 6.0 + ctx.connection_count * 0.5):.1f}x Relationship Return",
        "bars": [
            {"behavior_code": "conn", "label": "CONN", "height_fraction": 1.0},
            {"behavior_code": "supp", "label": "SUPP", "height_fraction": 0.78},
            {"behavior_code": "exp", "label": "EXP", "height_fraction": 0.55},
        ],
    }

    emotional_dna = {
        "dominant_label": "CONNECTOR",
        "segments": [
            {"segment_id": "trust", "label": "Trust", "percent": 42, "color_token": "primary"},
            {"segment_id": "warmth", "label": "Warmth", "percent": 33, "color_token": "tertiary"},
            {"segment_id": "presence", "label": "Presence", "percent": 25, "color_token": "secondary"},
        ],
        "insight_body": "Your relational tone blends trust with warm presence.",
    }

    behavioral_patterns = gate_and_dedupe_patterns(
        [
            {
                "pattern_id": "weekend_connections",
                "icon": "weekend",
                "title": "Weekend Connection Pattern",
                "subtitle": "Meaningful contact clusters on weekends",
                "confidence_percent": min(90, 50 + ctx.connection_count * 8),
            },
            {
                "pattern_id": "support_after_stress",
                "icon": "volunteer_activism",
                "title": "Support Response Pattern",
                "subtitle": "Support logs follow challenging periods",
                "confidence_percent": min(85, 45 + ctx.support_count * 6),
            },
        ],
        evidence_counts={
            "weekend_connections": ctx.connection_count,
            "support_after_stress": ctx.support_count,
        },
    )

    evolution_timeline = [
        {"phase_id": "rebuilding", "label": "Rebuilding", "is_active": False},
        {"phase_id": "connecting", "label": "Connecting", "is_active": True},
        {"phase_id": "thriving", "label": "Thriving", "is_active": False},
    ]

    ai_interpretation = {
        "quote": "Momentra sees your relationships as an intentional system — connection and support reinforce each other.",
    }

    next_growth_edge = {
        "title": "Increase Connection Intentionality",
        "body": "More deliberate connection time will lift bond index faster than passive contact.",
        "cta_label": "Log Connection",
        "priority": "HIGH",
        "roi_multiplier": 8.6,
    }

    recommendations = [
        {
            "recommendation_id": "quality_time",
            "title": "Schedule quality time",
            "body": "Block intentional time with your highest-priority relationships.",
            "priority": "HIGH",
        },
        {
            "recommendation_id": "repair",
            "title": "Address neglected areas",
            "body": profile.primary_relationship_gap if profile else "Check-ins need attention.",
            "priority": "MEDIUM",
        },
    ]

    growth_summary = {
        "title": "Relationship Growth",
        "body": f"{ctx.connection_count} connections and {ctx.support_count} support moments logged.",
        "trend_label": "Building" if ctx.timeline_count < 5 else "Strengthening",
    }

    reflection = {
        "prompt": "What relationship felt most alive this week?",
        "body": "Reflection helps Momentra understand what connection patterns matter most to you.",
    }

    return {
        "moment_type_code": _RS,
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
        "recommendations": recommendations,
        "growth_summary": growth_summary,
        "reflection": reflection,
    }


def build_relationships_memory_aggregate(ctx: RelationshipsProjectionContext) -> dict[str, Any]:
    projection = build_relationships_memory(ctx)
    signals = ctx.signals
    profile = ctx.profile
    potential = profile.relationship_potential if profile else "MODERATE"
    focus_percent = signals.trust if signals else 70
    return {
        "section_label": "Relationships Memory",
        "status_label": "ACTIVE",
        "synthesis_title": projection["identity_snapshot"]["title"],
        "synthesis_body": projection["identity_snapshot"]["body"],
        "system_state": profile.current_relationship_state if profile else "Connecting",
        "days_analyzed": max(1, ctx.timeline_count),
        "confidence_percent": signals.relationship_health if signals else 70,
        "confidence_title": "Pattern Confidence",
        "confidence_body": projection["ai_interpretation"]["quote"],
        "identity_label": projection["identity_snapshot"]["title"],
        "style_label": profile.relationship_focus if profile else "Family",
        "neural_growth_title": "Relationship DNA Map",
        "neural_growth_subtitle": "How your connection patterns are wiring in",
        "breakthrough_title": f"{potential} Bond Window",
        "breakthrough_body": (
            profile.primary_relationship_opportunity
            if profile and profile.primary_relationship_opportunity
            else "Your next relationship lift is forming through consistent connection."
        ),
        "breakthrough_active": potential == "HIGH",
        "focus_title": "Trust Optimization",
        "focus_percent": focus_percent,
        "focus_body": "Trust and presence are the highest-leverage drivers of relationship health.",
        "metrics": projection,
    }
