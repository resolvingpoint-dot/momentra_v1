"""Evidence logging for acceptance HTTP calls."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

_SENSITIVE = re.compile(
    r"(authorization|password|token|cookie|secret|api[-_]?key)",
    re.I,
)

_ARTIFACTS = Path(__file__).resolve().parents[4] / "artifacts"
# parents: assertions -> integration -> tests -> app -> backend — wrong
# __file__ = backend/app/tests/integration/assertions/reporting.py
# parents[0]=assertions, [1]=integration, [2]=tests, [3]=app, [4]=backend
# Want monorepo root artifacts or backend/artifacts


def _artifacts_dir() -> Path:
    # backend/artifacts
    backend_root = Path(__file__).resolve().parents[4]
    # parents[4] from reporting.py:
    # 0 assertions, 1 integration, 2 tests, 3 app, 4 backend — yes backend
    out = backend_root / "artifacts"
    out.mkdir(parents=True, exist_ok=True)
    return out


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if _SENSITIVE.search(str(k)):
                out[k] = "***REDACTED***"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str) and len(obj) > 40 and obj.startswith("eyJ"):
        return "***JWT***"
    return obj


class EvidenceLog:
    def __init__(self, scenario: str = "goa-trip") -> None:
        self.scenario = scenario
        self.steps: list[dict[str, Any]] = []
        self.path = _artifacts_dir() / "request-response-log.jsonl"

    def record(
        self,
        *,
        title: str,
        method: str,
        url: str,
        status_code: int,
        request_json: Any = None,
        response_json: Any = None,
        duration_ms: float,
        user: str | None = None,
        context: str | None = None,
        before: Any = None,
        after: Any = None,
        expected: Any = None,
        passed: bool = True,
        error: str | None = None,
    ) -> None:
        step = {
            "step": len(self.steps) + 1,
            "title": title,
            "timestamp": time.time(),
            "user": user,
            "context": context,
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "request": redact(request_json),
            "response": redact(response_json),
            "before_balances": before,
            "after_balances": after,
            "expected_balances": expected,
            "passed": passed,
            "error": error,
            "scenario": self.scenario,
        }
        self.steps.append(step)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(step, default=str) + "\n")


def write_acceptance_summary(payload: dict[str, Any]) -> Path:
    path = _artifacts_dir() / "acceptance-summary.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def write_ledger_summary(payload: dict[str, Any]) -> Path:
    path = _artifacts_dir() / "financial-ledger-summary.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path
