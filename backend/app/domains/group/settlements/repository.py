"""Settlement persistence in moment_store runtime ``settlements`` collection."""
from __future__ import annotations

from app.domains.group import moment_store as store
from app.domains.group.settlements.schemas import SettlementRecord
from app.domains.moments.models import MomentModel

_COLLECTION = "settlements"


def _active(items: list[dict]) -> list[dict]:
    return [row for row in items if not row.get("deleted")]


class SettlementRepository:
    def list_all(self, moment: MomentModel) -> list[dict]:
        return _active(store.list_items(moment, _COLLECTION))

    def get_by_id(self, moment: MomentModel, settlement_id: str, *, include_deleted: bool = False) -> dict | None:
        for row in store.list_items(moment, _COLLECTION):
            if str(row.get("id")) == settlement_id and (include_deleted or not row.get("deleted")):
                return row
        return None

    def get_by_client_request_id(self, moment: MomentModel, client_request_id: str) -> dict | None:
        for row in store.list_items(moment, _COLLECTION):
            if str(row.get("client_request_id") or "") == client_request_id and not row.get("deleted"):
                return row
        return None

    def create(self, moment: MomentModel, row: dict) -> dict:
        store.append_item(moment, _COLLECTION, row)
        return row

    def update(self, moment: MomentModel, settlement_id: str, patch: dict) -> dict | None:
        state = store.read_state(moment)
        items = state["runtime"].setdefault(_COLLECTION, [])
        for item in items:
            if str(item.get("id")) == settlement_id and not item.get("deleted"):
                item.update(patch)
                item["updated_at"] = store.now_iso()
                store.write_state(moment, state)
                return item
        return None

    def soft_delete(self, moment: MomentModel, settlement_id: str) -> dict | None:
        now = store.now_iso()
        return self.update(
            moment,
            settlement_id,
            {"deleted": True, "deleted_at": now},
        )

    @staticmethod
    def to_record(moment: MomentModel, row: dict) -> SettlementRecord:
        return SettlementRecord(
            id=str(row.get("id") or ""),
            moment_id=str(moment.id),
            from_member_id=str(row.get("from_member_id") or ""),
            to_member_id=str(row.get("to_member_id") or ""),
            amount_minor=int(row.get("amount_minor") or 0),
            currency_code=str(row.get("currency_code") or "INR"),
            status=row.get("status") or "OPEN",
            description=row.get("description"),
            client_request_id=row.get("client_request_id"),
            created_at=str(row.get("created_at") or ""),
            updated_at=str(row.get("updated_at") or row.get("created_at") or ""),
            settled_at=row.get("settled_at"),
            deleted=bool(row.get("deleted")),
        )
