"""Group domain services (one per table).

Each service inherits the full orchestration + business-logic skeleton
from app.core.service.BaseService (validation, permission checks,
workflow/state transitions, snapshot refresh, cache invalidation, event
creation) and always returns schemas -- never SQLAlchemy models. No HTTP.
"""
from __future__ import annotations

from app.core.service import BaseService
from app.domains.group.repository import (
    GroupActivityEditsRepository,
    GroupAiInsightsRepository,
    GroupAttachmentsRepository,
    GroupAttendanceRepository,
    GroupChangeHistoryRepository,
    GroupContributionsRepository,
    GroupDecisionsRepository,
    GroupExpenseSplitsRepository,
    GroupExpensesRepository,
    GroupFieldValueConfigRepository,
    GroupHealthSnapshotsRepository,
    GroupJourneyMetricsRepository,
    GroupLifeDimensionScoresRepository,
    GroupLifeDriverEffectsRepository,
    GroupLifeMasterSnapshotsRepository,
    GroupLifeMomentLinksRepository,
    GroupLifeSnapshotsRepository,
    GroupLifeSpacesRepository,
    GroupLiveFeedRepository,
    GroupMemoryEntriesRepository,
    GroupMemoryPatternsRepository,
    GroupMemorySnapshotsRepository,
    GroupMomentMembersRepository,
    GroupMomentProfilesRepository,
    GroupMomentResourcesRepository,
    GroupMomentRolesRepository,
    GroupMomentStageHistoryRepository,
    GroupMomentWorkItemsRepository,
    GroupMomentsRepository,
    GroupPeopleImpactScoresRepository,
    GroupPollOptionsRepository,
    GroupPollVotesRepository,
    GroupPollsRepository,
    GroupPulseSnapshotsRepository,
    GroupQuickAddConfigRepository,
    GroupQuickAddEventsRepository,
    GroupRecommendationsRepository,
    GroupSignalsRepository,
    GroupUpdatesRepository,
)
from app.domains.group.schemas import (
    GroupActivityEditsSchema,
    GroupAiInsightsSchema,
    GroupAttachmentsSchema,
    GroupAttendanceSchema,
    GroupChangeHistorySchema,
    GroupContributionsSchema,
    GroupDecisionsSchema,
    GroupExpenseSplitsSchema,
    GroupExpensesSchema,
    GroupFieldValueConfigSchema,
    GroupHealthSnapshotsSchema,
    GroupJourneyMetricsSchema,
    GroupLifeDimensionScoresSchema,
    GroupLifeDriverEffectsSchema,
    GroupLifeMasterSnapshotsSchema,
    GroupLifeMomentLinksSchema,
    GroupLifeSnapshotsSchema,
    GroupLifeSpacesSchema,
    GroupLiveFeedSchema,
    GroupMemoryEntriesSchema,
    GroupMemoryPatternsSchema,
    GroupMemorySnapshotsSchema,
    GroupMomentMembersSchema,
    GroupMomentProfilesSchema,
    GroupMomentResourcesSchema,
    GroupMomentRolesSchema,
    GroupMomentStageHistorySchema,
    GroupMomentWorkItemsSchema,
    GroupMomentsSchema,
    GroupPeopleImpactScoresSchema,
    GroupPollOptionsSchema,
    GroupPollVotesSchema,
    GroupPollsSchema,
    GroupPulseSnapshotsSchema,
    GroupQuickAddConfigSchema,
    GroupQuickAddEventsSchema,
    GroupRecommendationsSchema,
    GroupSignalsSchema,
    GroupUpdatesSchema,
)


class GroupActivityEditsService(BaseService):
    repository_class = GroupActivityEditsRepository
    schema = GroupActivityEditsSchema


class GroupAiInsightsService(BaseService):
    repository_class = GroupAiInsightsRepository
    schema = GroupAiInsightsSchema


class GroupAttachmentsService(BaseService):
    repository_class = GroupAttachmentsRepository
    schema = GroupAttachmentsSchema


class GroupAttendanceService(BaseService):
    repository_class = GroupAttendanceRepository
    schema = GroupAttendanceSchema


class GroupChangeHistoryService(BaseService):
    repository_class = GroupChangeHistoryRepository
    schema = GroupChangeHistorySchema


class GroupContributionsService(BaseService):
    repository_class = GroupContributionsRepository
    schema = GroupContributionsSchema


class GroupDecisionsService(BaseService):
    repository_class = GroupDecisionsRepository
    schema = GroupDecisionsSchema


class GroupExpenseSplitsService(BaseService):
    repository_class = GroupExpenseSplitsRepository
    schema = GroupExpenseSplitsSchema


class GroupExpensesService(BaseService):
    repository_class = GroupExpensesRepository
    schema = GroupExpensesSchema


class GroupFieldValueConfigService(BaseService):
    repository_class = GroupFieldValueConfigRepository
    schema = GroupFieldValueConfigSchema


class GroupHealthSnapshotsService(BaseService):
    repository_class = GroupHealthSnapshotsRepository
    schema = GroupHealthSnapshotsSchema


class GroupJourneyMetricsService(BaseService):
    repository_class = GroupJourneyMetricsRepository
    schema = GroupJourneyMetricsSchema


class GroupLifeDimensionScoresService(BaseService):
    repository_class = GroupLifeDimensionScoresRepository
    schema = GroupLifeDimensionScoresSchema


class GroupLifeDriverEffectsService(BaseService):
    repository_class = GroupLifeDriverEffectsRepository
    schema = GroupLifeDriverEffectsSchema


class GroupLifeMasterSnapshotsService(BaseService):
    repository_class = GroupLifeMasterSnapshotsRepository
    schema = GroupLifeMasterSnapshotsSchema


class GroupLifeMomentLinksService(BaseService):
    repository_class = GroupLifeMomentLinksRepository
    schema = GroupLifeMomentLinksSchema


class GroupLifeSnapshotsService(BaseService):
    repository_class = GroupLifeSnapshotsRepository
    schema = GroupLifeSnapshotsSchema


class GroupLifeSpacesService(BaseService):
    repository_class = GroupLifeSpacesRepository
    schema = GroupLifeSpacesSchema


class GroupLiveFeedService(BaseService):
    repository_class = GroupLiveFeedRepository
    schema = GroupLiveFeedSchema


class GroupMemoryEntriesService(BaseService):
    repository_class = GroupMemoryEntriesRepository
    schema = GroupMemoryEntriesSchema


class GroupMemoryPatternsService(BaseService):
    repository_class = GroupMemoryPatternsRepository
    schema = GroupMemoryPatternsSchema


class GroupMemorySnapshotsService(BaseService):
    repository_class = GroupMemorySnapshotsRepository
    schema = GroupMemorySnapshotsSchema


class GroupMomentMembersService(BaseService):
    repository_class = GroupMomentMembersRepository
    schema = GroupMomentMembersSchema


class GroupMomentProfilesService(BaseService):
    repository_class = GroupMomentProfilesRepository
    schema = GroupMomentProfilesSchema


class GroupMomentResourcesService(BaseService):
    repository_class = GroupMomentResourcesRepository
    schema = GroupMomentResourcesSchema


class GroupMomentRolesService(BaseService):
    repository_class = GroupMomentRolesRepository
    schema = GroupMomentRolesSchema


class GroupMomentStageHistoryService(BaseService):
    repository_class = GroupMomentStageHistoryRepository
    schema = GroupMomentStageHistorySchema


class GroupMomentWorkItemsService(BaseService):
    repository_class = GroupMomentWorkItemsRepository
    schema = GroupMomentWorkItemsSchema


class GroupMomentsService(BaseService):
    repository_class = GroupMomentsRepository
    schema = GroupMomentsSchema


class GroupPeopleImpactScoresService(BaseService):
    repository_class = GroupPeopleImpactScoresRepository
    schema = GroupPeopleImpactScoresSchema


class GroupPollOptionsService(BaseService):
    repository_class = GroupPollOptionsRepository
    schema = GroupPollOptionsSchema


class GroupPollVotesService(BaseService):
    repository_class = GroupPollVotesRepository
    schema = GroupPollVotesSchema


class GroupPollsService(BaseService):
    repository_class = GroupPollsRepository
    schema = GroupPollsSchema


class GroupPulseSnapshotsService(BaseService):
    repository_class = GroupPulseSnapshotsRepository
    schema = GroupPulseSnapshotsSchema


class GroupQuickAddConfigService(BaseService):
    repository_class = GroupQuickAddConfigRepository
    schema = GroupQuickAddConfigSchema


class GroupQuickAddEventsService(BaseService):
    repository_class = GroupQuickAddEventsRepository
    schema = GroupQuickAddEventsSchema


class GroupRecommendationsService(BaseService):
    repository_class = GroupRecommendationsRepository
    schema = GroupRecommendationsSchema


class GroupSignalsService(BaseService):
    repository_class = GroupSignalsRepository
    schema = GroupSignalsSchema


class GroupUpdatesService(BaseService):
    repository_class = GroupUpdatesRepository
    schema = GroupUpdatesSchema
