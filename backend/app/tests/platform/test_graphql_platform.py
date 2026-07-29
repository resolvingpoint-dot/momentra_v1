"""GraphQL read platform contract tests (Phase 2)."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.application.queries.group_moment_detail import (
    GroupMomentDetailDTO,
    GroupMomentMemberDTO,
)
from app.auth.principal import Principal
from app.domains.users.models import UserModel


def _gql(
    client: TestClient,
    query: str,
    variables: dict | None = None,
    headers: dict | None = None,
):
    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables
    return client.post("/graphql", json=payload, headers=headers or {})


def test_graphql_health_no_auth(client: TestClient):
    resp = _gql(client, "{ health }")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("data", {}).get("health") == "ok"
    assert not body.get("errors")


def test_graphql_group_moment_unauthenticated(client: TestClient):
    mid = str(uuid4())
    resp = _gql(
        client,
        "query ($id: ID!) { groupMoment(id: $id) { id } }",
        {"id": mid},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("data", {}).get("groupMoment") is None
    errors = body.get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "unauthenticated"


@patch("app.api.v1.auth.verify_firebase_token")
@patch("app.api.graphql.directives.require", new_callable=AsyncMock)
def test_graphql_group_moment_happy_path(
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
    assert exchange.status_code == 200
    access = exchange.json()["tokens"]["access_token"]

    with patch(
        "app.api.graphql.queries.group_moment.get_group_moment_detail",
        new_callable=AsyncMock,
        return_value=detail,
    ):
        resp = _gql(
            client,
            "query ($id: ID!) { groupMoment(id: $id) { id title status members { id displayName role } } }",
            {"id": str(moment_id)},
            headers={"Authorization": f"Bearer {access}"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    gm = body["data"]["groupMoment"]
    assert gm["id"] == str(moment_id)
    assert gm["title"] == "Trip"
    assert gm["status"] == "ACTIVE"
    assert len(gm["members"]) == 1
    assert gm["members"][0]["displayName"] == "Alex"


def test_graphql_query_too_complex(client: TestClient, monkeypatch):
    import strawberry
    from strawberry.fastapi import GraphQLRouter

    from app.api.graphql.context import get_graphql_context
    from app.api.graphql.extensions import QueryComplexityLimiter
    from app.api.graphql import extensions as ext_mod
    from app.main import app

    monkeypatch.setattr(ext_mod.settings, "graphql_max_complexity", 3)

    @strawberry.type
    class Q:
        @strawberry.field
        def health(self) -> str:
            return "ok"

    schema = strawberry.Schema(query=Q, extensions=[QueryComplexityLimiter])
    router = GraphQLRouter(
        schema,
        path="/graphql-complexity-test",
        context_getter=get_graphql_context,
        graphql_ide=None,
    )
    app.include_router(router)

    fat = "{ health health2: health health3: health health4: health }"
    bad = client.post("/graphql-complexity-test", json={"query": fat})
    assert bad.status_code == 200
    errors = bad.json().get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "query_too_complex"


def test_graphql_extensions_include_depth_and_complexity():
    from strawberry.extensions import QueryDepthLimiter

    from app.api.graphql.extensions import (
        QueryComplexityLimiter,
        build_extensions,
    )

    built = build_extensions()
    assert any(
        (callable(x) and not isinstance(x, type))
        or x is QueryDepthLimiter
        or (callable(x) and getattr(x, "__name__", "") == "<lambda>")
        for x in built
    )
    assert QueryComplexityLimiter in built


def test_paginate_list_cursor():
    from app.api.graphql.types.common import paginate_list

    items = list(range(5))
    page = paginate_list(items, first=2, after=None)
    assert page.nodes == [0, 1]
    assert page.page_info.has_next_page is True
    page2 = paginate_list(items, first=2, after=page.page_info.end_cursor)
    assert page2.nodes == [2, 3]


def test_principal_for_graphql_scopes():
    p = Principal(user_id=uuid4(), firebase_uid="x", auth_type="session")
    assert "momentra:user" in p.scopes
