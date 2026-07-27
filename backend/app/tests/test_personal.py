from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.domains.personal.catalog import MOMENT_TYPES, moment_type_id
from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


@patch("app.dependencies.auth.verify_firebase_token")
def test_pulse_empty_state(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/personal/pulse", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_empty"] is True
    assert data["active_moment_count"] == 0
    assert data["overall_rhythm_state"] == "EMPTY"


@patch("app.dependencies.auth.verify_firebase_token")
def test_session_bootstrap_shape(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/personal/session/bootstrap", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert "pulse" in data and "moments_home" in data
    assert data["pulse"]["is_empty"] is True
    # moments_home always exposes one card per personal moment type
    assert len(data["moments_home"]["cards"]) == len(MOMENT_TYPES)


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_options_lists_all_types(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/personal/create/options", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    codes = {c["moment_type_code"] for c in data["cards"]}
    assert codes == {mt.code for mt in MOMENT_TYPES}


@patch("app.dependencies.auth.verify_firebase_token")
def test_list_moment_types(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.get("/api/v1/personal/moment-types", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(MOMENT_TYPES)
    assert data[0]["moment_type_id"] == moment_type_id(data[0]["moment_type_code"])


@patch("app.dependencies.auth.verify_firebase_token")
def test_create_and_list_moment(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "LIFE_OPERATIONS", "moment_name": "My Operations"},
        headers=AUTH,
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["moment_type_code"] == "LIFE_OPERATIONS"
    assert created["moment_name"] == "My Operations"
    assert created["moment_type_id"] == moment_type_id("LIFE_OPERATIONS")
    assert created["status"] == "DRAFT"

    listed = client.get("/api/v1/personal/moments", headers=AUTH)
    assert listed.status_code == 200
    ids = {m["moment_id"] for m in listed.json()}
    assert created["moment_id"] in ids


@patch("app.dependencies.auth.verify_firebase_token")
def test_memory_and_life_empty(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    mem = client.get("/api/v1/personal/memory", headers=AUTH)
    assert mem.status_code == 200
    assert mem.json()["is_empty"] is True

    life = client.get("/api/v1/personal/life", headers=AUTH)
    assert life.status_code == 200
    assert life.json()["is_empty"] is True


@patch("app.dependencies.auth.verify_firebase_token")
def test_quick_add_options_and_submit(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    opts = client.get("/api/v1/personal/live/quick-add/options", headers=AUTH)
    assert opts.status_code == 200
    body = opts.json()
    assert "moments" in body and "tabs" in body
    assert len(body["tabs"]) == 5
    assert body["metadata"] is not None
    tab_types = {t["event_type"] for t in body["tabs"]}
    assert tab_types == {"EXPENSE", "COMMITMENT", "RECOVERY", "REFLECTION", "RHYTHM"}
    for tab in body["tabs"]:
        assert tab.get("description")
    status_opts = body["metadata"]["commitment_status_options"]
    assert status_opts[0]["value"]
    assert status_opts[0]["label"]

    submit = client.post(
        "/api/v1/personal/live/quick-add",
        json={"moment_id": "abc", "event_type": "EXPENSE", "event_title": "Coffee"},
        headers=AUTH,
    )
    assert submit.status_code in (400, 422)


@patch("app.dependencies.auth.verify_firebase_token")
def test_accounts_and_master_expense_options(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)

    accounts = client.get("/api/v1/personal/accounts", headers=AUTH)
    assert accounts.status_code == 200
    assert accounts.json() == []

    options = client.get("/api/v1/personal/master-expense/options", headers=AUTH)
    assert options.status_code == 200
    assert "accounts" in options.json()


@patch("app.dependencies.auth.verify_firebase_token")
def test_requires_auth(mock_verify, client: TestClient, mock_db):
    resp = client.get("/api/v1/personal/pulse")
    assert resp.status_code == 401


@patch("app.dependencies.auth.verify_firebase_token")
@patch("app.workers.procedures.refresh_personal_orchestration", new_callable=AsyncMock)
def test_aggregate_pulse_includes_future_building_block(
    _mock_orch, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "FUTURE_BUILDING", "moment_name": "Future"},
        headers=AUTH,
    )
    moment_id = created.json()["moment_id"]
    client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={
            "answers": {
                "building_focus": "CAREER_GROWTH",
                "current_state": "JUST_STARTING",
                "values": ["GROWTH"],
                "friction_sources": ["LACK_OF_TIME"],
                "momentum_drivers": ["LEARNING"],
                "future_feeling": "HOPEFUL",
            }
        },
        headers=AUTH,
    )

    resp = client.get("/api/v1/personal/pulse", headers=AUTH)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_empty"] is False
    assert data["future_building"] is not None
    assert data["future_building"]["metrics"] is not None


FB_SETUP_ANSWERS = {
    "building_focus": "CAREER_GROWTH",
    "current_state": "JUST_STARTING",
    "values": ["GROWTH"],
    "friction_sources": ["LACK_OF_TIME"],
    "momentum_drivers": ["LEARNING"],
    "future_feeling": "HOPEFUL",
}


@patch("app.dependencies.auth.verify_firebase_token")
@patch(
    "app.workers.procedures.refresh_personal_orchestration",
    new_callable=AsyncMock,
    side_effect=RuntimeError("orchestration proc unavailable"),
)
def test_future_building_setup_commit_succeeds_when_orchestration_fails(
    _mock_orch, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "FUTURE_BUILDING", "moment_name": "Future"},
        headers=AUTH,
    )
    assert created.status_code == 201
    moment_id = created.json()["moment_id"]

    commit = client.post(
        f"/api/v1/personal/moments/{moment_id}/setup",
        json={"answers": FB_SETUP_ANSWERS},
        headers=AUTH,
    )
    assert commit.status_code == 200
    body = commit.json()
    assert body["status"] == "ACTIVE"
    assert body["moment_id"] == moment_id


@patch("app.dependencies.auth.verify_firebase_token")
@patch(
    "app.workers.procedures.refresh_personal_orchestration",
    new_callable=AsyncMock,
)
@patch(
    "app.domains.personal.app_service.try_ensure_personal_moment",
    new_callable=AsyncMock,
    return_value=False,
)
def test_future_building_setup_commit_ensures_personal_moment_before_profile(
    _mock_try_ensure,
    _mock_orch,
    mock_verify,
    client: TestClient,
    mock_db,
    sample_user: UserModel,
):
    """Regression: profile upsert requires personal_moments FK even when create-time sync failed."""
    from unittest.mock import call

    from app.domains.personal import app_service

    _auth(mock_verify)
    mock_db.add(sample_user)

    created = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "FUTURE_BUILDING", "moment_name": "Future"},
        headers=AUTH,
    )
    assert created.status_code == 201
    moment_id = created.json()["moment_id"]

    with patch.object(
        app_service,
        "ensure_personal_moment",
        new_callable=AsyncMock,
    ) as mock_ensure:
        commit = client.post(
            f"/api/v1/personal/moments/{moment_id}/setup",
            json={"answers": FB_SETUP_ANSWERS},
            headers=AUTH,
        )
        assert commit.status_code == 200
        assert commit.json()["status"] == "ACTIVE"
        assert mock_ensure.await_count >= 1
        first_call = mock_ensure.await_args_list[0]
        assert first_call == call(mock_db, mock_db._stores["moments"][moment_id])

@patch("app.dependencies.auth.verify_firebase_token")
@patch(
    "app.workers.procedures.refresh_personal_orchestration",
    new_callable=AsyncMock,
)
def test_create_options_prefers_active_over_newer_draft(
    _mock_orch, mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """When duplicate moments exist per type, link cards to ACTIVE not newest DRAFT."""
    _auth(mock_verify)
    mock_db.add(sample_user)

    lo = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "LIFE_OPERATIONS", "moment_name": "Ops"},
        headers=AUTH,
    )
    assert lo.status_code == 201
    lo_id = lo.json()["moment_id"]
    lo_commit = client.post(
        f"/api/v1/personal/moments/{lo_id}/setup",
        json={"answers": {}},
        headers=AUTH,
    )
    assert lo_commit.status_code == 200

    fb = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "FUTURE_BUILDING", "moment_name": "Future"},
        headers=AUTH,
    )
    assert fb.status_code == 201
    fb_id = fb.json()["moment_id"]
    fb_commit = client.post(
        f"/api/v1/personal/moments/{fb_id}/setup",
        json={"answers": FB_SETUP_ANSWERS},
        headers=AUTH,
    )
    assert fb_commit.status_code == 200

    newer_draft = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "FUTURE_BUILDING", "moment_name": "Future retry"},
        headers=AUTH,
    )
    assert newer_draft.status_code == 201
    assert newer_draft.json()["moment_id"] != fb_id

    opts = client.get("/api/v1/personal/create/options", headers=AUTH)
    assert opts.status_code == 200
    cards = {c["moment_type_code"]: c for c in opts.json()["cards"]}
    assert cards["FUTURE_BUILDING"]["linked_moment_id"] == fb_id
    assert cards["FUTURE_BUILDING"]["linked_moment_status"] == "ACTIVE"

    home = client.get("/api/v1/personal/moments/home", headers=AUTH)
    assert home.status_code == 200
    home_cards = {c["moment_type_code"]: c for c in home.json()["cards"]}
    assert home_cards["FUTURE_BUILDING"]["is_active"] is True
    assert home_cards["FUTURE_BUILDING"]["linked_moment_id"] == fb_id
