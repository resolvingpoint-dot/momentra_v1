"""Memory sub-domain aggregator.

Momentra's memory tables live inside their parent domains (personal / group /
business / life360). This module simply re-exports those models so they can be
imported from a single "memory" namespace.
"""
from __future__ import annotations

from app.domains.personal.models import PersonalMemoryDriverRankings, PersonalMemoryEmotionalDna, PersonalMemoryEvolutionSnapshots, PersonalMemoryIdentitySnapshots, PersonalMemoryPatterns
from app.domains.group.models import GroupMemoryEntries, GroupMemoryPatterns, GroupMemorySnapshots
from app.domains.business.models import BusinessMemoryLearnings, BusinessMemoryPatterns, BusinessMemorySnapshots, BusinessRiskMemory, BusinessSuccessMemory
from app.domains.life360.models import SharedExperienceMemoryHighlights

__all__ = [
    "BusinessMemoryLearnings",
    "BusinessMemoryPatterns",
    "BusinessMemorySnapshots",
    "BusinessRiskMemory",
    "BusinessSuccessMemory",
    "GroupMemoryEntries",
    "GroupMemoryPatterns",
    "GroupMemorySnapshots",
    "PersonalMemoryDriverRankings",
    "PersonalMemoryEmotionalDna",
    "PersonalMemoryEvolutionSnapshots",
    "PersonalMemoryIdentitySnapshots",
    "PersonalMemoryPatterns",
    "SharedExperienceMemoryHighlights",
]
