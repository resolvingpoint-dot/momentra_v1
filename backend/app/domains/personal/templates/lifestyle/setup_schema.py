"""Lifestyle setup template contract — versioned field mapping and validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.domains.personal.models import PersonalLifestyleProfile
from app.domains.personal.templates.lifestyle.constants import (
    MOMENT_TYPE_CODE,
    TEMPLATE_ID,
    TEMPLATE_VERSION,
)

_STYLE_LABELS = {
    "BALANCED": "Balanced",
    "ADVENTUROUS": "Adventurous",
    "MINIMAL": "Minimal",
    "SOCIAL": "Social",
    "CREATIVE": "Creative",
    "WELLNESS_FOCUSED": "Wellness Focused",
}

_STATE_LABELS = {
    "THRIVING": "Thriving",
    "STEADY": "Steady",
    "STRETCHED": "Stretched",
    "RECOVERING": "Recovering",
    "REINVENTING": "Reinventing",
}

_ENERGY_LABELS = {
    "LOW": "Low",
    "STEADY": "Steady",
    "HIGH": "High",
    "VARIABLE": "Variable",
}

_VECTOR_LABELS = {
    "JOY": "Joy",
    "REST": "Rest",
    "CONNECTION": "Connection",
    "CREATIVITY": "Creativity",
    "ADVENTURE": "Adventure",
    "HEALTH": "Health",
    "BALANCE": "Balance",
    "GROWTH": "Growth",
}

_NEGLECTED_LABELS = {
    "SELF_CARE": "Self Care",
    "RELATIONSHIPS": "Relationships",
    "HOBBIES": "Hobbies",
    "MOVEMENT": "Movement",
    "LEARNING": "Learning",
    "REST": "Rest",
    "HOME": "Home",
    "NUTRITION": "Nutrition",
}

_ENRICHMENT_LABELS = {
    "MORE_EXPERIENCES": "More Experiences",
    "DEEPER_CONNECTIONS": "Deeper Connections",
    "BETTER_ROUTINES": "Better Routines",
    "NEW_PASSIONS": "New Passions",
    "CALMER_HOME": "Calmer Home",
    "STRONGER_HEALTH": "Stronger Health",
}

_GOAL_LABELS = {
    "VIBRANT_HEALTH": "Vibrant Health",
    "DEEP_CONNECTIONS": "Deep Connections",
    "CREATIVE_LIFE": "Creative Life",
    "ADVENTURE_READY": "Adventure Ready",
    "BALANCED_RHYTHM": "Balanced Rhythm",
}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    if isinstance(value, str) and value:
        return [value]
    return []


@dataclass
class TemplateSetupContract:
    template_id: str
    template_version: int
    moment_type_code: str
    required_fields: list[str] = field(default_factory=list)

    def migrate_answers(self, answers: dict[str, Any]) -> dict[str, Any]:
        migrated = dict(answers)
        migrated["template_version"] = int(migrated.get("template_version") or TEMPLATE_VERSION)
        return migrated

    def normalize_answers(self, answers: dict[str, Any]) -> dict[str, Any]:
        migrated = self.migrate_answers(answers)
        style = str(
            migrated.get("lifestyle_vision")
            or migrated.get("lifestyle_style")
            or "BALANCED"
        )
        state = str(
            migrated.get("current_lifestyle")
            or migrated.get("current_lifestyle_state")
            or "STEADY"
        )
        energy = str(
            migrated.get("health_energy")
            or migrated.get("current_energy")
            or "STEADY"
        )
        habits = _as_list(migrated.get("daily_habits") or migrated.get("best_day_drivers"))
        balance = _as_list(migrated.get("work_life_balance"))
        social = _as_list(migrated.get("relationships_social"))
        environment = _as_list(migrated.get("home_environment"))
        priorities = _as_list(
            migrated.get("personal_priorities")
            or migrated.get("want_more")
            or migrated.get("desired_lifestyle_vectors")
        )
        neglected = _as_list(
            migrated.get("neglected")
            or migrated.get("neglected_lifestyle_areas")
        )
        enrichment = _as_list(
            migrated.get("future_lifestyle_goals")
            or migrated.get("richer_life")
            or migrated.get("lifestyle_enrichment_factors")
        )
        if balance:
            enrichment = list(dict.fromkeys(enrichment + balance))
        if social:
            priorities = list(dict.fromkeys(priorities + social))
        if environment:
            enrichment = list(dict.fromkeys(enrichment + environment))
        normalized = {
            "template_id": migrated.get("template_id") or self.template_id,
            "template_version": int(migrated.get("template_version") or self.template_version),
            "lifestyle_style": style,
            "current_lifestyle_state": state,
            "current_energy": energy,
            "want_more": priorities,
            "neglected": neglected,
            "richer_life": enrichment[0] if enrichment else "MORE_EXPERIENCES",
            "daily_habits": habits,
            "personal_priorities": priorities,
            "future_lifestyle_goals": enrichment,
        }
        if migrated.get("moment_name"):
            normalized["moment_name"] = str(migrated["moment_name"])
        return normalized

    def validate(self, answers: dict[str, Any]) -> None:
        n = self.normalize_answers(answers)
        if not n.get("want_more"):
            raise ValidationError("At least one personal priority must be selected")
        if not n.get("neglected"):
            raise ValidationError("At least one neglected area must be selected")

    def to_profile_fields(self, answers: dict[str, Any]) -> dict[str, Any]:
        n = self.normalize_answers(answers)
        style = _STYLE_LABELS.get(n["lifestyle_style"], n["lifestyle_style"])
        state = _STATE_LABELS.get(n["current_lifestyle_state"], n["current_lifestyle_state"])
        energy = _ENERGY_LABELS.get(n["current_energy"], n["current_energy"])
        vectors = [_VECTOR_LABELS.get(v, v) for v in n["want_more"]]
        neglected = [_NEGLECTED_LABELS.get(v, v) for v in n["neglected"]]
        habits = n.get("daily_habits") or ["Morning movement", "Evening reflection"]
        enrichment = [
            _ENRICHMENT_LABELS.get(v, v) for v in n.get("future_lifestyle_goals") or [n["richer_life"]]
        ]
        identity = _assign_identity(style, vectors)
        gap = neglected[0] if neglected else "Recovery"
        opportunity = enrichment[0] if enrichment else "More Experiences"
        potential = "HIGH" if len(vectors) >= 3 else "MODERATE"
        return {
            "lifestyle_style": style,
            "current_lifestyle_state": state,
            "desired_lifestyle_vectors": vectors,
            "neglected_lifestyle_areas": neglected,
            "best_day_drivers": habits[:4],
            "lifestyle_enrichment_factors": enrichment[:4],
            "lifestyle_identity": identity,
            "lifestyle_energy": energy,
            "primary_lifestyle_gap": gap,
            "primary_lifestyle_opportunity": opportunity,
            "lifestyle_potential": potential,
        }

    def preview_block(self, answers: dict[str, Any]) -> dict[str, Any]:
        fields = self.to_profile_fields(answers)
        vitality_pct = _vitality_percent(answers)
        return {
            "assigned_identity": {
                "badge_label": "Assigned Identity",
                "title": fields["lifestyle_identity"],
                "body": (
                    f"You are shaping a {fields['lifestyle_style'].lower()} lifestyle with "
                    f"{fields['current_lifestyle_state'].lower()} rhythm."
                ),
                "icon_name": "spa",
            },
            "runtime_projection": [
                {"label": "Lifestyle Style", "value": fields["lifestyle_style"]},
                {"label": "Current State", "value": fields["current_lifestyle_state"]},
                {"label": "Energy", "value": fields["lifestyle_energy"]},
                {"label": "Priority", "value": fields["desired_lifestyle_vectors"][0] if fields["desired_lifestyle_vectors"] else "Joy"},
                {"label": "Gap", "value": fields["primary_lifestyle_gap"], "accent": "error"},
                {"label": "Opportunity", "value": fields["primary_lifestyle_opportunity"]},
            ],
            "lifestyle_horizon": {
                "trajectory": fields["current_lifestyle_state"],
                "vitality_percent": vitality_pct,
                "opportunity": fields["primary_lifestyle_opportunity"],
                "breakthrough": fields["lifestyle_potential"],
                "obstacle_title": fields["primary_lifestyle_gap"],
                "obstacle_body": f"{fields['primary_lifestyle_gap']} is the lifestyle area asking for attention.",
            },
        }


LIFESTYLE_TEMPLATE_CONTRACT = TemplateSetupContract(
    template_id=TEMPLATE_ID,
    template_version=TEMPLATE_VERSION,
    moment_type_code=MOMENT_TYPE_CODE,
    required_fields=[
        "lifestyle_style",
        "current_lifestyle_state",
        "current_energy",
        "want_more",
        "neglected",
        "richer_life",
    ],
)


def _assign_identity(style: str, vectors: list[str]) -> str:
    primary = vectors[0] if vectors else "Balance"
    if "Adventurous" in style:
        return f"Adventurous {primary} Seeker"
    if "Wellness" in style:
        return f"Wellness {primary} Builder"
    if "Creative" in style:
        return f"Creative {primary} Curator"
    return f"Lifestyle {primary} Curator"


def _vitality_percent(answers: dict[str, Any]) -> int:
    n = LIFESTYLE_TEMPLATE_CONTRACT.normalize_answers(answers)
    base = 62
    base += min(12, len(n.get("want_more") or []) * 3)
    base += 6 if n.get("current_energy") == "HIGH" else 0
    return max(45, min(92, base))


def to_setup_fields() -> list[dict[str, Any]]:
    return [
        {
            "field_key": "moment_name",
            "label": "Name this moment",
            "helper_text": "Give your lifestyle journey a name.",
            "field_type": "TEXT",
            "required": True,
        },
        {
            "field_key": "lifestyle_vision",
            "label": "Lifestyle vision",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _STYLE_LABELS.items()],
        },
        {
            "field_key": "current_lifestyle",
            "label": "Current lifestyle",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _STATE_LABELS.items()],
        },
        {
            "field_key": "health_energy",
            "label": "Health & energy",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _ENERGY_LABELS.items()],
        },
        {
            "field_key": "daily_habits",
            "label": "Daily habits",
            "field_type": "MULTI_SELECT",
            "required": False,
            "options": [
                {"value": "MORNING_ROUTINE", "label": "Morning Routine"},
                {"value": "MOVEMENT", "label": "Movement"},
                {"value": "MINDFULNESS", "label": "Mindfulness"},
                {"value": "SLEEP", "label": "Sleep"},
                {"value": "MEAL_PREP", "label": "Meal Prep"},
            ],
        },
        {
            "field_key": "work_life_balance",
            "label": "Work-life balance",
            "field_type": "MULTI_SELECT",
            "required": False,
            "options": [
                {"value": "BOUNDARIES", "label": "Boundaries"},
                {"value": "RECOVERY", "label": "Recovery"},
                {"value": "FOCUS_BLOCKS", "label": "Focus Blocks"},
                {"value": "FLEXIBILITY", "label": "Flexibility"},
            ],
        },
        {
            "field_key": "relationships_social",
            "label": "Relationships & social",
            "field_type": "MULTI_SELECT",
            "required": False,
            "options": [
                {"value": "QUALITY_TIME", "label": "Quality Time"},
                {"value": "COMMUNITY", "label": "Community"},
                {"value": "FAMILY", "label": "Family"},
                {"value": "FRIENDS", "label": "Friends"},
            ],
        },
        {
            "field_key": "home_environment",
            "label": "Home & environment",
            "field_type": "MULTI_SELECT",
            "required": False,
            "options": [
                {"value": "CALM_SPACE", "label": "Calm Space"},
                {"value": "ORGANIZED", "label": "Organized"},
                {"value": "NATURE", "label": "Nature"},
                {"value": "INSPIRING", "label": "Inspiring"},
            ],
        },
        {
            "field_key": "personal_priorities",
            "label": "Personal priorities",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _VECTOR_LABELS.items()],
        },
        {
            "field_key": "neglected",
            "label": "What feels neglected?",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _NEGLECTED_LABELS.items()],
        },
        {
            "field_key": "future_lifestyle_goals",
            "label": "Future lifestyle goals",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _GOAL_LABELS.items()],
        },
    ]


def answers_from_profile(profile: PersonalLifestyleProfile) -> dict[str, Any]:
    reverse_style = {v: k for k, v in _STYLE_LABELS.items()}
    reverse_state = {v: k for k, v in _STATE_LABELS.items()}
    reverse_energy = {v: k for k, v in _ENERGY_LABELS.items()}
    reverse_vector = {v: k for k, v in _VECTOR_LABELS.items()}
    reverse_neglected = {v: k for k, v in _NEGLECTED_LABELS.items()}
    reverse_goal = {v: k for k, v in _GOAL_LABELS.items()}
    return {
        "template_id": TEMPLATE_ID,
        "template_version": TEMPLATE_VERSION,
        "lifestyle_vision": reverse_style.get(profile.lifestyle_style or "", "BALANCED"),
        "current_lifestyle": reverse_state.get(profile.current_lifestyle_state or "", "STEADY"),
        "health_energy": reverse_energy.get(profile.lifestyle_energy or "", "STEADY"),
        "personal_priorities": [
            reverse_vector.get(v, v) for v in (profile.desired_lifestyle_vectors or [])
        ],
        "neglected": [
            reverse_neglected.get(v, v) for v in (profile.neglected_lifestyle_areas or [])
        ],
        "future_lifestyle_goals": [
            reverse_goal.get(v, v) for v in (profile.lifestyle_enrichment_factors or [])
        ],
        "daily_habits": list(profile.best_day_drivers or []),
    }


def merge_saved_answers(
    draft: dict[str, Any] | None,
    profile: PersonalLifestyleProfile | None,
) -> dict[str, Any] | None:
    if draft:
        return LIFESTYLE_TEMPLATE_CONTRACT.normalize_answers(draft)
    if profile:
        return answers_from_profile(profile)
    return None


async def upsert_lifestyle_profile(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    LIFESTYLE_TEMPLATE_CONTRACT.validate(answers)
    fields = LIFESTYLE_TEMPLATE_CONTRACT.to_profile_fields(answers)
    result = await session.execute(
        select(PersonalLifestyleProfile).where(
            PersonalLifestyleProfile.moment_id == moment_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        row = PersonalLifestyleProfile(
            moment_id=moment_id,
            user_id=user_id,
            **fields,
        )
        session.add(row)
    else:
        for key, value in fields.items():
            setattr(existing, key, value)
    await session.flush()
