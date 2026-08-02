"""Shared mutation consistency assertion helpers (API-level)."""
from __future__ import annotations

from typing import Any, Callable


def assert_create_visible(
    *,
    list_items: list[dict[str, Any]],
    item_id: str,
    id_key: str = "id",
) -> None:
    matches = [i for i in list_items if str(i.get(id_key)) == str(item_id)]
    assert len(matches) == 1, f"expected exactly one item {item_id}, found {len(matches)}"


def assert_update_applied(
    *,
    item: dict[str, Any],
    expected_fields: dict[str, Any],
) -> None:
    for key, value in expected_fields.items():
        assert item.get(key) == value, f"{key}: expected {value!r}, got {item.get(key)!r}"


def assert_delete_absent(
    *,
    list_items: list[dict[str, Any]],
    item_id: str,
    id_key: str = "id",
) -> None:
    matches = [i for i in list_items if str(i.get(id_key)) == str(item_id)]
    assert not matches, f"deleted item {item_id} still present"


def assert_moment_removed_from_inventory(
    *,
    moments: list[dict[str, Any]],
    moment_id: str,
    id_key: str = "id",
) -> None:
    assert_delete_absent(list_items=moments, item_id=moment_id, id_key=id_key)


def assert_selected_moment_fallback(
    *,
    selected_id: str | None,
    inventory_ids: set[str],
) -> None:
    if selected_id is None:
        return
    assert str(selected_id) in inventory_ids, "selected moment not in inventory after delete"


def assert_pulse_excludes_item(
    *,
    pulse: dict[str, Any],
    item_id: str,
    walk: Callable[[dict[str, Any]], list[str]] | None = None,
) -> None:
    """Best-effort: ensure item id does not appear in common pulse list fields."""
    if walk is not None:
        ids = walk(pulse)
        assert str(item_id) not in ids
        return
    blob = str(pulse)
    assert str(item_id) not in blob
