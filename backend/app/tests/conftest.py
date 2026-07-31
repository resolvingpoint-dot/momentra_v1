from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Generator
from unittest.mock import MagicMock, PropertyMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.domains.users.models import UserModel
from app.main import app

MOCK_USER_ID = uuid4()


class MockSession:
    """In-memory mock that mimics the AsyncSession interface."""

    def __init__(self) -> None:
        self._stores: dict[str, dict] = {
            "users": {},
            "user_preferences": {},
            "module_states": {},
            "moments": {},
            "business_workspaces": {},
            "business_workspace_members": {},
            "business_workspace_invitations": {},
            "business_moments": {},
            "business_moment_setup": {},
            "business_moment_structure": {},
            "business_moment_governance": {},
            "business_moment_members": {},
            "business_moment_invitations": {},
            "business_runway_setup": {},
            "business_runway_structure": {},
            "business_runway_governance_rules": {},
            "business_operations_setup": {},
            "business_operations_structure": {},
            "business_operations_governance_rules": {},
            "business_operations_budget_categories": {},
            "auth_refresh_sessions": {},
            "group_moments": {},
            "group_moment_members": {},
            "platform_invites": {},
        }

    def _get_from_store(self, store_name: str, key: str) -> Any:
        return self._stores.get(store_name, {}).get(key)

    def _store_has_items(self, store_name: str) -> bool:
        return len(self._stores.get(store_name, {})) > 0

    def _store_count(self, store_name: str) -> int:
        return len(self._stores.get(store_name, {}))

    def _get_store_values(self, store_name: str) -> list:
        return list(self._stores.get(store_name, {}).values())

    async def execute(self, stmt: Any) -> Any:
        result = MagicMock()
        target_table = self._resolve_table(stmt)

        if target_table is None:
            result.scalar_one_or_none.return_value = None
            result.scalars.return_value.all.return_value = []
            result.scalar.return_value = 0
            return result

        handler = getattr(self, f"_handle_{target_table}", None)
        if handler:
            return handler(stmt, result)
        # Generic in-memory table support for Business SQL bridge tests.
        if target_table in self._stores:
            return self._handle_generic_table(target_table, stmt, result)
        return result

    def _handle_generic_table(self, table: str, stmt: Any, result: MagicMock) -> MagicMock:
        conds = self._extract_conditions(stmt.whereclause if hasattr(stmt, "whereclause") else None)
        values = self._get_store_values(table)
        matched = []
        for item in values:
            ok = True
            for key, value in conds.items():
                if str(getattr(item, key, None)) != str(value):
                    ok = False
                    break
            if ok:
                matched.append(item)
        if not conds:
            matched = values
        result.scalar_one_or_none.return_value = matched[0] if matched else None
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = matched
        scalars_mock.first.return_value = matched[0] if matched else None
        result.scalars.return_value = scalars_mock
        result.scalar.return_value = len(matched)
        # Column-only selects (e.g. select(BusinessMoments.moment_id))
        try:
            cols = list(getattr(stmt, "selected_columns", []) or [])
            if len(cols) == 1 and matched:
                key = getattr(cols[0], "key", None) or getattr(cols[0], "name", None)
                if key:
                    result.all.return_value = [(getattr(item, key),) for item in matched]
                else:
                    result.all.return_value = [(item,) for item in matched]
            else:
                result.all.return_value = matched
        except Exception:
            result.all.return_value = matched
        return result

    def _resolve_table(self, stmt: Any) -> str | None:
        if hasattr(stmt, "froms") and stmt.froms:
            for f in stmt.froms:
                if hasattr(f, "name"):
                    return f.name
        return None

    def _handle_users(self, stmt: Any, result: MagicMock) -> MagicMock:
        where = stmt.whereclause if hasattr(stmt, "whereclause") else None
        if where is not None:
            try:
                val = where.right.value
                item = self._get_from_store("users", val)
                result.scalar_one_or_none.return_value = item
                return result
            except Exception:
                pass
        result.scalar_one_or_none.return_value = None
        return result

    def _handle_user_preferences(self, stmt: Any, result: MagicMock) -> MagicMock:
        where = stmt.whereclause if hasattr(stmt, "whereclause") else None
        if where is not None:
            try:
                val = where.right.value
                item = self._get_from_store("user_preferences", val)
                if item is not None:
                    result.scalar_one_or_none.return_value = item
                    return result
            except Exception:
                pass
        vals = self._get_store_values("user_preferences")
        result.scalar_one_or_none.return_value = vals[0] if vals else None
        return result

    def _handle_module_states(self, stmt: Any, result: MagicMock) -> MagicMock:
        where = stmt.whereclause if hasattr(stmt, "whereclause") else None
        if where is not None:
            try:
                val = where.right.value
                item = self._get_from_store("module_states", val)
                result.scalar_one_or_none.return_value = item
                return result
            except Exception:
                pass
        result.scalar_one_or_none.return_value = None
        result.scalars.return_value.all.return_value = self._get_store_values("module_states")
        result.scalar.return_value = self._store_count("module_states")
        return result

    @staticmethod
    def _collect_binary(expr: Any, conds: dict[str, Any]) -> None:
        try:
            name = getattr(expr.left, "key", None) or getattr(expr.left, "name", None)
            value = expr.right.value
            if name is not None:
                conds[str(name)] = value
        except Exception:
            pass

    def _extract_conditions(self, where: Any) -> dict[str, Any]:
        conds: dict[str, Any] = {}
        if where is None:
            return conds
        clauses = getattr(where, "clauses", None)
        if clauses is not None:
            for clause in clauses:
                self._collect_binary(clause, conds)
        else:
            self._collect_binary(where, conds)
        return conds

    def _filter_moments(self, conds: dict[str, Any]) -> list:
        out = []
        for moment in self._get_store_values("moments"):
            match = True
            for key, value in conds.items():
                attr = getattr(moment, key, None)
                if key == "id" or key == "user_id":
                    if str(attr) != str(value):
                        match = False
                        break
                elif attr != value:
                    match = False
                    break
            if match:
                out.append(moment)
        # Repositories order by created_at desc; mimic newest-first.
        return list(reversed(out))

    def _handle_moments(self, stmt: Any, result: MagicMock) -> MagicMock:
        from sqlalchemy.sql.functions import FunctionElement

        is_count = False
        if hasattr(stmt, "selected_columns"):
            for col in stmt.selected_columns:
                if isinstance(col, FunctionElement):
                    is_count = True
                    break

        where = stmt.whereclause if hasattr(stmt, "whereclause") else None
        conds = self._extract_conditions(where)

        if is_count:
            result.scalar.return_value = len(self._filter_moments(conds))
            return result

        # Single-row lookups by primary key (with optional owner check).
        if "id" in conds:
            item = self._get_from_store("moments", str(conds["id"]))
            if item is not None and "user_id" in conds:
                if str(getattr(item, "user_id", "")) != str(conds["user_id"]):
                    item = None
            result.scalar_one_or_none.return_value = item
            return result

        moments = self._filter_moments(conds)
        result.scalars.return_value.all.return_value = moments
        result.scalar.return_value = len(moments)
        result.scalar_one_or_none.return_value = moments[0] if moments else None
        return result

    def add(self, model: Any) -> None:
        # Mimic the DB assigning a primary key on flush so newly-provisioned
        # rows have a usable ``id`` (real sessions apply the column default).
        if hasattr(model, "id") and getattr(model, "id", None) is None:
            try:
                model.id = uuid4()
            except Exception:
                pass
        table = model.__tablename__
        if table == "users":
            self._stores["users"][model.firebase_uid] = model
        elif table == "user_preferences":
            self._stores["user_preferences"][str(model.user_id)] = model
        elif table == "module_states":
            self._stores["module_states"][f"{model.user_id}:{model.module_key}"] = model
        elif table == "moments":
            self._stores["moments"][str(model.id)] = model
        elif table in self._stores:
            pk = None
            preferred = {
                "business_moments": ("moment_id",),
                "business_workspaces": ("workspace_id",),
                "business_workspace_members": ("member_id",),
                "business_workspace_invitations": ("invitation_id",),
                "business_moment_setup": ("setup_id", "moment_id"),
                "business_moment_structure": ("structure_id", "moment_id"),
                "business_moment_governance": ("governance_id", "moment_id"),
                "business_moment_members": ("member_id",),
                "business_moment_invitations": ("invite_id",),
                "business_runway_setup": ("runway_setup_id", "moment_id"),
                "business_runway_structure": ("structure_id", "moment_id"),
                "business_runway_governance_rules": ("governance_rule_id", "moment_id"),
                "business_operations_setup": ("operations_setup_id", "moment_id"),
                "business_operations_structure": ("operations_structure_id", "moment_id"),
                "business_operations_governance_rules": ("operations_governance_id", "moment_id"),
                "business_operations_budget_categories": ("budget_category_id", "allocation_id"),
                "group_moments": ("moment_id",),
                "group_moment_members": ("member_id",),
                "platform_invites": ("id",),
            }
            for attr in preferred.get(table, ("id",)):
                if hasattr(model, attr) and getattr(model, attr, None) is not None:
                    pk = str(getattr(model, attr))
                    break
            if pk is None:
                try:
                    for attr in preferred.get(table, ("id",)):
                        if hasattr(model, attr) and getattr(model, attr, None) is None:
                            setattr(model, attr, uuid4())
                            pk = str(getattr(model, attr))
                            break
                except Exception:
                    pk = str(uuid4())
            # Index business_moments by moment_id for bridge assertions.
            if table == "business_moments" and getattr(model, "moment_id", None) is not None:
                pk = str(model.moment_id)
            self._stores[table][pk or str(uuid4())] = model

    async def flush(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def refresh(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def delete(self, model: Any) -> None:
        table = model.__tablename__
        if table == "moments":
            self._stores["moments"].pop(str(model.id), None)
        elif table == "users":
            self._stores["users"].pop(model.firebase_uid, None)
        elif table == "user_preferences":
            self._stores["user_preferences"].pop(str(model.user_id), None)
        elif table == "module_states":
            key = f"{model.user_id}:{model.module_key}"
            self._stores["module_states"].pop(key, None)

    async def rollback(self) -> None:
        pass

    def begin_nested(self):
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def _nested():
            yield self

        return _nested()

    async def close(self) -> None:
        pass

    def __aenter__(self) -> AsyncGenerator[MockSession, None]:
        return self  # type: ignore[return-value]

    async def __aexit__(self, *args: Any) -> None:
        pass


@pytest.fixture(autouse=True)
def _reset_projection_cache_between_tests():
    from app.core.cache import reset_cache_for_tests
    from app.domains.personal.projection.cache import reset_projection_cache_for_tests

    reset_projection_cache_for_tests()
    reset_cache_for_tests()
    yield
    reset_projection_cache_for_tests()
    reset_cache_for_tests()


@pytest.fixture(autouse=True)
def _disable_celery_enqueue_in_tests(request, monkeypatch):
    """Avoid blocking on Redis when lifecycle handlers enqueue background jobs."""
    if request.node.get_closest_marker("celery_enqueue"):
        return
    from app.core.config import settings

    monkeypatch.setattr(
        type(settings),
        "effective_celery_broker",
        PropertyMock(return_value=""),
    )


@pytest.fixture
def mock_db() -> MockSession:
    return MockSession()


@pytest.fixture
def client(mock_db: MockSession) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user() -> UserModel:
    now = datetime.now(timezone.utc)
    return UserModel(
        id=MOCK_USER_ID,
        firebase_uid="test123",
        email="test@example.com",
        display_name="Test User",
        created_at=now,
        updated_at=now,
        last_login_at=now,
    )
