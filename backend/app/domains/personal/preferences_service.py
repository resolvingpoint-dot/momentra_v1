"""Personal user preferences — week start, notifications, privacy."""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.models import PersonalUserPreferences
from app.domains.personal.schemas import (
    PersonalUserPreferencesSchema,
    PersonalUserPreferencesUpdateSchema,
)

VALID_WEEK_START = {"MONDAY", "SUNDAY"}


class PersonalPreferencesService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> PersonalUserPreferences | None:
        result = await self.session.execute(
            select(PersonalUserPreferences).where(
                PersonalUserPreferences.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        user_id: UUID,
        *,
        default_currency_code: str = "INR",
        timezone_name: str = "Asia/Kolkata",
    ) -> PersonalUserPreferences:
        pref = await self.get_by_user_id(user_id)
        if pref is not None:
            return pref
        now = datetime.now(timezone.utc)
        pref = PersonalUserPreferences(
            preference_id=uuid4(),
            user_id=user_id,
            default_currency_code=default_currency_code,
            timezone_name=timezone_name,
            notification_enabled=True,
            quick_add_reminder_enabled=False,
            daily_summary_enabled=False,
            privacy_mode_enabled=False,
            week_start_day="MONDAY",
            created_at=now,
            updated_at=now,
        )
        self.session.add(pref)
        await self.session.flush()
        return pref

    async def sync_from_app_preferences(
        self,
        user_id: UUID,
        *,
        default_currency_code: str | None = None,
        timezone_name: str | None = None,
    ) -> PersonalUserPreferences | None:
        """Keep personal currency/timezone columns aligned with app prefs."""
        if default_currency_code is None and timezone_name is None:
            return await self.get_by_user_id(user_id)

        pref = await self.get_or_create(
            user_id,
            default_currency_code=default_currency_code or "INR",
            timezone_name=timezone_name or "Asia/Kolkata",
        )
        if default_currency_code is not None:
            pref.default_currency_code = default_currency_code
        if timezone_name is not None:
            pref.timezone_name = timezone_name
        pref.updated_at = datetime.now(timezone.utc)
        return pref

    async def update(
        self, user_id: UUID, body: PersonalUserPreferencesUpdateSchema
    ) -> PersonalUserPreferences:
        pref = await self.get_or_create(user_id)

        if body.week_start_day is not None:
            day = body.week_start_day.upper()
            if day not in VALID_WEEK_START:
                raise ValueError(
                    f"Invalid week_start_day: {body.week_start_day}. "
                    f"Must be one of {VALID_WEEK_START}"
                )
            pref.week_start_day = day
        if body.notification_enabled is not None:
            pref.notification_enabled = body.notification_enabled
        if body.quick_add_reminder_enabled is not None:
            pref.quick_add_reminder_enabled = body.quick_add_reminder_enabled
        if body.daily_summary_enabled is not None:
            pref.daily_summary_enabled = body.daily_summary_enabled
        if body.privacy_mode_enabled is not None:
            pref.privacy_mode_enabled = body.privacy_mode_enabled
        if body.preferred_summary_time is not None:
            pref.preferred_summary_time = body.preferred_summary_time
        if "preferred_summary_time" in body.model_fields_set and body.preferred_summary_time is None:
            pref.preferred_summary_time = None
        if body.default_account_id is not None:
            pref.default_account_id = body.default_account_id
        if "default_account_id" in body.model_fields_set and body.default_account_id is None:
            pref.default_account_id = None
        if body.default_currency_code is not None:
            pref.default_currency_code = body.default_currency_code
        if body.timezone_name is not None:
            pref.timezone_name = body.timezone_name

        pref.updated_at = datetime.now(timezone.utc)
        return pref

    def to_schema(self, pref: PersonalUserPreferences) -> PersonalUserPreferencesSchema:
        return PersonalUserPreferencesSchema.model_validate(pref)

    def to_bootstrap_dict(self, pref: PersonalUserPreferences) -> dict:
        summary_time: time | None = pref.preferred_summary_time
        return {
            "preference_id": str(pref.preference_id),
            "user_id": str(pref.user_id),
            "week_start_day": pref.week_start_day or "MONDAY",
            "notification_enabled": pref.notification_enabled,
            "quick_add_reminder_enabled": pref.quick_add_reminder_enabled,
            "daily_summary_enabled": pref.daily_summary_enabled,
            "privacy_mode_enabled": pref.privacy_mode_enabled,
            "preferred_summary_time": (
                summary_time.isoformat() if summary_time is not None else None
            ),
            "default_account_id": (
                str(pref.default_account_id) if pref.default_account_id else None
            ),
        }


def compute_week_bounds(
    now: datetime,
    week_start_day: str | None = "MONDAY",
) -> tuple[datetime, datetime]:
    """Return (week_start, last_week_start) at midnight of ``now``'s date."""
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day = (week_start_day or "MONDAY").upper()
    if day == "SUNDAY":
        days_since = (today_start.weekday() + 1) % 7
    else:
        days_since = today_start.weekday()
    week_start = today_start - timedelta(days=days_since)
    last_week_start = week_start - timedelta(days=7)
    return week_start, last_week_start
