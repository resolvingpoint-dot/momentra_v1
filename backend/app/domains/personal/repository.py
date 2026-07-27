"""Personal domain repositories (personal_* tables).

One async repository per table. Each inherits the full operation set from
``app.core.repository.AsyncRepository``: create, update, delete, get-by-id,
list, search, pagination, filtering, transactions, bulk insert/update and soft
delete (where the model exposes a soft-delete column). Database access only --
no business logic, no HTTP, no FastAPI.
"""
from __future__ import annotations

from app.core.repository import AsyncRepository
from app.domains.personal.models import (
    PersonalAccounts,
    PersonalActivityTimeline,
    PersonalAiInterpretationRuns,
    PersonalCategories,
    PersonalEventEdits,
    PersonalEventVoids,
    PersonalFutureBuildingProfile,
    PersonalFutureLearningEvents,
    PersonalFutureMilestoneEvents,
    PersonalFutureOpportunityEvents,
    PersonalFuturePivotEvents,
    PersonalFutureProgressEvents,
    PersonalInsights,
    PersonalLifeAdjustEvents,
    PersonalLifeAggregateSnapshots,
    PersonalLifeAttentionEvents,
    PersonalLifeConnections,
    PersonalLifeDimensionScores,
    PersonalLifeDriftAlerts,
    PersonalLifeHealthSnapshots,
    PersonalLifeJourneyEvents,
    PersonalLifeMonthlyChanges,
    PersonalLifeMoodEvents,
    PersonalLifeOperationsProfile,
    PersonalLifeRecoveryEvents,
    PersonalLifestyleAdjustEvents,
    PersonalLifestyleDiscoveryEvents,
    PersonalLifestyleExperienceEvents,
    PersonalLifestyleExpressionEvents,
    PersonalLifestyleProfile,
    PersonalLifestyleWellbeingEvents,
    PersonalLivePriorities,
    PersonalMemoryDriverRankings,
    PersonalMemoryEmotionalDna,
    PersonalMemoryEvolutionSnapshots,
    PersonalMemoryIdentitySnapshots,
    PersonalMemoryPatterns,
    PersonalMetricSnapshots,
    PersonalMomentHighlights,
    PersonalMomentProfiles,
    PersonalMomentTurningPoints,
    PersonalMomentTypes,
    PersonalMoments,
    PersonalMoneyEvents,
    PersonalNotificationQueue,
    PersonalPulseSnapshots,
    PersonalQuickAddEvents,
    PersonalRecommendations,
    PersonalRelationshipAdjustEvents,
    PersonalRelationshipConnectionEvents,
    PersonalRelationshipExperienceEvents,
    PersonalRelationshipInvestmentEvents,
    PersonalRelationshipSupportEvents,
    PersonalRelationshipsProfile,
    PersonalRuntimeSnapshots,
    PersonalSignals,
    PersonalUserPreferences,)


class PersonalAccountsRepository(AsyncRepository[PersonalAccounts]):
    model = PersonalAccounts


class PersonalActivityTimelineRepository(AsyncRepository[PersonalActivityTimeline]):
    model = PersonalActivityTimeline


class PersonalAiInterpretationRunsRepository(AsyncRepository[PersonalAiInterpretationRuns]):
    model = PersonalAiInterpretationRuns


class PersonalCategoriesRepository(AsyncRepository[PersonalCategories]):
    model = PersonalCategories


class PersonalEventEditsRepository(AsyncRepository[PersonalEventEdits]):
    model = PersonalEventEdits


class PersonalEventVoidsRepository(AsyncRepository[PersonalEventVoids]):
    model = PersonalEventVoids


class PersonalFutureBuildingProfileRepository(AsyncRepository[PersonalFutureBuildingProfile]):
    model = PersonalFutureBuildingProfile


class PersonalFutureLearningEventsRepository(AsyncRepository[PersonalFutureLearningEvents]):
    model = PersonalFutureLearningEvents


class PersonalFutureMilestoneEventsRepository(AsyncRepository[PersonalFutureMilestoneEvents]):
    model = PersonalFutureMilestoneEvents


class PersonalFutureOpportunityEventsRepository(AsyncRepository[PersonalFutureOpportunityEvents]):
    model = PersonalFutureOpportunityEvents


class PersonalFuturePivotEventsRepository(AsyncRepository[PersonalFuturePivotEvents]):
    model = PersonalFuturePivotEvents


class PersonalFutureProgressEventsRepository(AsyncRepository[PersonalFutureProgressEvents]):
    model = PersonalFutureProgressEvents


class PersonalInsightsRepository(AsyncRepository[PersonalInsights]):
    model = PersonalInsights


class PersonalLifeAdjustEventsRepository(AsyncRepository[PersonalLifeAdjustEvents]):
    model = PersonalLifeAdjustEvents


class PersonalLifeAggregateSnapshotsRepository(AsyncRepository[PersonalLifeAggregateSnapshots]):
    model = PersonalLifeAggregateSnapshots


class PersonalLifeAttentionEventsRepository(AsyncRepository[PersonalLifeAttentionEvents]):
    model = PersonalLifeAttentionEvents


class PersonalLifeConnectionsRepository(AsyncRepository[PersonalLifeConnections]):
    model = PersonalLifeConnections


class PersonalLifeDimensionScoresRepository(AsyncRepository[PersonalLifeDimensionScores]):
    model = PersonalLifeDimensionScores


class PersonalLifeDriftAlertsRepository(AsyncRepository[PersonalLifeDriftAlerts]):
    model = PersonalLifeDriftAlerts


class PersonalLifeHealthSnapshotsRepository(AsyncRepository[PersonalLifeHealthSnapshots]):
    model = PersonalLifeHealthSnapshots


class PersonalLifeJourneyEventsRepository(AsyncRepository[PersonalLifeJourneyEvents]):
    model = PersonalLifeJourneyEvents


class PersonalLifeMonthlyChangesRepository(AsyncRepository[PersonalLifeMonthlyChanges]):
    model = PersonalLifeMonthlyChanges


class PersonalLifeMoodEventsRepository(AsyncRepository[PersonalLifeMoodEvents]):
    model = PersonalLifeMoodEvents


class PersonalLifeOperationsProfileRepository(AsyncRepository[PersonalLifeOperationsProfile]):
    model = PersonalLifeOperationsProfile


class PersonalLifeRecoveryEventsRepository(AsyncRepository[PersonalLifeRecoveryEvents]):
    model = PersonalLifeRecoveryEvents


class PersonalLifestyleAdjustEventsRepository(AsyncRepository[PersonalLifestyleAdjustEvents]):
    model = PersonalLifestyleAdjustEvents


class PersonalLifestyleDiscoveryEventsRepository(AsyncRepository[PersonalLifestyleDiscoveryEvents]):
    model = PersonalLifestyleDiscoveryEvents


class PersonalLifestyleExperienceEventsRepository(AsyncRepository[PersonalLifestyleExperienceEvents]):
    model = PersonalLifestyleExperienceEvents


class PersonalLifestyleExpressionEventsRepository(AsyncRepository[PersonalLifestyleExpressionEvents]):
    model = PersonalLifestyleExpressionEvents


class PersonalLifestyleProfileRepository(AsyncRepository[PersonalLifestyleProfile]):
    model = PersonalLifestyleProfile


class PersonalLifestyleWellbeingEventsRepository(AsyncRepository[PersonalLifestyleWellbeingEvents]):
    model = PersonalLifestyleWellbeingEvents


class PersonalLivePrioritiesRepository(AsyncRepository[PersonalLivePriorities]):
    model = PersonalLivePriorities


class PersonalMemoryDriverRankingsRepository(AsyncRepository[PersonalMemoryDriverRankings]):
    model = PersonalMemoryDriverRankings


class PersonalMemoryEmotionalDnaRepository(AsyncRepository[PersonalMemoryEmotionalDna]):
    model = PersonalMemoryEmotionalDna


class PersonalMemoryEvolutionSnapshotsRepository(AsyncRepository[PersonalMemoryEvolutionSnapshots]):
    model = PersonalMemoryEvolutionSnapshots


class PersonalMemoryIdentitySnapshotsRepository(AsyncRepository[PersonalMemoryIdentitySnapshots]):
    model = PersonalMemoryIdentitySnapshots


class PersonalMemoryPatternsRepository(AsyncRepository[PersonalMemoryPatterns]):
    model = PersonalMemoryPatterns


class PersonalMetricSnapshotsRepository(AsyncRepository[PersonalMetricSnapshots]):
    model = PersonalMetricSnapshots


class PersonalMomentHighlightsRepository(AsyncRepository[PersonalMomentHighlights]):
    model = PersonalMomentHighlights


class PersonalMomentProfilesRepository(AsyncRepository[PersonalMomentProfiles]):
    model = PersonalMomentProfiles


class PersonalMomentTurningPointsRepository(AsyncRepository[PersonalMomentTurningPoints]):
    model = PersonalMomentTurningPoints


class PersonalMomentTypesRepository(AsyncRepository[PersonalMomentTypes]):
    model = PersonalMomentTypes


class PersonalMomentsRepository(AsyncRepository[PersonalMoments]):
    model = PersonalMoments


class PersonalMoneyEventsRepository(AsyncRepository[PersonalMoneyEvents]):
    model = PersonalMoneyEvents


class PersonalNotificationQueueRepository(AsyncRepository[PersonalNotificationQueue]):
    model = PersonalNotificationQueue


class PersonalPulseSnapshotsRepository(AsyncRepository[PersonalPulseSnapshots]):
    model = PersonalPulseSnapshots


class PersonalQuickAddEventsRepository(AsyncRepository[PersonalQuickAddEvents]):
    model = PersonalQuickAddEvents


class PersonalRecommendationsRepository(AsyncRepository[PersonalRecommendations]):
    model = PersonalRecommendations


class PersonalRelationshipAdjustEventsRepository(AsyncRepository[PersonalRelationshipAdjustEvents]):
    model = PersonalRelationshipAdjustEvents


class PersonalRelationshipConnectionEventsRepository(AsyncRepository[PersonalRelationshipConnectionEvents]):
    model = PersonalRelationshipConnectionEvents


class PersonalRelationshipExperienceEventsRepository(AsyncRepository[PersonalRelationshipExperienceEvents]):
    model = PersonalRelationshipExperienceEvents


class PersonalRelationshipInvestmentEventsRepository(AsyncRepository[PersonalRelationshipInvestmentEvents]):
    model = PersonalRelationshipInvestmentEvents


class PersonalRelationshipSupportEventsRepository(AsyncRepository[PersonalRelationshipSupportEvents]):
    model = PersonalRelationshipSupportEvents


class PersonalRelationshipsProfileRepository(AsyncRepository[PersonalRelationshipsProfile]):
    model = PersonalRelationshipsProfile


class PersonalRuntimeSnapshotsRepository(AsyncRepository[PersonalRuntimeSnapshots]):
    model = PersonalRuntimeSnapshots


class PersonalSignalsRepository(AsyncRepository[PersonalSignals]):
    model = PersonalSignals


class PersonalUserPreferencesRepository(AsyncRepository[PersonalUserPreferences]):
    model = PersonalUserPreferences
