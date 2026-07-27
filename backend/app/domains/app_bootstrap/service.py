from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import delete_cached, get_cached, set_cached
from app.core.version_registry import get_platform_versions, sync_reference_data_version
from app.domains.app_bootstrap.schemas import (
    BootstrapResponse,
    ModuleEntrySchema,
    SummaryCountsSchema,
)
from app.domains.module_states.schemas import ContextSchema
from app.domains.module_states.service import ModuleStateService
from app.domains.moments.service import MomentService
from app.domains.preferences.service import UserPreferenceService
from app.domains.reference_data.service import get_reference_data_service
from app.domains.users.models import UserModel
from app.domains.users.schemas import UserResponse
from app.domains.users.service import UserService

CONTEXT_LABELS = {
    "MY_MONEY": "My Money",
    "GROUP": "Group",
    "BUSINESS": "Business",
    "CIRCLE": "Circle",
}

CONTEXT_MODULE_KEYS = ["MY_MONEY", "GROUP", "BUSINESS", "CIRCLE"]

MODULE_KEYS = ["pulse", "moments", "life360", "circle", "memory"]


class AppBootstrapService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)
        self.pref_service = UserPreferenceService(session)
        self.module_service = ModuleStateService(session)
        self.moment_service = MomentService(session)

    async def get_bootstrap(self, firebase_uid: str) -> BootstrapResponse:
        user = await self.user_service.get_user(firebase_uid)
        if user is None:
            raise RuntimeError("User not found")

        cache_key = f"app_bootstrap:{user.id}"
        cached = await get_cached(cache_key)
        if cached is not None:
            return BootstrapResponse(**cached)

        result = await self._build_bootstrap(user)
        await set_cached(cache_key, result.model_dump(mode="json"), ttl=30)
        return result

    async def _build_bootstrap(self, user: UserModel) -> BootstrapResponse:
        pref = await self.pref_service.get_or_create(user.id)
        module_states = await self.module_service.get_all_for_user(user.id)

        state_map = {ms.module_key: ms.state for ms in module_states}

        contexts: list[ContextSchema] = []
        for key in CONTEXT_MODULE_KEYS:
            contexts.append(
                ContextSchema(
                    key=key,
                    label=CONTEXT_LABELS.get(key, key),
                    state=state_map.get(key, "EMPTY"),
                )
            )

        module_entry_map: dict[str, ModuleEntrySchema] = {}
        for mkey in MODULE_KEYS:
            db_key = mkey.upper()
            module_entry_map[mkey] = ModuleEntrySchema(
                state=state_map.get(db_key, "EMPTY")
            )

        my_money_count = await self.moment_service.count_by_context_type(
            user.id, "MY_MONEY"
        )
        group_count = await self.moment_service.count_by_context_type(
            user.id, "GROUP"
        )
        business_count = await self.moment_service.count_by_context_type(
            user.id, "BUSINESS"
        )

        summary = SummaryCountsSchema(
            my_money_moments=my_money_count,
            group_moments=group_count,
            business_moments=business_count,
        )

        reference_data = get_reference_data_service()
        ref_version = reference_data.get_version()
        sync_reference_data_version(ref_version)
        versions = get_platform_versions()

        return BootstrapResponse(
            user=UserResponse.model_validate(user),
            preferences=pref,  # type: ignore[arg-type]
            contexts=contexts,
            modules=module_entry_map,
            summary_counts=summary,
            reference_data_version=versions.reference_data_version,
            template_version=versions.template_version,
            ui_schema_version=versions.ui_schema_version,
            quick_add_version=versions.quick_add_version,
            setup_version=versions.setup_version,
            metadata_version=versions.metadata_version,
            server_time=datetime.now(timezone.utc).isoformat(),
        )

    async def invalidate_cache(self, user_id) -> None:
        await delete_cached(f"app_bootstrap:{user_id}")
