"""Memory sub-domain repository aggregator.

Memory tables live in their parent domains, so their repositories are defined
there. This module re-exports them under a single "memory" namespace,
mirroring app/domains/memory/models.py.
"""
from __future__ import annotations

from app.domains.personal.repository import PersonalMemoryDriverRankingsRepository, PersonalMemoryEmotionalDnaRepository, PersonalMemoryEvolutionSnapshotsRepository, PersonalMemoryIdentitySnapshotsRepository, PersonalMemoryPatternsRepository
from app.domains.group.repository import GroupMemoryEntriesRepository, GroupMemoryPatternsRepository, GroupMemorySnapshotsRepository
from app.domains.business.repository import BusinessMemoryLearningsRepository, BusinessMemoryPatternsRepository, BusinessMemorySnapshotsRepository, BusinessRiskMemoryRepository, BusinessSuccessMemoryRepository
from app.domains.life360.repository import SharedExperienceMemoryHighlightsRepository

__all__ = [
    "BusinessMemoryLearningsRepository",
    "BusinessMemoryPatternsRepository",
    "BusinessMemorySnapshotsRepository",
    "BusinessRiskMemoryRepository",
    "BusinessSuccessMemoryRepository",
    "GroupMemoryEntriesRepository",
    "GroupMemoryPatternsRepository",
    "GroupMemorySnapshotsRepository",
    "PersonalMemoryDriverRankingsRepository",
    "PersonalMemoryEmotionalDnaRepository",
    "PersonalMemoryEvolutionSnapshotsRepository",
    "PersonalMemoryIdentitySnapshotsRepository",
    "PersonalMemoryPatternsRepository",
    "SharedExperienceMemoryHighlightsRepository",
]
