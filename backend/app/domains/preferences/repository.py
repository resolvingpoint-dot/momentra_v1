from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.preferences.models import UserPreferencesModel


class UserPreferenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(self, user_id) -> UserPreferencesModel | None:
        stmt = select(UserPreferencesModel).where(
            UserPreferencesModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, user_id, selected_context: str = "MY_MONEY"
    ) -> UserPreferencesModel:
        now = datetime.now(timezone.utc)
        pref = UserPreferencesModel(
            id=uuid4(),
            user_id=user_id,
            selected_context=selected_context,
            default_currency_code="INR",
            locale="en-IN",
            country_code="IN",
            timezone="Asia/Kolkata",
            created_at=now,
            updated_at=now,
        )
        self.session.add(pref)
        return pref

    async def update_preferences(
        self,
        user_id,
        *,
        selected_context: str | None = None,
        default_currency_code: str | None = None,
        locale: str | None = None,
        country_code: str | None = None,
        timezone_name: str | None = None,
    ) -> UserPreferencesModel | None:
        pref = await self.get_by_user_id(user_id)
        if pref is None:
            return None
        if selected_context is not None:
            pref.selected_context = selected_context
        if default_currency_code is not None:
            pref.default_currency_code = default_currency_code
        if locale is not None:
            pref.locale = locale
        if country_code is not None:
            pref.country_code = country_code
        if timezone_name is not None:
            pref.timezone = timezone_name
        pref.updated_at = datetime.now(timezone.utc)
        return pref

    async def update_selected_context(self, user_id, selected_context: str) -> UserPreferencesModel | None:
        return await self.update_preferences(user_id, selected_context=selected_context)
