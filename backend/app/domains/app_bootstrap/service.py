from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import delete_cached, get_cached, set_cached
from app.core.errors import PermissionDeniedError
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
        if getattr(user, "deleted_at", None) is not None:
            raise PermissionDeniedError(
                "Account has been deleted",
                code="account_deleted",
            )

        cache_key = f"app_bootstrap:{user.id}"
        cached = await get_cached(cache_key)
        if cached is not None:
            return BootstrapResponse(**cached)

        result = await self._build_bootstrap(user)
        await set_cached(cache_key, result.model_dump(mode="json"), ttl=30)
        return result

    async def _build_bootstrap(self, user: UserModel) -> BootstrapResponse:
        pref = await self.pref_service.get_or_create(user.id)
        # Heal context/module flags from inventory before clients resolve empty/setup.
        await self._heal_module_states_from_inventory(user.id)
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

        from app.domains.personal.preferences_service import PersonalPreferencesService
        from app.domains.personal.schemas import BootstrapPersonalPreferencesSchema

        personal_pref = await PersonalPreferencesService(self.session).get_or_create(
            user.id,
            default_currency_code=pref.default_currency_code,
            timezone_name=pref.timezone,
        )
        personal_preferences = BootstrapPersonalPreferencesSchema(
            **PersonalPreferencesService(self.session).to_bootstrap_dict(personal_pref)
        )

        return BootstrapResponse(
            user=UserResponse.model_validate(user),
            preferences=pref,  # type: ignore[arg-type]
            personal_preferences=personal_preferences,
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

    async def _heal_module_states_from_inventory(self, user_id) -> None:
        """Promote SETUP/EMPTY → ACTIVE when ACTIVE moments exist.

        Draft creates in Business/Group historically demoted shared ``PULSE`` (and
        occasionally left ``MY_MONEY`` stuck at SETUP) even though Personal/Group
        still had ACTIVE moments — clients then rendered brand-new empty/setup UX.
        """
        from sqlalchemy import func, select

        from app.domains.moments.models import MomentModel

        result = await self.session.execute(
            select(MomentModel.context_type, func.count(MomentModel.id))
            .where(
                MomentModel.user_id == user_id,
                MomentModel.status == "ACTIVE",
            )
            .group_by(MomentModel.context_type)
        )
        active_by_ctx = {row[0]: int(row[1]) for row in result}
        if not active_by_ctx:
            return

        existing = await self.module_service.get_all_for_user(user_id)
        state_map = {ms.module_key: (ms.state or "").upper() for ms in existing}
        changed = False

        async def _promote(key: str, reason: str) -> None:
            nonlocal changed
            if state_map.get(key) == "ACTIVE":
                return
            await self.module_service.set_state(user_id, key, "ACTIVE", reason)
            state_map[key] = "ACTIVE"
            changed = True

        if active_by_ctx.get("MY_MONEY", 0) > 0:
            await _promote("MY_MONEY", "bootstrap_heal_active_personal")
            await _promote("MEMORY", "bootstrap_heal_active_personal")
        if active_by_ctx.get("GROUP", 0) > 0:
            await _promote("GROUP", "bootstrap_heal_active_group")
        if active_by_ctx.get("BUSINESS", 0) > 0:
            await _promote("BUSINESS", "bootstrap_heal_active_business")

        if any(active_by_ctx.get(k, 0) > 0 for k in ("MY_MONEY", "GROUP", "BUSINESS")):
            await _promote("PULSE", "bootstrap_heal_active_inventory")
            await _promote("MOMENTS", "bootstrap_heal_active_inventory")

        if changed:
            await self.session.flush()
