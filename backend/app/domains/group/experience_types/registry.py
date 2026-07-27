"""Experience type registry — profile-specific copy, colors, quick-add, memory prompts."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.domains.group import shared_catalog as cat


@dataclass(frozen=True)
class ExperienceTypeDefinition:
    code: str
    name: str
    icon: str
    primary_color: str
    pulse_readiness_title: str
    pulse_readiness_narrative: str
    quick_add_modules: list[str] = field(default_factory=list)
    timeline_stages: list[str] = field(default_factory=list)
    memory_prompts: list[str] = field(default_factory=list)
    capability_chips: list[str] = field(default_factory=list)


_DEFAULT_QUICK_ADD = [
    "PARTICIPANT",
    "PLANNING_ITEM",
    "BOOKING",
    "EXPENSE",
    "CONTRIBUTION",
    "BUDGET",
    "VENDOR",
    "ATTENDANCE",
    "UPDATE",
    "MEMORY",
    "POLL",
]

_REGISTRY: dict[str, ExperienceTypeDefinition] = {
    "TRIP_VACATION": ExperienceTypeDefinition(
        code="TRIP_VACATION",
        name="Trip / Vacation",
        icon="airplane",
        primary_color="#FF7A3D",
        pulse_readiness_title="Let's get this trip moving",
        pulse_readiness_narrative="Invite your crew and add the first plan item to build momentum.",
        quick_add_modules=_DEFAULT_QUICK_ADD,
        timeline_stages=["Plan", "Travel", "Live", "Remember"],
        memory_prompts=["Best moment", "Funny memory", "Group photo", "Lesson learned"],
        capability_chips=["Plan", "Split costs", "Capture memories"],
    ),
    "WEDDING": ExperienceTypeDefinition(
        code="WEDDING",
        name="Wedding",
        icon="rings",
        primary_color="#FFB598",
        pulse_readiness_title="Your celebration is taking shape",
        pulse_readiness_narrative="Add vendors, guests, and milestones so everyone stays in sync.",
        quick_add_modules=["PARTICIPANT", "VENDOR", "EXPENSE", "BOOKING", "MEMORY", "POLL"],
        timeline_stages=["Engage", "Plan", "Celebrate", "Remember"],
        memory_prompts=["Ceremony highlight", "Family moment", "Toast", "Behind the scenes"],
        capability_chips=["Guests", "Vendors", "Budget", "Memories"],
    ),
    "CELEBRATION": ExperienceTypeDefinition(
        code="CELEBRATION",
        name="Celebration",
        icon="party",
        primary_color="#FFB951",
        pulse_readiness_title="Let's make this celebration count",
        pulse_readiness_narrative="Invite people and capture the first shared moment.",
        quick_add_modules=_DEFAULT_QUICK_ADD,
        timeline_stages=["Invite", "Gather", "Celebrate", "Remember"],
        memory_prompts=["Highlight reel", "Group photo", "Toast moment"],
        capability_chips=["Guests", "Expenses", "Memories"],
    ),
    "OFFICE_OUTING": ExperienceTypeDefinition(
        code="OFFICE_OUTING",
        name="Office Outing",
        icon="briefcase",
        primary_color="#5B8DEF",
        pulse_readiness_title="Team outing readiness",
        pulse_readiness_narrative="Align the team on plans, costs, and logistics.",
        quick_add_modules=["PARTICIPANT", "EXPENSE", "BOOKING", "ATTENDANCE", "UPDATE"],
        timeline_stages=["Plan", "Coordinate", "Go", "Debrief"],
        memory_prompts=["Team highlight", "Funny moment", "Lessons"],
        capability_chips=["Team", "Budget", "Logistics"],
    ),
    "PILGRIMAGE": ExperienceTypeDefinition(
        code="PILGRIMAGE",
        name="Pilgrimage",
        icon="temple",
        primary_color="#8B7355",
        pulse_readiness_title="Journey preparation",
        pulse_readiness_narrative="Coordinate travel, lodging, and group rituals.",
        quick_add_modules=["PARTICIPANT", "BOOKING", "EXPENSE", "MEMORY", "ATTENDANCE"],
        timeline_stages=["Prepare", "Travel", "Observe", "Reflect"],
        memory_prompts=["Sacred moment", "Group photo", "Reflection"],
        capability_chips=["Travel", "Group", "Memories"],
    ),
    "BIRTHDAY": ExperienceTypeDefinition(
        code="BIRTHDAY",
        name="Birthday",
        icon="cake",
        primary_color="#FF6B9D",
        pulse_readiness_title="Birthday celebration prep",
        pulse_readiness_narrative="Invite guests and plan surprises.",
        quick_add_modules=["PARTICIPANT", "EXPENSE", "MEMORY", "POLL", "PLANNING_ITEM"],
        timeline_stages=["Plan", "Surprise", "Celebrate", "Remember"],
        memory_prompts=["Cake moment", "Surprise reveal", "Group wish"],
        capability_chips=["Guests", "Gifts", "Memories"],
    ),
    "CONFERENCE": ExperienceTypeDefinition(
        code="CONFERENCE",
        name="Conference",
        icon="mic",
        primary_color="#5856D6",
        pulse_readiness_title="Conference coordination",
        pulse_readiness_narrative="Align schedules, travel, and shared costs.",
        quick_add_modules=["PARTICIPANT", "BOOKING", "EXPENSE", "ATTENDANCE", "UPDATE"],
        timeline_stages=["Register", "Travel", "Attend", "Debrief"],
        memory_prompts=["Keynote highlight", "Networking win", "Team dinner"],
        capability_chips=["Schedule", "Travel", "Budget"],
    ),
    "FAMILY_REUNION": ExperienceTypeDefinition(
        code="FAMILY_REUNION",
        name="Family Reunion",
        icon="family",
        primary_color="#34C759",
        pulse_readiness_title="Family gathering prep",
        pulse_readiness_narrative="Bring everyone together with a shared plan.",
        quick_add_modules=["PARTICIPANT", "EXPENSE", "MEMORY", "BOOKING", "CONTRIBUTION"],
        timeline_stages=["Invite", "Gather", "Celebrate", "Remember"],
        memory_prompts=["Family photo", "Tradition moment", "Stories"],
        capability_chips=["Family", "Memories", "Costs"],
    ),
    "CUSTOM": ExperienceTypeDefinition(
        code="CUSTOM",
        name="Custom Experience",
        icon="sliders",
        primary_color="#8E8E93",
        pulse_readiness_title="Your experience is taking shape",
        pulse_readiness_narrative="Define your group flow and start adding activity.",
        quick_add_modules=_DEFAULT_QUICK_ADD,
        timeline_stages=["Plan", "Go", "Remember"],
        memory_prompts=["Highlight", "Photo", "Lesson"],
        capability_chips=["Flexible", "Group", "Memories"],
    ),
}


class ExperienceTypeRegistry:
    @staticmethod
    def get(code: str | None) -> ExperienceTypeDefinition:
        return get_experience_type(code)

    @staticmethod
    def all_codes() -> list[str]:
        return list(_REGISTRY.keys())

    @staticmethod
    def register(defn: ExperienceTypeDefinition) -> None:
        _REGISTRY[defn.code] = defn


def get_experience_type(code: str | None) -> ExperienceTypeDefinition:
    if code and code in _REGISTRY:
        return _REGISTRY[code]
    # Fallback to catalog default profile
    profs = cat.profiles_for(cat.EXPERIENCE)
    fallback_code = profs[0].code if profs else "TRIP_VACATION"
    return _REGISTRY.get(fallback_code, _REGISTRY["TRIP_VACATION"])
