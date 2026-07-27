"""Life360 domain services (one per table).

Each service inherits the full orchestration + business-logic skeleton
from app.core.service.BaseService (validation, permission checks,
workflow/state transitions, snapshot refresh, cache invalidation, event
creation) and always returns schemas -- never SQLAlchemy models. No HTTP.
"""
from __future__ import annotations

from app.core.service import BaseService
from app.domains.life360.repository import (
    AiSignalsRepository,
    BudgetMasterCategoriesRepository,
    CommunityCoordinationDetailsRepository,
    ExperienceBudgetTemplatesRepository,
    Life360SnapshotsRepository,
    SharedExperienceBudgetAllocationsRepository,
    SharedExperienceBudgetPlansRepository,
    SharedExperienceBudgetSplitsRepository,
    SharedExperienceDetailsRepository,
    SharedExperienceMemoryHighlightsRepository,
    SharedExperiencePlanningItemsRepository,
    SharedExperienceSettlementsRepository,
    SharedGoalDetailsRepository,
    SharedLivingAssetsRepository,
    SharedLivingDetailsRepository,
    SharedLivingHomePersonalityRepository,
    SharedLivingMaintenanceRepository,
    SharedLivingResidentDynamicsRepository,
    SharedLivingResidentsRepository,
    SharedLivingRulesRepository,
    SharedLivingTasksRepository,
    SharedPurchaseContributorsRepository,
    SharedPurchaseDeliveryRepository,
    SharedPurchaseDetailsRepository,
    SharedPurchaseItemsRepository,
    SharedPurchaseOwnershipRepository,
    SharedPurchaseOwnershipInsightsRepository,
    SharedPurchaseVendorsRepository,
)
from app.domains.life360.schemas import (
    AiSignalsSchema,
    BudgetMasterCategoriesSchema,
    CommunityCoordinationDetailsSchema,
    ExperienceBudgetTemplatesSchema,
    Life360SnapshotsSchema,
    SharedExperienceBudgetAllocationsSchema,
    SharedExperienceBudgetPlansSchema,
    SharedExperienceBudgetSplitsSchema,
    SharedExperienceDetailsSchema,
    SharedExperienceMemoryHighlightsSchema,
    SharedExperiencePlanningItemsSchema,
    SharedExperienceSettlementsSchema,
    SharedGoalDetailsSchema,
    SharedLivingAssetsSchema,
    SharedLivingDetailsSchema,
    SharedLivingHomePersonalitySchema,
    SharedLivingMaintenanceSchema,
    SharedLivingResidentDynamicsSchema,
    SharedLivingResidentsSchema,
    SharedLivingRulesSchema,
    SharedLivingTasksSchema,
    SharedPurchaseContributorsSchema,
    SharedPurchaseDeliverySchema,
    SharedPurchaseDetailsSchema,
    SharedPurchaseItemsSchema,
    SharedPurchaseOwnershipSchema,
    SharedPurchaseOwnershipInsightsSchema,
    SharedPurchaseVendorsSchema,
)


class AiSignalsService(BaseService):
    repository_class = AiSignalsRepository
    schema = AiSignalsSchema


class BudgetMasterCategoriesService(BaseService):
    repository_class = BudgetMasterCategoriesRepository
    schema = BudgetMasterCategoriesSchema


class CommunityCoordinationDetailsService(BaseService):
    repository_class = CommunityCoordinationDetailsRepository
    schema = CommunityCoordinationDetailsSchema


class ExperienceBudgetTemplatesService(BaseService):
    repository_class = ExperienceBudgetTemplatesRepository
    schema = ExperienceBudgetTemplatesSchema


class Life360SnapshotsService(BaseService):
    repository_class = Life360SnapshotsRepository
    schema = Life360SnapshotsSchema


class SharedExperienceBudgetAllocationsService(BaseService):
    repository_class = SharedExperienceBudgetAllocationsRepository
    schema = SharedExperienceBudgetAllocationsSchema


class SharedExperienceBudgetPlansService(BaseService):
    repository_class = SharedExperienceBudgetPlansRepository
    schema = SharedExperienceBudgetPlansSchema


class SharedExperienceBudgetSplitsService(BaseService):
    repository_class = SharedExperienceBudgetSplitsRepository
    schema = SharedExperienceBudgetSplitsSchema


class SharedExperienceDetailsService(BaseService):
    repository_class = SharedExperienceDetailsRepository
    schema = SharedExperienceDetailsSchema


class SharedExperienceMemoryHighlightsService(BaseService):
    repository_class = SharedExperienceMemoryHighlightsRepository
    schema = SharedExperienceMemoryHighlightsSchema


class SharedExperiencePlanningItemsService(BaseService):
    repository_class = SharedExperiencePlanningItemsRepository
    schema = SharedExperiencePlanningItemsSchema


class SharedExperienceSettlementsService(BaseService):
    repository_class = SharedExperienceSettlementsRepository
    schema = SharedExperienceSettlementsSchema


class SharedGoalDetailsService(BaseService):
    repository_class = SharedGoalDetailsRepository
    schema = SharedGoalDetailsSchema


class SharedLivingAssetsService(BaseService):
    repository_class = SharedLivingAssetsRepository
    schema = SharedLivingAssetsSchema


class SharedLivingDetailsService(BaseService):
    repository_class = SharedLivingDetailsRepository
    schema = SharedLivingDetailsSchema


class SharedLivingHomePersonalityService(BaseService):
    repository_class = SharedLivingHomePersonalityRepository
    schema = SharedLivingHomePersonalitySchema


class SharedLivingMaintenanceService(BaseService):
    repository_class = SharedLivingMaintenanceRepository
    schema = SharedLivingMaintenanceSchema


class SharedLivingResidentDynamicsService(BaseService):
    repository_class = SharedLivingResidentDynamicsRepository
    schema = SharedLivingResidentDynamicsSchema


class SharedLivingResidentsService(BaseService):
    repository_class = SharedLivingResidentsRepository
    schema = SharedLivingResidentsSchema


class SharedLivingRulesService(BaseService):
    repository_class = SharedLivingRulesRepository
    schema = SharedLivingRulesSchema


class SharedLivingTasksService(BaseService):
    repository_class = SharedLivingTasksRepository
    schema = SharedLivingTasksSchema


class SharedPurchaseContributorsService(BaseService):
    repository_class = SharedPurchaseContributorsRepository
    schema = SharedPurchaseContributorsSchema


class SharedPurchaseDeliveryService(BaseService):
    repository_class = SharedPurchaseDeliveryRepository
    schema = SharedPurchaseDeliverySchema


class SharedPurchaseDetailsService(BaseService):
    repository_class = SharedPurchaseDetailsRepository
    schema = SharedPurchaseDetailsSchema


class SharedPurchaseItemsService(BaseService):
    repository_class = SharedPurchaseItemsRepository
    schema = SharedPurchaseItemsSchema


class SharedPurchaseOwnershipService(BaseService):
    repository_class = SharedPurchaseOwnershipRepository
    schema = SharedPurchaseOwnershipSchema


class SharedPurchaseOwnershipInsightsService(BaseService):
    repository_class = SharedPurchaseOwnershipInsightsRepository
    schema = SharedPurchaseOwnershipInsightsSchema


class SharedPurchaseVendorsService(BaseService):
    repository_class = SharedPurchaseVendorsRepository
    schema = SharedPurchaseVendorsSchema
