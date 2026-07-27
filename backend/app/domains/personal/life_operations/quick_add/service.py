"""Life Operations quick-add orchestration."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, StateTransitionError, ValidationError
from app.domains.moments.models import MomentModel
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.life_operations.quick_add.constants import EVENT_TO_TAB
from app.domains.personal.life_operations.quick_add.events import QUICK_ADD_CREATED
from app.domains.personal.life_operations.quick_add.handlers.base import QuickAddContext
from app.domains.personal.life_operations.quick_add.handlers.registry import dispatch
from app.domains.personal.life_operations.quick_add.handlers.timeline import (
    insert_timeline_row,
)
from app.domains.personal.life_operations.quick_add.options_builder import (
    LifeOpsQuickAddOptionsBuilder,
)
from app.domains.personal.life_operations.quick_add.validators.expense import (
    validate_expense_payload,
)
from app.domains.personal.accounts_service import PersonalAccountsService
from app.domains.personal.models import PersonalMoments, PersonalQuickAddEvents
from app.domains.personal.personal_moment_sync import ensure_personal_moment
from app.domains.preferences.service import UserPreferenceService
from app.domains.reference_data.catalog import get_reference_catalog
from app.shared.events.base import DomainEvent
from app.shared.events.publisher import get_event_publisher

_ACTIVE = {"ACTIVE"}
_LIFE_OPS = "LIFE_OPERATIONS"


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class LifeOpsQuickAddService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._options_builder = LifeOpsQuickAddOptionsBuilder()

    async def options(
        self,
        user_id: UUID,
        moments: list[MomentModel],
    ) -> dict[str, Any]:
        pref_service = UserPreferenceService(self.session)
        pref = await pref_service.get_or_create(user_id)
        accounts = await self._list_accounts(user_id)
        entries_today = await self._entries_today_count(user_id)
        catalog = get_reference_catalog()
        return self._options_builder.build(
            user_id=user_id,
            moments=moments,
            accounts=accounts,
            entries_today_count=entries_today,
            default_currency_code=pref.default_currency_code,
            catalog=catalog,
        )

    async def _existing_by_client_request_id(
        self, user_id: UUID, client_request_id: UUID
    ) -> PersonalQuickAddEvents | None:
        result = await self.session.execute(
            select(PersonalQuickAddEvents).where(
                PersonalQuickAddEvents.user_id == user_id,
                PersonalQuickAddEvents.client_request_id == client_request_id,
                PersonalQuickAddEvents.is_voided.is_(False),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _response_for_event(parent: PersonalQuickAddEvents) -> dict[str, Any]:
        payload = parent.raw_payload or {}
        event_title = str(
            payload.get("event_title")
            or parent.event_type.replace("_", " ").title()
        )
        return {
            "quick_add_event_id": str(parent.quick_add_event_id),
            "event_type": parent.event_type,
            "event_title": event_title,
            "moment_id": str(parent.moment_id),
            "idempotent_replay": True,
        }

    async def submit(
        self,
        user_id: UUID,
        shared_moment: MomentModel,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        raw_client_request_id = body.get("client_request_id")
        if raw_client_request_id:
            try:
                client_request_id = UUID(str(raw_client_request_id))
            except ValueError as exc:
                raise ValidationError("Invalid client_request_id") from exc
            existing = await self._existing_by_client_request_id(
                user_id, client_request_id
            )
            if existing is not None:
                return self._response_for_event(existing)

        if shared_moment.status not in _ACTIVE:
            raise StateTransitionError(
                "Quick add is only allowed on ACTIVE moments"
            )

        event_type = str(body.get("event_type") or "").upper()
        if event_type not in EVENT_TO_TAB:
            raise ValidationError(f"Unsupported event type: {event_type}")

        if event_type == "EXPENSE":
            validated = await validate_expense_payload(
                body, session=self.session, user_id=user_id
            )
            expense = dict(body.get("expense") or {})
            expense.update(validated)
            body = jsonable_encoder({**body, "expense": expense})

        moment_type_code = normalize_moment_type_code(shared_moment.moment_type or "")
        await ensure_personal_moment(self.session, shared_moment)
        moment_id = shared_moment.id
        now = _now()
        tab_code = EVENT_TO_TAB[event_type]
        event_title = str(body.get("event_title") or event_type.replace("_", " ").title())

        parsed_client_request_id: UUID | None = None
        if raw_client_request_id:
            parsed_client_request_id = UUID(str(raw_client_request_id))

        parent = PersonalQuickAddEvents(
            moment_id=moment_id,
            user_id=user_id,
            moment_type_code=moment_type_code,
            quick_add_tab_code=tab_code,
            event_type=event_type,
            event_occurred_at=now,
            raw_payload=body,
            client_request_id=parsed_client_request_id,
        )
        self.session.add(parent)
        await self.session.flush()

        ctx = QuickAddContext(
            session=self.session,
            user_id=user_id,
            moment_id=moment_id,
            moment_type_code=moment_type_code,
            quick_add_event_id=parent.quick_add_event_id,
            event_type=event_type,
            event_title=event_title,
            body=body,
            occurred_at=now,
        )
        timeline_draft = await dispatch(ctx)
        await insert_timeline_row(ctx, timeline_draft)

        result = await self.session.execute(
            select(PersonalMoments).where(PersonalMoments.moment_id == moment_id)
        )
        personal_moment = result.scalar_one_or_none()
        if personal_moment is not None:
            personal_moment.last_activity_at = now
            personal_moment.updated_at = now

        await self.session.commit()
        await self.session.refresh(parent)

        await get_event_publisher().publish(
            DomainEvent(
                name=QUICK_ADD_CREATED,
                user_id=user_id,
                moment_id=moment_id,
                context="MY_MONEY",
                moment_type=moment_type_code,
                payload={
                    "session": self.session,
                    "event_type": event_type,
                    "quick_add_event_id": str(parent.quick_add_event_id),
                },
            )
        )

        return {
            "quick_add_event_id": str(parent.quick_add_event_id),
            "event_type": event_type,
            "event_title": event_title,
            "moment_id": str(moment_id),
        }

    async def list_accounts(self, user_id: UUID) -> list[dict[str, Any]]:
        return await PersonalAccountsService(self.session).list_accounts(user_id)

    async def create_account(
        self,
        user_id: UUID,
        *,
        account_name: str,
        account_type: str,
        currency_code: str = "INR",
        opening_balance: str | None = None,
        opening_balance_minor: int | None = None,
        is_primary: bool = False,
    ) -> dict[str, Any]:
        return await PersonalAccountsService(self.session).create_account(
            user_id,
            account_name=account_name,
            account_type=account_type,
            currency_code=currency_code,
            opening_balance=opening_balance,
            opening_balance_minor=opening_balance_minor,
            is_primary=is_primary,
        )

    async def _list_accounts(self, user_id: UUID) -> list[dict[str, Any]]:
        return await self.list_accounts(user_id)

    async def _entries_today_count(self, user_id: UUID) -> int:
        today = date.today()
        result = await self.session.execute(
            select(func.count())
            .select_from(PersonalQuickAddEvents)
            .where(
                PersonalQuickAddEvents.user_id == user_id,
                PersonalQuickAddEvents.moment_type_code == _LIFE_OPS,
                func.date(PersonalQuickAddEvents.event_occurred_at) == today,
                PersonalQuickAddEvents.is_voided.is_(False),
            )
        )
        return int(result.scalar_one() or 0)
