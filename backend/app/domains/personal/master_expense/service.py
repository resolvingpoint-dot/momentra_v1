"""Master Expense Orchestrator — fan-out to Life Ops, Lifestyle, Relationships."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import StateTransitionError, ValidationError
from app.domains.moments.models import MomentModel
from app.domains.personal.accounts_service import PersonalAccountsService
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.life_operations.quick_add.constants import EVENT_TO_TAB as LO_EVENT_TO_TAB
from app.domains.personal.life_operations.quick_add.events import QUICK_ADD_CREATED
from app.domains.personal.life_operations.quick_add.handlers.base import QuickAddContext
from app.domains.personal.life_operations.quick_add.handlers.registry import (
    dispatch as dispatch_life_ops,
)
from app.domains.personal.life_operations.quick_add.handlers.timeline import insert_timeline_row
from app.domains.personal.life_operations.quick_add.validators.expense import (
    validate_expense_payload,
)
from app.domains.personal.lifestyle.quick_add.constants import EVENT_TO_TAB as LS_EVENT_TO_TAB
from app.domains.personal.lifestyle.quick_add.handlers.registry import (
    dispatch as dispatch_lifestyle,
)
from app.domains.personal.master_expense.events import MASTER_EXPENSE_CREATED
from app.domains.personal.master_expense.mapper import (
    build_life_operations_body,
    build_lifestyle_body,
    build_relationships_body,
    legacy_event_refs,
    normalize_legacy_body,
    parse_occurred_at,
)
from app.domains.personal.master_expense.models import PersonalMasterExpenses
from app.domains.personal.master_expense.repository import MasterExpenseRepository
from app.domains.personal.master_expense.schemas import (
    MASTER_EXPENSE_CONTEXT_REASONS,
    MASTER_EXPENSE_FEELINGS,
    MASTER_EXPENSE_RELATIONSHIP_IMPACTS,
    MASTER_EXPENSE_SCALE_LEVELS,
    MASTER_EXPENSE_SHARED_WITH,
    MasterExpenseContextInput,
    MasterExpenseCreateRequest,
    MasterExpenseCreateResponse,
    MasterExpenseCreatedEvents,
    MasterExpenseExperienceInput,
    MasterExpenseSharedInput,
    build_impact_preview,
)
from app.domains.personal.models import PersonalMoments, PersonalQuickAddEvents
from app.domains.personal.personal_moment_sync import ensure_personal_moment
from app.domains.personal.relationships.quick_add.constants import (
    EVENT_TO_TAB as RS_EVENT_TO_TAB,
)
from app.domains.personal.relationships.quick_add.handlers.registry import (
    dispatch as dispatch_relationships,
)
from app.domains.projections.invalidation import invalidate_for_master_expense
from app.domains.reference_data.catalog import get_reference_catalog
from app.shared.events.base import DomainEvent
from app.shared.events.publisher import get_event_publisher

_ACTIVE = {"ACTIVE"}
_REQUIRED_TEMPLATES = ("LIFE_OPERATIONS", "LIFESTYLE")


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class MasterExpenseService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = MasterExpenseRepository(session)

    async def options(
        self,
        user_id: UUID,
        moments: list[MomentModel],
    ) -> dict[str, Any]:
        catalog = get_reference_catalog()
        accounts = await PersonalAccountsService(self.session).list_accounts(user_id)
        categories = [
            {
                "category_id": item["code"],
                "category_name": item["label"],
                "category_group": item.get("group") or "General",
                "children": [
                    {
                        "category_id": child["code"],
                        "category_name": child["label"],
                    }
                    for child in (item.get("children") or [])
                    if child.get("is_active", True)
                ],
            }
            for item in catalog.get("expense_categories", active_only=True)
            if not item.get("parent_code")
        ]
        latest = self._latest_by_code(moments)
        return {
            "accounts": accounts,
            "categories": categories,
            "feelings": MASTER_EXPENSE_FEELINGS,
            "scale_levels": MASTER_EXPENSE_SCALE_LEVELS,
            "shared_with": MASTER_EXPENSE_SHARED_WITH,
            "relationship_impacts": MASTER_EXPENSE_RELATIONSHIP_IMPACTS,
            "context_reasons": MASTER_EXPENSE_CONTEXT_REASONS,
            "life_operations_moment_id": (
                str(latest["LIFE_OPERATIONS"].id) if "LIFE_OPERATIONS" in latest else None
            ),
            "lifestyle_moment_id": (
                str(latest["LIFESTYLE"].id) if "LIFESTYLE" in latest else None
            ),
            "emotional_security_moment_id": (
                str(latest["RELATIONSHIPS"].id) if "RELATIONSHIPS" in latest else None
            ),
        }

    @staticmethod
    def _latest_by_code(moments: list[MomentModel]) -> dict[str, MomentModel]:
        best: dict[str, MomentModel] = {}
        for moment in moments:
            code = normalize_moment_type_code(moment.moment_type or "")
            if not code:
                continue
            existing = best.get(code)
            if existing is None:
                best[code] = moment
                continue
            if existing.status != "ACTIVE" and moment.status == "ACTIVE":
                best[code] = moment
        return best

    async def _response_from_row(
        self, row: PersonalMasterExpenses, *, idempotent_replay: bool
    ) -> dict[str, Any]:
        moment_ids = await self._moment_ids_for_row(row)
        events = legacy_event_refs(
            life_ops_id=row.life_operations_event_id,
            lifestyle_id=row.lifestyle_event_id,
            relationships_id=row.relationships_event_id,
            life_ops_moment_id=moment_ids["life_operations"],
            lifestyle_moment_id=moment_ids["lifestyle"],
            relationships_moment_id=moment_ids.get("relationships"),
        )
        created = MasterExpenseCreatedEvents(
            life_operations=(
                str(row.life_operations_event_id) if row.life_operations_event_id else None
            ),
            lifestyle=str(row.lifestyle_event_id) if row.lifestyle_event_id else None,
            relationships=(
                str(row.relationships_event_id) if row.relationships_event_id else None
            ),
        )
        response = MasterExpenseCreateResponse(
            id=str(row.master_expense_id),
            master_expense_id=str(row.master_expense_id),
            created_events=created,
            impact_preview=build_impact_preview(
                life_operations=row.life_operations_event_id is not None,
                lifestyle=row.lifestyle_event_id is not None,
                relationships=row.relationships_event_id is not None,
            ),
            idempotent_replay=idempotent_replay,
            master_expense_group_id=str(row.master_expense_id),
            transaction_id=str(row.life_operations_event_id or row.master_expense_id),
            account_id=str(row.account_id),
            amount_minor=int(row.amount_minor),
            events=events,
        )
        return response.model_dump(mode="json")

    async def create(self, user_id: UUID, body: dict[str, Any]) -> dict[str, Any]:
        normalized = normalize_legacy_body(body)
        raw_client_request_id = normalized.get("client_request_id")
        parsed_client_request_id: UUID | None = None
        if raw_client_request_id:
            try:
                parsed_client_request_id = UUID(str(raw_client_request_id))
            except ValueError as exc:
                raise ValidationError("Invalid client_request_id") from exc
            existing = await self._repo.get_by_client_request_id(
                user_id, parsed_client_request_id
            )
            if existing is not None:
                return await self._response_from_row(existing, idempotent_replay=True)

        shared_input = self._parse_shared(normalized)

        from app.domains.preferences.service import UserPreferenceService

        pref = await UserPreferenceService(self.session).get_or_create(user_id)
        currency_code = str(normalized.get("currency_code") or pref.default_currency_code)

        validated_expense = await validate_expense_payload(
            {
                "expense": {
                    "amount_minor": normalized.get("amount_minor"),
                    "amount": normalized.get("amount"),
                    "currency_code": currency_code,
                    "account_id": normalized.get("account_id"),
                    "category_code": normalized.get("category_code"),
                    "category_name": normalized.get("category_name"),
                    "subcategory_code": normalized.get("subcategory_code"),
                }
            },
            session=self.session,
            user_id=user_id,
        )

        from app.domains.reference_data.expense_taxonomy import validate_expense_category_pair

        cat, sub = validate_expense_category_pair(
            validated_expense.get("category_code"),
            normalized.get("subcategory_code"),
        )
        validated_expense["category_code"] = cat or validated_expense.get("category_code")
        validated_expense["subcategory_code"] = sub

        req = MasterExpenseCreateRequest(
            client_request_id=str(parsed_client_request_id) if parsed_client_request_id else None,
            title=str(normalized.get("title") or "").strip(),
            amount_minor=int(validated_expense["amount_minor"]),
            currency_code=str(validated_expense["currency_code"]),
            account_id=str(validated_expense["account_id"]),
            category_code=str(validated_expense["category_code"]),
            subcategory_code=sub,
            occurred_at=normalized.get("occurred_at"),
            experience=self._parse_experience(normalized.get("experience")),
            shared=shared_input,
            context=self._parse_context(normalized.get("context")),
            notes=(str(normalized.get("notes")).strip()[:200] if normalized.get("notes") else None),
        )

        if not req.title:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="title is required",
            )

        moments = await self._load_active_moments(user_id)
        latest = self._latest_by_code(moments)
        for code in _REQUIRED_TEMPLATES:
            moment = latest.get(code)
            if moment is None or moment.status not in _ACTIVE:
                raise StateTransitionError(
                    f"Active {code.replace('_', ' ').title()} moment is required for Master Expense"
                )

        life_ops_moment = latest["LIFE_OPERATIONS"]
        lifestyle_moment = latest["LIFESTYLE"]
        relationships_moment = latest.get("RELATIONSHIPS")
        occurred_at = parse_occurred_at(req.occurred_at, fallback=_now())
        master_expense_id = uuid4()

        life_ops_body = build_life_operations_body(
            req,
            master_expense_id=master_expense_id,
            validated_expense=validated_expense,
        )
        lifestyle_body = build_lifestyle_body(
            req,
            master_expense_id=master_expense_id,
            validated_expense=validated_expense,
        )

        life_ops_event = await self._create_quick_add_event(
            user_id=user_id,
            moment=life_ops_moment,
            event_type="EXPENSE",
            tab_map=LO_EVENT_TO_TAB,
            body=life_ops_body,
            occurred_at=occurred_at,
            dispatch_fn=dispatch_life_ops,
        )
        lifestyle_event = await self._create_quick_add_event(
            user_id=user_id,
            moment=lifestyle_moment,
            event_type="EXPERIENCE",
            tab_map=LS_EVENT_TO_TAB,
            body=lifestyle_body,
            occurred_at=occurred_at,
            dispatch_fn=dispatch_lifestyle,
        )

        relationships_event: PersonalQuickAddEvents | None = None
        if shared_input.is_shared and relationships_moment is not None:
            if relationships_moment.status in _ACTIVE:
                relationships_body = build_relationships_body(
                    req,
                    master_expense_id=master_expense_id,
                    validated_expense=validated_expense,
                    shared=shared_input,
                )
                relationships_event = await self._create_quick_add_event(
                    user_id=user_id,
                    moment=relationships_moment,
                    event_type="SHARED_EXPERIENCE",
                    tab_map=RS_EVENT_TO_TAB,
                    body=relationships_body,
                    occurred_at=occurred_at,
                    dispatch_fn=dispatch_relationships,
                )

        master_row = PersonalMasterExpenses(
            master_expense_id=master_expense_id,
            user_id=user_id,
            title=req.title,
            amount_minor=int(validated_expense["amount_minor"]),
            currency_code=str(validated_expense["currency_code"]),
            account_id=UUID(str(validated_expense["account_id"])),
            category_code=str(validated_expense["category_code"]),
            subcategory_code=req.subcategory_code,
            occurred_at=occurred_at,
            feeling=req.experience.feeling if req.experience else None,
            meaningfulness=req.experience.meaningfulness if req.experience else None,
            memorability=req.experience.memorability if req.experience else None,
            is_shared=shared_input.is_shared,
            shared_with=shared_input.shared_with,
            relationship_impact=shared_input.relationship_impact,
            context_reason=req.context.reason if req.context else None,
            notes=req.notes,
            client_request_id=parsed_client_request_id,
            life_operations_event_id=life_ops_event.quick_add_event_id,
            lifestyle_event_id=lifestyle_event.quick_add_event_id,
            relationships_event_id=(
                relationships_event.quick_add_event_id if relationships_event else None
            ),
        )
        self._repo.add(master_row)
        await self.session.commit()
        await self.session.refresh(master_row)

        await self._publish_events(
            user_id=user_id,
            master_row=master_row,
            life_ops_event=life_ops_event,
            lifestyle_event=lifestyle_event,
            relationships_event=relationships_event,
        )
        await invalidate_for_master_expense(
            user_id,
            include_relationships=relationships_event is not None,
        )

        return await self._response_from_row(master_row, idempotent_replay=False)

    async def _moment_ids_for_row(
        self, row: PersonalMasterExpenses
    ) -> dict[str, UUID]:
        ids: dict[str, UUID] = {}
        event_ids = [
            ("life_operations", row.life_operations_event_id),
            ("lifestyle", row.lifestyle_event_id),
            ("relationships", row.relationships_event_id),
        ]
        for key, event_id in event_ids:
            if event_id is None:
                continue
            result = await self.session.execute(
                select(PersonalQuickAddEvents.moment_id).where(
                    PersonalQuickAddEvents.quick_add_event_id == event_id
                )
            )
            moment_id = result.scalar_one_or_none()
            if moment_id is not None:
                ids[key] = moment_id
        if "life_operations" not in ids:
            ids["life_operations"] = row.master_expense_id
        if "lifestyle" not in ids:
            ids["lifestyle"] = row.master_expense_id
        return ids

    async def _load_active_moments(self, user_id: UUID) -> list[MomentModel]:
        from app.domains.moments.repository import MomentRepository
        from app.domains.personal.catalog import PERSONAL_CONTEXT

        repo = MomentRepository(self.session)
        moments = await repo.list_by_context(user_id, PERSONAL_CONTEXT)
        return [m for m in moments if m.status in _ACTIVE | {"DRAFT", "SETUP"}]

    async def _create_quick_add_event(
        self,
        *,
        user_id: UUID,
        moment: MomentModel,
        event_type: str,
        tab_map: dict[str, str],
        body: dict[str, Any],
        occurred_at: datetime,
        dispatch_fn: Any,
    ) -> PersonalQuickAddEvents:
        moment_type_code = normalize_moment_type_code(moment.moment_type or "")
        await ensure_personal_moment(self.session, moment)
        tab_code = tab_map[event_type]
        event_title = str(body.get("event_title") or event_type.replace("_", " ").title())
        encoded_body = jsonable_encoder(body)

        parent = PersonalQuickAddEvents(
            moment_id=moment.id,
            user_id=user_id,
            moment_type_code=moment_type_code,
            quick_add_tab_code=tab_code,
            event_type=event_type,
            event_occurred_at=occurred_at,
            raw_payload=encoded_body,
            client_request_id=None,
        )
        self.session.add(parent)
        await self.session.flush()

        ctx = QuickAddContext(
            session=self.session,
            user_id=user_id,
            moment_id=moment.id,
            moment_type_code=moment_type_code,
            quick_add_event_id=parent.quick_add_event_id,
            event_type=event_type,
            event_title=event_title,
            body=encoded_body,
            occurred_at=occurred_at,
        )
        timeline_draft = await dispatch_fn(ctx)
        await insert_timeline_row(ctx, timeline_draft)

        result = await self.session.execute(
            select(PersonalMoments).where(PersonalMoments.moment_id == moment.id)
        )
        personal_moment = result.scalar_one_or_none()
        if personal_moment is not None:
            personal_moment.last_activity_at = occurred_at
            personal_moment.updated_at = _now()

        return parent

    async def _publish_events(
        self,
        *,
        user_id: UUID,
        master_row: PersonalMasterExpenses,
        life_ops_event: PersonalQuickAddEvents,
        lifestyle_event: PersonalQuickAddEvents,
        relationships_event: PersonalQuickAddEvents | None,
    ) -> None:
        publisher = get_event_publisher()
        await publisher.publish(
            DomainEvent(
                name=MASTER_EXPENSE_CREATED,
                user_id=user_id,
                moment_id=life_ops_event.moment_id,
                context="MY_MONEY",
                moment_type="LIFE_OPERATIONS",
                payload={
                    "master_expense_id": str(master_row.master_expense_id),
                    "amount_minor": int(master_row.amount_minor),
                    "is_shared": master_row.is_shared,
                    "life_operations_event_id": str(life_ops_event.quick_add_event_id),
                    "lifestyle_event_id": str(lifestyle_event.quick_add_event_id),
                    "relationships_event_id": (
                        str(relationships_event.quick_add_event_id)
                        if relationships_event
                        else None
                    ),
                },
            )
        )

        for event in (life_ops_event, lifestyle_event, relationships_event):
            if event is None:
                continue
            await publisher.publish(
                DomainEvent(
                    name=QUICK_ADD_CREATED,
                    user_id=user_id,
                    moment_id=event.moment_id,
                    context="MY_MONEY",
                    moment_type=event.moment_type_code,
                    payload={
                        "session": self.session,
                        "event_type": event.event_type,
                        "quick_add_event_id": str(event.quick_add_event_id),
                        "master_expense_id": str(master_row.master_expense_id),
                        "skip_projection_invalidation": True,
                    },
                )
            )

    @staticmethod
    def _parse_experience(raw: Any) -> MasterExpenseExperienceInput | None:
        if not isinstance(raw, dict):
            return None
        return MasterExpenseExperienceInput(
            feeling=raw.get("feeling"),
            meaningfulness=raw.get("meaningfulness"),
            memorability=raw.get("memorability"),
        )

    @staticmethod
    def _parse_shared(raw: dict[str, Any]) -> MasterExpenseSharedInput:
        shared = raw.get("shared") if isinstance(raw.get("shared"), dict) else {}
        impacts = shared.get("relationship_impact") or []
        if isinstance(impacts, str):
            impacts = [impacts]
        shared_with = shared.get("shared_with") or []
        if not isinstance(shared_with, list):
            shared_with = []
        if not isinstance(impacts, list):
            impacts = []
        is_shared = bool(shared.get("is_shared", shared.get("enabled", False)))
        return MasterExpenseSharedInput(
            is_shared=is_shared,
            shared_with=[str(v) for v in shared_with],
            relationship_impact=[str(v) for v in impacts],
        )

    @staticmethod
    def _parse_context(raw: Any) -> MasterExpenseContextInput | None:
        if not isinstance(raw, dict):
            return None
        return MasterExpenseContextInput(reason=raw.get("reason"))
