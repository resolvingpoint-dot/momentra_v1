"""Safety guards for financial acceptance tests."""

from __future__ import annotations

import os

# Hard refuse these substrings in acceptance DB URLs (case-insensitive),
# unless the database name is explicitly momentra_test.
_FORBIDDEN = (
    "prod",
    "production",
    "supabase.co",
    "neon.tech",
    "amazonaws.com",
    "azure.com",
    "cloudsql",
)


def assert_safe_acceptance_database_url(url: str | None) -> str:
    """Abort if URL looks like production or is not momentra_test."""
    if not url or not url.strip():
        raise RuntimeError(
            "Acceptance tests require ACCEPTANCE_DATABASE_URL or DATABASE_URL "
            "pointing at an isolated `momentra_test` database."
        )
    cleaned = url.strip()
    lower = cleaned.lower()
    if "momentra_test" not in lower:
        raise RuntimeError(
            "Acceptance DATABASE_URL must include database name `momentra_test`. "
            f"Got: {cleaned.split('@')[-1] if '@' in cleaned else cleaned}"
        )
    for needle in _FORBIDDEN:
        if needle in lower.replace("momentra_test", ""):
            raise RuntimeError(
                f"Refusing acceptance against suspected production DB (matched '{needle}'). "
                "Use docker-compose.test.yml / momentra_test only."
            )
    return cleaned


def acceptance_database_url_from_env() -> str | None:
    return (
        os.environ.get("ACCEPTANCE_DATABASE_URL")
        or os.environ.get("DATABASE_URL")
        or None
    )


def require_test_auth_env() -> None:
    debug = os.environ.get("DEBUG", "").lower() in {"1", "true", "yes"}
    allow = os.environ.get("ALLOW_TEST_AUTH", "").lower() in {"1", "true", "yes"}
    if not (debug and allow):
        raise RuntimeError(
            "Acceptance auth requires DEBUG=true and ALLOW_TEST_AUTH=true"
        )
