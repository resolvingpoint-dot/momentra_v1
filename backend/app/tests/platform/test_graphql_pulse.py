"""Phase 3 Pulse landing GraphQL contracts."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.application.queries.pulse import (
    BusinessPulseDTO,
    GroupPulseDTO,
    PersonalPulseDTO,
    PulseTypeCardDTO,
)
from app.domains.users.models import UserModel


def _gql(client: TestClient, query: str, variables: dict | None = None, headers: dict | None = None):
    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables
    return client.post("/graphql", json=payload, headers=headers or {})


def test_pulse_unauthenticated(client: TestClient):
    resp = _gql(client, "query { pulse(scope: PERSONAL) { __typename } }")
    assert resp.status_code == 200
    body = resp.json()
    data = body.get("data") or {}
    assert data.get("pulse") is None
    errors = body.get("errors") or []
    assert errors
    assert errors[0].get("extensions", {}).get("code") == "unauthenticated"


@patch("app.api.v1.auth.verify_firebase_token")
def test_pulse_personal_landing(
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

    dto = PersonalPulseDTO(
        overall_rhythm_state="STEADY",
        active_moment_count=2,
        is_empty=False,
        hero_title="Your rhythm",
        cta_label="Continue",
        life_operations={"rhythm_label": "On track"},
    )
    with patch(
        "app.api.graphql.queries.pulse.get_pulse_landing",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              pulse(scope: PERSONAL) {
                __typename
                ... on PersonalPulse {
                  overallRhythmState
                  activeMomentCount
                  isEmpty
                  heroTitle
                  lifeOperations
                }
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    pulse = body["data"]["pulse"]
    assert pulse["__typename"] == "PersonalPulse"
    assert pulse["overallRhythmState"] == "STEADY"
    assert pulse["activeMomentCount"] == 2
    assert pulse["lifeOperations"]["rhythm_label"] == "On track"


@patch("app.api.v1.auth.verify_firebase_token")
def test_pulse_group_landing(
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

    dto = GroupPulseDTO(
        is_empty=True,
        active_moment_count=0,
        hero_title="Better together",
        hero_subtitle="Plan together",
        type_cards=[
            PulseTypeCardDTO(
                moment_type_id="1",
                moment_type_code="SHARED_EXPERIENCE",
                moment_type_name="Shared Experience",
            )
        ],
    )
    with patch(
        "app.api.graphql.queries.pulse.get_pulse_landing",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              pulse(scope: GROUP) {
                __typename
                ... on GroupPulse {
                  heroTitle
                  isEmpty
                  typeCards { momentTypeCode momentTypeName }
                }
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    pulse = body["data"]["pulse"]
    assert pulse["__typename"] == "GroupPulse"
    assert pulse["typeCards"][0]["momentTypeCode"] == "SHARED_EXPERIENCE"


@patch("app.api.v1.auth.verify_firebase_token")
def test_pulse_business_landing(
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

    dto = BusinessPulseDTO(
        is_empty=True,
        active_moment_count=0,
        hero_title="Run with clarity",
        cta_label="Create",
    )
    with patch(
        "app.api.graphql.queries.pulse.get_pulse_landing",
        new_callable=AsyncMock,
        return_value=dto,
    ):
        resp = _gql(
            client,
            """
            query {
              pulse(scope: BUSINESS) {
                __typename
                ... on BusinessPulse {
                  heroTitle
                  ctaLabel
                  isEmpty
                }
              }
            }
            """,
            headers={"Authorization": f"Bearer {access}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert not body.get("errors"), body
    pulse = body["data"]["pulse"]
    assert pulse["__typename"] == "BusinessPulse"
    assert pulse["heroTitle"] == "Run with clarity"
