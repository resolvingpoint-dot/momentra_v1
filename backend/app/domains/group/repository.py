"""Group domain repositories (group_* tables).

One async repository per table. Each inherits the full operation set from
``app.core.repository.AsyncRepository``: create, update, delete, get-by-id,
list, search, pagination, filtering, transactions, bulk insert/update and soft
delete (where the model exposes a soft-delete column). Database access only --
no business logic, no HTTP, no FastAPI.
"""
from __future__ import annotations

from app.core.repository import AsyncRepository
from app.domains.group.models import (
    GroupActivityEdits,
    GroupAiInsights,
    GroupAttachments,
    GroupAttendance,
    GroupChangeHistory,
    GroupContributions,
    GroupDecisions,
    GroupExpenseSplits,
    GroupExpenses,
    GroupFieldValueConfig,
    GroupHealthSnapshots,
    GroupJourneyMetrics,
    GroupLifeDimensionScores,
    GroupLifeDriverEffects,
    GroupLifeMasterSnapshots,
    GroupLifeMomentLinks,
    GroupLifeSnapshots,
    GroupLifeSpaces,
    GroupLiveFeed,
    GroupMemoryEntries,
    GroupMemoryPatterns,
    GroupMemorySnapshots,
    GroupMomentMembers,
    GroupMomentProfiles,
    GroupMomentResources,
    GroupMomentRoles,
    GroupMomentStageHistory,
    GroupMomentWorkItems,
    GroupMoments,
    GroupPeopleImpactScores,
    GroupPollOptions,
    GroupPollVotes,
    GroupPolls,
    GroupPulseSnapshots,
    GroupQuickAddConfig,
    GroupQuickAddEvents,
    GroupRecommendations,
    GroupSignals,
    GroupUpdates,)


class GroupActivityEditsRepository(AsyncRepository[GroupActivityEdits]):
    model = GroupActivityEdits


class GroupAiInsightsRepository(AsyncRepository[GroupAiInsights]):
    model = GroupAiInsights


class GroupAttachmentsRepository(AsyncRepository[GroupAttachments]):
    model = GroupAttachments


class GroupAttendanceRepository(AsyncRepository[GroupAttendance]):
    model = GroupAttendance


class GroupChangeHistoryRepository(AsyncRepository[GroupChangeHistory]):
    model = GroupChangeHistory


class GroupContributionsRepository(AsyncRepository[GroupContributions]):
    model = GroupContributions


class GroupDecisionsRepository(AsyncRepository[GroupDecisions]):
    model = GroupDecisions


class GroupExpenseSplitsRepository(AsyncRepository[GroupExpenseSplits]):
    model = GroupExpenseSplits


class GroupExpensesRepository(AsyncRepository[GroupExpenses]):
    model = GroupExpenses


class GroupFieldValueConfigRepository(AsyncRepository[GroupFieldValueConfig]):
    model = GroupFieldValueConfig


class GroupHealthSnapshotsRepository(AsyncRepository[GroupHealthSnapshots]):
    model = GroupHealthSnapshots


class GroupJourneyMetricsRepository(AsyncRepository[GroupJourneyMetrics]):
    model = GroupJourneyMetrics


class GroupLifeDimensionScoresRepository(AsyncRepository[GroupLifeDimensionScores]):
    model = GroupLifeDimensionScores


class GroupLifeDriverEffectsRepository(AsyncRepository[GroupLifeDriverEffects]):
    model = GroupLifeDriverEffects


class GroupLifeMasterSnapshotsRepository(AsyncRepository[GroupLifeMasterSnapshots]):
    model = GroupLifeMasterSnapshots


class GroupLifeMomentLinksRepository(AsyncRepository[GroupLifeMomentLinks]):
    model = GroupLifeMomentLinks


class GroupLifeSnapshotsRepository(AsyncRepository[GroupLifeSnapshots]):
    model = GroupLifeSnapshots


class GroupLifeSpacesRepository(AsyncRepository[GroupLifeSpaces]):
    model = GroupLifeSpaces


class GroupLiveFeedRepository(AsyncRepository[GroupLiveFeed]):
    model = GroupLiveFeed


class GroupMemoryEntriesRepository(AsyncRepository[GroupMemoryEntries]):
    model = GroupMemoryEntries


class GroupMemoryPatternsRepository(AsyncRepository[GroupMemoryPatterns]):
    model = GroupMemoryPatterns


class GroupMemorySnapshotsRepository(AsyncRepository[GroupMemorySnapshots]):
    model = GroupMemorySnapshots


class GroupMomentMembersRepository(AsyncRepository[GroupMomentMembers]):
    model = GroupMomentMembers


class GroupMomentProfilesRepository(AsyncRepository[GroupMomentProfiles]):
    model = GroupMomentProfiles


class GroupMomentResourcesRepository(AsyncRepository[GroupMomentResources]):
    model = GroupMomentResources


class GroupMomentRolesRepository(AsyncRepository[GroupMomentRoles]):
    model = GroupMomentRoles


class GroupMomentStageHistoryRepository(AsyncRepository[GroupMomentStageHistory]):
    model = GroupMomentStageHistory


class GroupMomentWorkItemsRepository(AsyncRepository[GroupMomentWorkItems]):
    model = GroupMomentWorkItems


class GroupMomentsRepository(AsyncRepository[GroupMoments]):
    model = GroupMoments


class GroupPeopleImpactScoresRepository(AsyncRepository[GroupPeopleImpactScores]):
    model = GroupPeopleImpactScores


class GroupPollOptionsRepository(AsyncRepository[GroupPollOptions]):
    model = GroupPollOptions


class GroupPollVotesRepository(AsyncRepository[GroupPollVotes]):
    model = GroupPollVotes


class GroupPollsRepository(AsyncRepository[GroupPolls]):
    model = GroupPolls


class GroupPulseSnapshotsRepository(AsyncRepository[GroupPulseSnapshots]):
    model = GroupPulseSnapshots


class GroupQuickAddConfigRepository(AsyncRepository[GroupQuickAddConfig]):
    model = GroupQuickAddConfig


class GroupQuickAddEventsRepository(AsyncRepository[GroupQuickAddEvents]):
    model = GroupQuickAddEvents


class GroupRecommendationsRepository(AsyncRepository[GroupRecommendations]):
    model = GroupRecommendations


class GroupSignalsRepository(AsyncRepository[GroupSignals]):
    model = GroupSignals


class GroupUpdatesRepository(AsyncRepository[GroupUpdates]):
    model = GroupUpdates
