"""Relationships setup template contract — versioned field mapping and validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.domains.personal.models import PersonalRelationshipsProfile
from app.domains.personal.templates.relationships.constants import (
    MOMENT_TYPE_CODE,
    TEMPLATE_ID,
    TEMPLATE_VERSION,
)

_FOCUS_LABELS = {
    "PARTNER": "Partner",
    "FAMILY": "Family",
    "FRIENDS": "Friends",
    "COMMUNITY": "Community",
    "WORK": "Work",
    "SELF": "Self",
}

_STATE_LABELS = {
    "CONNECTED": "Connected",
    "DISTANT": "Distant",
    "REBUILDING": "Rebuilding",
    "OVERWHELMED": "Overwhelmed",
    "GROWING": "Growing",
}

_WANT_MORE_LABELS = {
    "QUALITY_TIME": "Quality Time",
    "TRUST": "Trust",
    "OPENNESS": "Openness",
    "SUPPORT": "Support",
    "FUN": "Fun",
}

_NEGLECTED_LABELS = {
    "CHECK_INS": "Check-ins",
    "BOUNDARIES": "Boundaries",
    "APPRECIATION": "Appreciation",
    "SHARED_TIME": "Shared Time",
    "EMOTIONAL_SUPPORT": "Emotional Support",
}

_STRENGTH_LABELS = {
    "CONSISTENCY": "Consistency",
    "HONESTY": "Honesty",
    "EMPATHY": "Empathy",
    "SHARED_GOALS": "Shared Goals",
    "PRESENCE": "Presence",
}

_INVESTMENT_LABELS = {
    "LISTENING": "Listening",
    "PLANNING": "Planning",
    "CELEBRATING": "Celebrating",
    "REPAIRING": "Repairing",
    "BOUNDARIES": "Boundaries",
}

_NETWORK_LABELS = {
    "FAMILY": "Family",
    "PARTNER": "Partner",
    "FRIENDS": "Friends",
    "PROFESSIONAL": "Professional Network",
    "COMMUNITY": "Community",
}

_COMMUNICATION_LABELS = {
    "DIRECT": "Direct",
    "GENTLE": "Gentle",
    "LISTENING_FIRST": "Listening First",
    "WRITTEN": "Written",
    "SPONTANEOUS": "Spontaneous",
}

_GOAL_LABELS = {
    "DEEPER_BONDS": "Deeper Bonds",
    "REPAIR_RELATIONSHIPS": "Repair Relationships",
    "EXPAND_NETWORK": "Expand Network",
    "BETTER_BOUNDARIES": "Better Boundaries",
    "MORE_PRESENCE": "More Presence",
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
        focus = str(
            migrated.get("relationship_focus")
            or migrated.get("relationship_vision")
            or "FAMILY"
        )
        if isinstance(focus, list):
            focus = focus[0] if focus else "FAMILY"
        state = str(
            migrated.get("current_state")
            or migrated.get("current_relationship_state")
            or "CONNECTED"
        )
        want_more = _as_list(migrated.get("want_more") or migrated.get("desired_connection_types"))
        neglected = _as_list(
            migrated.get("neglected") or migrated.get("neglected_relationship_areas")
        )
        strength = _as_list(
            migrated.get("strength_drivers") or migrated.get("relationship_strength_factors")
        )
        investment = _as_list(
            migrated.get("investment_areas") or migrated.get("relationship_investment_areas")
        )
        network_sections = _as_list(migrated.get("family")) + _as_list(migrated.get("partner"))
        network_sections += _as_list(migrated.get("friends"))
        network_sections += _as_list(migrated.get("professional_network"))
        network_sections += _as_list(migrated.get("community"))
        communication = _as_list(migrated.get("communication_style"))
        goals = _as_list(migrated.get("relationship_goals"))
        if network_sections:
            want_more = list(dict.fromkeys(want_more + network_sections))
        if communication:
            strength = list(dict.fromkeys(strength + communication))
        if goals:
            investment = list(dict.fromkeys(investment + goals))
        normalized = {
            "template_id": migrated.get("template_id") or self.template_id,
            "template_version": int(migrated.get("template_version") or self.template_version),
            "relationship_focus": focus,
            "current_state": state,
            "want_more": want_more,
            "neglected": neglected,
            "strength_drivers": strength,
            "investment_areas": investment,
            "communication_style": communication,
            "relationship_goals": goals,
        }
        if migrated.get("moment_name"):
            normalized["moment_name"] = str(migrated["moment_name"])
        return normalized

    def validate(self, answers: dict[str, Any]) -> None:
        n = self.normalize_answers(answers)
        if not n.get("want_more"):
            raise ValidationError("At least one connection type must be selected")
        if not n.get("neglected"):
            raise ValidationError("At least one neglected area must be selected")
        if not n.get("strength_drivers"):
            raise ValidationError("At least one strength driver must be selected")
        if not n.get("investment_areas"):
            raise ValidationError("At least one investment area must be selected")

    def to_profile_fields(self, answers: dict[str, Any]) -> dict[str, Any]:
        n = self.normalize_answers(answers)
        focus = _FOCUS_LABELS.get(n["relationship_focus"], n["relationship_focus"])
        state = _STATE_LABELS.get(n["current_state"], n["current_state"])
        desired = [_WANT_MORE_LABELS.get(v, _NETWORK_LABELS.get(v, v)) for v in n["want_more"]]
        neglected = [_NEGLECTED_LABELS.get(v, v) for v in n["neglected"]]
        strength = [_STRENGTH_LABELS.get(v, _COMMUNICATION_LABELS.get(v, v)) for v in n["strength_drivers"]]
        investment = [_INVESTMENT_LABELS.get(v, _GOAL_LABELS.get(v, v)) for v in n["investment_areas"]]
        identity = _assign_identity(focus, desired)
        gap = neglected[0] if neglected else "Check-ins"
        opportunity = desired[0] if desired else "Quality Time"
        potential = "HIGH" if len(desired) >= 3 else "MODERATE"
        energy = "High" if state in {"Growing", "Connected"} else "Steady"
        return {
            "relationship_focus": focus,
            "current_relationship_state": state,
            "desired_connection_types": desired,
            "neglected_relationship_areas": neglected,
            "relationship_strength_factors": strength,
            "relationship_investment_areas": investment,
            "relationship_identity": identity,
            "relationship_energy": energy,
            "primary_relationship_gap": gap,
            "primary_relationship_opportunity": opportunity,
            "relationship_potential": potential,
        }

    def preview_block(self, answers: dict[str, Any]) -> dict[str, Any]:
        fields = self.to_profile_fields(answers)
        bond_pct = _bond_percent(answers)
        return {
            "assigned_identity": {
                "badge_label": "Assigned Identity",
                "title": fields["relationship_identity"],
                "body": (
                    f"You are investing in {fields['relationship_focus'].lower()} relationships "
                    f"with a {fields['current_relationship_state'].lower()} rhythm."
                ),
                "icon_name": "favorite",
            },
            "runtime_projection": [
                {"label": "Focus", "value": fields["relationship_focus"]},
                {"label": "Current State", "value": fields["current_relationship_state"]},
                {"label": "Energy", "value": fields["relationship_energy"]},
                {"label": "Priority", "value": fields["desired_connection_types"][0] if fields["desired_connection_types"] else "Trust"},
                {"label": "Gap", "value": fields["primary_relationship_gap"], "accent": "error"},
                {"label": "Opportunity", "value": fields["primary_relationship_opportunity"]},
            ],
            "relationship_horizon": {
                "trajectory": fields["current_relationship_state"],
                "bond_percent": bond_pct,
                "opportunity": fields["primary_relationship_opportunity"],
                "breakthrough": fields["relationship_potential"],
                "obstacle_title": fields["primary_relationship_gap"],
                "obstacle_body": f"{fields['primary_relationship_gap']} is the relationship area asking for attention.",
            },
        }


RELATIONSHIPS_TEMPLATE_CONTRACT = TemplateSetupContract(
    template_id=TEMPLATE_ID,
    template_version=TEMPLATE_VERSION,
    moment_type_code=MOMENT_TYPE_CODE,
    required_fields=[
        "relationship_focus",
        "current_state",
        "want_more",
        "neglected",
        "strength_drivers",
        "investment_areas",
    ],
)


def _assign_identity(focus: str, desired: list[str]) -> str:
    primary = desired[0] if desired else "Connection"
    if "Partner" in focus:
        return f"Intentional {primary} Partner"
    if "Family" in focus:
        return f"Family {primary} Builder"
    if "Friends" in focus:
        return f"Social {primary} Connector"
    return f"Relationship {primary} Builder"


def _bond_percent(answers: dict[str, Any]) -> int:
    n = RELATIONSHIPS_TEMPLATE_CONTRACT.normalize_answers(answers)
    base = 62
    base += min(12, len(n.get("want_more") or []) * 3)
    base += 6 if n.get("current_state") in {"GROWING", "CONNECTED"} else 0
    return max(45, min(92, base))


def to_setup_fields() -> list[dict[str, Any]]:
    return [
        {
            "field_key": "moment_name",
            "label": "Name this moment",
            "helper_text": "Give your relationships journey a name.",
            "field_type": "TEXT",
            "required": True,
        },
        {
            "field_key": "relationship_focus",
            "label": "Relationship vision",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _FOCUS_LABELS.items()],
        },
        {
            "field_key": "current_state",
            "label": "Current relationships",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _STATE_LABELS.items()],
        },
        {
            "field_key": "want_more",
            "label": "What do you want more of?",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _WANT_MORE_LABELS.items()],
        },
        {
            "field_key": "neglected",
            "label": "What feels neglected?",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _NEGLECTED_LABELS.items()],
        },
        {
            "field_key": "strength_drivers",
            "label": "Communication style",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _STRENGTH_LABELS.items()],
        },
        {
            "field_key": "investment_areas",
            "label": "Relationship goals",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [{"value": k, "label": v} for k, v in _INVESTMENT_LABELS.items()],
        },
    ]


def answers_from_profile(profile: PersonalRelationshipsProfile) -> dict[str, Any]:
    reverse_focus = {v: k for k, v in _FOCUS_LABELS.items()}
    reverse_state = {v: k for k, v in _STATE_LABELS.items()}
    reverse_want = {v: k for k, v in _WANT_MORE_LABELS.items()}
    reverse_neglected = {v: k for k, v in _NEGLECTED_LABELS.items()}
    reverse_strength = {v: k for k, v in _STRENGTH_LABELS.items()}
    reverse_investment = {v: k for k, v in _INVESTMENT_LABELS.items()}
    return {
        "template_id": TEMPLATE_ID,
        "template_version": TEMPLATE_VERSION,
        "relationship_focus": reverse_focus.get(profile.relationship_focus or "", "FAMILY"),
        "current_state": reverse_state.get(profile.current_relationship_state or "", "CONNECTED"),
        "want_more": [
            reverse_want.get(v, v) for v in (profile.desired_connection_types or [])
        ],
        "neglected": [
            reverse_neglected.get(v, v) for v in (profile.neglected_relationship_areas or [])
        ],
        "strength_drivers": [
            reverse_strength.get(v, v) for v in (profile.relationship_strength_factors or [])
        ],
        "investment_areas": [
            reverse_investment.get(v, v) for v in (profile.relationship_investment_areas or [])
        ],
    }


def merge_saved_answers(
    draft: dict[str, Any] | None,
    profile: PersonalRelationshipsProfile | None,
) -> dict[str, Any] | None:
    if draft:
        return RELATIONSHIPS_TEMPLATE_CONTRACT.normalize_answers(draft)
    if profile:
        return answers_from_profile(profile)
    return None


async def upsert_relationships_profile(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    RELATIONSHIPS_TEMPLATE_CONTRACT.validate(answers)
    fields = RELATIONSHIPS_TEMPLATE_CONTRACT.to_profile_fields(answers)
    result = await session.execute(
        select(PersonalRelationshipsProfile).where(
            PersonalRelationshipsProfile.moment_id == moment_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        row = PersonalRelationshipsProfile(
            moment_id=moment_id,
            user_id=user_id,
            **fields,
        )
        session.add(row)
    else:
        for key, value in fields.items():
            setattr(existing, key, value)
    await session.flush()
