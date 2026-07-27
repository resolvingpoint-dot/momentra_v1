"""Generic asynchronous repository base for Momentra models.

The repository layer performs database access only -- it contains no business
logic, no HTTP and no FastAPI. Every concrete repository subclasses
``AsyncRepository`` and therefore inherits the full operation set:

* create / update / delete / get-by-id / list / search
* pagination, filtering and ordering
* transactions (commit / rollback / flush / savepoint context manager)
* bulk insert, bulk update, bulk (conditional) delete
* soft delete / restore where the model exposes a soft-delete column

All methods take/derive an :class:`~sqlalchemy.ext.asyncio.AsyncSession`.
Mutating methods flush (so server-generated keys/defaults are populated and
constraint errors surface early) but never commit -- transaction control is
left to the caller or to :meth:`AsyncRepository.transaction`.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Generic, Mapping, Sequence, TypeVar

from sqlalchemy import String, Text, delete as sa_delete, func, insert as sa_insert, inspect, or_, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement

from app.domains.users.models import Base

ModelT = TypeVar("ModelT", bound=Base)

# Column names that, when present, make a model "soft-deletable".
# Order = precedence. Value = how the flag encodes "deleted".
_SOFT_DELETE_TIMESTAMP = ("archived_at", "deleted_at")
_SOFT_DELETE_FLAG_TRUE = ("is_deleted",)   # deleted == True
_SOFT_DELETE_FLAG_FALSE = ("is_active",)   # active == True (deleted == False)

# Supported filter operator suffixes, e.g. filters={"amount__gte": 10}.
_OPERATORS = ("ne", "gt", "gte", "lt", "lte", "in", "notin", "like", "ilike", "isnull")


@dataclass(slots=True)
class Page(Generic[ModelT]):
    """A single page of results plus the total row count for the query."""

    items: list[ModelT]
    total: int
    limit: int | None
    offset: int

    @property
    def has_more(self) -> bool:
        if self.limit is None:
            return False
        return self.offset + len(self.items) < self.total


class AsyncRepository(Generic[ModelT]):
    """Base async repository. Subclasses only need to set ``model``."""

    model: type[ModelT]
    # Optional override; when None, all String/Text columns are searched.
    search_fields: tuple[str, ...] | None = None
    # Keep an ``updated_at`` column fresh on update/soft-delete when present.
    touch_updated_at: bool = True

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        mapper = inspect(self.model)
        self._pk_cols = list(mapper.primary_key)
        self._columns = {c.key for c in mapper.columns}
        self._soft = self._detect_soft_delete()

    # ------------------------------------------------------------------ #
    # introspection helpers
    # ------------------------------------------------------------------ #
    def _detect_soft_delete(self) -> tuple[str, str] | None:
        for name in _SOFT_DELETE_TIMESTAMP:
            if name in self._columns:
                return (name, "timestamp")
        for name in _SOFT_DELETE_FLAG_TRUE:
            if name in self._columns:
                return (name, "flag_true")
        for name in _SOFT_DELETE_FLAG_FALSE:
            if name in self._columns:
                return (name, "flag_false")
        return None

    @property
    def supports_soft_delete(self) -> bool:
        return self._soft is not None

    def _col(self, name: str) -> InstrumentedAttribute:
        return getattr(self.model, name)

    @property
    def _pk(self) -> InstrumentedAttribute:
        if len(self._pk_cols) != 1:
            raise TypeError(
                f"{self.model.__name__} has a composite primary key; "
                "pass explicit filters instead of a scalar id."
            )
        return self._col(self._pk_cols[0].key)

    # ------------------------------------------------------------------ #
    # query construction (filtering / ordering / soft-delete visibility)
    # ------------------------------------------------------------------ #
    def _filter_clause(self, key: str, value: Any) -> ColumnElement[bool]:
        field, _, op = key.partition("__")
        if op and op not in _OPERATORS:
            # not an operator suffix -> treat the whole thing as a column name
            field, op = key, ""
        column = self._col(field)
        if op in ("", None):
            if value is None:
                return column.is_(None)
            if isinstance(value, (list, tuple, set)):
                return column.in_(list(value))
            return column == value
        if op == "ne":
            return column.is_not(None) if value is None else column != value
        if op == "gt":
            return column > value
        if op == "gte":
            return column >= value
        if op == "lt":
            return column < value
        if op == "lte":
            return column <= value
        if op == "in":
            return column.in_(list(value))
        if op == "notin":
            return column.not_in(list(value))
        if op == "like":
            return column.like(value)
        if op == "ilike":
            return column.ilike(value)
        if op == "isnull":
            return column.is_(None) if value else column.is_not(None)
        raise ValueError(f"Unsupported filter operator: {op!r}")

    def _apply_filters(self, stmt, filters: Mapping[str, Any] | None):
        if filters:
            stmt = stmt.where(*[self._filter_clause(k, v) for k, v in filters.items()])
        return stmt

    def _active_clause(self) -> ColumnElement[bool] | None:
        if not self._soft:
            return None
        name, kind = self._soft
        column = self._col(name)
        if kind == "timestamp":
            return column.is_(None)
        if kind == "flag_true":
            return column.is_(False)
        return column.is_(True)  # flag_false: active == True

    def _apply_active(self, stmt, include_deleted: bool):
        if not include_deleted:
            clause = self._active_clause()
            if clause is not None:
                stmt = stmt.where(clause)
        return stmt

    def _apply_order(self, stmt, order_by: str | Sequence[str] | None):
        if order_by is None:
            return stmt
        specs = [order_by] if isinstance(order_by, str) else list(order_by)
        cols = []
        for spec in specs:
            desc = spec.startswith("-")
            name = spec[1:] if desc else spec
            column = self._col(name)
            cols.append(column.desc() if desc else column.asc())
        return stmt.order_by(*cols)

    def _search_columns(self) -> list[InstrumentedAttribute]:
        if self.search_fields is not None:
            return [self._col(n) for n in self.search_fields]
        mapper = inspect(self.model)
        return [
            getattr(self.model, c.key)
            for c in mapper.columns
            if isinstance(c.type, (String, Text))
        ]

    # ------------------------------------------------------------------ #
    # create
    # ------------------------------------------------------------------ #
    async def create(self, data: Mapping[str, Any] | None = None, /, **values: Any) -> ModelT:
        payload = dict(data or {})
        payload.update(values)
        obj = self.model(**payload)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def add(self, obj: ModelT, *, flush: bool = True) -> ModelT:
        self.session.add(obj)
        if flush:
            await self.session.flush()
        return obj

    # ------------------------------------------------------------------ #
    # read
    # ------------------------------------------------------------------ #
    async def get_by_id(self, id_: Any) -> ModelT | None:
        return await self.session.get(self.model, id_)

    async def get_by(self, **filters: Any) -> ModelT | None:
        stmt = self._apply_filters(select(self.model), filters).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists(self, **filters: Any) -> bool:
        stmt = self._apply_filters(select(self._pk_cols[0]), filters).limit(1)
        result = await self.session.execute(stmt)
        return result.first() is not None

    async def count(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        include_deleted: bool = False,
    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_active(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)

    async def list(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        order_by: str | Sequence[str] | None = None,
        limit: int | None = 100,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> list[ModelT]:
        stmt = select(self.model)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_active(stmt, include_deleted)
        stmt = self._apply_order(stmt, order_by)
        if offset:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def paginate(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        order_by: str | Sequence[str] | None = None,
        limit: int = 50,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> Page[ModelT]:
        total = await self.count(filters=filters, include_deleted=include_deleted)
        items = await self.list(
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
        )
        return Page(items=items, total=total, limit=limit, offset=offset)

    async def search(
        self,
        term: str,
        *,
        fields: Sequence[str] | None = None,
        filters: Mapping[str, Any] | None = None,
        order_by: str | Sequence[str] | None = None,
        limit: int | None = 50,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> list[ModelT]:
        columns = [self._col(n) for n in fields] if fields else self._search_columns()
        stmt = select(self.model)
        stmt = self._apply_filters(stmt, filters)
        stmt = self._apply_active(stmt, include_deleted)
        if term and columns:
            pattern = f"%{term}%"
            stmt = stmt.where(or_(*[c.ilike(pattern) for c in columns]))
        stmt = self._apply_order(stmt, order_by)
        if offset:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------ #
    # update
    # ------------------------------------------------------------------ #
    async def update(self, id_: Any, data: Mapping[str, Any] | None = None, /, **values: Any) -> ModelT | None:
        payload = dict(data or {})
        payload.update(values)
        obj = await self.session.get(self.model, id_)
        if obj is None:
            return None
        for key, value in payload.items():
            setattr(obj, key, value)
        self._touch(obj)
        await self.session.flush()
        return obj

    async def update_where(self, filters: Mapping[str, Any], values: Mapping[str, Any]) -> int:
        payload = dict(values)
        if self.touch_updated_at and "updated_at" in self._columns and "updated_at" not in payload:
            payload["updated_at"] = datetime.now(timezone.utc)
        stmt = self._apply_filters(sa_update(self.model), filters).values(**payload)
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    def _touch(self, obj: ModelT) -> None:
        if self.touch_updated_at and "updated_at" in self._columns:
            obj.updated_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------ #
    # delete (hard + soft)
    # ------------------------------------------------------------------ #
    async def delete(self, id_: Any) -> bool:
        obj = await self.session.get(self.model, id_)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def delete_where(self, filters: Mapping[str, Any]) -> int:
        stmt = self._apply_filters(sa_delete(self.model), filters)
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    def _soft_value(self) -> Any:
        assert self._soft is not None
        _, kind = self._soft
        if kind == "timestamp":
            return datetime.now(timezone.utc)
        if kind == "flag_true":
            return True
        return False  # flag_false: mark inactive

    def _restore_value(self) -> Any:
        assert self._soft is not None
        _, kind = self._soft
        if kind == "timestamp":
            return None
        if kind == "flag_true":
            return False
        return True  # flag_false: mark active

    async def soft_delete(self, id_: Any) -> ModelT | None:
        if not self._soft:
            raise NotImplementedError(f"{self.model.__name__} has no soft-delete column")
        name, _ = self._soft
        obj = await self.session.get(self.model, id_)
        if obj is None:
            return None
        setattr(obj, name, self._soft_value())
        self._touch(obj)
        await self.session.flush()
        return obj

    async def restore(self, id_: Any) -> ModelT | None:
        if not self._soft:
            raise NotImplementedError(f"{self.model.__name__} has no soft-delete column")
        name, _ = self._soft
        obj = await self.session.get(self.model, id_)
        if obj is None:
            return None
        setattr(obj, name, self._restore_value())
        self._touch(obj)
        await self.session.flush()
        return obj

    async def soft_delete_where(self, filters: Mapping[str, Any]) -> int:
        if not self._soft:
            raise NotImplementedError(f"{self.model.__name__} has no soft-delete column")
        name, _ = self._soft
        values: dict[str, Any] = {name: self._soft_value()}
        if self.touch_updated_at and "updated_at" in self._columns:
            values["updated_at"] = datetime.now(timezone.utc)
        stmt = self._apply_filters(sa_update(self.model), filters).values(**values)
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    # ------------------------------------------------------------------ #
    # bulk operations
    # ------------------------------------------------------------------ #
    async def bulk_create(self, rows: Sequence[Mapping[str, Any] | ModelT]) -> list[ModelT]:
        objs = [r if isinstance(r, self.model) else self.model(**dict(r)) for r in rows]
        self.session.add_all(objs)
        await self.session.flush()
        return objs

    async def bulk_insert(self, mappings: Sequence[Mapping[str, Any]]) -> int:
        if not mappings:
            return 0
        result = await self.session.execute(sa_insert(self.model), list(mappings))
        return result.rowcount or 0

    async def bulk_update(self, mappings: Sequence[Mapping[str, Any]]) -> int:
        """Per-row UPDATE keyed by primary key (each mapping must include the PK)."""
        if not mappings:
            return 0
        await self.session.execute(sa_update(self.model), list(mappings))
        return len(mappings)

    # ------------------------------------------------------------------ #
    # transactions / unit-of-work helpers
    # ------------------------------------------------------------------ #
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        """Run a block in a transaction, using a SAVEPOINT if one is active."""
        if self.session.in_transaction():
            async with self.session.begin_nested():
                yield self.session
        else:
            async with self.session.begin():
                yield self.session

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def refresh(self, obj: ModelT, attribute_names: Sequence[str] | None = None) -> ModelT:
        await self.session.refresh(obj, attribute_names=list(attribute_names) if attribute_names else None)
        return obj
