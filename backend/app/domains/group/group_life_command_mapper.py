"""Aggregate active group moments into the Command Center life metrics contract."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.domains.group.catalog import GROUP_MOMENT_TYPES, group_type_name
from app.domains.group.templates.shared_experience.life_mapper import build_life as build_experience_life
from app.domains.group.templates.shared_experience.projection_builder import SharedExperienceProjectionBuilder
from app.domains.group.templates.shared_living.life_mapper import build_life as build_living_life
from app.domains.group.templates.shared_living.projection_builder import SharedLivingProjectionBuilder
from app.domains.group.templates.shared_purchase.life_mapper import build_life as build_purchase_life
from app.domains.group.templates.shared_purchase.projection_builder import SharedPurchaseProjectionBuilder
from app.domains.moments.models import MomentModel

_SATELLITE_TYPES: list[tuple[str, str, str]] = [
    ("SHARED_EXPERIENCE", "Experience", "primary"),
    ("SHARED_PURCHASE", "Purchase", "primary_container"),
    ("SHARED_LIVING", "Living", "secondary"),
    ("SHARED_GOAL", "Goal", "tertiary"),
    ("COMMUNITY_COORDINATION", "Community", "indigo"),
]

_BALANCE_DIMS: list[tuple[str, str, str]] = [
    ("PARTICIPATION", "Participation", "primary"),
    ("CONTRIBUTION", "Contribution", "primary_container"),
    ("COORDINATION", "Coordination", "secondary"),
    ("PROGRESS", "Progress", "tertiary"),
    ("COMMUNITY", "Community", "indigo"),
]

_DRIVER_RELATIONS: dict[str, tuple[str, str, str]] = {
    "SHARED_EXPERIENCE": ("Drives Participation", "celebration", "primary"),
    "SHARED_PURCHASE": ("Drives Contributions", "shopping_cart", "primary_container"),
    "SHARED_LIVING": ("Drives Community", "home", "secondary"),
    "SHARED_GOAL": ("Drives Progress", "flag", "tertiary"),
    "COMMUNITY_COORDINATION": ("Drives Community", "public", "indigo"),
}

_QUICK_ACTION_TYPES: list[tuple[str, str, str]] = [
    ("SHARED_EXPERIENCE", "Experience", "primary"),
    ("SHARED_PURCHASE", "Purchase", "primary_container"),
    ("SHARED_LIVING", "Living", "secondary"),
    ("SHARED_GOAL", "Goal", "tertiary"),
    ("COMMUNITY_COORDINATION", "Community", "indigo"),
]


def _clamp_score(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return default


def _status_label(score: int) -> str:
    if score >= 85:
        return "Optimal"
    if score >= 75:
        return "Healthy"
    if score >= 65:
        return "Stable"
    if score >= 55:
        return "On Track"
    return "Building"


def _life_status_label(score: int) -> str:
    if score >= 80:
        return "Strong"
    if score >= 65:
        return "Balanced"
    if score >= 50:
        return "Growing"
    return "Getting started"


def _build_life_payload(moment: MomentModel) -> dict[str, Any]:
    code = (moment.moment_type or "").upper()
    if code == "SHARED_EXPERIENCE":
        ctx = SharedExperienceProjectionBuilder.build_from_moment(moment)
        return build_experience_life(ctx)
    if code == "SHARED_PURCHASE":
        ctx = SharedPurchaseProjectionBuilder.build_from_moment(moment)
        return build_purchase_life(ctx)
    if code == "SHARED_LIVING":
        ctx = SharedLivingProjectionBuilder.build_from_moment(moment)
        return build_living_life(ctx)
    return {}


def _dimension_scores_from_life(life: dict[str, Any]) -> list[float]:
    scores: list[float] = []
    for key, value in life.items():
        if isinstance(value, dict) and "score" in value:
            scores.append(float(value["score"]))
    return scores


def _moment_type_score(moment: MomentModel, life: dict[str, Any]) -> int:
    code = (moment.moment_type or "").upper()
    dim_scores = _dimension_scores_from_life(life)
    if dim_scores:
        return _clamp_score(sum(dim_scores) / len(dim_scores))
    stats = life.get("stats") or {}
    if code == "SHARED_EXPERIENCE":
        guests = int(stats.get("guests") or 0)
        plans = int(stats.get("plans") or 0)
        memories = int(stats.get("memories") or 0)
        expenses = int(stats.get("expenses_minor") or 0)
        raw = 35 + guests * 10 + plans * 6 + memories * 5 + (12 if expenses > 0 else 0)
        return _clamp_score(raw, default=40)
    return 50


def _participation_score(lives: list[dict[str, Any]]) -> int:
    parts: list[float] = []
    for life in lives:
        stats = life.get("stats") or {}
        guests = stats.get("guests") or stats.get("residents") or stats.get("contributors") or 0
        parts.append(min(100.0, 40 + int(guests) * 12))
    return _clamp_score(sum(parts) / len(parts)) if parts else 0


def _contribution_score(lives: list[dict[str, Any]]) -> int:
    parts: list[float] = []
    for life in lives:
        stats = life.get("stats") or {}
        contrib = int(stats.get("contributions_minor") or 0)
        expenses = int(stats.get("expenses_minor") or 0)
        if expenses <= 0:
            parts.append(45.0 if contrib > 0 else 35.0)
        else:
            ratio = min(1.0, contrib / max(expenses, 1))
            parts.append(40 + ratio * 55)
    return _clamp_score(sum(parts) / len(parts)) if parts else 0


def _coordination_score(lives: list[dict[str, Any]]) -> int:
    parts: list[float] = []
    for life in lives:
        stats = life.get("stats") or {}
        plans = int(stats.get("plans") or stats.get("milestones") or stats.get("chores") or 0)
        parts.append(min(100.0, 38 + plans * 8))
    return _clamp_score(sum(parts) / len(parts)) if parts else 0


def _progress_score(lives: list[dict[str, Any]]) -> int:
    parts: list[float] = []
    for life in lives:
        stats = life.get("stats") or {}
        milestones = int(stats.get("milestones") or stats.get("plans") or 0)
        memories = int(stats.get("memories") or 0)
        parts.append(min(100.0, 30 + milestones * 10 + memories * 4))
    return _clamp_score(sum(parts) / len(parts)) if parts else 0


def _community_score(type_scores: dict[str, int | None]) -> int:
    active = [s for s in type_scores.values() if s is not None]
    if not active:
        return 0
    diversity = len(active)
    avg = sum(active) / len(active)
    return _clamp_score(avg * 0.7 + diversity * 8)


def _monthly_delta(current: int, seed: int) -> int:
    """Deterministic delta from current score and moment count seed."""
    if current <= 0:
        return 0
    base = max(-5, min(15, (current % 17) - 4 + (seed % 5)))
    return base


def _evolution_points(current: int, seed: int) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for i in range(6):
        drift = _monthly_delta(current, seed + i) // 2
        value = _clamp_score(current - (5 - i) * 2 + drift)
        points.append({"label": f"w{i + 1}", "value": value})
    return points


def _journey_items(active_moments: list[MomentModel], lives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for moment, life in zip(active_moments, lives):
        code = (moment.moment_type or "").upper()
        accent = {
            "SHARED_EXPERIENCE": "primary",
            "SHARED_PURCHASE": "primary_container",
            "SHARED_LIVING": "secondary",
        }.get(code, "primary")
        icon = {
            "SHARED_EXPERIENCE": "trip_origin",
            "SHARED_PURCHASE": "shopping_cart",
            "SHARED_LIVING": "apartment",
        }.get(code, "flag")
        title = life.get("moment_name") or moment.title or group_type_name(code)
        subtitle = life.get("stage_badge") or "Active"
        items.append(
            {
                "event_key": str(moment.id),
                "title": title,
                "subtitle": subtitle,
                "icon": icon,
                "accent_token": accent,
                "is_current": True,
            }
        )
        stats = life.get("stats") or {}
        if int(stats.get("memories") or 0) > 0:
            items.append(
                {
                    "event_key": f"{moment.id}:memory",
                    "title": "Memory captured",
                    "subtitle": f"{stats.get('memories')} memories",
                    "icon": "photo_library",
                    "accent_token": accent,
                    "is_current": False,
                }
            )
    return items[:8]


def build_group_life_command_center(active_moments: list[MomentModel]) -> dict[str, Any]:
    lives = [_build_life_payload(m) for m in active_moments]
    active_codes = {(m.moment_type or "").upper() for m in active_moments}

    type_scores: dict[str, int | None] = {code: None for code, _, _ in _SATELLITE_TYPES}
    for moment, life in zip(active_moments, lives):
        code = (moment.moment_type or "").upper()
        if code in type_scores:
            type_scores[code] = _moment_type_score(moment, life)

    satellite_scores = [
        {
            "moment_type_code": code,
            "label": label,
            "score": type_scores.get(code),
            "color_token": token,
        }
        for code, label, token in _SATELLITE_TYPES
    ]

    active_type_values = [s for s in type_scores.values() if s is not None]
    life_score = _clamp_score(sum(active_type_values) / len(active_type_values)) if active_type_values else 0
    delta_month = _monthly_delta(life_score, len(active_moments))

    balance_values = {
        "PARTICIPATION": _participation_score(lives),
        "CONTRIBUTION": _contribution_score(lives),
        "COORDINATION": _coordination_score(lives),
        "PROGRESS": _progress_score(lives),
        "COMMUNITY": _community_score(type_scores),
    }

    balance_dimensions = [
        {
            "dimension_code": code,
            "label": label,
            "score": balance_values[code],
            "badge_label": f"{balance_values[code]} {_status_label(balance_values[code])}",
            "badge_color_token": token,
        }
        for code, label, token in _BALANCE_DIMS
    ]

    drivers: list[dict[str, Any]] = []
    ranked_types = sorted(
        [(code, type_scores[code]) for code in active_codes if type_scores.get(code) is not None],
        key=lambda item: item[1] or 0,
        reverse=True,
    )
    for code, score in ranked_types[:3]:
        relation, icon, accent = _DRIVER_RELATIONS.get(code, ("Drives Growth", "auto_awesome", "primary"))
        impact = _clamp_score((score or 0) // 5 + 8)
        drivers.append(
            {
                "source_type_code": code,
                "title": group_type_name(code),
                "relation": relation,
                "icon": icon,
                "accent_token": accent,
                "impact_percent": impact,
                "body": f"Active {group_type_name(code).lower()} is shaping your group's {relation.split()[-1].lower()}.",
                "action": f"Review {group_type_name(code).lower()} activity",
                "priority": "HIGH" if impact >= 15 else "MEDIUM",
            }
        )

    lowest = min(balance_dimensions, key=lambda d: d["score"])
    drift_alert: dict[str, Any] | None = None
    if lowest["score"] < 70:
        drift_alert = {
            "title": f"{lowest['label']} ↓",
            "body": f"{lowest['label']} is trailing other balance dimensions.",
            "impact_label": "Potential Impact",
            "impact_body": f"Other dimensions may soften if {lowest['label'].lower()} stays low.",
        }

    leverage: dict[str, Any] | None = None
    top_rec = None
    for life in lives:
        recs = life.get("recommendations") or []
        if recs:
            top_rec = recs[0]
            break
    if top_rec:
        leverage = {
            "title": top_rec.get("title") or "Take the next step",
            "impact_lines": [top_rec.get("description") or "Improve group coordination."],
            "impact_score": _clamp_score(life_score + 8),
            "confidence_label": "Medium Confidence" if top_rec.get("priority") == "MEDIUM" else "High Confidence",
        }
    elif drivers:
        leverage = {
            "title": drivers[0]["action"],
            "impact_lines": [
                f"+{_clamp_score(drivers[0]['impact_percent'] // 2)} Participation",
                f"+{_clamp_score(drivers[0]['impact_percent'] // 3)} Coordination",
            ],
            "impact_score": _clamp_score(life_score + drivers[0]["impact_percent"]),
            "confidence_label": "High Confidence",
        }

    evolution_codes = ["PARTICIPATION", "CONTRIBUTION", "COORDINATION"]
    evolution = [
        {
            "dimension_code": code,
            "label": next(l for c, l, _ in _BALANCE_DIMS if c == code),
            "delta_percent": _monthly_delta(balance_values[code], len(active_moments) + i),
            "color_token": token,
            "points": _evolution_points(balance_values[code], len(active_moments) + i),
        }
        for i, (code, token) in enumerate(
            [("PARTICIPATION", "primary"), ("CONTRIBUTION", "primary_container"), ("COORDINATION", "secondary")]
        )
    ]

    monthly_changes = [
        {
            "change_code": code,
            "label": label,
            "delta_percent": _monthly_delta(balance_values[code], len(active_moments)),
            "color_token": token,
        }
        for code, label, token in _BALANCE_DIMS
    ]

    journey = _journey_items(active_moments, lives)

    dominant_code = ranked_types[0][0] if ranked_types else "SHARED_EXPERIENCE"
    dominant_label = group_type_name(dominant_code)
    intelligence = {
        "insight_text": (
            f"Strongest ecosystem driver: {dominant_label}. "
            f"Focus on {lowest['label'].lower()} to lift overall group health."
        ),
        "confidence_label": "High Confidence" if life_score >= 65 else "Medium Confidence",
        "dimension_pills": [label for code, label, _ in _SATELLITE_TYPES if type_scores.get(code) is not None],
    }

    quick_actions = [
        {
            "action_code": f"create_{code.lower()}",
            "label": label,
            "moment_type_code": code,
            "color_token": token,
        }
        for code, label, token in _QUICK_ACTION_TYPES
        if code not in active_codes
    ]

    now = datetime.now(timezone.utc)
    date_range_label = now.strftime("%B %Y")

    return {
        "date_range_label": date_range_label,
        "life_health": {
            "life_score": life_score,
            "status_label": _life_status_label(life_score),
            "delta_month": delta_month,
            "insight_quote": intelligence["insight_text"],
            "satellite_scores": satellite_scores,
        },
        "balance_model": {
            "subtitle": "How your group balances participation, contribution, and coordination.",
            "dimensions": balance_dimensions,
        },
        "drivers": drivers,
        "drift_alert": drift_alert,
        "leverage": leverage,
        "evolution": evolution,
        "monthly_changes": monthly_changes,
        "journey": journey,
        "intelligence": intelligence,
        "quick_actions": quick_actions,
    }
