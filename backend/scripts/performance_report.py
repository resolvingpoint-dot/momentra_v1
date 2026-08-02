"""
Aggregate performance journey results into artifacts/performance/*.

Usage:
  python backend/scripts/performance_report.py --input path/to/results.jsonl
  python backend/scripts/performance_report.py --demo

Does not auto-update baselines. Pass --check-baseline to emit regressions.json
and exit non-zero when regressions exceed tolerance.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


VERDICTS = {
    "PASS",
    "INVESTIGATE",
    "FAIL",
    "NOT MEASURED",
    "DEVICE VERIFICATION REQUIRED",
}

DIAGNOSIS = [
    "BACKEND",
    "DATABASE",
    "REDIS",
    "CELERY_QUEUE",
    "PROJECTION",
    "NETWORK",
    "WEB_RENDER",
    "ANDROID_CLIENT",
    "IOS_CLIENT",
    "CACHE_INVALIDATION",
    "DUPLICATE_REQUEST",
    "SEQUENTIAL_REQUESTS",
    "STATE_RECONCILIATION",
    "UNKNOWN",
]


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    k = (len(ordered) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return ordered[int(k)]
    return ordered[f] * (c - k) + ordered[c] * (k - f)


def summarize_flow(samples: list[dict[str, Any]]) -> dict[str, Any]:
    durations = [float(s["duration_ms"]) for s in samples if s.get("duration_ms") is not None]
    platforms = {s.get("platform") for s in samples}
    fails = [s for s in samples if s.get("verdict") == "FAIL" or s.get("success") is False]
    verdict = "PASS"
    if any(s.get("verdict") == "NOT MEASURED" for s in samples) and not durations:
        verdict = "NOT MEASURED"
    elif any(s.get("verdict") == "DEVICE VERIFICATION REQUIRED" for s in samples):
        verdict = "DEVICE VERIFICATION REQUIRED"
    elif fails:
        verdict = "FAIL"
    elif any(s.get("verdict") == "INVESTIGATE" for s in samples):
        verdict = "INVESTIGATE"

    diagnosis = "UNKNOWN"
    if fails:
        diagnosis = fails[0].get("diagnosis") or "UNKNOWN"

    return {
        "flow": samples[0].get("flow") or samples[0].get("name"),
        "n": len(samples),
        "platforms": sorted(p for p in platforms if p),
        "p50": percentile(durations, 50),
        "p75": percentile(durations, 75),
        "p95": percentile(durations, 95),
        "p99": percentile(durations, 99),
        "mean_not_primary": statistics.mean(durations) if durations else None,
        "request_count_p95": percentile(
            [float(s.get("request_count") or 0) for s in samples], 95
        ),
        "final_consistency_p95": percentile(
            [
                float(s["final_consistency_ms"])
                for s in samples
                if s.get("final_consistency_ms") is not None
            ],
            95,
        ),
        "verdict": verdict,
        "diagnosis": diagnosis,
        "waterfall": fails[0].get("waterfall") if fails else None,
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def demo_samples() -> list[dict[str, Any]]:
    """Parity-shaped demo: same flows across platforms for dashboard illustration."""
    rows: list[dict[str, Any]] = []
    # Business resume — Android outlier
    for platform, ms, verdict in [
        ("backend", 180, "PASS"),
        ("web", 420, "PASS"),
        ("android", 910, "INVESTIGATE"),
        ("ios", 440, "PASS"),
    ]:
        rows.append(
            {
                "flow": "setup.resume",
                "platform": platform,
                "duration_ms": ms,
                "backend_duration_ms": 180 if platform != "backend" else ms,
                "request_count": 2,
                "verdict": verdict,
                "success": True,
                "cold_warm_state": "cached",
                "context": "BUSINESS",
            }
        )
    # Quick Add — all pass
    for platform, ms in [("backend", 210), ("web", 320), ("android", 350), ("ios", 330)]:
        rows.append(
            {
                "flow": "quick_add.personal.expense",
                "platform": platform,
                "duration_ms": ms,
                "backend_duration_ms": 210 if platform != "backend" else ms,
                "request_count": 1,
                "final_consistency_ms": 900 if platform != "backend" else None,
                "verdict": "PASS",
                "success": True,
            }
        )
    # Delete — all pass
    for platform, ms in [("backend", 160), ("web", 290), ("android", 310), ("ios", 300)]:
        rows.append(
            {
                "flow": "mutation.delete",
                "platform": platform,
                "duration_ms": ms,
                "backend_duration_ms": 160 if platform != "backend" else ms,
                "request_count": 1,
                "verdict": "PASS",
                "success": True,
            }
        )
    # Activity refresh — shared projection delay
    for platform, ms in [("backend", 620), ("web", 910), ("android", 940), ("ios", 930)]:
        rows.append(
            {
                "flow": "activity.refresh",
                "platform": platform,
                "duration_ms": ms,
                "backend_duration_ms": 620 if platform != "backend" else ms,
                "request_count": 1,
                "verdict": "INVESTIGATE",
                "diagnosis": "PROJECTION",
                "success": True,
            }
        )
    return rows


def _p95_for_platform(samples: list[dict[str, Any]], platform: str) -> float | None:
    values = [
        float(s["duration_ms"])
        for s in samples
        if s.get("platform") == platform and s.get("duration_ms") is not None
    ]
    return percentile(values, 95)


def _backend_p95(samples: list[dict[str, Any]]) -> float | None:
    """Prefer platform=backend samples; else use backend_duration_ms from clients."""
    direct = _p95_for_platform(samples, "backend")
    if direct is not None:
        return direct
    values = [
        float(s["backend_duration_ms"])
        for s in samples
        if s.get("backend_duration_ms") is not None
    ]
    return percentile(values, 95)


def parity_verdict(row: dict[str, float | None | str]) -> str:
    """Attribute bottleneck: shared backend, one client, or all clients / projection."""
    backend = row.get("backend_p95")
    web = row.get("web_p95")
    android = row.get("android_p95")
    ios = row.get("ios_p95")
    clients = [(n, v) for n, v in (("web", web), ("android", android), ("ios", ios)) if v is not None]
    if backend is None and not clients:
        return "NOT MEASURED"
    if not clients:
        return "PASS" if backend is not None else "NOT MEASURED"

    # Shared projection / backend delay: all clients high and close to each other,
    # backend also elevated relative to client UX budgets (~300ms shell paths).
    if (
        backend is not None
        and backend >= 500
        and len(clients) >= 2
        and all(v >= 800 for _, v in clients)
    ):
        return "Projection delay"

    # Single-platform outlier: one client >= 1.5x median of other measured clients
    if len(clients) >= 2:
        vals = [v for _, v in clients]
        med = statistics.median(vals)
        outliers = [name for name, v in clients if med > 0 and v >= med * 1.5 and v >= 500]
        if len(outliers) == 1:
            label = {"web": "Web", "android": "Android", "ios": "iOS"}[outliers[0]]
            return f"{label} issue"

    if backend is not None and clients:
        client_min = min(v for _, v in clients)
        if backend >= 0.7 * client_min and backend >= 400:
            return "Backend issue"

    if any(v is not None and v >= 1000 for _, v in clients):
        return "INVESTIGATE"
    return "Pass"


def build_parity_dashboard(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_flow: dict[str, list[dict[str, Any]]] = {}
    for s in samples:
        key = str(s.get("flow") or s.get("name") or "unknown")
        by_flow.setdefault(key, []).append(s)

    rows: list[dict[str, Any]] = []
    for flow, group in sorted(by_flow.items()):
        row: dict[str, Any] = {
            "flow": flow,
            "backend_p95": _backend_p95(group),
            "web_p95": _p95_for_platform(group, "web"),
            "android_p95": _p95_for_platform(group, "android"),
            "ios_p95": _p95_for_platform(group, "ios"),
        }
        # Prefer explicit sample diagnosis when uniform
        diagnoses = {s.get("diagnosis") for s in group if s.get("diagnosis")}
        row["verdict"] = parity_verdict(row)
        if len(diagnoses) == 1:
            only = next(iter(diagnoses))
            if row["verdict"] == "Pass":
                row["verdict"] = only
            elif row["verdict"] == "INVESTIGATE" and only:
                row["verdict"] = only if only == "PROJECTION" else row["verdict"]
                if only == "PROJECTION":
                    row["verdict"] = "Projection delay"
        rows.append(row)
    return rows


def write_parity_dashboard(rows: list[dict[str, Any]], out_dir: Path) -> None:
    (out_dir / "platform-parity.json").write_text(
        json.dumps({"flows": rows}, indent=2), encoding="utf-8"
    )
    md = [
        "# Platform Parity Dashboard",
        "",
        "p95 durations in ms. Verdict attributes backend vs platform-specific vs shared projection delay.",
        "",
        "| Flow | Backend | Web | Android | iOS | Verdict |",
        "|------|---------|-----|---------|-----|---------|",
    ]
    for r in rows:
        md.append(
            "| {flow} | {backend} | {web} | {android} | {ios} | {verdict} |".format(
                flow=r["flow"],
                backend=_fmt(r.get("backend_p95")),
                web=_fmt(r.get("web_p95")),
                android=_fmt(r.get("android_p95")),
                ios=_fmt(r.get("ios_p95")),
                verdict=r.get("verdict") or "—",
            )
        )
    (out_dir / "platform-parity.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    with (out_dir / "platform-parity.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["flow", "backend_p95", "web_p95", "android_p95", "ios_p95", "verdict"])
        for r in rows:
            writer.writerow(
                [
                    r["flow"],
                    r.get("backend_p95"),
                    r.get("web_p95"),
                    r.get("android_p95"),
                    r.get("ios_p95"),
                    r.get("verdict"),
                ]
            )


def write_report(
    samples: list[dict[str, Any]],
    out_dir: Path,
    baseline: dict[str, Any] | None,
    tolerance_pct: float,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "flow-details").mkdir(exist_ok=True)

    by_flow: dict[str, list[dict[str, Any]]] = {}
    for s in samples:
        key = str(s.get("flow") or s.get("name") or "unknown")
        by_flow.setdefault(key, []).append(s)

    summaries = [summarize_flow(v) for v in by_flow.values()]
    summary = {
        "flows": summaries,
        "sample_count": len(samples),
        "verdicts_allowed": sorted(VERDICTS),
        "diagnosis_categories": DIAGNOSIS,
    }

    md_lines = [
        "# Performance summary",
        "",
        "| Flow | p50 | p95 | p99 | Requests p95 | Final consistency p95 | Verdict | Diagnosis |",
        "|------|-----|-----|-----|--------------|-----------------------|---------|-----------|",
    ]
    for f in summaries:
        md_lines.append(
            "| {flow} | {p50} | {p95} | {p99} | {req} | {fc} | {verdict} | {diag} |".format(
                flow=f["flow"],
                p50=_fmt(f["p50"]),
                p95=_fmt(f["p95"]),
                p99=_fmt(f["p99"]),
                req=_fmt(f["request_count_p95"]),
                fc=_fmt(f["final_consistency_p95"]),
                verdict=f["verdict"],
                diag=f["diagnosis"],
            )
        )
        detail_path = out_dir / "flow-details" / f"{f['flow'].replace('/', '_')}.json"
        detail_path.write_text(json.dumps(f, indent=2), encoding="utf-8")

    (out_dir / "latest-summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    parity_rows = build_parity_dashboard(samples)
    write_parity_dashboard(parity_rows, out_dir)
    summary["platform_parity"] = parity_rows
    (out_dir / "latest-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    with (out_dir / "platform-comparison.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "flow",
                "platforms",
                "p50",
                "p95",
                "p99",
                "requests_p95",
                "final_consistency_p95",
                "verdict",
            ]
        )
        for f in summaries:
            writer.writerow(
                [
                    f["flow"],
                    "|".join(f["platforms"]),
                    f["p50"],
                    f["p95"],
                    f["p99"],
                    f["request_count_p95"],
                    f["final_consistency_p95"],
                    f["verdict"],
                ]
            )

    regressions: list[dict[str, Any]] = []
    if baseline:
        base_flows = {b["flow"]: b for b in baseline.get("flows", [])}
        for f in summaries:
            prev = base_flows.get(f["flow"])
            if not prev or prev.get("p95") is None or f.get("p95") is None:
                continue
            prev_p95 = float(prev["p95"])
            if prev_p95 <= 0:
                continue
            delta = (float(f["p95"]) - prev_p95) / prev_p95 * 100.0
            if delta > tolerance_pct:
                regressions.append(
                    {
                        "flow": f["flow"],
                        "baseline_p95": prev_p95,
                        "current_p95": f["p95"],
                        "delta_pct": round(delta, 2),
                        "tolerance_pct": tolerance_pct,
                    }
                )
            req_base = prev.get("request_count_p95")
            req_cur = f.get("request_count_p95")
            if req_base is not None and req_cur is not None and float(req_cur) > float(req_base):
                regressions.append(
                    {
                        "flow": f["flow"],
                        "type": "request_count",
                        "baseline": req_base,
                        "current": req_cur,
                    }
                )

    (out_dir / "regressions.json").write_text(
        json.dumps({"regressions": regressions}, indent=2), encoding="utf-8"
    )
    return 1 if regressions else 0


def _fmt(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:.1f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="JSONL journey samples")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/performance"),
    )
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--check-baseline", action="store_true")
    parser.add_argument("--tolerance-pct", type=float, default=25.0)
    args = parser.parse_args()

    if args.demo:
        samples = demo_samples()
    elif args.input:
        samples = load_jsonl(args.input)
    else:
        parser.error("Provide --input or --demo")
        return 2

    baseline = None
    if args.baseline and args.baseline.exists():
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    elif args.check_baseline:
        default_base = args.out / "baselines" / "approved.json"
        if default_base.exists():
            baseline = json.loads(default_base.read_text(encoding="utf-8"))

    code = write_report(samples, args.out, baseline, args.tolerance_pct)
    print(f"Wrote report to {args.out}")
    if args.check_baseline:
        return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
