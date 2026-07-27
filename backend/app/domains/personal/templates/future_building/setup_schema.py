"""Future Building setup template contract — versioned field mapping and validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.domains.personal.models import PersonalFutureBuildingProfile

TEMPLATE_ID = "future_building"
TEMPLATE_VERSION = 1
MOMENT_TYPE_CODE = "FUTURE_BUILDING"

_FEELING_MAP = {
    "EXCITING": "Exciting",
    "HOPEFUL": "Hopeful",
    "CONFIDENT": "Confident",
    "UNCLEAR": "Unclear",
    "STUCK": "Stuck",
    "OVERWHELMING": "Overwhelming",
}

_BUILDING_FOCUS_LABELS = {
    "CAREER_GROWTH": "Career Growth",
    "BUSINESS_GROWTH": "Business Growth",
    "FINANCIAL_FREEDOM": "Financial Freedom",
    "LEARNING_SKILLS": "Learning & Skills",
    "CREATIVE_PROJECT": "Creative Project",
    "PERSONAL_REINVENTION": "Personal Reinvention",
}

_STATE_LABELS = {
    "JUST_STARTING": "Just Starting",
    "EXPLORING_OPTIONS": "Exploring Options",
    "MAKING_PROGRESS": "Making Progress",
    "BUILDING_MOMENTUM": "Building Momentum",
}

_VALUE_LABELS = {
    "GROWTH": "Growth",
    "FREEDOM": "Freedom",
    "IMPACT": "Impact",
    "SECURITY": "Security",
    "PURPOSE": "Purpose",
}

_FRICTION_LABELS = {
    "LACK_OF_TIME": "Lack Of Time",
    "LACK_OF_CLARITY": "Lack Of Clarity",
    "DISTRACTIONS": "Distractions",
    "BURNOUT": "Burnout",
}

_DRIVER_LABELS = {
    "DAILY_PROGRESS": "Daily Progress",
    "LEARNING": "Learning",
    "FOCUS_TIME": "Focus Time",
    "ROUTINE": "Routine",
}


@dataclass
class TemplateSetupContract:
    template_id: str
    template_version: int
    moment_type_code: str
    required_fields: list[str] = field(default_factory=list)

    def migrate_answers(self, answers: dict[str, Any]) -> dict[str, Any]:
        version = int(answers.get("template_version") or TEMPLATE_VERSION)
        if version < TEMPLATE_VERSION:
            # Future v2 migrations go here.
            answers = dict(answers)
            answers["template_version"] = TEMPLATE_VERSION
        return answers

    def normalize_answers(self, answers: dict[str, Any]) -> dict[str, Any]:
        migrated = self.migrate_answers(answers)
        normalized = {
            "template_id": migrated.get("template_id") or self.template_id,
            "template_version": int(migrated.get("template_version") or self.template_version),
            "building_focus": str(migrated.get("building_focus") or "CAREER_GROWTH"),
            "current_state": str(migrated.get("current_state") or "JUST_STARTING"),
            "values": _as_list(migrated.get("values")),
            "friction_sources": _as_list(migrated.get("friction_sources")),
            "momentum_drivers": _as_list(migrated.get("momentum_drivers")),
            "future_feeling": str(migrated.get("future_feeling") or "HOPEFUL"),
        }
        if migrated.get("moment_name"):
            normalized["moment_name"] = str(migrated["moment_name"])
        return normalized

    def validate(self, answers: dict[str, Any]) -> None:
        normalized = self.normalize_answers(answers)
        if not normalized.get("values"):
            raise ValidationError("At least one value must be selected")
        if not normalized.get("friction_sources"):
            raise ValidationError("At least one friction source must be selected")
        if not normalized.get("momentum_drivers"):
            raise ValidationError("At least one momentum driver must be selected")

    def to_profile_fields(self, answers: dict[str, Any]) -> dict[str, Any]:
        n = self.normalize_answers(answers)
        theme = _BUILDING_FOCUS_LABELS.get(n["building_focus"], n["building_focus"])
        state = _STATE_LABELS.get(n["current_state"], n["current_state"])
        values = [_VALUE_LABELS.get(v, v) for v in n["values"]]
        friction = [_FRICTION_LABELS.get(f, f) for f in n["friction_sources"]]
        drivers = [_DRIVER_LABELS.get(d, d) for d in n["momentum_drivers"]]
        feeling = _FEELING_MAP.get(n["future_feeling"], n["future_feeling"])
        identity = _assign_identity(theme, values)
        largest_friction = friction[0] if friction else "Clarity Gap"
        opportunity = _primary_opportunity(theme, drivers)
        breakthrough = _breakthrough_potential(n["current_state"], feeling)
        return {
            "future_theme": theme,
            "current_momentum_state": state,
            "future_values": values,
            "friction_sources": friction,
            "momentum_drivers": drivers,
            "future_confidence": feeling,
            "future_identity": identity,
            "largest_friction_label": largest_friction,
            "primary_opportunity_label": opportunity,
            "breakthrough_potential": breakthrough,
        }

    def preview_block(self, answers: dict[str, Any]) -> dict[str, Any]:
        fields = self.to_profile_fields(answers)
        momentum_pct = _momentum_percent(answers)
        return {
            "assigned_identity": {
                "badge_label": "Assigned Identity",
                "title": fields["future_identity"],
                "body": (
                    f"You are building toward {fields['future_theme']} with "
                    f"{fields['current_momentum_state'].lower()} momentum."
                ),
                "icon_name": "auto_awesome",
            },
            "runtime_projection": [
                {"label": "Future Theme", "value": fields["future_theme"]},
                {"label": "Current State", "value": fields["current_momentum_state"]},
                {"label": "Future Confidence", "value": fields["future_confidence"]},
                {"label": "Primary Value", "value": fields["future_values"][0] if fields["future_values"] else "Growth"},
                {"label": "Largest Friction", "value": fields["largest_friction_label"], "accent": "error"},
                {"label": "Momentum Driver", "value": fields["momentum_drivers"][0] if fields["momentum_drivers"] else "Learning"},
            ],
            "future_horizon": {
                "trajectory": fields["current_momentum_state"],
                "momentum_percent": momentum_pct,
                "opportunity": fields["primary_opportunity_label"],
                "breakthrough": fields["breakthrough_potential"],
                "obstacle_title": fields["largest_friction_label"],
                "obstacle_body": f"{fields['largest_friction_label']} is the primary friction slowing your future momentum.",
            },
        }


FUTURE_BUILDING_TEMPLATE_CONTRACT = TemplateSetupContract(
    template_id=TEMPLATE_ID,
    template_version=TEMPLATE_VERSION,
    moment_type_code=MOMENT_TYPE_CODE,
    required_fields=[
        "building_focus",
        "current_state",
        "values",
        "friction_sources",
        "momentum_drivers",
        "future_feeling",
    ],
)


def to_setup_fields() -> list[dict[str, Any]]:
    """API field definitions for Future Building setup GET."""
    return [
        {
            "field_key": "moment_name",
            "label": "Name this moment",
            "helper_text": "Give your future-building journey a name.",
            "field_type": "TEXT",
            "required": True,
        },
        {
            "field_key": "building_focus",
            "label": "Building focus",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [
                {"value": k, "label": v} for k, v in _BUILDING_FOCUS_LABELS.items()
            ],
        },
        {
            "field_key": "current_state",
            "label": "Current state",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _STATE_LABELS.items()],
        },
        {
            "field_key": "values",
            "label": "Core values",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _VALUE_LABELS.items()],
        },
        {
            "field_key": "friction_sources",
            "label": "Friction sources",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [
                {"value": k, "label": v} for k, v in _FRICTION_LABELS.items()
            ],
        },
        {
            "field_key": "momentum_drivers",
            "label": "Momentum drivers",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _DRIVER_LABELS.items()],
        },
        {
            "field_key": "future_feeling",
            "label": "Future feeling",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _FEELING_MAP.items()],
        },
    ]


def answers_from_profile(profile: PersonalFutureBuildingProfile) -> dict[str, Any]:
    reverse_focus = {v: k for k, v in _BUILDING_FOCUS_LABELS.items()}
    reverse_state = {v: k for k, v in _STATE_LABELS.items()}
    reverse_value = {v: k for k, v in _VALUE_LABELS.items()}
    reverse_friction = {v: k for k, v in _FRICTION_LABELS.items()}
    reverse_driver = {v: k for k, v in _DRIVER_LABELS.items()}
    reverse_feeling = {v: k for k, v in _FEELING_MAP.items()}
    values = profile.future_values or []
    friction = profile.friction_sources or []
    drivers = profile.momentum_drivers or []
    return {
        "template_id": TEMPLATE_ID,
        "template_version": TEMPLATE_VERSION,
        "building_focus": reverse_focus.get(
            profile.future_theme or "", "CAREER_GROWTH"
        ),
        "current_state": reverse_state.get(
            profile.current_momentum_state or "", "JUST_STARTING"
        ),
        "values": [reverse_value.get(v, v) for v in values],
        "friction_sources": [reverse_friction.get(f, f) for f in friction],
        "momentum_drivers": [reverse_driver.get(d, d) for d in drivers],
        "future_feeling": reverse_feeling.get(
            profile.future_confidence or "", "HOPEFUL"
        ),
    }


def merge_saved_answers(
    saved: dict[str, Any] | None, profile: PersonalFutureBuildingProfile | None
) -> dict[str, Any]:
    base: dict[str, Any] = {}
    if profile is not None:
        base.update(answers_from_profile(profile))
    if saved:
        migrated = FUTURE_BUILDING_TEMPLATE_CONTRACT.migrate_answers(saved)
        base.update(migrated)
    return FUTURE_BUILDING_TEMPLATE_CONTRACT.normalize_answers(base) if base else {}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return [str(value)]


def _assign_identity(theme: str, values: list[str]) -> str:
    if "Learning" in theme or "Skills" in theme:
        return "Growth Architect"
    if "Business" in theme:
        return "Strategic Builder"
    if "Impact" in values or "Purpose" in values:
        return "Purpose-Driven Builder"
    return "Consistent Builder"


def _primary_opportunity(theme: str, drivers: list[str]) -> str:
    if "Learning" in drivers:
        return "Deep Skill Development"
    if "Business" in theme:
        return "Market Expansion"
    return "Focused Execution"


def _breakthrough_potential(state: str, feeling: str) -> str:
    if state in {"BUILDING_MOMENTUM", "MAKING_PROGRESS"} and feeling in {"Exciting", "Confident", "Hopeful"}:
        return "HIGH"
    if state == "EXPLORING_OPTIONS":
        return "MODERATE"
    return "LOW"


def _momentum_percent(answers: dict[str, Any]) -> int:
    state = str(answers.get("current_state") or "")
    base = {"JUST_STARTING": 35, "EXPLORING_OPTIONS": 50, "MAKING_PROGRESS": 65, "BUILDING_MOMENTUM": 80}.get(
        state, 50
    )
    return min(95, base)


async def upsert_future_building_profile(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    answers: dict[str, Any],
) -> PersonalFutureBuildingProfile:
    contract = FUTURE_BUILDING_TEMPLATE_CONTRACT
    contract.validate(answers)
    fields = contract.to_profile_fields(answers)

    result = await session.execute(
        select(PersonalFutureBuildingProfile).where(
            PersonalFutureBuildingProfile.moment_id == moment_id
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = PersonalFutureBuildingProfile(
            moment_id=moment_id,
            user_id=user_id,
            **fields,
        )
        session.add(profile)
    else:
        for key, value in fields.items():
            setattr(profile, key, value)
    await session.flush()
    return profile
