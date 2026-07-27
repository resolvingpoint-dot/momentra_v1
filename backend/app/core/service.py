"""Generic asynchronous service base for Momentra.

The service layer holds business logic and orchestrates repositories. It is the
only layer allowed to contain rules, permission checks, workflow / state
transitions, snapshot refresh, cache invalidation and event creation.

Hard rules enforced here:

* Services **never return SQLAlchemy models** -- every read/mutation returns a
  Pydantic schema (or a :class:`Page` of schemas / a plain scalar).
* No HTTP and no FastAPI imports.

``BaseService`` provides the orchestration skeleton and safe defaults for every
responsibility; concrete services override the hooks
(``validate_create``/``validate_update``, ``check_permission``,
``emit_events``, ``refresh_snapshots``, ``cache_keys`` ...) to add real domain
behaviour. Owner-based permission + query scoping is derived automatically from
a ``user_id`` / ``owner_id`` / ``created_by`` column when present.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Generic, Mapping, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import delete_cached
from app.core.errors import NotFoundError, PermissionDeniedError, StateTransitionError, ValidationError
from app.core.repository import AsyncRepository

ModelT = TypeVar("ModelT")
SchemaT = TypeVar("SchemaT", bound=BaseModel)

_OWNER_CANDIDATES = ("user_id", "owner_id", "created_by")
_SENTINEL: Any = object()


class Page(BaseModel, Generic[SchemaT]):
    """A page of schema results plus the total count (schema, never a model)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[SchemaT]
    total: int
    limit: int | None = None
    offset: int = 0

    @property
    def has_more(self) -> bool:
        if self.limit is None:
            return False
        return self.offset + len(self.items) < self.total


class BaseService(Generic[ModelT, SchemaT]):
    """Base service. Subclasses set ``repository_class`` and ``schema``."""

    repository_class: type[AsyncRepository]
    schema: type[BaseModel]

    # Commit the unit of work at the end of each mutation. Set False to let a
    # caller compose several service calls into one transaction.
    auto_commit: bool = True
    # Column used for ownership permission checks + list scoping. Resolved from
    # the model automatically when left as the sentinel; set to None to disable.
    owner_field: Any = _SENTINEL
    # Prefix for cache keys invalidated on mutations (None disables cache work).
    cache_prefix: str | None = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo: AsyncRepository = self.repository_class(session)
        self.model = self.repo.model
        self._columns = self.repo._columns
        if self.owner_field is _SENTINEL:
            self.owner_field = next((c for c in _OWNER_CANDIDATES if c in self._columns), None)

    # ------------------------------------------------------------------ #
    # serialization -- the single place models become schemas
    # ------------------------------------------------------------------ #
    def _to_schema(self, obj: ModelT) -> SchemaT:
        return self.schema.model_validate(obj)  # type: ignore[return-value]

    def _to_schemas(self, objs: Sequence[ModelT]) -> list[SchemaT]:
        return [self._to_schema(o) for o in objs]

    # ------------------------------------------------------------------ #
    # orchestration helpers
    # ------------------------------------------------------------------ #
    def repo_for(self, repository_class: type[AsyncRepository]) -> AsyncRepository:
        """Build a sibling repository on the same session (for orchestration)."""
        return repository_class(self.session)

    async def _commit(self) -> None:
        if self.auto_commit:
            await self.session.commit()

    @asynccontextmanager
    async def atomic(self) -> AsyncIterator[AsyncSession]:
        """Group several operations into one transaction (disables auto-commit)."""
        previous = self.auto_commit
        self.auto_commit = False
        try:
            async with self.repo.transaction():
                yield self.session
        finally:
            self.auto_commit = previous

    async def call_db_function(self, sql: str, params: Mapping[str, Any] | None = None) -> Any:
        """Run a stored function/procedure (e.g. a snapshot-refresh routine)."""
        result = await self.session.execute(text(sql), dict(params or {}))
        return result

    def _scoped_filters(
        self, filters: Mapping[str, Any] | None, actor: Any
    ) -> dict[str, Any]:
        merged = dict(filters or {})
        if actor is not None and self.owner_field and self.owner_field not in merged:
            merged[self.owner_field] = actor
        return merged

    # ------------------------------------------------------------------ #
    # overridable hooks (business logic lives in subclasses)
    # ------------------------------------------------------------------ #
    async def check_permission(self, action: str, actor: Any, obj: ModelT | None = None) -> None:
        """Ownership check by default; override for role/rule-based policies."""
        if actor is None or not self.owner_field:
            return
        if obj is not None and getattr(obj, self.owner_field, _SENTINEL) not in (actor, _SENTINEL):
            raise PermissionDeniedError(
                f"Actor not permitted to {action} this {self.model.__name__}",
            )

    async def validate_create(self, data: dict[str, Any], actor: Any) -> dict[str, Any]:
        """Validate/normalize creation input. Return the (possibly mutated) data."""
        self._reject_unknown(data)
        return data

    async def validate_update(self, obj: ModelT, data: dict[str, Any], actor: Any) -> dict[str, Any]:
        self._reject_unknown(data)
        return data

    async def validate_transition(self, obj: ModelT, field: str, to_value: Any, actor: Any) -> None:
        return None

    async def emit_events(self, action: str, obj: ModelT, actor: Any) -> None:
        """Create domain event rows. Default: no-op (override per domain)."""
        return None

    async def refresh_snapshots(self, action: str, obj: ModelT, actor: Any) -> None:
        """Recompute derived snapshot/aggregate tables. Default: no-op."""
        return None

    def cache_keys(self, data: SchemaT, actor: Any) -> list[str]:
        """Cache keys to invalidate after a mutation."""
        if not self.cache_prefix:
            return []
        keys = [self.cache_prefix]
        if actor is not None:
            keys.append(f"{self.cache_prefix}:owner:{actor}")
        return keys

    async def invalidate_cache(self, data: SchemaT, actor: Any) -> None:
        for key in self.cache_keys(data, actor):
            await delete_cached(key)

    def _reject_unknown(self, data: Mapping[str, Any]) -> None:
        unknown = set(data) - self._columns
        if unknown:
            raise ValidationError(
                f"Unknown field(s) for {self.model.__name__}: {sorted(unknown)}",
                details=sorted(unknown),
            )

    # ------------------------------------------------------------------ #
    # read operations (return schemas)
    # ------------------------------------------------------------------ #
    async def get(self, id_: Any, *, actor: Any = None) -> SchemaT | None:
        obj = await self.repo.get_by_id(id_)
        if obj is None:
            return None
        await self.check_permission("read", actor, obj)
        return self._to_schema(obj)

    async def get_or_raise(self, id_: Any, *, actor: Any = None) -> SchemaT:
        schema = await self.get(id_, actor=actor)
        if schema is None:
            raise NotFoundError(f"{self.model.__name__} not found")
        return schema

    async def list(
        self,
        *,
        actor: Any = None,
        filters: Mapping[str, Any] | None = None,
        order_by: str | Sequence[str] | None = None,
        limit: int | None = 100,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> list[SchemaT]:
        objs = await self.repo.list(
            filters=self._scoped_filters(filters, actor),
            order_by=order_by,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
        )
        return self._to_schemas(objs)

    async def paginate(
        self,
        *,
        actor: Any = None,
        filters: Mapping[str, Any] | None = None,
        order_by: str | Sequence[str] | None = None,
        limit: int = 50,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> Page[SchemaT]:
        scoped = self._scoped_filters(filters, actor)
        total = await self.repo.count(filters=scoped, include_deleted=include_deleted)
        objs = await self.repo.list(
            filters=scoped,
            order_by=order_by,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
        )
        return Page[self.schema](  # type: ignore[name-defined]
            items=self._to_schemas(objs), total=total, limit=limit, offset=offset
        )

    async def search(
        self,
        term: str,
        *,
        actor: Any = None,
        fields: Sequence[str] | None = None,
        filters: Mapping[str, Any] | None = None,
        order_by: str | Sequence[str] | None = None,
        limit: int | None = 50,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> list[SchemaT]:
        objs = await self.repo.search(
            term,
            fields=fields,
            filters=self._scoped_filters(filters, actor),
            order_by=order_by,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
        )
        return self._to_schemas(objs)

    # ------------------------------------------------------------------ #
    # write operations (validate -> permit -> persist -> events/snapshots
    # -> commit -> cache invalidation -> return schema)
    # ------------------------------------------------------------------ #
    async def create(self, data: Mapping[str, Any] | None = None, *, actor: Any = None, **values: Any) -> SchemaT:
        payload = {**(data or {}), **values}
        if actor is not None and self.owner_field and self.owner_field in self._columns:
            payload.setdefault(self.owner_field, actor)
        await self.check_permission("create", actor)
        payload = await self.validate_create(payload, actor)
        obj = await self.repo.create(payload)
        await self.session.refresh(obj)  # populate server-side defaults for the schema
        schema = self._to_schema(obj)
        await self.emit_events("create", obj, actor)
        await self.refresh_snapshots("create", obj, actor)
        await self._commit()
        await self.invalidate_cache(schema, actor)
        return schema

    async def update(self, id_: Any, data: Mapping[str, Any] | None = None, *, actor: Any = None, **values: Any) -> SchemaT:
        payload = {**(data or {}), **values}
        obj = await self.repo.get_by_id(id_)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} not found")
        await self.check_permission("update", actor, obj)
        payload = await self.validate_update(obj, payload, actor)
        for key, value in payload.items():
            setattr(obj, key, value)
        self.repo._touch(obj)
        await self.repo.flush()
        schema = self._to_schema(obj)
        await self.emit_events("update", obj, actor)
        await self.refresh_snapshots("update", obj, actor)
        await self._commit()
        await self.invalidate_cache(schema, actor)
        return schema

    async def transition(
        self,
        id_: Any,
        field: str,
        to_value: Any,
        *,
        allowed_from: Sequence[Any] | None = None,
        actor: Any = None,
    ) -> SchemaT:
        """State-transition workflow: guard the current value then move it."""
        obj = await self.repo.get_by_id(id_)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} not found")
        await self.check_permission("update", actor, obj)
        current = getattr(obj, field, None)
        if allowed_from is not None and current not in allowed_from:
            raise StateTransitionError(
                f"Cannot move {self.model.__name__}.{field} from {current!r} to {to_value!r}",
            )
        await self.validate_transition(obj, field, to_value, actor)
        setattr(obj, field, to_value)
        self.repo._touch(obj)
        await self.repo.flush()
        schema = self._to_schema(obj)
        await self.emit_events(f"transition:{field}", obj, actor)
        await self.refresh_snapshots("transition", obj, actor)
        await self._commit()
        await self.invalidate_cache(schema, actor)
        return schema

    async def delete(self, id_: Any, *, actor: Any = None) -> bool:
        obj = await self.repo.get_by_id(id_)
        if obj is None:
            return False
        await self.check_permission("delete", actor, obj)
        await self.emit_events("delete", obj, actor)
        schema = self._to_schema(obj)
        await self.repo.delete(id_)
        await self.refresh_snapshots("delete", obj, actor)
        await self._commit()
        await self.invalidate_cache(schema, actor)
        return True

    async def soft_delete(self, id_: Any, *, actor: Any = None) -> SchemaT:
        if not self.repo.supports_soft_delete:
            raise ValidationError(f"{self.model.__name__} does not support soft delete")
        obj = await self.repo.get_by_id(id_)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} not found")
        await self.check_permission("delete", actor, obj)
        await self.emit_events("soft_delete", obj, actor)
        obj = await self.repo.soft_delete(id_)
        schema = self._to_schema(obj)
        await self.refresh_snapshots("soft_delete", obj, actor)
        await self._commit()
        await self.invalidate_cache(schema, actor)
        return schema

    async def restore(self, id_: Any, *, actor: Any = None) -> SchemaT:
        if not self.repo.supports_soft_delete:
            raise ValidationError(f"{self.model.__name__} does not support soft delete")
        obj = await self.repo.get_by_id(id_)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} not found")
        await self.check_permission("update", actor, obj)
        obj = await self.repo.restore(id_)
        schema = self._to_schema(obj)
        await self.refresh_snapshots("restore", obj, actor)
        await self._commit()
        await self.invalidate_cache(schema, actor)
        return schema

    # ------------------------------------------------------------------ #
    # bulk operations (return schemas)
    # ------------------------------------------------------------------ #
    async def bulk_create(self, rows: Sequence[Mapping[str, Any]], *, actor: Any = None) -> list[SchemaT]:
        await self.check_permission("create", actor)
        payloads: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            if actor is not None and self.owner_field and self.owner_field in self._columns:
                payload.setdefault(self.owner_field, actor)
            payloads.append(await self.validate_create(payload, actor))
        objs = await self.repo.bulk_create(payloads)
        for obj in objs:
            await self.session.refresh(obj)  # populate server-side defaults
        schemas = self._to_schemas(objs)
        await self._commit()
        return schemas

    async def count(self, *, actor: Any = None, filters: Mapping[str, Any] | None = None, include_deleted: bool = False) -> int:
        return await self.repo.count(
            filters=self._scoped_filters(filters, actor), include_deleted=include_deleted
        )
