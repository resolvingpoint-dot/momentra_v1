"""Phase 3 Unified Activity GraphQL contracts."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.application.queries.activity import (
    ActivityScope,
    MomentActivityDTO,
    PersonalActivityDTO,
)
from app.domains.users.models import UserModel


def _gql(client: TestClient, query: str, variables: dict | None = None, headers: dict | None = None):
    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables
    return client.post("/graphql", json=payload, headers=headers or {})


def _auth(client: TestClient, mock_verify, mock_db, sample_user: UserModel) -> str:
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
    return exchange.json()["tokens"]["access_token"]


def test_activity_unauthenticated(client: TestClient):
    resp = _gql(client, "query { activity(scope: PERSONAL) { __typename } }")
    assert resp.status_code == 200
    body = resp.json()
    data = body.get("data") or {}
    assert data.get("activity") is None
    errors = body.get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "unauthenticated"


@patch("app.api.v1.auth.verify_firebase_token")
def test_activity_personal_unified(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    access = _auth(client, mock_verify, mock_db, sample_user)
    dto = PersonalActivityDTO(
        snapshot={
            "headline": "Quiet day",
            "today_activity_count": 1,
            "today_amount_minor": 500,
        },
        insights=[{"id": "i1", "kind": "spend", "title": "Spend", "value": "₹5"}],
        items=[{"id": "a1", "title": "Coffee"}],
        next_cursor=None,
    )
    with patch(
        "app.api.graphql.queries.activity.get_activity",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              activity(scope: PERSONAL, range: "week") {
                __typename
                ... on PersonalActivityFeed {
                  snapshot { headline todayActivityCount }
                  insights { id title }
                  items
                }
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    feed = body["data"]["activity"]
    assert feed["__typename"] == "PersonalActivityFeed"
    assert feed["snapshot"]["headline"] == "Quiet day"
    assert feed["items"][0]["title"] == "Coffee"


@patch("app.api.v1.auth.verify_firebase_token")
def test_activity_group_moment(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    access = _auth(client, mock_verify, mock_db, sample_user)
    mid = uuid4()
    dto = MomentActivityDTO(
        scope=ActivityScope.GROUP,
        moment_id=mid,
        items=[{"id": "e1", "title": "Paid rent"}],
        total=1,
        summary={"total": 1},
        payload={"moment_id": str(mid), "items": [{"id": "e1"}]},
    )
    with patch(
        "app.api.graphql.queries.activity.get_activity",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query ($id: ID!) {
              activity(scope: GROUP, momentId: $id) {
                __typename
                ... on GroupActivityFeed {
                  momentId
                  total
                  items
                }
              }
            }
            """,
            variables={"id": str(mid)},
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    feed = body["data"]["activity"]
    assert feed["__typename"] == "GroupActivityFeed"
    assert feed["total"] == 1


@patch("app.api.v1.auth.verify_firebase_token")
def test_activity_not_found_null(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    from app.core.errors import NotFoundError

    access = _auth(client, mock_verify, mock_db, sample_user)
    with patch(
        "app.api.graphql.queries.activity.get_activity",
        new_callable=AsyncMock,
        side_effect=NotFoundError("Moment not found", code="not_found"),
    ):
        resp = _gql(
            client,
            """
            query ($id: ID!) {
              activity(scope: BUSINESS, momentId: $id) { __typename }
            }
            """,
            variables={"id": str(uuid4())},
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    assert body["data"]["activity"] is None
