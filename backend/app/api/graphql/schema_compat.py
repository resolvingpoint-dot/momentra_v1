"""Detect breaking GraphQL SDL changes for mobile client safety."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from graphql import build_schema, parse
from graphql.type import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLUnionType,
    is_enum_type,
    is_input_object_type,
    is_object_type,
)


@dataclass(frozen=True)
class BreakingChange:
    kind: str
    path: str
    detail: str


def _unwrap(t: Any) -> Any:
    while isinstance(t, (GraphQLNonNull, GraphQLList)):
        t = t.of_type
    return t


def _nullability_rank(t: Any) -> int:
    """Higher = more nullable / less strict for output fields.

    Breaking: making an output field more nullable OR removing non-null from a list wrapper incorrectly.
    """
    if isinstance(t, GraphQLNonNull):
        return _nullability_rank(t.of_type)
    if isinstance(t, GraphQLList):
        return 1 + _nullability_rank(t.of_type)
    return 2


def _is_more_nullable(old: Any, new: Any) -> bool:
    """True when new type is weaker (client may break expecting non-null)."""
    # Simplified: if old was NonNull and new is not NonNull of same core, breaking.
    old_nn = isinstance(old, GraphQLNonNull)
    new_nn = isinstance(new, GraphQLNonNull)
    if old_nn and not new_nn:
        return True
    if old_nn and new_nn:
        return _is_more_nullable(old.of_type, new.of_type)
    if isinstance(old, GraphQLList) and isinstance(new, GraphQLList):
        return _is_more_nullable(old.of_type, new.of_type)
    return False


def _type_name(t: Any) -> str:
    core = _unwrap(t)
    return getattr(core, "name", str(core))


def compare_sdl(old_sdl: str, new_sdl: str) -> list[BreakingChange]:
    old_schema = build_schema(old_sdl)
    new_schema = build_schema(new_sdl)
    breaking: list[BreakingChange] = []

    for name, old_type in old_schema.type_map.items():
        if name.startswith("__"):
            continue
        new_type = new_schema.type_map.get(name)
        if new_type is None:
            breaking.append(
                BreakingChange("type_removed", name, f"Type {name} was removed")
            )
            continue

        if is_object_type(old_type) and is_object_type(new_type):
            assert isinstance(old_type, GraphQLObjectType)
            assert isinstance(new_type, GraphQLObjectType)
            for field_name, old_field in old_type.fields.items():
                new_field = new_type.fields.get(field_name)
                if new_field is None:
                    breaking.append(
                        BreakingChange(
                            "field_removed",
                            f"{name}.{field_name}",
                            f"Field {name}.{field_name} was removed",
                        )
                    )
                    continue
                if _type_name(old_field.type) != _type_name(new_field.type):
                    # Rename / type change
                    breaking.append(
                        BreakingChange(
                            "field_type_changed",
                            f"{name}.{field_name}",
                            f"{_type_name(old_field.type)} -> {_type_name(new_field.type)}",
                        )
                    )
                elif _is_more_nullable(old_field.type, new_field.type):
                    breaking.append(
                        BreakingChange(
                            "nullability_relaxed",
                            f"{name}.{field_name}",
                            "Output field became more nullable",
                        )
                    )

        if is_enum_type(old_type) and is_enum_type(new_type):
            assert isinstance(old_type, GraphQLEnumType)
            assert isinstance(new_type, GraphQLEnumType)
            for value in old_type.values:
                if value not in new_type.values:
                    breaking.append(
                        BreakingChange(
                            "enum_value_removed",
                            f"{name}.{value}",
                            f"Enum value {name}.{value} was removed",
                        )
                    )

        if is_input_object_type(old_type) and is_input_object_type(new_type):
            assert isinstance(old_type, GraphQLInputObjectType)
            assert isinstance(new_type, GraphQLInputObjectType)
            for field_name, old_field in old_type.fields.items():
                new_field = new_type.fields.get(field_name)
                if new_field is None:
                    breaking.append(
                        BreakingChange(
                            "input_field_removed",
                            f"{name}.{field_name}",
                            f"Input field {name}.{field_name} was removed",
                        )
                    )

    return breaking


def assert_compatible(old_sdl: str, new_sdl: str) -> None:
    changes = compare_sdl(old_sdl, new_sdl)
    if changes:
        msg = "; ".join(f"{c.kind}:{c.path}" for c in changes)
        raise AssertionError(f"Breaking GraphQL schema changes: {msg}")
