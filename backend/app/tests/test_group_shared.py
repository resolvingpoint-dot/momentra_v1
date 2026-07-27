from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


CATEGORIES = [
    ("shared-experience", "experience_profile", "TRIP_VACATION", "moment_name", "setup"),
    ("shared-purchase", "purchase_profile", "GIFT_POOL", "moment_name", "setup"),
    ("shared-living", "living_type", "FLATMATES", "living_name", "setup"),
]


@pytest.mark.parametrize("path,_pk,_pc,_nk,_sk", CATEGORIES)
@patch("app.dependencies.auth.verify_firebase_token")
def test_shared_profiles(mock_verify, client: TestClient, mock_db, sample_user: UserModel, path, _pk, _pc, _nk, _sk):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get(f"/api/v1/group/{path}/profiles", headers=AUTH)
    assert resp.status_code == 200, resp.text
    profiles = resp.json()["profiles"]
    assert profiles
    assert all(p["profile_code"] and p["profile_name"] for p in profiles)


@pytest.mark.parametrize("path,profile_key,profile_code,name_key,_sk", CATEGORIES)
@patch("app.dependencies.auth.verify_firebase_token")
def test_shared_setup_flow(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel, path, profile_key, profile_code, name_key, _sk
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        f"/api/v1/group/{path}/moments",
        json={profile_key: profile_code},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]

    setup = client.get(f"/api/v1/group/{path}/moments/{moment_id}/setup", headers=AUTH)
    assert setup.status_code == 200, setup.text
    assert setup.json()["profiles"]
    assert setup.json().get("saved_answers") is not None
    assert setup.json().get("moment_type_code")

    draft = client.put(
        f"/api/v1/group/{path}/moments/{moment_id}/setup/draft",
        json={profile_key: profile_code, name_key: "My Shared Moment"},
        headers=AUTH,
    )
    assert draft.status_code == 200, draft.text
    state = draft.json()
    assert state.get(name_key) == "My Shared Moment"

    preview = client.get(f"/api/v1/group/{path}/moments/{moment_id}/setup/preview", headers=AUTH)
    assert preview.status_code == 200, preview.text
    assert preview.json()["profile_code"] == profile_code
    assert preview.json()["insight_text"]
    assert preview.json().get("preview_blocks") is not None

    activate = client.post(f"/api/v1/group/{path}/moments/{moment_id}/setup/activate", headers=AUTH)
    assert activate.status_code == 200, activate.text
    assert activate.json()["lifecycle_status"] == "active"


@patch("app.dependencies.auth.verify_firebase_token")
def test_trip_product_aliases_round_trip(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    path = "shared-experience"

    created = client.post(
        f"/api/v1/group/{path}/moments",
        json={"experience_profile": "TRIP_VACATION"},
        headers=AUTH,
    )
    assert created.status_code == 201, created.text
    moment_id = created.json()["moment_id"]

    draft = client.put(
        f"/api/v1/group/{path}/moments/{moment_id}/setup/draft",
        json={
            "trip_name": "Goa 2026",
            "destination": "Goa",
            "start_date": "2026-08-01",
            "end_date": "2026-08-07",
            "participants": 4,
            "budget_currency": "INR",
            "estimated_budget": 50000,
            "split_style": "SPLIT_LATER",
            "trip_style": "TRIP_VACATION",
        },
        headers=AUTH,
    )
    assert draft.status_code == 200, draft.text
    body = draft.json()
    assert body["moment_name"] == "Goa 2026"
    assert body["trip_name"] == "Goa 2026"
    assert body["location"] == "Goa"
    assert body["destination"] == "Goa"
    assert body["expected_participants"] == 4
    assert body["money_tracking_mode"] == "SPLIT_LATER"
    assert body["saved_answers"]["trip_name"] == "Goa 2026"

    preview = client.get(f"/api/v1/group/{path}/moments/{moment_id}/setup/preview", headers=AUTH)
    assert preview.status_code == 200
    assert preview.json()["trip_name"] == "Goa 2026"
    assert any(b["label"] == "Destination" for b in preview.json()["preview_blocks"])
    assert any(b["label"] == "Shared Experience Name" for b in preview.json()["preview_blocks"])
    assert any(b["label"] == "Shared Experience Type" for b in preview.json()["preview_blocks"])


@patch("app.dependencies.auth.verify_firebase_token")
def test_experience_type_and_name_aliases(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    path = "shared-experience"
    created = client.post(
        f"/api/v1/group/{path}/moments",
        json={"experience_profile": "WEDDING"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    draft = client.put(
        f"/api/v1/group/{path}/moments/{moment_id}/setup/draft",
        json={
            "experience_type": "WEDDING",
            "experience_name": "Rahul & Priya Wedding",
            "start_date": "2026-10-01",
            "end_date": "2026-10-03",
        },
        headers=AUTH,
    )
    assert draft.status_code == 200, draft.text
    body = draft.json()
    assert body["moment_name"] == "Rahul & Priya Wedding"
    assert body["experience_name"] == "Rahul & Priya Wedding"
    assert body["experience_type"] == "WEDDING"
    assert body["experience_profile"] == "WEDDING"
    assert "Trip name" not in str(body.get("saved_answers", {}))
    preview = client.get(f"/api/v1/group/{path}/moments/{moment_id}/setup/preview", headers=AUTH)
    assert preview.status_code == 200
    labels = [b["label"] for b in preview.json()["preview_blocks"]]
    assert "Shared Experience Name" in labels
    assert "Trip name" not in labels


@patch("app.dependencies.auth.verify_firebase_token")
def test_end_date_before_start_rejected(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    created = client.post(
        "/api/v1/group/shared-experience/moments",
        json={"experience_profile": "TRIP_VACATION"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    draft = client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={"start_date": "2026-08-10", "end_date": "2026-08-01"},
        headers=AUTH,
    )
    assert draft.status_code == 400
    payload = draft.json()
    detail = payload.get("detail") or payload.get("message") or str(payload)
    assert "end_date" in str(detail)


@patch("app.dependencies.auth.verify_firebase_token")
def test_purchase_and_living_aliases(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    purchase = client.post(
        "/api/v1/group/shared-purchase/moments",
        json={"purchase_profile": "GIFT_POOL"},
        headers=AUTH,
    )
    pid = purchase.json()["moment_id"]
    draft = client.put(
        f"/api/v1/group/shared-purchase/moments/{pid}/setup/draft",
        json={
            "purchase_name": "Birthday Gift",
            "item_or_goal": "Watch",
            "expected_amount": 12000,
            "currency_code": "INR",
            "contributors": 3,
            "payment_plan": "EQUAL",
            "ownership_style": "SHARED",
            "decision_deadline": "2026-09-01",
        },
        headers=AUTH,
    )
    assert draft.status_code == 200, draft.text
    assert draft.json()["moment_name"] == "Birthday Gift"
    assert draft.json()["item_or_goal"] == "Watch"
    assert draft.json()["funding_style"] == "EQUAL"

    living = client.post(
        "/api/v1/group/shared-living/moments",
        json={"living_type": "FLATMATES"},
        headers=AUTH,
    )
    lid = living.json()["moment_id"]
    ldraft = client.put(
        f"/api/v1/group/shared-living/moments/{lid}/setup/draft",
        json={
            "home_name": "Indiranagar Flat",
            "members": 3,
            "monthly_budget": "45000",
            "currency_code": "INR",
            "rent_split_style": "SHARED",
            "chores_style": "ROTATION",
            "rules_or_notes": "Quiet after 11pm",
        },
        headers=AUTH,
    )
    assert ldraft.status_code == 200, ldraft.text
    assert ldraft.json()["living_name"] == "Indiranagar Flat"
    assert ldraft.json()["home_name"] == "Indiranagar Flat"
    assert ldraft.json()["expected_residents"] == 3
    assert ldraft.json()["chores_style"] == "ROTATION"
    assert ldraft.json()["management"] == "SHARED"


@patch("app.dependencies.auth.verify_firebase_token")
def test_answers_wrapper_and_activate_bootstrap(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/group/shared-experience/moments",
        json={"experience_profile": "TRIP_VACATION"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]

    draft = client.put(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
        json={"answers": {"trip_name": "Wrapped Trip", "destination": "Manali"}},
        headers=AUTH,
    )
    assert draft.status_code == 200
    assert draft.json()["moment_name"] == "Wrapped Trip"

    session = client.get("/api/v1/group/session/bootstrap", headers=AUTH)
    assert session.status_code == 200
    assert session.json().get("has_draft") is True
    assert session.json().get("draft_moment_id") == moment_id

    activate = client.post(
        f"/api/v1/group/shared-experience/moments/{moment_id}/setup/activate",
        headers=AUTH,
    )
    assert activate.status_code == 200
    assert activate.json()["lifecycle_status"] == "active"

    session2 = client.get("/api/v1/group/session/bootstrap", headers=AUTH)
    assert session2.status_code == 200
    assert session2.json().get("active_moment_id") == moment_id
    assert session2.json().get("has_draft") is False


@patch("app.dependencies.auth.verify_firebase_token")
def test_shared_setup_unknown_moment_404(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get(
        "/api/v1/group/shared-experience/moments/00000000-0000-0000-0000-000000000000/setup",
        headers=AUTH,
    )
    assert resp.status_code == 404


def test_shared_requires_auth(client: TestClient, mock_db):
    resp = client.get("/api/v1/group/shared-experience/profiles")
    assert resp.status_code == 401
