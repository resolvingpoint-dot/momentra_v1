"""Phase 3 Memory GraphQL contracts."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.application.queries.memory import MemoryDTO, MemoryScope
from app.domains.users.models import UserModel


def _gql(client: TestClient, query: str, headers: dict | None = None):
    return client.post("/graphql", json={"query": query}, headers=headers or {})


def test_memory_unauthenticated(client: TestClient):
    resp = _gql(client, "query { memory(scope: PERSONAL) { __typename } }")
    assert resp.status_code == 200
    body = resp.json()
    data = body.get("data") or {}
    assert data.get("memory") is None
    errors = body.get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "unauthenticated"


@patch("app.api.v1.auth.verify_firebase_token")
def test_memory_personal(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    mock_verify.return_value = {
        "uid": sample_user.firebase_uid,
        "email": sample_user.email,
        "name": sample_user.display_name,
    }
    mock_db.add(sample_user)
    exchange = client.post(
        "/api/v1/auth/firebase/exchange",
        json={"id_token": "firebase-id-token"},
    )
    access = exchange.json()["tokens"]["access_token"]
    dto = MemoryDTO(
        scope=MemoryScope.PERSONAL,
        is_empty=False,
        pattern_insight_count=3,
        hero_title="Patterns forming",
        hero_badge="PATTERN INTELLIGENCE",
        payload={"featured_insights": [{"id": "1"}]},
    )
    with patch(
        "app.api.graphql.queries.memory.get_memory",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              memory(scope: PERSONAL) {
                __typename
                ... on PersonalMemory {
                  isEmpty
                  patternInsightCount
                  heroTitle
                  payload
                }
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    mem = body["data"]["memory"]
    assert mem["__typename"] == "PersonalMemory"
    assert mem["patternInsightCount"] == 3
