"""Phase 2.5 GraphQL platform hardening contracts."""
from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.application.queries.group_moment_detail import (
    GroupMomentDetailDTO,
    GroupMomentMemberDTO,
)
from app.core.config import settings
from app.domains.users.models import UserModel

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "api" / "graphql" / "schema.graphql"
META_PATH = ROOT / "api" / "graphql" / "schema.meta.json"


def _gql(client: TestClient, payload: dict, headers: dict | None = None):
    return client.post("/graphql", json=payload, headers=headers or {})


def test_sdl_snapshot_matches_live_schema():
    from app.api.graphql.schema import schema

    live = schema.as_str().strip() + "\n"
    assert SCHEMA_PATH.exists(), "Run: python scripts/export_graphql_schema.py"
    committed = SCHEMA_PATH.read_text(encoding="utf-8")
    assert live == committed, "GraphQL SDL drifted — re-export schema.graphql"


def test_schema_meta_checksum_matches_sdl():
    import json

    sdl = SCHEMA_PATH.read_text(encoding="utf-8")
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    digest = hashlib.sha256(sdl.encode("utf-8")).hexdigest()
    assert meta["checksum_sha256"] == digest
    assert meta["version"] == digest[:12]


def test_schema_compat_detects_removed_field():
    from app.api.graphql.schema_compat import compare_sdl

    old = """
    type Query { health: String! groupMoment(id: ID!): GroupMoment }
    type GroupMoment { id: ID! title: String }
    """
    new = """
    type Query { health: String! groupMoment(id: ID!): GroupMoment }
    type GroupMoment { id: ID! }
    """
    changes = compare_sdl(old, new)
    assert any(c.kind == "field_removed" and "title" in c.path for c in changes)


def test_introspection_disabled_when_configured(client: TestClient):
    from app.api.graphql.extensions import build_extensions
    from strawberry.extensions import DisableIntrospection

    assert settings.graphql_disable_introspection is True
    assert DisableIntrospection in build_extensions()
    resp = _gql(client, {"query": "{ __schema { queryType { name } } }"})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("errors") or body.get("data", {}).get("__schema") is None


def test_body_too_large(client: TestClient, monkeypatch):
    monkeypatch.setattr(settings, "graphql_max_body_bytes", 32)
    fat = {"query": "{ health }", "pad": "x" * 200}
    resp = client.post("/graphql", json=fat)
    assert resp.status_code == 413
    assert resp.json()["errors"][0]["extensions"]["code"] == "body_too_large"


def test_apq_miss_then_store_and_hit(client: TestClient):
    query = "{ health }"
    digest = hashlib.sha256(query.encode()).hexdigest()
    miss = _gql(
        client,
        {
            "extensions": {
                "persistedQuery": {"version": 1, "sha256Hash": digest}
            }
        },
    )
    assert miss.status_code == 200
    assert miss.json()["errors"][0]["extensions"]["code"] == "persisted_query_not_found"

    store = _gql(
        client,
        {
            "query": query,
            "extensions": {
                "persistedQuery": {"version": 1, "sha256Hash": digest}
            },
        },
    )
    assert store.status_code == 200
    assert store.json().get("data", {}).get("health") == "ok"

    hit = _gql(
        client,
        {
            "extensions": {
                "persistedQuery": {"version": 1, "sha256Hash": digest}
            }
        },
    )
    assert hit.status_code == 200
    assert hit.json().get("data", {}).get("health") == "ok"


def test_persisted_only_mode(client: TestClient, monkeypatch):
    monkeypatch.setattr(settings, "graphql_persisted_only", True)
    resp = _gql(client, {"query": "{ health }"})
    assert resp.status_code == 200
    assert resp.json()["errors"][0]["extensions"]["code"] == "persisted_query_required"


def test_max_operations(client: TestClient, monkeypatch):
    monkeypatch.setattr(settings, "graphql_max_operations", 1)
    resp = _gql(
        client,
        {
            "query": "query A { health } query B { health }",
            "operationName": "A",
        },
    )
    assert resp.status_code == 200
    errors = resp.json().get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "too_many_operations"


def test_paginate_respects_max_page_size(monkeypatch):
    from app.api.graphql.types.common import paginate_list

    monkeypatch.setattr(settings, "graphql_max_page_size", 2)
    page = paginate_list(list(range(10)), first=100)
    assert len(page.nodes) == 2


@patch("app.api.v1.auth.verify_firebase_token")
@patch("app.api.graphql.directives.require", new_callable=AsyncMock)
def test_group_moment_with_permission_extension(
    mock_require, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    claims = {
        "uid": sample_user.firebase_uid,
        "email": sample_user.email,
        "name": sample_user.display_name,
    }
    mock_verify.return_value = claims
    mock_db.add(sample_user)
    mock_require.return_value = None

    moment_id = uuid4()
    detail = GroupMomentDetailDTO(
        id=moment_id,
        title="Trip",
        status="ACTIVE",
        members=[
            GroupMomentMemberDTO(
                id=str(uuid4()),
                display_name="Alex",
                role="OWNER",
                user_id=str(sample_user.id),
            )
        ],
    )

    exchange = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    access = exchange.json()["tokens"]["access_token"]

    with patch(
        "app.api.graphql.queries.group_moment.get_group_moment_detail",
        new_callable=AsyncMock,
        return_value=detail,
    ):
        resp = _gql(
            client,
            {
                "query": "query ($id: ID!) { groupMoment(id: $id) { id title } }",
                "variables": {"id": str(moment_id)},
            },
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    assert not resp.json().get("errors"), resp.json()
    assert resp.json()["data"]["groupMoment"]["id"] == str(moment_id)
