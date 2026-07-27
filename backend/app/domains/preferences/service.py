from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.preferences.models import UserPreferencesModel
from app.domains.preferences.repository import UserPreferenceRepository
from app.domains.preferences.schemas import PreferenceUpdateSchema
from app.domains.reference_data.service import get_reference_data_service


class UserPreferenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserPreferenceRepository(session)
        self.reference_data = get_reference_data_service()

    async def get_or_create(self, user_id) -> UserPreferencesModel:
        pref = await self.repo.get_by_user_id(user_id)
        if pref is None:
            pref = await self.repo.create(user_id)
        return pref

    async def update_selected_context(self, user_id, selected_context: str) -> UserPreferencesModel | None:
        return await self.repo.update_selected_context(user_id, selected_context)

    async def update_preferences(
        self, user_id, body: PreferenceUpdateSchema
    ) -> UserPreferencesModel | None:
        currency = body.default_currency_code
        country = body.country_code
        locale = body.locale
        timezone_name = body.timezone

        if currency is not None:
            currency = self.reference_data.validate_currency(currency)
        if country is not None:
            country = self.reference_data.validate_country(country)
        if locale is not None:
            locale = self.reference_data.validate_locale(locale)
        if timezone_name is not None:
            timezone_name = self.reference_data.validate_timezone(timezone_name)

        return await self.repo.update_preferences(
            user_id,
            selected_context=body.selected_context,
            default_currency_code=currency,
            locale=locale,
            country_code=country,
            timezone_name=timezone_name,
        )

    async def update_preferences_and_notify(
        self, user_id, body: PreferenceUpdateSchema
    ) -> UserPreferencesModel | None:
        updated = await self.update_preferences(user_id, body)
        if updated is not None:
            from uuid import UUID

            from app.domains.projections.handlers import PREFERENCES_UPDATED
            from app.shared.events.base import DomainEvent
            from app.shared.events.publisher import get_event_publisher

            uid = user_id if isinstance(user_id, UUID) else UUID(str(user_id))
            # Preferences are user-scoped (not moment-scoped); DomainEvent requires moment_id.
            await get_event_publisher().publish(
                DomainEvent(
                    name=PREFERENCES_UPDATED,
                    user_id=uid,
                    moment_id=UUID(int=0),
                    context=updated.selected_context or "MY_MONEY",
                    payload={
                        "selected_context": updated.selected_context,
                    },
                )
            )
        return updated
