"""Life Operations setup template contract — field mapping, preview, and profile upsert."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.domains.personal.models import PersonalLifeOperationsProfile
from app.domains.personal.templates.life_operations.constants import (
    MOMENT_TYPE_CODE,
    TEMPLATE_ID,
    TEMPLATE_VERSION,
)

_STATE_LABELS = {
    "MOSTLY_STABLE": "Mostly Stable",
    "OVERWHELMING": "Overwhelming",
    "VERY_BUSY": "Very Busy",
    "UNPREDICTABLE": "Unpredictable",
    "TRYING_TO_RESET": "Trying to Reset",
    "BUILDING_MOMENTUM": "Building Momentum",
}

_STATE_BAR = {
    "MOSTLY_STABLE": 0.35,
    "OVERWHELMING": 0.85,
    "VERY_BUSY": 0.7,
    "UNPREDICTABLE": 0.55,
    "TRYING_TO_RESET": 0.45,
    "BUILDING_MOMENTUM": 0.65,
}

_STATE_ACCENT = {
    "MOSTLY_STABLE": "primary",
    "OVERWHELMING": "error",
    "VERY_BUSY": "tertiary",
    "UNPREDICTABLE": "tertiary",
    "TRYING_TO_RESET": "primary",
    "BUILDING_MOMENTUM": "primary",
}

_DIRECTION_LABELS = {
    "CALMNESS": "Calmness",
    "STRUCTURE": "Structure",
    "ENERGY": "Energy",
    "RECOVERY": "Recovery",
    "FOCUS": "Focus",
    "STABILITY": "Stability",
    "FLEXIBILITY": "Flexibility",
    "MOMENTUM": "Momentum",
}

_PRESSURE_LABELS = {
    "COMMITMENTS": "Commitments",
    "MONEY": "Money",
    "NO_ROUTINE": "No Routine",
    "BURNOUT": "Burnout",
    "OVERLOAD": "Overload",
    "TASKS": "Tasks",
    "NO_RECOVERY": "No Recovery",
    "CHANGE": "Change",
}

_RECOVERY_LABELS = {
    "QUIET_TIME": "Quiet Time",
    "WALKS": "Walks",
    "SLEEP": "Sleep",
    "REFLECTION": "Reflection",
    "EXERCISE": "Exercise",
    "PEOPLE": "People",
    "FLEXIBILITY": "Flexibility",
    "FINANCIAL_CLARITY": "Financial Clarity",
}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    if isinstance(value, str) and value:
        return [value]
    return []


def _labels(mapping: dict[str, str], values: list[str]) -> list[str]:
    return [mapping.get(v, v) for v in values]


@dataclass
class TemplateSetupContract:
    template_id: str
    template_version: int
    moment_type_code: str
    required_fields: list[str] = field(default_factory=list)

    def migrate_answers(self, answers: dict[str, Any]) -> dict[str, Any]:
        migrated = dict(answers)
        migrated["template_version"] = int(
            migrated.get("template_version") or TEMPLATE_VERSION
        )
        return migrated

    def normalize_answers(self, answers: dict[str, Any]) -> dict[str, Any]:
        migrated = self.migrate_answers(answers)
        state = str(migrated.get("current_life_state") or "MOSTLY_STABLE").upper()
        if state not in _STATE_LABELS:
            state = "MOSTLY_STABLE"
        directions = [
            v.upper()
            for v in _as_list(migrated.get("desired_directions"))
            if v.upper() in _DIRECTION_LABELS
        ]
        pressures = [
            v.upper()
            for v in _as_list(migrated.get("pressure_sources"))
            if v.upper() in _PRESSURE_LABELS
        ]
        recovery = [
            v.upper()
            for v in _as_list(migrated.get("recovery_supports"))
            if v.upper() in _RECOVERY_LABELS
        ]
        normalized = {
            "template_id": migrated.get("template_id") or self.template_id,
            "template_version": int(
                migrated.get("template_version") or self.template_version
            ),
            "current_life_state": state,
            "desired_directions": directions,
            "pressure_sources": pressures,
            "recovery_supports": recovery,
        }
        if migrated.get("moment_name"):
            normalized["moment_name"] = str(migrated["moment_name"])
        return normalized

    def validate(self, answers: dict[str, Any]) -> None:
        n = self.normalize_answers(answers)
        if not n.get("current_life_state"):
            raise ValidationError("Current life state is required")
        if not n.get("desired_directions"):
            raise ValidationError("At least one desired direction must be selected")
        if not n.get("pressure_sources"):
            raise ValidationError("At least one pressure source must be selected")
        if not n.get("recovery_supports"):
            raise ValidationError("At least one recovery support must be selected")

    def to_profile_fields(self, answers: dict[str, Any]) -> dict[str, Any]:
        n = self.normalize_answers(answers)
        state_label = _STATE_LABELS[n["current_life_state"]]
        directions = _labels(_DIRECTION_LABELS, n["desired_directions"])
        pressures = _labels(_PRESSURE_LABELS, n["pressure_sources"])
        recovery = _labels(_RECOVERY_LABELS, n["recovery_supports"])
        identity = _assign_identity(directions, pressures)
        focus = directions[0] if directions else "Structure"
        pressure_level = _pressure_load(n["current_life_state"], pressures)
        recovery_score = _recovery_score(recovery, pressures)
        return {
            "current_life_state": state_label,
            "desired_directions": directions,
            "pressure_sources": pressures,
            "recovery_supports": recovery,
            "runtime_identity": identity,
            "initial_runtime_focus": focus,
            "pressure_load_level": pressure_level,
            "recovery_integrity_score": recovery_score,
        }

    def preview_block(self, answers: dict[str, Any]) -> dict[str, Any]:
        fields = self.to_profile_fields(answers)
        n = self.normalize_answers(answers)
        rhythm_pct, pressure_pct, recovery_pct = _meter_pcts(n)
        narrative = (
            f"Your rhythm is {fields['current_life_state'].lower()} while carrying "
            f"{fields['pressure_load_level'].lower()} pressure. "
            f"Protecting {fields['recovery_supports'][0].lower() if fields['recovery_supports'] else 'recovery'} "
            "will make the system more sustainable."
        )
        priorities = []
        if fields["recovery_supports"]:
            priorities.append(
                f"Protect {fields['recovery_supports'][0].lower()} windows"
            )
        if fields["desired_directions"]:
            priorities.append(
                f"Keep {fields['desired_directions'][0].lower()} without stacking load"
            )
        if len(fields["recovery_supports"]) > 1:
            priorities.append(
                f"Use {fields['recovery_supports'][1].lower()} as a reset point"
            )
        else:
            priorities.append("Use sleep and walks as reset points")
        return {
            "narrative": narrative,
            "rhythm": {"label": _rhythm_label(rhythm_pct), "pct": rhythm_pct},
            "pressure": {"label": _pressure_label(pressure_pct), "pct": pressure_pct},
            "recovery": {"label": _recovery_label(recovery_pct), "pct": recovery_pct},
            "runtime_priorities": priorities[:3],
            "identity_chips": [fields["runtime_identity"]],
            "assigned_identity": {
                "badge_label": "Intelligence Profile",
                "title": fields["runtime_identity"],
                "body": (
                    f"A {fields['current_life_state'].lower()} rhythm with "
                    f"protected recovery windows."
                ),
                "icon_name": "intelligence",
            },
        }


LIFE_OPERATIONS_TEMPLATE_CONTRACT = TemplateSetupContract(
    template_id=TEMPLATE_ID,
    template_version=TEMPLATE_VERSION,
    moment_type_code=MOMENT_TYPE_CODE,
    required_fields=[
        "current_life_state",
        "desired_directions",
        "pressure_sources",
        "recovery_supports",
    ],
)


def _assign_identity(directions: list[str], pressures: list[str]) -> str:
    if "Structure" in directions:
        return "Structure Seeker"
    if "Recovery" in directions:
        return "Recovery Architect"
    if "Calmness" in directions:
        return "Calm Operator"
    if "Momentum" in directions:
        return "Momentum Builder"
    if "Money" in pressures:
        return "Pressure Balancer"
    return "Rhythm Operator"


def _pressure_load(state: str, pressures: list[str]) -> str:
    if state in ("OVERWHELMING",) or len(pressures) >= 4:
        return "HIGH"
    if state in ("VERY_BUSY", "UNPREDICTABLE") or len(pressures) >= 2:
        return "MODERATE"
    return "LOW"


def _recovery_score(recovery: list[str], pressures: list[str]) -> float:
    base = 45.0 + min(30.0, len(recovery) * 8.0) - min(20.0, len(pressures) * 4.0)
    return max(10.0, min(95.0, round(base, 2)))


def _meter_pcts(n: dict[str, Any]) -> tuple[int, int, int]:
    bar = _STATE_BAR.get(n["current_life_state"], 0.5)
    pressure_pct = min(92, int(35 + len(n["pressure_sources"]) * 12 + bar * 20))
    recovery_pct = max(18, min(88, int(30 + len(n["recovery_supports"]) * 10 - bar * 15)))
    rhythm_pct = max(35, min(85, int(70 - pressure_pct * 0.25 + recovery_pct * 0.2)))
    return rhythm_pct, pressure_pct, recovery_pct


def _rhythm_label(pct: int) -> str:
    if pct >= 70:
        return "Steady"
    if pct >= 50:
        return "Building"
    return "Fragile"


def _pressure_label(pct: int) -> str:
    if pct >= 75:
        return "Elevated"
    if pct >= 50:
        return "Moderate"
    return "Light"


def _recovery_label(pct: int) -> str:
    if pct >= 65:
        return "Supported"
    if pct >= 40:
        return "Needs support"
    return "Depleted"


def to_setup_fields() -> list[dict[str, Any]]:
    return [
        {
            "field_key": "current_life_state",
            "label": "How does life feel right now?",
            "helper_text": "Choose the state closest to your current rhythm.",
            "field_type": "SINGLE_SELECT",
            "required": True,
            "options": [
                {
                    "value": k,
                    "label": v,
                    "bar_level": _STATE_BAR[k],
                    "accent": _STATE_ACCENT[k],
                }
                for k, v in _STATE_LABELS.items()
            ],
        },
        {
            "field_key": "desired_directions",
            "label": "What do you want more of?",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [
                {"value": k, "label": v} for k, v in _DIRECTION_LABELS.items()
            ],
        },
        {
            "field_key": "pressure_sources",
            "label": "What creates pressure?",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [
                {"value": k, "label": v} for k, v in _PRESSURE_LABELS.items()
            ],
        },
        {
            "field_key": "recovery_supports",
            "label": "What restores you?",
            "field_type": "MULTI_SELECT",
            "required": True,
            "options": [
                {"value": k, "label": v} for k, v in _RECOVERY_LABELS.items()
            ],
        },
    ]


def answers_from_profile(profile: PersonalLifeOperationsProfile) -> dict[str, Any]:
    reverse_state = {v: k for k, v in _STATE_LABELS.items()}
    reverse_dir = {v: k for k, v in _DIRECTION_LABELS.items()}
    reverse_pressure = {v: k for k, v in _PRESSURE_LABELS.items()}
    reverse_recovery = {v: k for k, v in _RECOVERY_LABELS.items()}
    return {
        "template_id": TEMPLATE_ID,
        "template_version": TEMPLATE_VERSION,
        "current_life_state": reverse_state.get(
            profile.current_life_state or "", "MOSTLY_STABLE"
        ),
        "desired_directions": [
            reverse_dir.get(v, v) for v in (profile.desired_directions or [])
        ],
        "pressure_sources": [
            reverse_pressure.get(v, v) for v in (profile.pressure_sources or [])
        ],
        "recovery_supports": [
            reverse_recovery.get(v, v) for v in (profile.recovery_supports or [])
        ],
    }


def merge_saved_answers(
    draft: dict[str, Any] | None,
    profile: PersonalLifeOperationsProfile | None,
) -> dict[str, Any] | None:
    if draft:
        return LIFE_OPERATIONS_TEMPLATE_CONTRACT.normalize_answers(draft)
    if profile:
        return answers_from_profile(profile)
    return None


async def upsert_life_operations_profile(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    LIFE_OPERATIONS_TEMPLATE_CONTRACT.validate(answers)
    fields = LIFE_OPERATIONS_TEMPLATE_CONTRACT.to_profile_fields(answers)
    result = await session.execute(
        select(PersonalLifeOperationsProfile).where(
            PersonalLifeOperationsProfile.moment_id == moment_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing is None:
        row = PersonalLifeOperationsProfile(
            moment_id=moment_id,
            user_id=user_id,
            **fields,
        )
        session.add(row)
    else:
        for key, value in fields.items():
            setattr(existing, key, value)
    await session.flush()
