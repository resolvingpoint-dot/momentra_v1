"""Personal domain services (one per table).

Each service inherits the full orchestration + business-logic skeleton
from app.core.service.BaseService (validation, permission checks,
workflow/state transitions, snapshot refresh, cache invalidation, event
creation) and always returns schemas -- never SQLAlchemy models. No HTTP.
"""
from __future__ import annotations

from app.core.service import BaseService
from app.domains.personal.repository import (
    PersonalAccountsRepository,
    PersonalActivityTimelineRepository,
    PersonalAiInterpretationRunsRepository,
    PersonalCategoriesRepository,
    PersonalEventEditsRepository,
    PersonalEventVoidsRepository,
    PersonalFutureBuildingProfileRepository,
    PersonalFutureLearningEventsRepository,
    PersonalFutureMilestoneEventsRepository,
    PersonalFutureOpportunityEventsRepository,
    PersonalFuturePivotEventsRepository,
    PersonalFutureProgressEventsRepository,
    PersonalInsightsRepository,
    PersonalLifeAdjustEventsRepository,
    PersonalLifeAggregateSnapshotsRepository,
    PersonalLifeAttentionEventsRepository,
    PersonalLifeConnectionsRepository,
    PersonalLifeDimensionScoresRepository,
    PersonalLifeDriftAlertsRepository,
    PersonalLifeHealthSnapshotsRepository,
    PersonalLifeJourneyEventsRepository,
    PersonalLifeMonthlyChangesRepository,
    PersonalLifeMoodEventsRepository,
    PersonalLifeOperationsProfileRepository,
    PersonalLifeRecoveryEventsRepository,
    PersonalLifestyleAdjustEventsRepository,
    PersonalLifestyleDiscoveryEventsRepository,
    PersonalLifestyleExperienceEventsRepository,
    PersonalLifestyleExpressionEventsRepository,
    PersonalLifestyleProfileRepository,
    PersonalLifestyleWellbeingEventsRepository,
    PersonalLivePrioritiesRepository,
    PersonalMemoryDriverRankingsRepository,
    PersonalMemoryEmotionalDnaRepository,
    PersonalMemoryEvolutionSnapshotsRepository,
    PersonalMemoryIdentitySnapshotsRepository,
    PersonalMemoryPatternsRepository,
    PersonalMetricSnapshotsRepository,
    PersonalMomentHighlightsRepository,
    PersonalMomentProfilesRepository,
    PersonalMomentTurningPointsRepository,
    PersonalMomentTypesRepository,
    PersonalMomentsRepository,
    PersonalMoneyEventsRepository,
    PersonalNotificationQueueRepository,
    PersonalPulseSnapshotsRepository,
    PersonalQuickAddEventsRepository,
    PersonalRecommendationsRepository,
    PersonalRelationshipAdjustEventsRepository,
    PersonalRelationshipConnectionEventsRepository,
    PersonalRelationshipExperienceEventsRepository,
    PersonalRelationshipInvestmentEventsRepository,
    PersonalRelationshipSupportEventsRepository,
    PersonalRelationshipsProfileRepository,
    PersonalRuntimeSnapshotsRepository,
    PersonalSignalsRepository,
    PersonalUserPreferencesRepository,
)
from app.domains.personal.schemas import (
    PersonalAccountsSchema,
    PersonalActivityTimelineSchema,
    PersonalAiInterpretationRunsSchema,
    PersonalCategoriesSchema,
    PersonalEventEditsSchema,
    PersonalEventVoidsSchema,
    PersonalFutureBuildingProfileSchema,
    PersonalFutureLearningEventsSchema,
    PersonalFutureMilestoneEventsSchema,
    PersonalFutureOpportunityEventsSchema,
    PersonalFuturePivotEventsSchema,
    PersonalFutureProgressEventsSchema,
    PersonalInsightsSchema,
    PersonalLifeAdjustEventsSchema,
    PersonalLifeAggregateSnapshotsSchema,
    PersonalLifeAttentionEventsSchema,
    PersonalLifeConnectionsSchema,
    PersonalLifeDimensionScoresSchema,
    PersonalLifeDriftAlertsSchema,
    PersonalLifeHealthSnapshotsSchema,
    PersonalLifeJourneyEventsSchema,
    PersonalLifeMonthlyChangesSchema,
    PersonalLifeMoodEventsSchema,
    PersonalLifeOperationsProfileSchema,
    PersonalLifeRecoveryEventsSchema,
    PersonalLifestyleAdjustEventsSchema,
    PersonalLifestyleDiscoveryEventsSchema,
    PersonalLifestyleExperienceEventsSchema,
    PersonalLifestyleExpressionEventsSchema,
    PersonalLifestyleProfileSchema,
    PersonalLifestyleWellbeingEventsSchema,
    PersonalLivePrioritiesSchema,
    PersonalMemoryDriverRankingsSchema,
    PersonalMemoryEmotionalDnaSchema,
    PersonalMemoryEvolutionSnapshotsSchema,
    PersonalMemoryIdentitySnapshotsSchema,
    PersonalMemoryPatternsSchema,
    PersonalMetricSnapshotsSchema,
    PersonalMomentHighlightsSchema,
    PersonalMomentProfilesSchema,
    PersonalMomentTurningPointsSchema,
    PersonalMomentTypesSchema,
    PersonalMomentsSchema,
    PersonalMoneyEventsSchema,
    PersonalNotificationQueueSchema,
    PersonalPulseSnapshotsSchema,
    PersonalQuickAddEventsSchema,
    PersonalRecommendationsSchema,
    PersonalRelationshipAdjustEventsSchema,
    PersonalRelationshipConnectionEventsSchema,
    PersonalRelationshipExperienceEventsSchema,
    PersonalRelationshipInvestmentEventsSchema,
    PersonalRelationshipSupportEventsSchema,
    PersonalRelationshipsProfileSchema,
    PersonalRuntimeSnapshotsSchema,
    PersonalSignalsSchema,
    PersonalUserPreferencesSchema,
)


class PersonalAccountsService(BaseService):
    repository_class = PersonalAccountsRepository
    schema = PersonalAccountsSchema


class PersonalActivityTimelineService(BaseService):
    repository_class = PersonalActivityTimelineRepository
    schema = PersonalActivityTimelineSchema


class PersonalAiInterpretationRunsService(BaseService):
    repository_class = PersonalAiInterpretationRunsRepository
    schema = PersonalAiInterpretationRunsSchema


class PersonalCategoriesService(BaseService):
    repository_class = PersonalCategoriesRepository
    schema = PersonalCategoriesSchema


class PersonalEventEditsService(BaseService):
    repository_class = PersonalEventEditsRepository
    schema = PersonalEventEditsSchema


class PersonalEventVoidsService(BaseService):
    repository_class = PersonalEventVoidsRepository
    schema = PersonalEventVoidsSchema


class PersonalFutureBuildingProfileService(BaseService):
    repository_class = PersonalFutureBuildingProfileRepository
    schema = PersonalFutureBuildingProfileSchema


class PersonalFutureLearningEventsService(BaseService):
    repository_class = PersonalFutureLearningEventsRepository
    schema = PersonalFutureLearningEventsSchema


class PersonalFutureMilestoneEventsService(BaseService):
    repository_class = PersonalFutureMilestoneEventsRepository
    schema = PersonalFutureMilestoneEventsSchema


class PersonalFutureOpportunityEventsService(BaseService):
    repository_class = PersonalFutureOpportunityEventsRepository
    schema = PersonalFutureOpportunityEventsSchema


class PersonalFuturePivotEventsService(BaseService):
    repository_class = PersonalFuturePivotEventsRepository
    schema = PersonalFuturePivotEventsSchema


class PersonalFutureProgressEventsService(BaseService):
    repository_class = PersonalFutureProgressEventsRepository
    schema = PersonalFutureProgressEventsSchema


class PersonalInsightsService(BaseService):
    repository_class = PersonalInsightsRepository
    schema = PersonalInsightsSchema


class PersonalLifeAdjustEventsService(BaseService):
    repository_class = PersonalLifeAdjustEventsRepository
    schema = PersonalLifeAdjustEventsSchema


class PersonalLifeAggregateSnapshotsService(BaseService):
    repository_class = PersonalLifeAggregateSnapshotsRepository
    schema = PersonalLifeAggregateSnapshotsSchema


class PersonalLifeAttentionEventsService(BaseService):
    repository_class = PersonalLifeAttentionEventsRepository
    schema = PersonalLifeAttentionEventsSchema


class PersonalLifeConnectionsService(BaseService):
    repository_class = PersonalLifeConnectionsRepository
    schema = PersonalLifeConnectionsSchema


class PersonalLifeDimensionScoresService(BaseService):
    repository_class = PersonalLifeDimensionScoresRepository
    schema = PersonalLifeDimensionScoresSchema


class PersonalLifeDriftAlertsService(BaseService):
    repository_class = PersonalLifeDriftAlertsRepository
    schema = PersonalLifeDriftAlertsSchema


class PersonalLifeHealthSnapshotsService(BaseService):
    repository_class = PersonalLifeHealthSnapshotsRepository
    schema = PersonalLifeHealthSnapshotsSchema


class PersonalLifeJourneyEventsService(BaseService):
    repository_class = PersonalLifeJourneyEventsRepository
    schema = PersonalLifeJourneyEventsSchema


class PersonalLifeMonthlyChangesService(BaseService):
    repository_class = PersonalLifeMonthlyChangesRepository
    schema = PersonalLifeMonthlyChangesSchema


class PersonalLifeMoodEventsService(BaseService):
    repository_class = PersonalLifeMoodEventsRepository
    schema = PersonalLifeMoodEventsSchema


class PersonalLifeOperationsProfileService(BaseService):
    repository_class = PersonalLifeOperationsProfileRepository
    schema = PersonalLifeOperationsProfileSchema


class PersonalLifeRecoveryEventsService(BaseService):
    repository_class = PersonalLifeRecoveryEventsRepository
    schema = PersonalLifeRecoveryEventsSchema


class PersonalLifestyleAdjustEventsService(BaseService):
    repository_class = PersonalLifestyleAdjustEventsRepository
    schema = PersonalLifestyleAdjustEventsSchema


class PersonalLifestyleDiscoveryEventsService(BaseService):
    repository_class = PersonalLifestyleDiscoveryEventsRepository
    schema = PersonalLifestyleDiscoveryEventsSchema


class PersonalLifestyleExperienceEventsService(BaseService):
    repository_class = PersonalLifestyleExperienceEventsRepository
    schema = PersonalLifestyleExperienceEventsSchema


class PersonalLifestyleExpressionEventsService(BaseService):
    repository_class = PersonalLifestyleExpressionEventsRepository
    schema = PersonalLifestyleExpressionEventsSchema


class PersonalLifestyleProfileService(BaseService):
    repository_class = PersonalLifestyleProfileRepository
    schema = PersonalLifestyleProfileSchema


class PersonalLifestyleWellbeingEventsService(BaseService):
    repository_class = PersonalLifestyleWellbeingEventsRepository
    schema = PersonalLifestyleWellbeingEventsSchema


class PersonalLivePrioritiesService(BaseService):
    repository_class = PersonalLivePrioritiesRepository
    schema = PersonalLivePrioritiesSchema


class PersonalMemoryDriverRankingsService(BaseService):
    repository_class = PersonalMemoryDriverRankingsRepository
    schema = PersonalMemoryDriverRankingsSchema


class PersonalMemoryEmotionalDnaService(BaseService):
    repository_class = PersonalMemoryEmotionalDnaRepository
    schema = PersonalMemoryEmotionalDnaSchema


class PersonalMemoryEvolutionSnapshotsService(BaseService):
    repository_class = PersonalMemoryEvolutionSnapshotsRepository
    schema = PersonalMemoryEvolutionSnapshotsSchema


class PersonalMemoryIdentitySnapshotsService(BaseService):
    repository_class = PersonalMemoryIdentitySnapshotsRepository
    schema = PersonalMemoryIdentitySnapshotsSchema


class PersonalMemoryPatternsService(BaseService):
    repository_class = PersonalMemoryPatternsRepository
    schema = PersonalMemoryPatternsSchema


class PersonalMetricSnapshotsService(BaseService):
    repository_class = PersonalMetricSnapshotsRepository
    schema = PersonalMetricSnapshotsSchema


class PersonalMomentHighlightsService(BaseService):
    repository_class = PersonalMomentHighlightsRepository
    schema = PersonalMomentHighlightsSchema


class PersonalMomentProfilesService(BaseService):
    repository_class = PersonalMomentProfilesRepository
    schema = PersonalMomentProfilesSchema


class PersonalMomentTurningPointsService(BaseService):
    repository_class = PersonalMomentTurningPointsRepository
    schema = PersonalMomentTurningPointsSchema


class PersonalMomentTypesService(BaseService):
    repository_class = PersonalMomentTypesRepository
    schema = PersonalMomentTypesSchema


class PersonalMomentsService(BaseService):
    repository_class = PersonalMomentsRepository
    schema = PersonalMomentsSchema


class PersonalMoneyEventsService(BaseService):
    repository_class = PersonalMoneyEventsRepository
    schema = PersonalMoneyEventsSchema


class PersonalNotificationQueueService(BaseService):
    repository_class = PersonalNotificationQueueRepository
    schema = PersonalNotificationQueueSchema


class PersonalPulseSnapshotsService(BaseService):
    repository_class = PersonalPulseSnapshotsRepository
    schema = PersonalPulseSnapshotsSchema


class PersonalQuickAddEventsService(BaseService):
    repository_class = PersonalQuickAddEventsRepository
    schema = PersonalQuickAddEventsSchema


class PersonalRecommendationsService(BaseService):
    repository_class = PersonalRecommendationsRepository
    schema = PersonalRecommendationsSchema


class PersonalRelationshipAdjustEventsService(BaseService):
    repository_class = PersonalRelationshipAdjustEventsRepository
    schema = PersonalRelationshipAdjustEventsSchema


class PersonalRelationshipConnectionEventsService(BaseService):
    repository_class = PersonalRelationshipConnectionEventsRepository
    schema = PersonalRelationshipConnectionEventsSchema


class PersonalRelationshipExperienceEventsService(BaseService):
    repository_class = PersonalRelationshipExperienceEventsRepository
    schema = PersonalRelationshipExperienceEventsSchema


class PersonalRelationshipInvestmentEventsService(BaseService):
    repository_class = PersonalRelationshipInvestmentEventsRepository
    schema = PersonalRelationshipInvestmentEventsSchema


class PersonalRelationshipSupportEventsService(BaseService):
    repository_class = PersonalRelationshipSupportEventsRepository
    schema = PersonalRelationshipSupportEventsSchema


class PersonalRelationshipsProfileService(BaseService):
    repository_class = PersonalRelationshipsProfileRepository
    schema = PersonalRelationshipsProfileSchema


class PersonalRuntimeSnapshotsService(BaseService):
    repository_class = PersonalRuntimeSnapshotsRepository
    schema = PersonalRuntimeSnapshotsSchema


class PersonalSignalsService(BaseService):
    repository_class = PersonalSignalsRepository
    schema = PersonalSignalsSchema


class PersonalUserPreferencesService(BaseService):
    repository_class = PersonalUserPreferencesRepository
    schema = PersonalUserPreferencesSchema
