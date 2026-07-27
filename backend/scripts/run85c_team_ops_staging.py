#!/usr/bin/env python3
"""Run 8.5c — staging verification harness (HTTP only, no UI E2E)."""
from __future__ import annotations

import json
import statistics
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
OUT = Path(__file__).resolve().parent / "run85c_last_result.json"

COMPLETE_ANSWERS = {
    "moment_name": "85c Staging",
    "team_name": "85c Squad",
    "team_purpose": "Staging verification",
    "team_size": "SMALL",
    "work_style": "HYBRID",
    "operating_currency_code": "USD",
    "timezone": "America/New_York",
    "locale": "en-US",
    "country_code": "US",
    "coordination_style": "SHARED_OWNERSHIP",
    "monitoring_level": "STANDARD",
    "review_cycle": "MONTHLY",
    "visibility": "TEAM",
    "supported_roles": ["OWNER", "MEMBER", "APPROVER"],
    "approval_required_for_spend": False,
    "invite_on_activation": False,
    "members": [],
}

WARM_TARGETS_MS = {
    "pulse": 150,
    "moments": 200,
    "life": 200,
    "memory": 200,
    "activity": 250,
}


def login(client: httpx.Client, tag: str) -> dict[str, str]:
    r = client.post(
        "/api/v1/auth/test/login",
        json={"firebase_uid": f"test:85c-{tag}-{uuid.uuid4().hex[:8]}", "display_name": tag},
    )
    r.raise_for_status()
    token = r.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def timed_get(client: httpx.Client, path: str, headers: dict, *, bust: bool = False) -> tuple[float, int, str | None]:
    url = path
    if bust:
        sep = "&" if "?" in path else "?"
        url = f"{path}{sep}_bust={int(time.time() * 1000)}"
    t0 = time.perf_counter()
    r = client.get(url, headers=headers)
    ms = (time.perf_counter() - t0) * 1000
    return ms, r.status_code, r.headers.get("X-Cache-Hit")


def measure_surface(
    client: httpx.Client,
    name: str,
    path: str,
    headers: dict,
    *,
    warm_n: int = 15,
) -> dict:
    cold_ms, cold_status, cold_hit = timed_get(client, path, headers, bust=True)
    warms: list[float] = []
    hits = known = 0
    for _ in range(warm_n):
        ms, st, hit = timed_get(client, path, headers)
        if st >= 500:
            continue
        warms.append(ms)
        if hit is not None:
            known += 1
            if hit.lower() == "true":
                hits += 1
    warms_s = sorted(warms) if warms else [cold_ms]
    p50 = warms_s[len(warms_s) // 2]
    p95 = warms_s[int((len(warms_s) - 1) * 0.95)] if len(warms_s) > 1 else warms_s[0]
    return {
        "path": path,
        "cold_ms": round(cold_ms, 2),
        "cold_status": cold_status,
        "cold_x_cache_hit": cold_hit,
        "warm_p50_ms": round(p50, 2),
        "warm_p95_ms": round(p95, 2),
        "warm_avg_ms": round(sum(warms) / len(warms), 2) if warms else None,
        "warm_samples": len(warms),
        "cache_hit_rate": round(hits / known, 3) if known else None,
        "cache_hit_known": known,
        "cache_hits": hits,
    }


def main() -> int:
    blockers: list[str] = []
    report: dict = {}

    with httpx.Client(base_url=BASE, timeout=120.0) as client:
        # Part 1 — deployment
        live = client.get("/health/live")
        ready = client.get("/health/ready")
        report["deployment"] = {
            "live_status": live.status_code,
            "live": live.json() if live.status_code == 200 else live.text,
            "ready_status": ready.status_code,
            "ready": ready.json() if ready.status_code == 200 else ready.text,
        }
        if ready.status_code != 200:
            blockers.append(f"health/ready not 200: {ready.status_code}")
        else:
            body = ready.json()
            for dep in ("database", "redis", "celery"):
                if body.get(dep) != "up":
                    blockers.append(f"{dep} not up: {body.get(dep)}")

        owner_h = login(client, "owner")
        report["auth"] = {"ok": True}

        # Setup → activate
        mid = client.post(
            "/api/v1/business/moments",
            headers=owner_h,
            json={"moment_type_code": "TEAM_OPERATIONS", "title": "85c Staging"},
        ).json()["moment_id"]
        client.put(
            f"/api/v1/business/moments/{mid}/setup/draft",
            headers=owner_h,
            json={
                "answers": COMPLETE_ANSWERS,
                "progress": {"current_step": 4, "completed_steps": [1, 2, 3]},
                "template_id": "team_ops",
                "setup_version": "1",
            },
        )
        prev = client.post(
            f"/api/v1/business/moments/{mid}/setup/preview",
            headers=owner_h,
            json={"answers": COMPLETE_ANSWERS},
        )
        act = client.post(f"/api/v1/business/moments/{mid}/setup/activate", headers=owner_h)
        report["e2e_setup"] = {
            "moment_id": mid,
            "preview_ready": prev.json().get("activation_ready"),
            "activate_status": act.status_code,
            "activate_body_status": act.json().get("status") if act.status_code == 200 else act.text[:200],
        }
        if act.status_code != 200 or act.json().get("status") != "ACTIVE":
            blockers.append(f"activate failed: {act.status_code} {act.text[:120]}")

        # Part 2 — Redis cold/warm
        perf: dict = {}
        paths = {
            "pulse": f"/api/v1/business/active/{mid}/pulse",
            "moments": f"/api/v1/business/active/{mid}/moments",
            "life": "/api/v1/business/life",
            "memory": "/api/v1/business/memory",
            "activity_first_page": f"/api/v1/business/active/{mid}/activity?page=1&page_size=20",
        }
        for key, path in paths.items():
            perf[key] = measure_surface(client, key, path, owner_h)

        # Second-request cache hit spot check
        _, st1, h1 = timed_get(client, paths["life"], owner_h, bust=True)
        _, st2, h2 = timed_get(client, paths["life"], owner_h)
        report["redis_spot_check"] = {
            "life_first_hit": h1,
            "life_second_hit": h2,
            "life_second_status": st2,
        }
        if st2 == 200 and (h2 or "").lower() != "true":
            blockers.append("Redis warm Life second request X-Cache-Hit not true")

        report["performance"] = perf

        # Part 6 — perf targets (informational; remote DB may block)
        perf_failures = []
        for surf, limit in WARM_TARGETS_MS.items():
            key = "activity_first_page" if surf == "activity" else surf
            row = perf.get(key, {})
            p50 = row.get("warm_p50_ms")
            if p50 is not None and p50 >= limit:
                perf_failures.append(f"warm {surf} p50={p50}ms not <{limit}ms")
        report["performance_targets"] = {"failures": perf_failures, "met": not perf_failures}
        if perf_failures:
            blockers.extend(perf_failures)

        # Part 3 — Celery / mutations (async invalidate, no sync rebuild wait)
        t0 = time.perf_counter()
        cr = client.post(
            f"/api/v1/business/active/{mid}/activity",
            headers=owner_h,
            json={
                "action_type": "TEAM_UPDATE",
                "title": "85c standup",
                "payload": {"note": "x"},
                "source": "action_center",
                "client_request_id": str(uuid.uuid4()),
            },
        )
        create_ms = round((time.perf_counter() - t0) * 1000, 2)
        eid = None
        patch_ms = delete_ms = None
        patch_st = delete_st = None
        if cr.status_code < 300:
            body = cr.json()
            eid = body.get("event_id") or body.get("id")
        if eid:
            t0 = time.perf_counter()
            pr = client.patch(
                f"/api/v1/business/active/{mid}/activity/{eid}",
                headers=owner_h,
                json={"title": "edited"},
            )
            patch_ms = round((time.perf_counter() - t0) * 1000, 2)
            patch_st = pr.status_code
            t0 = time.perf_counter()
            dr = client.delete(f"/api/v1/business/active/{mid}/activity/{eid}", headers=owner_h)
            delete_ms = round((time.perf_counter() - t0) * 1000, 2)
            delete_st = dr.status_code

        for at, title in [("RECOGNITION", "kudos"), ("ISSUE", "bug"), ("APPROVAL_REQUEST", "approve")]:
            client.post(
                f"/api/v1/business/active/{mid}/activity",
                headers=owner_h,
                json={
                    "action_type": at,
                    "title": title,
                    "payload": {},
                    "source": "action_center",
                    "client_request_id": str(uuid.uuid4()),
                },
            )

        time.sleep(0.3)
        _, pulse_after_st, pulse_after_hit = timed_get(client, paths["pulse"], owner_h)

        report["activity_crud"] = {
            "create_status": cr.status_code,
            "create_ms": create_ms,
            "patch_status": patch_st,
            "patch_ms": patch_ms,
            "delete_status": delete_st,
            "delete_ms": delete_ms,
            "pulse_after_mutation_cache": pulse_after_hit,
            "pulse_after_mutation_status": pulse_after_st,
        }
        if cr.status_code >= 400:
            blockers.append(f"activity create failed: {cr.status_code}")

        # Part 5 — permissions (observer denied)
        obs_h = login(client, "observer")
        den = client.post(
            f"/api/v1/business/active/{mid}/activity",
            headers=obs_h,
            json={
                "action_type": "TEAM_UPDATE",
                "title": "nope",
                "payload": {},
                "source": "action_center",
            },
        )
        report["permissions"] = {
            "observer_create_status": den.status_code,
        }
        if den.status_code != 403:
            blockers.append(f"observer create expected 403 got {den.status_code}")

        # Archive (lifecycle)
        arc = client.post(f"/api/v1/business/moments/{mid}/archive", headers=owner_h)
        report["lifecycle"] = {
            "archive_status": arc.status_code,
            "archive_body": arc.text[:300],
        }
        if arc.status_code != 200:
            blockers.append(f"archive failed: {arc.status_code}")
        elif arc.json().get("status") != "ARCHIVED":
            blockers.append(f"archive status not ARCHIVED: {arc.json().get('status')}")

        # Parallel pulse
        def one_pulse(_: int) -> tuple[float, int, str | None]:
            return timed_get(client, paths["pulse"], owner_h)

        with ThreadPoolExecutor(10) as ex:
            outs = list(ex.map(one_pulse, range(10)))
        latencies = sorted(x[0] for x in outs)
        report["parallel_pulse"] = {
            "n": 10,
            "p50_ms": round(latencies[5], 2),
            "p95_ms": round(latencies[8], 2),
            "x_cache_hit_true": sum(1 for x in outs if (x[2] or "").lower() == "true"),
        }

    # Gaps that cannot be closed on this host
    report["gaps"] = {
        "web_ui_e2e": "NOT_RUN",
        "android_ui_e2e": "NOT_RUN",
        "ios_ui_e2e": "NOT_RUN",
        "ios_8_5b_smoke": "PENDING",
        "full_permission_matrix": "PARTIAL",
    }
    for gap in ("web_ui_e2e", "android_ui_e2e", "ios_ui_e2e", "ios_8_5b_smoke"):
        blockers.append(f"{gap}: NOT_RUN")

    decision = "COMPLETE" if not blockers else "BLOCKED"
    payload = {
        "run": "8.5c",
        "base_url": BASE,
        "report": report,
        "blockers": blockers,
        "decision": decision,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if decision == "COMPLETE" else 2


if __name__ == "__main__":
    sys.exit(main())
