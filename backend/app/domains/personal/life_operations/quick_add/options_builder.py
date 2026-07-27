"""Build Life Ops Quick Add options from Reference Catalog (adapter layer)."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from app.domains.moments.models import MomentModel
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.life_operations.quick_add.constants import (
    LIFE_OPS_QUICK_ADD_METADATA,
    LIFE_OPS_QUICK_ADD_TABS,
)
from app.domains.reference_data.catalog import ReferenceCatalog


class LifeOpsQuickAddOptionsBuilder:
    def build(
        self,
        *,
        user_id: UUID,
        moments: list[MomentModel],
        accounts: list[dict[str, Any]],
        entries_today_count: int,
        default_currency_code: str,
        catalog: ReferenceCatalog,
    ) -> dict[str, Any]:
        del user_id  # reserved for future per-user option filtering
        moment_options = [
            {
                "moment_id": str(m.id),
                "moment_name": m.title or "Untitled",
                "moment_type_code": normalize_moment_type_code(m.moment_type or ""),
            }
            for m in moments
        ]
        return {
            "moments": moment_options,
            "tabs": LIFE_OPS_QUICK_ADD_TABS,
            "categories": [],
            "accounts": accounts,
            "entries_today_count": entries_today_count,
            "default_currency_code": default_currency_code,
            "currencies": catalog.get("currencies", active_only=True),
            "expense_categories": catalog.get("expense_categories", active_only=True),
            "account_types": catalog.get("account_types", active_only=True),
            "metadata": LIFE_OPS_QUICK_ADD_METADATA,
        }
