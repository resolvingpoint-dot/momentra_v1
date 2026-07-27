"""Business domain repositories (business_*, operations_*, runway_*, team_* tables).

One async repository per table. Each inherits the full operation set from
``app.core.repository.AsyncRepository``: create, update, delete, get-by-id,
list, search, pagination, filtering, transactions, bulk insert/update and soft
delete (where the model exposes a soft-delete column). Database access only --
no business logic, no HTTP, no FastAPI.
"""
from __future__ import annotations

from app.core.repository import AsyncRepository
from app.domains.business.models import (
    BusinessActivityCenterItems,
    BusinessActivityPermissions,
    BusinessActivitySourceMapping,
    BusinessAttachmentFiles,
    BusinessAttentionItems,
    BusinessAuditHistory,
    BusinessDriverFormulaRegistry,
    BusinessHealthDriverScores,
    BusinessLifeConnections,
    BusinessLifeDimensions,
    BusinessLifeInsights,
    BusinessLifeSnapshots,
    BusinessLiveFeed,
    BusinessMemoryLearnings,
    BusinessMemoryPatterns,
    BusinessMemorySnapshots,
    BusinessMomentGovernance,
    BusinessMomentHighlights,
    BusinessMomentInvitations,
    BusinessMomentMembers,
    BusinessMomentMetrics,
    BusinessMomentSetup,
    BusinessMomentStructure,
    BusinessMoments,
    BusinessNotifications,
    BusinessOperationsBudgetCategories,
    BusinessOperationsGovernanceRules,
    BusinessOperationsSetup,
    BusinessOperationsSnapshots,
    BusinessOperationsStructure,
    BusinessOrchestrationJobs,
    BusinessPlaybooks,
    BusinessProgressSnapshots,
    BusinessPulseSnapshots,
    BusinessQuickAddDrafts,
    BusinessRecommendedActions,
    BusinessRiskMemory,
    BusinessRunwayGovernanceRules,
    BusinessRunwaySetup,
    BusinessRunwaySnapshots,
    BusinessRunwayStructure,
    BusinessSignalInsights,
    BusinessSuccessMemory,
    BusinessTransactionPermissions,
    BusinessVendorDirectory,
    BusinessWisdom,
    OperationsApprovalRequests,
    OperationsImprovements,
    OperationsIssues,
    OperationsSpendEntries,
    OperationsVendorUpdates,
    RunwayCashInflows,
    RunwayExpenseBurns,
    RunwayFinancialUpdates,
    RunwayRisks,
    RunwayStrategicDecisions,
    TeamActivities,
    TeamApprovalRequests,
    TeamIssueRisks,
    TeamUpdates,)


class BusinessActivityCenterItemsRepository(AsyncRepository[BusinessActivityCenterItems]):
    model = BusinessActivityCenterItems


class BusinessActivityPermissionsRepository(AsyncRepository[BusinessActivityPermissions]):
    model = BusinessActivityPermissions


class BusinessActivitySourceMappingRepository(AsyncRepository[BusinessActivitySourceMapping]):
    model = BusinessActivitySourceMapping


class BusinessAttachmentFilesRepository(AsyncRepository[BusinessAttachmentFiles]):
    model = BusinessAttachmentFiles


class BusinessAttentionItemsRepository(AsyncRepository[BusinessAttentionItems]):
    model = BusinessAttentionItems


class BusinessAuditHistoryRepository(AsyncRepository[BusinessAuditHistory]):
    model = BusinessAuditHistory


class BusinessDriverFormulaRegistryRepository(AsyncRepository[BusinessDriverFormulaRegistry]):
    model = BusinessDriverFormulaRegistry


class BusinessHealthDriverScoresRepository(AsyncRepository[BusinessHealthDriverScores]):
    model = BusinessHealthDriverScores


class BusinessLifeConnectionsRepository(AsyncRepository[BusinessLifeConnections]):
    model = BusinessLifeConnections


class BusinessLifeDimensionsRepository(AsyncRepository[BusinessLifeDimensions]):
    model = BusinessLifeDimensions


class BusinessLifeInsightsRepository(AsyncRepository[BusinessLifeInsights]):
    model = BusinessLifeInsights


class BusinessLifeSnapshotsRepository(AsyncRepository[BusinessLifeSnapshots]):
    model = BusinessLifeSnapshots


class BusinessLiveFeedRepository(AsyncRepository[BusinessLiveFeed]):
    model = BusinessLiveFeed


class BusinessMemoryLearningsRepository(AsyncRepository[BusinessMemoryLearnings]):
    model = BusinessMemoryLearnings


class BusinessMemoryPatternsRepository(AsyncRepository[BusinessMemoryPatterns]):
    model = BusinessMemoryPatterns


class BusinessMemorySnapshotsRepository(AsyncRepository[BusinessMemorySnapshots]):
    model = BusinessMemorySnapshots


class BusinessMomentGovernanceRepository(AsyncRepository[BusinessMomentGovernance]):
    model = BusinessMomentGovernance


class BusinessMomentHighlightsRepository(AsyncRepository[BusinessMomentHighlights]):
    model = BusinessMomentHighlights


class BusinessMomentInvitationsRepository(AsyncRepository[BusinessMomentInvitations]):
    model = BusinessMomentInvitations


class BusinessMomentMembersRepository(AsyncRepository[BusinessMomentMembers]):
    model = BusinessMomentMembers


class BusinessMomentMetricsRepository(AsyncRepository[BusinessMomentMetrics]):
    model = BusinessMomentMetrics


class BusinessMomentSetupRepository(AsyncRepository[BusinessMomentSetup]):
    model = BusinessMomentSetup


class BusinessMomentStructureRepository(AsyncRepository[BusinessMomentStructure]):
    model = BusinessMomentStructure


class BusinessMomentsRepository(AsyncRepository[BusinessMoments]):
    model = BusinessMoments


class BusinessNotificationsRepository(AsyncRepository[BusinessNotifications]):
    model = BusinessNotifications


class BusinessOperationsBudgetCategoriesRepository(AsyncRepository[BusinessOperationsBudgetCategories]):
    model = BusinessOperationsBudgetCategories


class BusinessOperationsGovernanceRulesRepository(AsyncRepository[BusinessOperationsGovernanceRules]):
    model = BusinessOperationsGovernanceRules


class BusinessOperationsSetupRepository(AsyncRepository[BusinessOperationsSetup]):
    model = BusinessOperationsSetup


class BusinessOperationsSnapshotsRepository(AsyncRepository[BusinessOperationsSnapshots]):
    model = BusinessOperationsSnapshots


class BusinessOperationsStructureRepository(AsyncRepository[BusinessOperationsStructure]):
    model = BusinessOperationsStructure


class BusinessOrchestrationJobsRepository(AsyncRepository[BusinessOrchestrationJobs]):
    model = BusinessOrchestrationJobs


class BusinessPlaybooksRepository(AsyncRepository[BusinessPlaybooks]):
    model = BusinessPlaybooks


class BusinessProgressSnapshotsRepository(AsyncRepository[BusinessProgressSnapshots]):
    model = BusinessProgressSnapshots


class BusinessPulseSnapshotsRepository(AsyncRepository[BusinessPulseSnapshots]):
    model = BusinessPulseSnapshots


class BusinessQuickAddDraftsRepository(AsyncRepository[BusinessQuickAddDrafts]):
    model = BusinessQuickAddDrafts


class BusinessRecommendedActionsRepository(AsyncRepository[BusinessRecommendedActions]):
    model = BusinessRecommendedActions


class BusinessRiskMemoryRepository(AsyncRepository[BusinessRiskMemory]):
    model = BusinessRiskMemory


class BusinessRunwayGovernanceRulesRepository(AsyncRepository[BusinessRunwayGovernanceRules]):
    model = BusinessRunwayGovernanceRules


class BusinessRunwaySetupRepository(AsyncRepository[BusinessRunwaySetup]):
    model = BusinessRunwaySetup


class BusinessRunwaySnapshotsRepository(AsyncRepository[BusinessRunwaySnapshots]):
    model = BusinessRunwaySnapshots


class BusinessRunwayStructureRepository(AsyncRepository[BusinessRunwayStructure]):
    model = BusinessRunwayStructure


class BusinessSignalInsightsRepository(AsyncRepository[BusinessSignalInsights]):
    model = BusinessSignalInsights


class BusinessSuccessMemoryRepository(AsyncRepository[BusinessSuccessMemory]):
    model = BusinessSuccessMemory


class BusinessTransactionPermissionsRepository(AsyncRepository[BusinessTransactionPermissions]):
    model = BusinessTransactionPermissions


class BusinessVendorDirectoryRepository(AsyncRepository[BusinessVendorDirectory]):
    model = BusinessVendorDirectory


class BusinessWisdomRepository(AsyncRepository[BusinessWisdom]):
    model = BusinessWisdom


class OperationsApprovalRequestsRepository(AsyncRepository[OperationsApprovalRequests]):
    model = OperationsApprovalRequests


class OperationsImprovementsRepository(AsyncRepository[OperationsImprovements]):
    model = OperationsImprovements


class OperationsIssuesRepository(AsyncRepository[OperationsIssues]):
    model = OperationsIssues


class OperationsSpendEntriesRepository(AsyncRepository[OperationsSpendEntries]):
    model = OperationsSpendEntries


class OperationsVendorUpdatesRepository(AsyncRepository[OperationsVendorUpdates]):
    model = OperationsVendorUpdates


class RunwayCashInflowsRepository(AsyncRepository[RunwayCashInflows]):
    model = RunwayCashInflows


class RunwayExpenseBurnsRepository(AsyncRepository[RunwayExpenseBurns]):
    model = RunwayExpenseBurns


class RunwayFinancialUpdatesRepository(AsyncRepository[RunwayFinancialUpdates]):
    model = RunwayFinancialUpdates


class RunwayRisksRepository(AsyncRepository[RunwayRisks]):
    model = RunwayRisks


class RunwayStrategicDecisionsRepository(AsyncRepository[RunwayStrategicDecisions]):
    model = RunwayStrategicDecisions


class TeamActivitiesRepository(AsyncRepository[TeamActivities]):
    model = TeamActivities


class TeamApprovalRequestsRepository(AsyncRepository[TeamApprovalRequests]):
    model = TeamApprovalRequests


class TeamIssueRisksRepository(AsyncRepository[TeamIssueRisks]):
    model = TeamIssueRisks


class TeamUpdatesRepository(AsyncRepository[TeamUpdates]):
    model = TeamUpdates
