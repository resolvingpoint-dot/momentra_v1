"""Phase 3 Group Home GraphQL contracts."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.application.queries.group_home import GroupHomeDTO
from app.application.queries.pulse import PulseTypeCardDTO
from app.domains.users.models import UserModel


def _gql(client: TestClient, query: str, headers: dict | None = None):
    return client.post("/graphql", json={"query": query}, headers=headers or {})


def test_group_home_unauthenticated(client: TestClient):
    resp = _gql(client, "query { groupHome { isEmpty } }")
    assert resp.status_code == 200
    body = resp.json()
    data = body.get("data") or {}
    assert data.get("groupHome") is None
    errors = body.get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "unauthenticated"


@patch("app.api.v1.auth.verify_firebase_token")
def test_group_home_happy_path(
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

    dto = GroupHomeDTO(
        is_empty=False,
        active_moment_count=2,
        hero_title="Your group moments",
        hero_subtitle="Together",
        cta_label="Create",
        cta_subtitle="Start",
        type_cards=[
            PulseTypeCardDTO(
                moment_type_id="1",
                moment_type_code="SHARED_EXPERIENCE",
                moment_type_name="Shared Experience",
            )
        ],
    )
    with patch(
        "app.api.graphql.queries.group_home.get_group_home",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              groupHome {
                isEmpty
                activeMomentCount
                heroTitle
                typeCards { momentTypeCode momentTypeName }
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    home = body["data"]["groupHome"]
    assert home["activeMomentCount"] == 2
    assert home["typeCards"][0]["momentTypeCode"] == "SHARED_EXPERIENCE"
