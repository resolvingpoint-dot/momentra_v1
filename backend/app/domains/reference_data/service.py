"""Reference Data Engine service."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status

from app.domains.reference_data.catalog import ReferenceCatalog
from app.domains.reference_data.constants import COLLECTION_KEYS
from app.domains.reference_data.repository import ReferenceDataRepository
from app.domains.reference_data.schemas import (
    CurrencySchema,
    ReferenceDataBootstrapSchema,
    ReferenceDataOptionsSchema,
    ReferenceItemSchema,
)


class ReferenceDataService:
    def __init__(self) -> None:
        self.repo = ReferenceDataRepository()
        self.catalog = ReferenceCatalog(self.repo)

    def get_version(self) -> int:
        return self.catalog.version()

    def get_catalog(self) -> ReferenceCatalog:
        return self.catalog

    def get_bootstrap(self) -> ReferenceDataBootstrapSchema:
        collections = self.repo.get_all_collections()
        from app.domains.reference_data.expense_taxonomy import nest_expense_categories

        categories: dict[str, list[Any]] = {}
        for group, items in self.repo.get_category_groups().items():
            if group == "expense":
                nested = nest_expense_categories(list(items))
                categories[group] = [ReferenceItemSchema.model_validate(i) for i in nested]
            else:
                categories[group] = [ReferenceItemSchema.model_validate(i) for i in items]
        return ReferenceDataBootstrapSchema(
            reference_data_version=self.repo.get_version(),
            currencies=[CurrencySchema.model_validate(c) for c in collections["currencies"]],
            countries=[ReferenceItemSchema.model_validate(c) for c in collections["countries"]],
            locales=[ReferenceItemSchema.model_validate(c) for c in collections["locales"]],
            timezones=[ReferenceItemSchema.model_validate(c) for c in collections["timezones"]],
            languages=[ReferenceItemSchema.model_validate(c) for c in collections["languages"]],
            categories=categories,
        )

    def get_options(self, keys: list[str]) -> ReferenceDataOptionsSchema:
        unknown = [k for k in keys if k not in COLLECTION_KEYS]
        if unknown:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown reference data keys: {', '.join(unknown)}",
            )
        data: dict[str, list[Any]] = {}
        for key in keys:
            if key == "expense_categories":
                data[key] = self.catalog.get(key, active_only=True)
            else:
                data[key] = self.repo.get_collection(key)
        return ReferenceDataOptionsSchema(
            reference_data_version=self.repo.get_version(),
            data=data,
        )

    def get_collection(self, key: str) -> list[dict[str, Any]]:
        return self.catalog.get(key)

    def validate_code(self, collection_key: str, code: str) -> str:
        return self.catalog.validate_code(collection_key, code)

    def validate_currency(self, code: str) -> str:
        return self.catalog.validate_currency(code)

    def validate_country(self, code: str) -> str:
        upper = code.strip().upper()
        if not self._code_exists("countries", upper):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid country code: {code}",
            )
        return upper

    def validate_locale(self, locale: str) -> str:
        normalized = locale.strip()
        if not self._code_exists("locales", normalized):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid locale: {locale}",
            )
        return normalized

    def validate_timezone(self, timezone_name: str) -> str:
        normalized = timezone_name.strip()
        if not self._code_exists("timezones", normalized):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid timezone: {timezone_name}",
            )
        return normalized

    def minor_unit_for(self, currency_code: str) -> int:
        return self.catalog.minor_unit_for(currency_code)

    def currency_exists(self, code: str) -> bool:
        return self.catalog._code_exists("currencies", code.strip().upper())

    def category_exists(self, collection_key: str, code: str) -> bool:
        return self.catalog._code_exists(collection_key, code.strip().upper())

    def resolve_category_code(
        self, collection_key: str, code: str | None, name: str | None
    ) -> str | None:
        return self.catalog.resolve_category_code(collection_key, code, name)

    def major_from_minor(self, amount_minor: int, currency_code: str) -> Decimal:
        return self.catalog.major_from_minor(amount_minor, currency_code)

    def minor_from_major_string(self, amount: str, currency_code: str) -> int:
        return self.catalog.minor_from_major_string(amount, currency_code)

    def _code_exists(self, collection_key: str, code: str) -> bool:
        return self.catalog._code_exists(collection_key, code)


_reference_data_service: ReferenceDataService | None = None


def get_reference_data_service() -> ReferenceDataService:
    global _reference_data_service
    if _reference_data_service is None:
        _reference_data_service = ReferenceDataService()
    return _reference_data_service


def get_reference_catalog() -> ReferenceCatalog:
    return get_reference_data_service().get_catalog()
