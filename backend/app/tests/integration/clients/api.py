"""HTTP API clients for acceptance tests (actual /api/v1 routes)."""

from __future__ import annotations

import time
from decimal import Decimal
from typing import Any

from fastapi.testclient import TestClient

from app.tests.integration.assertions.amounts import money_minor
from app.tests.integration.assertions.reporting import EvidenceLog


class ApiError(AssertionError):
    def __init__(self, message: str, *, status: int, body: Any) -> None:
        super().__init__(f"{message} (status={status}, body={body})")
        self.status = status
        self.body = body


class ApiClient:
    def __init__(
        self,
        client: TestClient,
        *,
        token: str,
        user_key: str,
        evidence: EvidenceLog | None = None,
    ) -> None:
        self._client = client
        self.token = token
        self.user_key = user_key
        self.evidence = evidence or EvidenceLog()
        self.user_id: str | None = None

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        title: str | None = None,
        expected_status: int | set[int] = 200,
        context: str | None = None,
    ) -> Any:
        expected = {expected_status} if isinstance(expected_status, int) else set(expected_status)
        t0 = time.perf_counter()
        resp = self._client.request(method, path, json=json, headers=self.headers)
        duration_ms = (time.perf_counter() - t0) * 1000
        try:
            body = resp.json()
        except Exception:
            body = {"raw": resp.text}
        ok = resp.status_code in expected
        self.evidence.record(
            title=title or f"{method} {path}",
            method=method,
            url=path,
            status_code=resp.status_code,
            request_json=json,
            response_json=body,
            duration_ms=duration_ms,
            user=self.user_key,
            context=context,
            passed=ok,
            error=None if ok else f"expected {expected}",
        )
        if not ok:
            raise ApiError(f"{method} {path} failed", status=resp.status_code, body=body)
        return body


class AuthClient:
    def __init__(self, client: TestClient, evidence: EvidenceLog | None = None) -> None:
        self._client = client
        self.evidence = evidence or EvidenceLog()

    def test_login(self, *, firebase_uid: str, display_name: str) -> ApiClient:
        t0 = time.perf_counter()
        resp = self._client.post(
            "/api/v1/auth/test/login",
            json={"firebase_uid": firebase_uid, "display_name": display_name},
        )
        duration_ms = (time.perf_counter() - t0) * 1000
        body = resp.json() if resp.content else {}
        self.evidence.record(
            title=f"test_login {display_name}",
            method="POST",
            url="/api/v1/auth/test/login",
            status_code=resp.status_code,
            request_json={"firebase_uid": firebase_uid, "display_name": display_name},
            response_json=body,
            duration_ms=duration_ms,
            user=display_name,
            context="auth",
            passed=resp.status_code == 200,
        )
        if resp.status_code != 200:
            raise ApiError("test login failed", status=resp.status_code, body=body)
        token = body["tokens"]["access_token"]
        api = ApiClient(self._client, token=token, user_key=display_name.lower(), evidence=self.evidence)
        api.user_id = body["user"]["id"]
        return api


class PersonalClient:
    def __init__(self, api: ApiClient) -> None:
        self.api = api

    def create_account(
        self,
        *,
        account_name: str,
        account_type: str,
        opening_balance: str,
        currency_code: str = "INR",
    ) -> dict:
        return self.api.request(
            "POST",
            "/api/v1/personal/accounts",
            json={
                "account_name": account_name,
                "account_type": account_type,
                "currency_code": currency_code,
                "opening_balance": opening_balance,
            },
            title=f"create account {account_name}",
            expected_status={200, 201},
            context="my_money",
        )

    def list_accounts(self) -> Any:
        return self.api.request(
            "GET",
            "/api/v1/personal/accounts",
            title="list accounts",
            context="my_money",
        )


class GroupClient:
    def __init__(self, api: ApiClient) -> None:
        self.api = api

    def create_shared_experience(self, *, profile: str = "TRIP_VACATION") -> str:
        data = self.api.request(
            "POST",
            "/api/v1/group/shared-experience/moments",
            json={"experience_profile": profile},
            title="create shared experience",
            expected_status=201,
            context="group",
        )
        return str(data["moment_id"])

    def setup_draft(self, moment_id: str, *, name: str = "Goa Trip", currency: str = "INR") -> None:
        self.api.request(
            "PUT",
            f"/api/v1/group/shared-experience/moments/{moment_id}/setup/draft",
            json={
                "answers": {
                    "moment_name": name,
                    "currency_code": currency,
                    "allow_multi_currency": False,
                    "money_tracking_mode": "EQUAL_SPLIT",
                }
            },
            title="setup draft",
            context="group",
        )

    def activate(self, moment_id: str) -> None:
        self.api.request(
            "POST",
            f"/api/v1/group/shared-experience/moments/{moment_id}/setup/activate",
            title="activate moment",
            context="group",
        )

    def add_guest(self, moment_id: str, body: dict[str, Any]) -> dict:
        return self.api.request(
            "POST",
            f"/api/v1/group/trips/{moment_id}/guests",
            json=body,
            title="add guest",
            expected_status={200, 201},
            context="group",
        )

    def create_expense(
        self,
        moment_id: str,
        *,
        title: str,
        amount: Decimal,
        paid_by_participant_id: str,
        participant_ids: list[str],
        split_style: str,
        client_request_id: str,
        split_details: list[dict[str, Any]] | None = None,
        currency_code: str = "INR",
    ) -> dict:
        payload: dict[str, Any] = {
            "title": title,
            "amount_minor": money_minor(amount),
            "currency_code": currency_code,
            "paid_by_participant_id": paid_by_participant_id,
            "participant_ids": participant_ids,
            "split_style": split_style,
            "client_request_id": client_request_id,
        }
        if split_details is not None:
            payload["split_details"] = split_details
        return self.api.request(
            "POST",
            f"/api/v1/group/trips/{moment_id}/expenses",
            json=payload,
            title=f"expense {title}",
            expected_status=201,
            context="group",
        )

    def list_expenses(self, moment_id: str) -> list:
        data = self.api.request(
            "GET",
            f"/api/v1/group/trips/{moment_id}/expenses",
            title="list expenses",
            context="group",
        )
        return data if isinstance(data, list) else data.get("expenses") or []

    def patch_expense(self, moment_id: str, expense_id: str, body: dict[str, Any]) -> dict:
        return self.api.request(
            "PATCH",
            f"/api/v1/group/trips/{moment_id}/expenses/{expense_id}",
            json=body,
            title=f"patch expense {expense_id}",
            context="group",
        )

    def delete_expense(self, moment_id: str, expense_id: str) -> Any:
        return self.api.request(
            "DELETE",
            f"/api/v1/group/trips/{moment_id}/expenses/{expense_id}",
            title=f"delete expense {expense_id}",
            expected_status={200, 204},
            context="group",
        )

    def settlement_preview(self, moment_id: str) -> dict:
        return self.api.request(
            "GET",
            f"/api/v1/group/moments/{moment_id}/settlements/preview",
            title="settlement preview",
            context="group",
        )

    def create_settlement(
        self,
        moment_id: str,
        *,
        from_member_id: str,
        to_member_id: str,
        amount: Decimal,
        client_request_id: str,
        currency_code: str = "INR",
        description: str | None = None,
    ) -> dict:
        return self.api.request(
            "POST",
            f"/api/v1/group/moments/{moment_id}/settlements",
            json={
                "from_member_id": from_member_id,
                "to_member_id": to_member_id,
                "amount_minor": money_minor(amount),
                "currency_code": currency_code,
                "client_request_id": client_request_id,
                "description": description,
            },
            title="create settlement",
            expected_status={200, 201},
            context="group",
        )

    def mark_settled(self, moment_id: str, settlement_id: str) -> dict:
        return self.api.request(
            "POST",
            f"/api/v1/group/moments/{moment_id}/settlements/{settlement_id}/mark-settled",
            title="mark settled",
            context="group",
        )
