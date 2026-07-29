"""Phase 3 Life Timeline GraphQL contracts."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.application.queries.life import LifeDTO, LifeScope
from app.domains.users.models import UserModel


def _gql(client: TestClient, query: str, headers: dict | None = None):
    return client.post("/graphql", json={"query": query}, headers=headers or {})


def test_life_unauthenticated(client: TestClient):
    resp = _gql(client, "query { life(scope: PERSONAL) { __typename } }")
    assert resp.status_code == 200
    body = resp.json()
    data = body.get("data") or {}
    assert data.get("life") is None
    errors = body.get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "unauthenticated"


@patch("app.api.v1.auth.verify_firebase_token")
def test_life_personal(
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
    dto = LifeDTO(
        scope=LifeScope.PERSONAL,
        is_empty=False,
        active_moment_count=2,
        date_range_label="This week",
        metrics={"ops_index": 71},
        payload={"is_empty": False, "metrics": {"ops_index": 71}},
    )
    with patch(
        "app.api.graphql.queries.life.get_life",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              life(scope: PERSONAL) {
                __typename
                ... on PersonalLife {
                  isEmpty
                  activeMomentCount
                  dateRangeLabel
                  metrics
                }
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    life = body["data"]["life"]
    assert life["__typename"] == "PersonalLife"
    assert life["metrics"]["ops_index"] == 71
