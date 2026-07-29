"""Phase 3 Personal Home GraphQL contracts."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.application.queries.personal_home import PersonalHomeCardDTO, PersonalHomeDTO
from app.domains.users.models import UserModel


def _gql(client: TestClient, query: str, headers: dict | None = None):
    return client.post("/graphql", json={"query": query}, headers=headers or {})


def test_personal_home_unauthenticated(client: TestClient):
    resp = _gql(client, "query { personalHome { isEmpty } }")
    assert resp.status_code == 200
    body = resp.json()
    data = body.get("data") or {}
    assert data.get("personalHome") is None
    errors = body.get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "unauthenticated"


@patch("app.api.v1.auth.verify_firebase_token")
def test_personal_home_happy_path(
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

    dto = PersonalHomeDTO(
        active_moment_count=1,
        is_empty=False,
        subtitle="Your OS",
        cards=[
            PersonalHomeCardDTO(
                moment_type_id="1",
                moment_type_code="LIFE_OPERATIONS",
                moment_type_name="Life Operations",
                is_active=True,
                action_label="Open",
            )
        ],
        future_building_detail={"kpis": []},
    )
    with patch(
        "app.api.graphql.queries.personal_home.get_personal_home",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              personalHome {
                isEmpty
                activeMomentCount
                subtitle
                cards { momentTypeCode momentTypeName isActive actionLabel }
                futureBuildingDetail
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    home = body["data"]["personalHome"]
    assert home["isEmpty"] is False
    assert home["cards"][0]["momentTypeCode"] == "LIFE_OPERATIONS"
    assert home["futureBuildingDetail"]["kpis"] == []
