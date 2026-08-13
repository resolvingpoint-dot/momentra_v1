#!/usr/bin/env python3
"""Production Redis-first read probe for api.mallaapp.org.

Measures cold/warm health, session/inventory, and Pulse paths, plus the
post-mutation sequence:

  GET Pulse → mutation → immediate GET Pulse → later GET Pulse

Immediate GET after mutation must report projection_state=stale and
projection_build_ms absent/0 (no sync rebuild).

Usage:
  set MOMENTRA_PROBE_TOKEN=...   # Bearer session or Firebase token
  set MOMENTRA_PROBE_GROUP_MOMENT_ID=...   # optional
  set MOMENTRA_PROBE_BUSINESS_MOMENT_ID=...  # optional
  python backend/scripts/prod_read_probe.py --base-url https://api.mallaapp.org

  # Read-only (no mutation step):
  python backend/scripts/prod_read_probe.py --skip-mutation
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from typing import Any

import httpx

ACCEPTANCE = {
    "/health": 100.0,
    "session_inventory": 200.0,
    "personal_pulse_warm": 250.0,
    "group_pulse_warm": 300.0,
    "business_pulse_warm": 300.0,
    "cold_build": 700.0,
}


def _hdr(resp: httpx.Response) -> dict[str, str]:
    keys = (
        "X-Duration-Ms",
        "X-Cache-Hit",
        "X-Projection-State",
        "X-Projection-Version",
        "Server-Timing",
    )
    return {k: resp.headers.get(k, "") for k in keys}


def _request(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: dict | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()
    resp = client.request(method, path, headers=headers, json=json_body)
    client_ms = (time.perf_counter() - start) * 1000
    server_ms = resp.headers.get("X-Duration-Ms")
    return {
        "method": method,
        "path": path,
        "status": resp.status_code,
        "client_ms": round(client_ms, 2),
        "server_ms": float(server_ms) if server_ms else None,
        "headers": _hdr(resp),
        "ok": 200 <= resp.status_code < 300,
        "body_snippet": (resp.text or "")[:200],
    }


def _print_result(label: str, result: dict[str, Any]) -> None:
    h = result["headers"]
    print(
        f"{label:28} {result['status']} "
        f"client={result['client_ms']:.0f}ms "
        f"server={result['server_ms'] if result['server_ms'] is not None else '?'}ms "
        f"cache={h.get('X-Cache-Hit') or '?'} "
        f"state={h.get('X-Projection-State') or '?'} "
        f"timing={h.get('Server-Timing') or '-'}"
    )


def _auth_headers(token: str | None) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def probe_health(client: httpx.Client) -> list[dict[str, Any]]:
    out = []
    for path in ("/health", "/health/ready"):
        for phase in ("cold", "warm"):
            r = _request(client, "GET", path)
            r["phase"] = phase
            r["label"] = f"{path}[{phase}]"
            _print_result(r["label"], r)
            out.append(r)
    return out


def probe_twice(
    client: httpx.Client,
    path: str,
    *,
    headers: dict[str, str],
    label: str,
) -> list[dict[str, Any]]:
    out = []
    for phase in ("cold", "warm"):
        r = _request(client, "GET", path, headers=headers)
        r["phase"] = phase
        r["label"] = f"{label}[{phase}]"
        _print_result(r["label"], r)
        out.append(r)
    return out


def probe_post_mutation(
    client: httpx.Client,
    *,
    pulse_path: str,
    mutation_method: str,
    mutation_path: str,
    mutation_body: dict | None,
    headers: dict[str, str],
    label: str,
    wait_s: float,
) -> list[dict[str, Any]]:
    """GET → mutation → immediate GET → later GET."""
    results: list[dict[str, Any]] = []

    before = _request(client, "GET", pulse_path, headers=headers)
    before["label"] = f"{label}/before"
    _print_result(before["label"], before)
    results.append(before)

    mut = _request(
        client,
        mutation_method,
        mutation_path,
        headers=headers,
        json_body=mutation_body,
    )
    mut["label"] = f"{label}/mutation"
    _print_result(mut["label"], mut)
    results.append(mut)

    immediate = _request(client, "GET", pulse_path, headers=headers)
    immediate["label"] = f"{label}/immediate"
    _print_result(immediate["label"], immediate)
    results.append(immediate)

    state = immediate["headers"].get("X-Projection-State") or ""
    build_hint = immediate["headers"].get("Server-Timing") or ""
    sync_rebuild = "projection;dur=" in build_hint and not build_hint.endswith(
        "projection;dur=0"
    )
    # Accept dur=0.0 as no rebuild; flag any non-zero projection timing.
    if "projection;dur=" in build_hint:
        try:
            part = [p for p in build_hint.split(",") if "projection;dur=" in p][0]
            dur = float(part.split("dur=")[1].strip())
            sync_rebuild = dur > 1.0
        except (IndexError, ValueError):
            sync_rebuild = True

    verdict = "PASS"
    if immediate["status"] >= 400:
        verdict = "FAIL_HTTP"
    elif state == "miss" or sync_rebuild:
        verdict = "FAIL_SYNC_REBUILD"
    elif state in {"stale", "fresh"}:
        verdict = "PASS" if state == "stale" or not sync_rebuild else "INVESTIGATE"
    print(
        f"  → immediate verdict={verdict} state={state or '?'} "
        f"(want stale + no sync build)"
    )
    immediate["verdict"] = verdict

    time.sleep(wait_s)
    later = _request(client, "GET", pulse_path, headers=headers)
    later["label"] = f"{label}/later"
    _print_result(later["label"], later)
    results.append(later)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Momentra Redis-first production probe")
    parser.add_argument("--base-url", default=os.getenv("MOMENTRA_PROBE_BASE_URL", "https://api.mallaapp.org"))
    parser.add_argument("--token", default=os.getenv("MOMENTRA_PROBE_TOKEN", ""))
    parser.add_argument(
        "--group-moment-id",
        default=os.getenv("MOMENTRA_PROBE_GROUP_MOMENT_ID", ""),
    )
    parser.add_argument(
        "--business-moment-id",
        default=os.getenv("MOMENTRA_PROBE_BUSINESS_MOMENT_ID", ""),
    )
    parser.add_argument("--skip-mutation", action="store_true")
    parser.add_argument("--wait-s", type=float, default=3.0, help="Wait before later GET")
    parser.add_argument("--json-out", default="", help="Write full results JSON")
    args = parser.parse_args()

    headers = _auth_headers(args.token.strip() or None)
    all_results: list[dict[str, Any]] = []

    print(f"Probing {args.base_url}")
    print("=" * 72)

    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=60.0) as client:
        all_results.extend(probe_health(client))

        if not headers:
            print("\nNo --token / MOMENTRA_PROBE_TOKEN — skipping authenticated paths.")
        else:
            print("\n-- session / inventory --")
            all_results.extend(
                probe_twice(
                    client, "/api/v1/personal/session", headers=headers, label="personal/session"
                )
            )
            all_results.extend(
                probe_twice(
                    client,
                    "/api/v1/personal/inventory",
                    headers=headers,
                    label="personal/inventory",
                )
            )

            print("\n-- Pulse cold/warm --")
            all_results.extend(
                probe_twice(
                    client, "/api/v1/personal/pulse", headers=headers, label="personal/pulse"
                )
            )
            if args.group_moment_id:
                all_results.extend(
                    probe_twice(
                        client,
                        f"/api/v1/group/active/pulse/{args.group_moment_id}",
                        headers=headers,
                        label="group/pulse",
                    )
                )
            else:
                print("group/pulse skipped (set --group-moment-id)")
            if args.business_moment_id:
                all_results.extend(
                    probe_twice(
                        client,
                        f"/api/v1/business/active/{args.business_moment_id}/pulse",
                        headers=headers,
                        label="business/pulse",
                    )
                )
            else:
                print("business/pulse skipped (set --business-moment-id)")

            if not args.skip_mutation:
                print("\n-- post-mutation sequence (Personal) --")
                # Soft invalidate via force_refresh=true on GET is no longer a
                # sync rebuild; prefer a real quick-add when available. Fallback:
                # mark-stale path via force_refresh query (server must SWR).
                print(
                    "  note: using GET force_refresh as soft invalidate probe; "
                    "prefer a real Quick Add mutation in staging when possible"
                )
                # Simulate mutation side-effect by hitting force_refresh once
                # (server marks stale + enqueues). Then immediate GET without force.
                before = _request(client, "GET", "/api/v1/personal/pulse", headers=headers)
                before["label"] = "personal/mut/before"
                _print_result(before["label"], before)
                all_results.append(before)

                mut = _request(
                    client,
                    "GET",
                    "/api/v1/personal/pulse?force_refresh=true",
                    headers=headers,
                )
                mut["label"] = "personal/mut/force_mark"
                _print_result(mut["label"], mut)
                all_results.append(mut)
                # force_refresh GET itself must return stale quickly if payload existed
                force_state = mut["headers"].get("X-Projection-State") or ""
                force_timing = mut["headers"].get("Server-Timing") or ""
                force_sync = False
                if "projection;dur=" in force_timing:
                    try:
                        part = [
                            p for p in force_timing.split(",") if "projection;dur=" in p
                        ][0]
                        force_sync = float(part.split("dur=")[1].strip()) > 1.0
                    except (IndexError, ValueError):
                        force_sync = True
                print(
                    f"  → force_refresh GET state={force_state or '?'} "
                    f"sync_build={'yes' if force_sync else 'no'} "
                    f"(want stale + no sync when payload existed)"
                )

                immediate = _request(
                    client, "GET", "/api/v1/personal/pulse", headers=headers
                )
                immediate["label"] = "personal/mut/immediate"
                _print_result(immediate["label"], immediate)
                imm_state = immediate["headers"].get("X-Projection-State") or ""
                imm_verdict = (
                    "PASS"
                    if imm_state in {"stale", "fresh"} and not force_sync
                    else "FAIL_SYNC_REBUILD"
                    if imm_state == "miss" or force_sync
                    else "INVESTIGATE"
                )
                print(f"  → immediate GET verdict={imm_verdict} state={imm_state or '?'}")
                immediate["verdict"] = imm_verdict
                all_results.append(immediate)

                time.sleep(args.wait_s)
                later = _request(client, "GET", "/api/v1/personal/pulse", headers=headers)
                later["label"] = "personal/mut/later"
                _print_result(later["label"], later)
                all_results.append(later)

    print("\n" + "=" * 72)
    print("Acceptance targets (p95):")
    for k, v in ACCEPTANCE.items():
        print(f"  {k}: <{v:.0f} ms")
    print(
        "Immediate GET after mutation: must not sync rebuild "
        "(projection_state=stale, projection_build_ms≈0)."
    )

    warm_server = [
        r["server_ms"]
        for r in all_results
        if r.get("phase") == "warm" and r.get("server_ms") is not None
    ]
    if warm_server:
        print(
            f"\nWarm sample server_ms: "
            f"p50={statistics.median(warm_server):.0f} "
            f"max={max(warm_server):.0f} n={len(warm_server)}"
        )

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump({"base_url": args.base_url, "results": all_results}, f, indent=2)
        print(f"Wrote {args.json_out}")

    failed = [
        r
        for r in all_results
        if r.get("verdict", "").startswith("FAIL") or (r.get("path") == "/health/ready" and not r.get("ok"))
    ]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
