"""Load and patch personal quick-add events for activity edit flows."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.domains.personal.life_operations.quick_add.events import (
    QUICK_ADD_DELETED,
    QUICK_ADD_UPDATED,
)
from app.domains.personal.life_operations.quick_add.handlers.mappings import (
    money_direction,
    pressure_score,
)
from app.domains.personal.life_operations.quick_add.validators.expense import (
    validate_expense_payload,
)
from app.domains.personal.models import (
    PersonalActivityTimeline,
    PersonalEventEdits,
    PersonalLifeMoodEvents,
    PersonalLifeRecoveryEvents,
    PersonalMoneyEvents,
    PersonalQuickAddEvents,
)
from app.domains.personal.quick_add.money import amount_minor_from_data
from app.domains.reference_data.catalog import ReferenceCatalog, get_reference_catalog
from app.shared.events.base import DomainEvent
from app.shared.events.publisher import get_event_publisher

_MONEY_EVENT_TYPES = frozenset(
    {
        "EXPENSE",
        "CONTRIBUTION",
        "SAVINGS",
        "INVESTMENT",
        "INCOME",
        "LIFESTYLE_EXPENSE",
        "RELATIONSHIP_INVESTMENT",
        "SHARED_EXPERIENCE_COST",
    }
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PersonalQuickAddEditService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def detail(self, user_id: UUID, event_id: str) -> dict[str, Any]:
        event = await self._resolve_event(user_id, event_id)
        return await self._build_detail(event)

    async def patch(
        self, user_id: UUID, event_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        event = await self._resolve_event(user_id, event_id)
        before = deepcopy(event.raw_payload or {})
        payload = deepcopy(before)

        if body.get("event_title") is not None:
            payload["event_title"] = body["event_title"]
        if "event_summary" in body:
            payload["event_summary"] = body.get("event_summary")

        for key in (
            "recovery",
            "reflection",
            "rhythm",
            "expense",
            "commitment",
            "future_building",
        ):
            if key in body and body[key] is not None:
                payload[key] = body[key]

        event_type = event.event_type.upper()
        expense_body = body.get("expense")
        if expense_body is not None:
            if event_type == "EXPENSE":
                validated = await validate_expense_payload(
                    {"expense": expense_body},
                    session=self.session,
                    user_id=user_id,
                )
                merged = dict(expense_body)
                merged.update(validated or {})
                payload["expense"] = jsonable_encoder(merged)
                title_from_expense = str(
                    merged.get("title") or merged.get("description") or ""
                ).strip()
                if title_from_expense and body.get("event_title") is None:
                    payload["event_title"] = title_from_expense[:150]
                await self._sync_money_event(event, merged, event_type)
            elif event_type in _MONEY_EVENT_TYPES:
                payload["expense"] = jsonable_encoder(expense_body)
                await self._sync_money_event(event, expense_body, event_type)

        if event_type == "REFLECTION" and body.get("reflection"):
            await self._sync_mood(event, body["reflection"])
        elif event_type == "RECOVERY" and body.get("recovery"):
            await self._sync_recovery(event, body["recovery"])

        event.raw_payload = payload
        event.updated_at = _now()
        await self._sync_timeline(event, payload)

        self.session.add(
            PersonalEventEdits(
                quick_add_event_id=event.quick_add_event_id,
                moment_id=event.moment_id,
                user_id=user_id,
                edited_table_name="personal_quick_add_events",
                edited_record_id=event.quick_add_event_id,
                before_payload=before,
                after_payload=payload,
            )
        )

        await self.session.commit()
        await self.session.refresh(event)

        await get_event_publisher().publish(
            DomainEvent(
                name=QUICK_ADD_UPDATED,
                user_id=user_id,
                moment_id=event.moment_id,
                context="MY_MONEY",
                moment_type=event.moment_type_code,
                payload={
                    "session": self.session,
                    "event_type": event.event_type,
                    "quick_add_event_id": str(event.quick_add_event_id),
                },
            )
        )

        event_title = str(
            payload.get("event_title") or event.event_type.replace("_", " ").title()
        )
        return {
            "quick_add_event_id": str(event.quick_add_event_id),
            "event_type": event.event_type,
            "event_title": event_title,
            "moment_id": str(event.moment_id),
        }

    async def delete(self, user_id: UUID, event_id: str) -> dict[str, Any]:
        try:
            event = await self._resolve_event(user_id, event_id)
        except NotFoundError:
            return {"deleted": False, "already_deleted": True}

        now = _now()
        event.is_voided = True
        event.updated_at = now

        tl_result = await self.session.execute(
            select(PersonalActivityTimeline).where(
                PersonalActivityTimeline.quick_add_event_id
                == event.quick_add_event_id,
                PersonalActivityTimeline.is_voided.is_(False),
            )
        )
        for row in tl_result.scalars().all():
            row.is_voided = True
            row.updated_at = now

        money_result = await self.session.execute(
            select(PersonalMoneyEvents).where(
                PersonalMoneyEvents.quick_add_event_id
                == event.quick_add_event_id,
                PersonalMoneyEvents.is_voided.is_(False),
            )
        )
        for row in money_result.scalars().all():
            row.is_voided = True
            row.updated_at = now

        await self.session.commit()

        await get_event_publisher().publish(
            DomainEvent(
                name=QUICK_ADD_DELETED,
                user_id=user_id,
                moment_id=event.moment_id,
                context="MY_MONEY",
                moment_type=event.moment_type_code,
                payload={
                    "session": self.session,
                    "event_type": event.event_type,
                    "quick_add_event_id": str(event.quick_add_event_id),
                },
            )
        )

        return {
            "deleted": True,
            "quick_add_event_id": str(event.quick_add_event_id),
            "moment_id": str(event.moment_id),
        }

    async def _resolve_event(
        self, user_id: UUID, event_id: str
    ) -> PersonalQuickAddEvents:
        try:
            parsed = UUID(str(event_id))
        except ValueError as exc:
            raise ValidationError("Invalid event_id") from exc

        result = await self.session.execute(
            select(PersonalQuickAddEvents).where(
                PersonalQuickAddEvents.quick_add_event_id == parsed,
                PersonalQuickAddEvents.user_id == user_id,
                PersonalQuickAddEvents.is_voided.is_(False),
            )
        )
        event = result.scalar_one_or_none()
        if event is not None:
            return event

        tl_result = await self.session.execute(
            select(PersonalActivityTimeline).where(
                PersonalActivityTimeline.timeline_id == parsed,
                PersonalActivityTimeline.user_id == user_id,
                PersonalActivityTimeline.is_voided.is_(False),
            )
        )
        timeline = tl_result.scalar_one_or_none()
        if timeline is None:
            raise NotFoundError("Quick-add event not found")

        result = await self.session.execute(
            select(PersonalQuickAddEvents).where(
                PersonalQuickAddEvents.quick_add_event_id
                == timeline.quick_add_event_id,
                PersonalQuickAddEvents.user_id == user_id,
                PersonalQuickAddEvents.is_voided.is_(False),
            )
        )
        event = result.scalar_one_or_none()
        if event is None:
            raise NotFoundError("Quick-add event not found")
        return event

    async def _build_detail(self, event: PersonalQuickAddEvents) -> dict[str, Any]:
        payload = dict(event.raw_payload or {})
        catalog = get_reference_catalog()
        event_title = str(
            payload.get("event_title") or event.event_type.replace("_", " ").title()
        )

        detail: dict[str, Any] = {
            "quick_add_event_id": str(event.quick_add_event_id),
            "moment_id": str(event.moment_id),
            "event_type": event.event_type,
            "event_title": event_title,
            "event_summary": payload.get("event_summary"),
            "captured_at": event.event_occurred_at.isoformat(),
        }

        for key in (
            "recovery",
            "reflection",
            "rhythm",
            "expense",
            "commitment",
            "future_building",
        ):
            if key in payload and payload[key] is not None:
                detail[key] = payload[key]

        money_result = await self.session.execute(
            select(PersonalMoneyEvents).where(
                PersonalMoneyEvents.quick_add_event_id == event.quick_add_event_id,
                PersonalMoneyEvents.is_voided.is_(False),
            )
        )
        money = money_result.scalar_one_or_none()
        if money is not None:
            detail["expense"] = self._expense_block_from_money(
                money, catalog, existing=payload.get("expense")
            )

        if "reflection" not in detail:
            mood_result = await self.session.execute(
                select(PersonalLifeMoodEvents).where(
                    PersonalLifeMoodEvents.quick_add_event_id
                    == event.quick_add_event_id
                )
            )
            mood = mood_result.scalar_one_or_none()
            if mood is not None:
                detail["reflection"] = {
                    "feeling_state": mood.mood_state,
                    "reflection_note": mood.reflection_text,
                }

        if "recovery" not in detail:
            rec_result = await self.session.execute(
                select(PersonalLifeRecoveryEvents).where(
                    PersonalLifeRecoveryEvents.quick_add_event_id
                    == event.quick_add_event_id
                )
            )
            rec = rec_result.scalar_one_or_none()
            if rec is not None:
                detail["recovery"] = {
                    "recovery_type": rec.recovery_type,
                    "recovery_intensity": rec.energy_impact,
                    "notes": rec.note,
                }

        return detail

    @staticmethod
    def _expense_block_from_money(
        money: PersonalMoneyEvents,
        catalog: ReferenceCatalog,
        *,
        existing: Any,
    ) -> dict[str, Any]:
        category_label = catalog.label_for("expense_categories", money.category_code)
        major = catalog.major_from_minor(
            int(money.amount_minor or 0), money.currency_code
        )
        block: dict[str, Any] = {
            "transaction_type": money.money_event_type,
            "amount_minor": int(money.amount_minor or 0),
            "amount": str(major),
            "currency_code": money.currency_code,
            "account_id": str(money.account_id) if money.account_id else "",
            "category_code": money.category_code,
            "subcategory_code": getattr(money, "subcategory_code", None),
            "category_name": category_label,
            "pressure_impact": money.impact_label,
            "title": getattr(money, "title", None) or "",
        }
        if isinstance(existing, dict):
            return {**existing, **{k: v for k, v in block.items() if v is not None}}
        return block

    async def _sync_money_event(
        self,
        event: PersonalQuickAddEvents,
        expense: dict[str, Any],
        event_type: str,
    ) -> None:
        catalog = get_reference_catalog()
        currency = str(expense.get("currency_code") or "INR").upper()
        amount_minor = amount_minor_from_data(
            expense, catalog=catalog, currency_code=currency
        )
        amount = catalog.major_from_minor(amount_minor, currency)
        category_code = str(expense.get("category_code") or "OTHER")
        if expense.get("category_name"):
            resolved = catalog.resolve_category_code(
                "expense_categories",
                None,
                expense.get("category_name"),
            )
            if resolved:
                category_code = resolved

        from app.domains.reference_data.expense_taxonomy import validate_expense_category_pair

        raw_sub = expense.get("subcategory_code")
        if "subcategory_code" in expense and expense.get("subcategory_code") is None:
            raw_sub = None
        cat, sub = validate_expense_category_pair(
            category_code,
            None if raw_sub in ("", None) else str(raw_sub),
            catalog=catalog,
        )
        category_code = cat or category_code

        account_id: UUID | None = None
        raw_account = expense.get("account_id")
        if raw_account:
            try:
                account_id = UUID(str(raw_account))
            except ValueError:
                account_id = None

        money_type = str(
            expense.get("transaction_type") or event_type or "EXPENSE"
        ).upper()
        result = await self.session.execute(
            select(PersonalMoneyEvents).where(
                PersonalMoneyEvents.quick_add_event_id == event.quick_add_event_id,
                PersonalMoneyEvents.is_voided.is_(False),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return

        row.amount = amount
        row.amount_minor = amount_minor
        row.currency_code = currency
        row.category_code = category_code[:80]
        row.subcategory_code = sub[:80] if sub else None
        row.account_id = account_id
        row.money_event_type = money_type
        row.direction = money_direction(money_type)
        row.impact_label = (
            str(expense.get("pressure_impact") or row.impact_label or "")[:80] or None
        )
        row.financial_pressure_score = pressure_score(
            str(expense.get("pressure_impact") or "")
        )
        from app.domains.personal.life_operations.quick_add.handlers.expense import (
            resolve_money_event_title,
        )

        if expense.get("title") is not None or expense.get("description") is not None:
            row.title = resolve_money_event_title(
                expense,
                event_title=None,
                category_label=catalog.label_for("expense_categories", category_code),
            )
        row.updated_at = _now()

    async def _sync_mood(
        self, event: PersonalQuickAddEvents, reflection: dict[str, Any]
    ) -> None:
        result = await self.session.execute(
            select(PersonalLifeMoodEvents).where(
                PersonalLifeMoodEvents.quick_add_event_id == event.quick_add_event_id
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return
        if reflection.get("feeling_state") is not None:
            row.mood_state = str(reflection["feeling_state"])[:50]
        if "reflection_note" in reflection:
            row.reflection_text = str(reflection.get("reflection_note") or "").strip() or None

        # Keep timeline denorm in sync so pulse/list mood_label stays accurate.
        timeline_result = await self.session.execute(
            select(PersonalActivityTimeline).where(
                PersonalActivityTimeline.quick_add_event_id
                == event.quick_add_event_id,
                PersonalActivityTimeline.is_voided.is_(False),
            )
        )
        timeline = timeline_result.scalar_one_or_none()
        if timeline is None:
            return
        labels = dict(timeline.impact_labels_json or {})
        if reflection.get("feeling_state") is not None:
            mood_state = str(reflection["feeling_state"])[:50]
            labels["mood_state"] = mood_state
            timeline.display_subtitle = mood_state.replace("_", " ").title()[:250]
        timeline.impact_labels_json = labels
        timeline.updated_at = _now()

    async def _sync_recovery(
        self, event: PersonalQuickAddEvents, recovery: dict[str, Any]
    ) -> None:
        result = await self.session.execute(
            select(PersonalLifeRecoveryEvents).where(
                PersonalLifeRecoveryEvents.quick_add_event_id
                == event.quick_add_event_id
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return
        if recovery.get("recovery_type") is not None:
            row.recovery_type = str(recovery["recovery_type"])[:100]
        if recovery.get("recovery_intensity") is not None:
            row.energy_impact = str(recovery["recovery_intensity"])[:50]
        if "notes" in recovery:
            row.note = str(recovery.get("notes") or "").strip() or None

    async def _sync_timeline(
        self, event: PersonalQuickAddEvents, payload: dict[str, Any]
    ) -> None:
        result = await self.session.execute(
            select(PersonalActivityTimeline).where(
                PersonalActivityTimeline.quick_add_event_id
                == event.quick_add_event_id,
                PersonalActivityTimeline.is_voided.is_(False),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return

        title = str(payload.get("event_title") or row.display_title)[:150]
        row.display_title = title
        summary = payload.get("event_summary")
        if summary:
            row.display_subtitle = str(summary)[:250]
        expense = payload.get("expense")
        if isinstance(expense, dict):
            catalog = get_reference_catalog()
            currency = str(expense.get("currency_code") or "INR").upper()
            amount_minor = amount_minor_from_data(
                expense, catalog=catalog, currency_code=currency
            )
            if amount_minor > 0:
                row.display_amount = Decimal(
                    str(catalog.major_from_minor(amount_minor, currency))
                )
        row.updated_at = _now()
