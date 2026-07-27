"""Reference Catalog — Catalog → Collection → Items."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from fastapi import HTTPException, status

from app.domains.reference_data.constants import COLLECTION_KEYS
from app.domains.reference_data.repository import ReferenceDataRepository


class ReferenceCatalog:
    def __init__(self, repo: ReferenceDataRepository | None = None) -> None:
        self._repo = repo or ReferenceDataRepository()

    def version(self) -> int:
        return self._repo.get_version()

    def get(self, key: str, *, active_only: bool = False) -> list[dict[str, Any]]:
        if key not in COLLECTION_KEYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown reference catalog key: {key}",
            )
        rows = list(self._repo.get_collection(key))
        if active_only:
            rows = [r for r in rows if r.get("is_active", True)]
        if key == "expense_categories":
            from app.domains.reference_data.expense_taxonomy import nest_expense_categories

            # Nest for API consumers; include inactive children when active_only=False.
            return nest_expense_categories(rows)
        rows.sort(key=lambda r: (int(r.get("sort_order", 0)), r.get("label", "")))
        return rows

    def get_flat(self, key: str, *, active_only: bool = False) -> list[dict[str, Any]]:
        """Raw flat collection (used by taxonomy validation)."""
        if key not in COLLECTION_KEYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown reference catalog key: {key}",
            )
        rows = list(self._repo.get_collection(key))
        if active_only:
            rows = [r for r in rows if r.get("is_active", True)]
        rows.sort(key=lambda r: (int(r.get("sort_order", 0)), r.get("label", "")))
        return rows

    def label_for(self, collection_key: str, code: str) -> str:
        upper = code.strip().upper()
        for row in self._repo.get_collection(collection_key):
            if row["code"] == upper:
                return str(row["label"])
        return code

    def validate_currency(self, code: str) -> str:
        upper = code.strip().upper()
        if not self._code_exists("currencies", upper):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid currency code: {code}",
            )
        return upper

    def validate_code(self, collection_key: str, code: str) -> str:
        upper = code.strip().upper()
        if not self._code_exists(collection_key, upper):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid {collection_key} code: {code}",
            )
        return upper

    def minor_unit_for(self, currency_code: str) -> int:
        for row in self._repo.get_collection("currencies"):
            if row["code"] == currency_code.upper():
                return int(row.get("minor_unit", 2))
        return 2

    def resolve_category_code(
        self, collection_key: str, code: str | None, name: str | None
    ) -> str | None:
        if code:
            upper = code.strip().upper()
            if self._code_exists(collection_key, upper):
                return upper
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid category code: {code}",
            )
        if name:
            normalized = name.strip().lower()
            for row in self._repo.get_collection(collection_key):
                if row["label"].lower() == normalized or row["code"].lower() == normalized:
                    return row["code"]
            if self._code_exists(collection_key, "OTHER"):
                return "OTHER"
        return None

    def major_from_minor(self, amount_minor: int, currency_code: str) -> Decimal:
        minor_unit = self.minor_unit_for(currency_code)
        divisor = Decimal(10) ** minor_unit
        if minor_unit == 0:
            quantize_exp = Decimal("1")
        else:
            quantize_exp = Decimal(1).scaleb(-minor_unit)
        return (Decimal(amount_minor) / divisor).quantize(quantize_exp, rounding=ROUND_HALF_UP)

    def minor_from_major_string(self, amount: str, currency_code: str) -> int:
        """Convert major-unit decimal string to minor units (signed).

        Negative values are allowed for account balances and credits.
        Callers that require non-negative amounts (e.g. expense entry) must
        validate separately after conversion.
        """
        minor_unit = self.minor_unit_for(currency_code)
        try:
            value = Decimal(amount.strip())
        except (InvalidOperation, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid amount",
            ) from exc
        multiplier = Decimal(10) ** minor_unit
        return int((value * multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def _code_exists(self, collection_key: str, code: str) -> bool:
        return any(row["code"] == code for row in self._repo.get_collection(collection_key))


_catalog: ReferenceCatalog | None = None


def get_reference_catalog() -> ReferenceCatalog:
    global _catalog
    if _catalog is None:
        _catalog = ReferenceCatalog()
    return _catalog
