"""Memory sub-domain schemas aggregator (re-exports from parent domains)."""
from __future__ import annotations

from app.domains.personal.schemas import PersonalMemoryDriverRankingsSchema, PersonalMemoryEmotionalDnaSchema, PersonalMemoryEvolutionSnapshotsSchema, PersonalMemoryIdentitySnapshotsSchema, PersonalMemoryPatternsSchema
from app.domains.group.schemas import GroupMemoryEntriesSchema, GroupMemoryPatternsSchema, GroupMemorySnapshotsSchema
from app.domains.business.schemas import BusinessMemoryLearningsSchema, BusinessMemoryPatternsSchema, BusinessMemorySnapshotsSchema, BusinessRiskMemorySchema, BusinessSuccessMemorySchema
from app.domains.life360.schemas import SharedExperienceMemoryHighlightsSchema

__all__ = [
    "BusinessMemoryLearningsSchema",
    "BusinessMemoryPatternsSchema",
    "BusinessMemorySnapshotsSchema",
    "BusinessRiskMemorySchema",
    "BusinessSuccessMemorySchema",
    "GroupMemoryEntriesSchema",
    "GroupMemoryPatternsSchema",
    "GroupMemorySnapshotsSchema",
    "PersonalMemoryDriverRankingsSchema",
    "PersonalMemoryEmotionalDnaSchema",
    "PersonalMemoryEvolutionSnapshotsSchema",
    "PersonalMemoryIdentitySnapshotsSchema",
    "PersonalMemoryPatternsSchema",
    "SharedExperienceMemoryHighlightsSchema",
]
