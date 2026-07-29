"""Settlement Engine v1 service — preview, CRUD, mark-settled."""
from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group.projection_cache import invalidate_group_projections
from app.domains.group.settlements import calculator
from app.domains.group.settlements.repository import SettlementRepository
from app.domains.group.settlements.schemas import (
    MarkSettledResponse,
    SettlementCreateRequest,
    SettlementListResponse,
    SettlementPatchRequest,
    SettlementPreview,
)
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository


def _active_expenses(moment: MomentModel) -> list[dict]:
    return [row for row in store.list_items(moment, "expenses") if not row.get("deleted")]


def _members(moment: MomentModel) -> list[dict]:
    """Roster for settlement balances: accepted members ∪ guests (deduped by id).

    Linked users may live only under guests while the organizer is in members;
    using members alone would drop guests from nets.
    """
    by_id: dict[str, dict] = {}
    for m in store.list_accepted_members(moment):
        mid = str(m.get("id") or "")
        if mid:
            by_id[mid] = {
                "id": mid,
                "full_name": m.get("display_name") or "Member",
                "phone": None,
                "email": None,
                "relationship_type": "member",
                "assigned_role": m.get("role_code"),
                "status": "active",
            }
    for g in store.guest_summaries(moment):
        gid = str(g.get("id") or "")
        if not gid:
            continue
        if gid in by_id:
            continue
        by_id[gid] = {
            "id": gid,
            "full_name": g.get("full_name") or "Guest",
            "phone": g.get("phone"),
            "email": g.get("email"),
            "relationship_type": g.get("relationship_type") or "friend",
            "assigned_role": g.get("assigned_role"),
            "status": str(g.get("status") or "active").lower(),
        }
    return list(by_id.values())


def _moment_currency(moment: MomentModel) -> str:
    state = store.read_state(moment)
    payload = state.get("payload") or {}
    return str(payload.get("currency_code") or "INR")


def _resolve_currency(moment: MomentModel, requested: str | None = None) -> str:
    moment_currency = _moment_currency(moment)
    if requested and requested != moment_currency:
        expenses = _active_expenses(moment)
        used = {str(row.get("currency_code") or moment_currency) for row in expenses}
        used.discard(moment_currency)
        if used and requested not in used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Moment uses single currency {moment_currency}",
            )
    return requested or moment_currency


def _validate_members(moment: MomentModel, *member_ids: str) -> None:
    valid = {str(m.get("id") or "") for m in _members(moment)}
    for member_id in member_ids:
        if member_id and member_id not in valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown member_id: {member_id}",
            )


def _enforce_single_currency(moment: MomentModel, currency_code: str) -> None:
    moment_currency = _moment_currency(moment)
    for row in _active_expenses(moment):
        row_currency = str(row.get("currency_code") or moment_currency)
        if row_currency != currency_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Moment supports a single currency for settlements",
            )


class SettlementService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.repo = SettlementRepository()

    async def _require(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        from app.domains.group.access import require_group_moment_access

        return await require_group_moment_access(self.session, user_id, moment_id)

    async def _invalidate(self, user_id: UUID, moment: MomentModel, reason: str) -> None:
        await invalidate_group_projections(
            user_id,
            moment.id,
            moment_type=moment.moment_type or "SHARED_EXPERIENCE",
            reason=reason,
        )

    def preview_for_moment(self, moment: MomentModel) -> SettlementPreview:
        from app.domains.group.settlements.trip_payload import build_preview_with_settlements

        return build_preview_with_settlements(moment)

    async def preview(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        return self.preview_for_moment(moment).model_dump(mode="json")

    async def list_settlements(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        currency = _moment_currency(moment)
        rows = [self.repo.to_record(moment, row) for row in self.repo.list_all(moment)]
        return SettlementListResponse(
            moment_id=str(moment.id),
            currency_code=currency,
            settlements=rows,
        ).model_dump(mode="json")

    async def create(self, user_id: UUID, moment_id: UUID, body: SettlementCreateRequest) -> dict:
        moment = await self._require(user_id, moment_id)
        if body.client_request_id:
            existing = self.repo.get_by_client_request_id(moment, body.client_request_id)
            if existing:
                return self.repo.to_record(moment, existing).model_dump(mode="json")

        currency = _resolve_currency(moment, body.currency_code)
        _enforce_single_currency(moment, currency)
        _validate_members(moment, body.from_member_id, body.to_member_id)
        if body.from_member_id == body.to_member_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="from_member_id and to_member_id must differ")

        now = store.now_iso()
        row = {
            "id": store.new_id(),
            "from_member_id": body.from_member_id,
            "to_member_id": body.to_member_id,
            "amount_minor": body.amount_minor,
            "currency_code": currency,
            "status": "OPEN",
            "description": body.description,
            "client_request_id": body.client_request_id,
            "created_at": now,
            "updated_at": now,
            "settled_at": None,
            "deleted": False,
        }
        self.repo.create(moment, row)
        await self.session.flush()
        await self._invalidate(user_id, moment, "settlement:create")
        return self.repo.to_record(moment, row).model_dump(mode="json")

    async def patch(
        self,
        user_id: UUID,
        moment_id: UUID,
        settlement_id: str,
        body: SettlementPatchRequest,
    ) -> dict:
        moment = await self._require(user_id, moment_id)
        existing = self.repo.get_by_id(moment, settlement_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found")

        patch = body.model_dump(exclude_unset=True)
        if not patch:
            return self.repo.to_record(moment, existing).model_dump(mode="json")

        from_id = str(patch.get("from_member_id") or existing.get("from_member_id") or "")
        to_id = str(patch.get("to_member_id") or existing.get("to_member_id") or "")
        _validate_members(moment, from_id, to_id)
        if from_id == to_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="from_member_id and to_member_id must differ")

        currency = patch.get("currency_code") or existing.get("currency_code")
        if currency:
            _resolve_currency(moment, str(currency))
            _enforce_single_currency(moment, str(currency))

        if patch.get("status") == "SETTLED":
            patch.setdefault("settled_at", store.now_iso())

        updated = self.repo.update(moment, settlement_id, patch)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found")
        await self.session.flush()
        await self._invalidate(user_id, moment, "settlement:patch")
        return self.repo.to_record(moment, updated).model_dump(mode="json")

    async def settle_suggestion(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        from_member_id: str,
        to_member_id: str,
        amount_minor: int,
        currency_code: str | None = None,
        client_request_id: str | None = None,
    ) -> dict:
        """Create a SETTLED settlement for a preview suggestion (Mark as Paid)."""
        body = SettlementCreateRequest(
            from_member_id=from_member_id,
            to_member_id=to_member_id,
            amount_minor=amount_minor,
            currency_code=currency_code or "INR",
            description="Marked paid from settlement suggestions",
            client_request_id=client_request_id,
        )
        created = await self.create(user_id, moment_id, body)
        settlement_id = str(created.get("id") or "")
        if not settlement_id:
            return created
        return await self.mark_settled(user_id, moment_id, settlement_id)

    async def settle_all_suggestions(self, user_id: UUID, moment_id: UUID) -> dict:
        """Settle every open transfer suggestion (Restore Crew Balance)."""
        moment = await self._require(user_id, moment_id)
        preview = self.preview_for_moment(moment)
        settled: list[dict] = []
        for idx, s in enumerate(preview.suggestions):
            row = await self.settle_suggestion(
                user_id,
                moment_id,
                from_member_id=s.from_member_id,
                to_member_id=s.to_member_id,
                amount_minor=s.amount_minor,
                currency_code=s.currency_code,
                client_request_id=f"restore:{moment_id}:{s.from_member_id}:{s.to_member_id}:{s.amount_minor}:{idx}",
            )
            settled.append(row)
        from app.domains.group.settlements.trip_payload import build_trip_settlement_payload

        payload = build_trip_settlement_payload(moment)
        payload["restored_count"] = len(settled)
        return payload

    async def mark_settled(self, user_id: UUID, moment_id: UUID, settlement_id: str) -> dict:
        moment = await self._require(user_id, moment_id)
        existing = self.repo.get_by_id(moment, settlement_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found")

        if existing.get("status") == "SETTLED":
            record = self.repo.to_record(moment, existing)
            return MarkSettledResponse(settlement=record, idempotent=True).model_dump(mode="json")

        now = store.now_iso()
        updated = self.repo.update(
            moment,
            settlement_id,
            {"status": "SETTLED", "settled_at": now},
        )
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found")
        await self.session.flush()
        await self._invalidate(user_id, moment, "settlement:mark-settled")
        record = self.repo.to_record(moment, updated)
        return MarkSettledResponse(settlement=record, idempotent=False).model_dump(mode="json")

    async def delete(self, user_id: UUID, moment_id: UUID, settlement_id: str) -> dict:
        moment = await self._require(user_id, moment_id)
        existing = self.repo.get_by_id(moment, settlement_id, include_deleted=True)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found")
        if existing.get("deleted"):
            return {"status": "deleted", "settlement_id": settlement_id, "idempotent": True}

        self.repo.soft_delete(moment, settlement_id)
        await self.session.flush()
        await self._invalidate(user_id, moment, "settlement:delete")
        return {"status": "deleted", "settlement_id": settlement_id, "idempotent": False}


def cheap_life_preview(moment: MomentModel) -> dict | None:
    """Compute settlement preview for life mappers when data is available."""
    expenses = _active_expenses(moment)
    members = _members(moment)
    if not expenses or len(members) < 2:
        return None
    from app.domains.group.settlements.trip_payload import build_preview_with_settlements

    preview = build_preview_with_settlements(moment)
    return calculator.life_preview_dict(preview)
