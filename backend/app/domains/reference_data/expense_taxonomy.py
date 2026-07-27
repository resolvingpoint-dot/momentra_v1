"""Expense category / subcategory taxonomy validation (Contract V2)."""
from __future__ import annotations

from typing import Any

from app.core.errors import AppError
from app.domains.reference_data.catalog import ReferenceCatalog, get_reference_catalog

# Living shared-home rent — frozen legacy domain codes (not EXPENSE taxonomy).
# Note: do not include "other" — that collides with EXPENSE parent OTHER.
LEGACY_LIVING_CATEGORY_CODES = frozenset({"rent", "utility", "utilities"})


class InvalidExpenseSubcategoryError(AppError):
    status_code = 422
    code = "invalid_expense_subcategory"

    def __init__(
        self,
        message: str = "The selected subcategory does not belong to this category.",
    ) -> None:
        super().__init__(message, code=self.code)


def nest_expense_categories(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assemble flat EXPENSE rows into parents with nested children."""
    parents: list[dict[str, Any]] = []
    children_by_parent: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        code = str(row.get("code") or "")
        parent_code = row.get("parent_code")
        if parent_code:
            key = str(parent_code).upper()
            child = {k: v for k, v in row.items() if k != "parent_code"}
            children_by_parent.setdefault(key, []).append(child)
        else:
            parents.append(dict(row))
    for parent in parents:
        code = str(parent.get("code") or "").upper()
        kids = children_by_parent.get(code, [])
        kids.sort(key=lambda r: (int(r.get("sort_order") or 0), str(r.get("label") or "")))
        parent["children"] = kids
    parents.sort(key=lambda r: (int(r.get("sort_order") or 0), str(r.get("label") or "")))
    return parents


def find_expense_row(
    catalog: ReferenceCatalog,
    code: str,
    *,
    active_only: bool = False,
) -> dict[str, Any] | None:
    upper = code.strip().upper()
    for row in catalog.get_flat("expense_categories", active_only=False):
        if str(row.get("code") or "").upper() == upper:
            if active_only and not row.get("is_active", True):
                return None
            return row
    return None


def normalize_expense_category_code(code: str | None) -> str | None:
    if code is None or str(code).strip() == "":
        return None
    raw = str(code).strip()
    # Preserve legacy living domain codes as lowercase.
    if raw.lower() in LEGACY_LIVING_CATEGORY_CODES:
        return raw.lower()
    return raw.upper()


def validate_expense_category_pair(
    category_code: str | None,
    subcategory_code: str | None,
    *,
    catalog: ReferenceCatalog | None = None,
    allow_legacy_living: bool = False,
) -> tuple[str | None, str | None]:
    """Validate and normalize category/subcategory for EXPENSE taxonomy writes.

    Returns (category_code, subcategory_code). subcategory may be None.
    Raises InvalidExpenseSubcategoryError on inconsistent/unknown/inactive child.
    """
    cat = normalize_expense_category_code(category_code)
    sub = normalize_expense_category_code(subcategory_code)

    # Legacy living categories: no subcategory taxonomy.
    if cat and cat.lower() in LEGACY_LIVING_CATEGORY_CODES:
        if sub is None or sub == "":
            return cat, None
        if allow_legacy_living:
            return cat, None
        raise InvalidExpenseSubcategoryError(
            "Subcategory is not supported for this legacy living category."
        )

    ref = catalog or get_reference_catalog()

    if cat:
        parent = find_expense_row(ref, cat, active_only=True)
        if parent is None or str(parent.get("taxonomy") or "") != "EXPENSE":
            raise InvalidExpenseSubcategoryError(
                "Invalid expense category."
            )
        if parent.get("parent_code"):
            raise InvalidExpenseSubcategoryError(
                "category_code must be a parent expense category."
            )
        cat = str(parent["code"]).upper()

    if sub is None or sub == "":
        return cat, None

    child = find_expense_row(ref, sub, active_only=True)
    if child is None:
        # Distinguish unknown vs inactive for clearer message (same error code).
        existing = find_expense_row(ref, sub, active_only=False)
        if existing is not None and not existing.get("is_active", True):
            raise InvalidExpenseSubcategoryError(
                "The selected subcategory is inactive and cannot be used for new writes."
            )
        raise InvalidExpenseSubcategoryError()

    if str(child.get("taxonomy") or "") != "EXPENSE":
        raise InvalidExpenseSubcategoryError()

    parent_code = child.get("parent_code")
    if not parent_code:
        raise InvalidExpenseSubcategoryError()

    parent_norm = str(parent_code).upper()
    if not cat:
        raise InvalidExpenseSubcategoryError(
            "Category is required when a subcategory is selected."
        )
    if cat != parent_norm:
        raise InvalidExpenseSubcategoryError()

    return cat, str(child["code"]).upper()
