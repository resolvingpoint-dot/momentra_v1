"""Phase 3 Business Home GraphQL contracts."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.application.queries.business_home import BusinessHomeDTO
from app.application.queries.pulse import PulseTypeCardDTO
from app.domains.users.models import UserModel


def _gql(client: TestClient, query: str, headers: dict | None = None):
    return client.post("/graphql", json={"query": query}, headers=headers or {})


def test_business_home_unauthenticated(client: TestClient):
    resp = _gql(client, "query { businessHome { isEmpty } }")
    assert resp.status_code == 200
    body = resp.json()
    data = body.get("data") or {}
    assert data.get("businessHome") is None
    errors = body.get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "unauthenticated"


@patch("app.api.v1.auth.verify_firebase_token")
def test_business_home_happy_path(
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

    dto = BusinessHomeDTO(
        is_empty=True,
        active_moment_count=0,
        hero_title="Your business moments",
        hero_subtitle="Operate in one place",
        cta_label="Create",
        cards=[
            PulseTypeCardDTO(
                moment_type_id="1",
                moment_type_code="BUSINESS_OPERATIONS",
                moment_type_name="Operations",
            )
        ],
        info_card_items=[{"item_code": "tip", "title": "Tip"}],
    )
    with patch(
        "app.api.graphql.queries.business_home.get_business_home",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              businessHome {
                isEmpty
                heroTitle
                cards { momentTypeCode }
                infoCardItems
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    home = body["data"]["businessHome"]
    assert home["heroTitle"] == "Your business moments"
    assert home["cards"][0]["momentTypeCode"] == "BUSINESS_OPERATIONS"
