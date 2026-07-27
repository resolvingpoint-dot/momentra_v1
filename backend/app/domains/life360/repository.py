"""Life360 / shared-experience domain repositories (shared_*, life360_snapshots, reference tables).

One async repository per table. Each inherits the full operation set from
``app.core.repository.AsyncRepository``: create, update, delete, get-by-id,
list, search, pagination, filtering, transactions, bulk insert/update and soft
delete (where the model exposes a soft-delete column). Database access only --
no business logic, no HTTP, no FastAPI.
"""
from __future__ import annotations

from app.core.repository import AsyncRepository
from app.domains.life360.models import (
    AiSignals,
    BudgetMasterCategories,
    CommunityCoordinationDetails,
    ExperienceBudgetTemplates,
    Life360Snapshots,
    SharedExperienceBudgetAllocations,
    SharedExperienceBudgetPlans,
    SharedExperienceBudgetSplits,
    SharedExperienceDetails,
    SharedExperienceMemoryHighlights,
    SharedExperiencePlanningItems,
    SharedExperienceSettlements,
    SharedGoalDetails,
    SharedLivingAssets,
    SharedLivingDetails,
    SharedLivingHomePersonality,
    SharedLivingMaintenance,
    SharedLivingResidentDynamics,
    SharedLivingResidents,
    SharedLivingRules,
    SharedLivingTasks,
    SharedPurchaseContributors,
    SharedPurchaseDelivery,
    SharedPurchaseDetails,
    SharedPurchaseItems,
    SharedPurchaseOwnership,
    SharedPurchaseOwnershipInsights,
    SharedPurchaseVendors,)


class AiSignalsRepository(AsyncRepository[AiSignals]):
    model = AiSignals


class BudgetMasterCategoriesRepository(AsyncRepository[BudgetMasterCategories]):
    model = BudgetMasterCategories


class CommunityCoordinationDetailsRepository(AsyncRepository[CommunityCoordinationDetails]):
    model = CommunityCoordinationDetails


class ExperienceBudgetTemplatesRepository(AsyncRepository[ExperienceBudgetTemplates]):
    model = ExperienceBudgetTemplates


class Life360SnapshotsRepository(AsyncRepository[Life360Snapshots]):
    model = Life360Snapshots


class SharedExperienceBudgetAllocationsRepository(AsyncRepository[SharedExperienceBudgetAllocations]):
    model = SharedExperienceBudgetAllocations


class SharedExperienceBudgetPlansRepository(AsyncRepository[SharedExperienceBudgetPlans]):
    model = SharedExperienceBudgetPlans


class SharedExperienceBudgetSplitsRepository(AsyncRepository[SharedExperienceBudgetSplits]):
    model = SharedExperienceBudgetSplits


class SharedExperienceDetailsRepository(AsyncRepository[SharedExperienceDetails]):
    model = SharedExperienceDetails


class SharedExperienceMemoryHighlightsRepository(AsyncRepository[SharedExperienceMemoryHighlights]):
    model = SharedExperienceMemoryHighlights


class SharedExperiencePlanningItemsRepository(AsyncRepository[SharedExperiencePlanningItems]):
    model = SharedExperiencePlanningItems


class SharedExperienceSettlementsRepository(AsyncRepository[SharedExperienceSettlements]):
    model = SharedExperienceSettlements


class SharedGoalDetailsRepository(AsyncRepository[SharedGoalDetails]):
    model = SharedGoalDetails


class SharedLivingAssetsRepository(AsyncRepository[SharedLivingAssets]):
    model = SharedLivingAssets


class SharedLivingDetailsRepository(AsyncRepository[SharedLivingDetails]):
    model = SharedLivingDetails


class SharedLivingHomePersonalityRepository(AsyncRepository[SharedLivingHomePersonality]):
    model = SharedLivingHomePersonality


class SharedLivingMaintenanceRepository(AsyncRepository[SharedLivingMaintenance]):
    model = SharedLivingMaintenance


class SharedLivingResidentDynamicsRepository(AsyncRepository[SharedLivingResidentDynamics]):
    model = SharedLivingResidentDynamics


class SharedLivingResidentsRepository(AsyncRepository[SharedLivingResidents]):
    model = SharedLivingResidents


class SharedLivingRulesRepository(AsyncRepository[SharedLivingRules]):
    model = SharedLivingRules


class SharedLivingTasksRepository(AsyncRepository[SharedLivingTasks]):
    model = SharedLivingTasks


class SharedPurchaseContributorsRepository(AsyncRepository[SharedPurchaseContributors]):
    model = SharedPurchaseContributors


class SharedPurchaseDeliveryRepository(AsyncRepository[SharedPurchaseDelivery]):
    model = SharedPurchaseDelivery


class SharedPurchaseDetailsRepository(AsyncRepository[SharedPurchaseDetails]):
    model = SharedPurchaseDetails


class SharedPurchaseItemsRepository(AsyncRepository[SharedPurchaseItems]):
    model = SharedPurchaseItems


class SharedPurchaseOwnershipRepository(AsyncRepository[SharedPurchaseOwnership]):
    model = SharedPurchaseOwnership


class SharedPurchaseOwnershipInsightsRepository(AsyncRepository[SharedPurchaseOwnershipInsights]):
    model = SharedPurchaseOwnershipInsights


class SharedPurchaseVendorsRepository(AsyncRepository[SharedPurchaseVendors]):
    model = SharedPurchaseVendors
