"""In-process HTTP metrics for optional Prometheus scrape."""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from app.domains.projections.projection_metrics import get_counters as projection_counters

_lock = Lock()
_request_count: dict[tuple[str, str, str], int] = defaultdict(int)
_request_duration_ms: dict[tuple[str, str], float] = defaultdict(float)
_request_duration_count: dict[tuple[str, str], int] = defaultdict(int)
_graphql_count: dict[tuple[str, str], int] = defaultdict(int)
_graphql_duration_ms: dict[str, float] = defaultdict(float)
_graphql_duration_count: dict[str, int] = defaultdict(int)
_graphql_apq: dict[str, int] = defaultdict(int)
_graphql_complexity_sum: float = 0.0
_graphql_complexity_count: int = 0
_graphql_dataloader_batches: int = 0
_graphql_sql_count: int = 0
_graphql_rejects: dict[str, int] = defaultdict(int)
_started_at = time.time()


def record_request(method: str, path: str, status: int, duration_ms: float) -> None:
    # Collapse high-cardinality UUID path segments to keep cardinality bounded.
    normalized = _normalize_path(path)
    status_class = f"{status // 100}xx"
    key = (method.upper(), normalized, status_class)
    dur_key = (method.upper(), normalized)
    with _lock:
        _request_count[key] += 1
        _request_duration_ms[dur_key] += duration_ms
        _request_duration_count[dur_key] += 1


def record_graphql_operation(operation_name: str, outcome: str) -> None:
    name = (operation_name or "anonymous")[:64]
    result = outcome if outcome in {"ok", "error"} else "error"
    with _lock:
        _graphql_count[(name, result)] += 1


def record_graphql_detail(
    *,
    operation: str,
    duration_ms: float,
    complexity: int,
    depth: int,
    apq_status: str,
    outcome: str,
    sql_count: int = 0,
    dataloader_batches: int = 0,
) -> None:
    name = (operation or "anonymous")[:64]
    with _lock:
        _graphql_duration_ms[name] += duration_ms
        _graphql_duration_count[name] += 1
        _graphql_apq[apq_status or "bypass"] += 1
        global _graphql_complexity_sum, _graphql_complexity_count
        global _graphql_dataloader_batches, _graphql_sql_count
        _graphql_complexity_sum += max(0, complexity)
        _graphql_complexity_count += 1
        _graphql_dataloader_batches += max(0, dataloader_batches)
        _graphql_sql_count += max(0, sql_count)
        if outcome != "ok":
            _graphql_rejects[outcome] += 1


def record_graphql_reject(code: str) -> None:
    with _lock:
        _graphql_rejects[(code or "error")[:64]] += 1


def _normalize_path(path: str) -> str:
    parts = path.split("/")
    out: list[str] = []
    for part in parts:
        if not part:
            out.append(part)
            continue
        if len(part) >= 32 and all(c in "0123456789abcdefABCDEF-" for c in part):
            out.append("{id}")
        else:
            out.append(part)
    return "/".join(out) or "/"


def render_prometheus() -> str:
    lines: list[str] = [
        "# HELP momentra_up Momentra API process up",
        "# TYPE momentra_up gauge",
        "momentra_up 1",
        "# HELP momentra_process_uptime_seconds Process uptime",
        "# TYPE momentra_process_uptime_seconds gauge",
        f"momentra_process_uptime_seconds {time.time() - _started_at:.3f}",
        "# HELP momentra_http_requests_total HTTP requests by method, path, status class",
        "# TYPE momentra_http_requests_total counter",
    ]
    with _lock:
        for (method, path, status_class), count in sorted(_request_count.items()):
            lines.append(
                f'momentra_http_requests_total{{method="{method}",path="{path}",status="{status_class}"}} {count}'
            )
        lines.append(
            "# HELP momentra_http_request_duration_ms_sum Sum of request durations in ms"
        )
        lines.append("# TYPE momentra_http_request_duration_ms_sum counter")
        for (method, path), total in sorted(_request_duration_ms.items()):
            lines.append(
                f'momentra_http_request_duration_ms_sum{{method="{method}",path="{path}"}} {total:.3f}'
            )
        lines.append(
            "# HELP momentra_http_request_duration_ms_count Count of timed requests"
        )
        lines.append("# TYPE momentra_http_request_duration_ms_count counter")
        for (method, path), count in sorted(_request_duration_count.items()):
            lines.append(
                f'momentra_http_request_duration_ms_count{{method="{method}",path="{path}"}} {count}'
            )
        lines.append(
            "# HELP momentra_graphql_operations_total GraphQL operations by name and outcome"
        )
        lines.append("# TYPE momentra_graphql_operations_total counter")
        for (op_name, outcome), count in sorted(_graphql_count.items()):
            lines.append(
                f'momentra_graphql_operations_total{{operation="{op_name}",outcome="{outcome}"}} {count}'
            )
        lines.append(
            "# HELP momentra_graphql_duration_ms_sum GraphQL operation duration sum"
        )
        lines.append("# TYPE momentra_graphql_duration_ms_sum counter")
        for op_name, total in sorted(_graphql_duration_ms.items()):
            lines.append(
                f'momentra_graphql_duration_ms_sum{{operation="{op_name}"}} {total:.3f}'
            )
        lines.append(
            "# HELP momentra_graphql_duration_ms_count GraphQL operation duration count"
        )
        lines.append("# TYPE momentra_graphql_duration_ms_count counter")
        for op_name, count in sorted(_graphql_duration_count.items()):
            lines.append(
                f'momentra_graphql_duration_ms_count{{operation="{op_name}"}} {count}'
            )
        lines.append("# HELP momentra_graphql_apq_total APQ hit/miss/store/bypass")
        lines.append("# TYPE momentra_graphql_apq_total counter")
        for status, count in sorted(_graphql_apq.items()):
            lines.append(f'momentra_graphql_apq_total{{status="{status}"}} {count}')
        lines.append(
            "# HELP momentra_graphql_complexity_sum Sum of measured query complexities"
        )
        lines.append("# TYPE momentra_graphql_complexity_sum counter")
        lines.append(f"momentra_graphql_complexity_sum {_graphql_complexity_sum:.3f}")
        lines.append("# HELP momentra_graphql_complexity_count Complexity samples")
        lines.append("# TYPE momentra_graphql_complexity_count counter")
        lines.append(f"momentra_graphql_complexity_count {_graphql_complexity_count}")
        lines.append(
            "# HELP momentra_graphql_dataloader_batches_total DataLoader batch invocations"
        )
        lines.append("# TYPE momentra_graphql_dataloader_batches_total counter")
        lines.append(
            f"momentra_graphql_dataloader_batches_total {_graphql_dataloader_batches}"
        )
        lines.append("# HELP momentra_graphql_sql_statements_total SQL statements in GQL")
        lines.append("# TYPE momentra_graphql_sql_statements_total counter")
        lines.append(f"momentra_graphql_sql_statements_total {_graphql_sql_count}")
        lines.append("# HELP momentra_graphql_rejects_total GraphQL reject outcomes")
        lines.append("# TYPE momentra_graphql_rejects_total counter")
        for code, count in sorted(_graphql_rejects.items()):
            lines.append(f'momentra_graphql_rejects_total{{code="{code}"}} {count}')

    proj = projection_counters()
    lines.append("# HELP momentra_projection_cache_hit_total Projection cache hits")
    lines.append("# TYPE momentra_projection_cache_hit_total counter")
    lines.append(
        f"momentra_projection_cache_hit_total {int(proj.get('projection_cache_hit', 0))}"
    )
    lines.append("# HELP momentra_projection_cache_miss_total Projection cache misses")
    lines.append("# TYPE momentra_projection_cache_miss_total counter")
    lines.append(
        f"momentra_projection_cache_miss_total {int(proj.get('projection_cache_miss', 0))}"
    )
    return "\n".join(lines) + "\n"
