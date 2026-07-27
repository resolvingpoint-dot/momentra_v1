"""Reference data repository — constants-backed; swap for DB later."""
from __future__ import annotations

from typing import Any

from app.domains.reference_data.constants import (
    CATEGORY_GROUPS,
    COLLECTIONS,
    REFERENCE_DATA_VERSION,
)


class ReferenceDataRepository:
  def get_version(self) -> int:
      return REFERENCE_DATA_VERSION

  def get_collection(self, key: str) -> list[dict[str, Any]]:
      return list(COLLECTIONS.get(key, []))

  def get_all_collections(self) -> dict[str, list[dict[str, Any]]]:
      return {key: list(items) for key, items in COLLECTIONS.items()}

  def get_category_groups(self) -> dict[str, list[dict[str, Any]]]:
      return {key: list(items) for key, items in CATEGORY_GROUPS.items()}
