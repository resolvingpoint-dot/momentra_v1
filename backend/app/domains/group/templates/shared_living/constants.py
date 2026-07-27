"""Shared Living template constants."""
from __future__ import annotations

from dataclasses import dataclass, field

MOMENT_TYPE = "SHARED_LIVING"

DEFAULT_QUICK_ADD_MODULES = [
    "RESIDENTS",
    "EXPENSES",
    "CONTRIBUTIONS",
    "TASKS",
    "RULES",
    "ASSETS",
    "MAINTENANCE",
    "UPDATES",
    "POLLS",
    "MEMORIES",
]


@dataclass(frozen=True)
class LivingProfileDefinition:
    code: str
    name: str
    pulse_readiness_title: str
    pulse_readiness_narrative: str
    quick_add_modules: list[str] = field(default_factory=lambda: list(DEFAULT_QUICK_ADD_MODULES))
    memory_prompts: list[str] = field(default_factory=lambda: ["Move-in day", "House milestone", "Shared memory"])


_PROFILES: dict[str, LivingProfileDefinition] = {
    "FLATMATES": LivingProfileDefinition(
        code="FLATMATES",
        name="Flatmates",
        pulse_readiness_title="Let's set up home",
        pulse_readiness_narrative="Invite residents and log the first shared expense to get going.",
    ),
    "FAMILY_HOUSEHOLD": LivingProfileDefinition(
        code="FAMILY_HOUSEHOLD",
        name="Family Household",
        pulse_readiness_title="Your household is taking shape",
        pulse_readiness_narrative="Add family members and track shared costs together.",
    ),
    "COLIVING": LivingProfileDefinition(
        code="COLIVING",
        name="Co-Living",
        pulse_readiness_title="Build your co-living rhythm",
        pulse_readiness_narrative="Invite residents and set up chores and house rules.",
    ),
    "CUSTOM_LIVING": LivingProfileDefinition(
        code="CUSTOM_LIVING",
        name="Custom Living",
        pulse_readiness_title="Your home is taking shape",
        pulse_readiness_narrative="Invite residents and log the first activity.",
    ),
}


def get_living_profile(code: str | None) -> LivingProfileDefinition:
    if code and code in _PROFILES:
        return _PROFILES[code]
    return _PROFILES["FLATMATES"]
