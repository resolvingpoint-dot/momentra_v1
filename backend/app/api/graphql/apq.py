"""Automatic Persisted Queries (APQ) — SHA-256 → query document only.

Never caches GraphQL JSON responses (AuthZ / user leakage risk).
Keys are versioned so schema-breaking deploys can invalidate: gql:apq:{version}:{sha256}.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any

from graphql import GraphQLError

from app.core.cache import get_cached, set_cached
from app.core.config import settings

logger = logging.getLogger(__name__)


def sha256_query(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()


def _key(digest: str) -> str:
    version = (settings.graphql_apq_schema_version or "1").strip() or "1"
    return f"gql:apq:{version}:{digest}"


async def lookup_persisted_query(digest: str) -> str | None:
    if not settings.graphql_apq_enabled:
        return None
    raw = await get_cached(_key(digest))
    if isinstance(raw, str) and raw.strip():
        return raw
    if isinstance(raw, dict) and raw.get("query"):
        return str(raw["query"])
    return None


async def store_persisted_query(digest: str, query: str) -> None:
    if not settings.graphql_apq_enabled:
        return
    await set_cached(
        _key(digest),
        query,
        ttl=max(60, int(settings.graphql_apq_ttl_seconds)),
    )


def extract_persisted_extension(payload: dict[str, Any]) -> dict[str, Any] | None:
    ext = payload.get("extensions") or {}
    if not isinstance(ext, dict):
        return None
    pq = ext.get("persistedQuery")
    return pq if isinstance(pq, dict) else None


async def resolve_query_document(payload: dict[str, Any]) -> tuple[str | None, str]:
    """Return (query_string, apq_status) where status is hit|miss|store|bypass|required.

    ``apq_status`` is for observability only.
    """
    pq = extract_persisted_extension(payload)
    body_query = payload.get("query")
    if isinstance(body_query, str) and body_query.strip():
        body_query = body_query.strip()
    else:
        body_query = None

    if not settings.graphql_apq_enabled:
        if settings.graphql_persisted_only:
            raise GraphQLError(
                "Persisted queries are required",
                extensions={"code": "persisted_query_required"},
            )
        return body_query, "bypass"

    if pq is None:
        if settings.graphql_persisted_only:
            raise GraphQLError(
                "Persisted queries are required",
                extensions={"code": "persisted_query_required"},
            )
        return body_query, "bypass"

    digest = str(pq.get("sha256Hash") or "").strip().lower()
    if not digest or len(digest) != 64:
        raise GraphQLError(
            "Invalid persistedQuery.sha256Hash",
            extensions={"code": "persisted_query_invalid"},
        )

    cached = await lookup_persisted_query(digest)
    if cached:
        if body_query and sha256_query(body_query) != digest:
            raise GraphQLError(
                "Persisted query hash does not match query body",
                extensions={"code": "persisted_query_mismatch"},
            )
        return cached, "hit"

    if not body_query:
        raise GraphQLError(
            "PersistedQueryNotFound",
            extensions={"code": "persisted_query_not_found"},
        )

    if sha256_query(body_query) != digest:
        raise GraphQLError(
            "Persisted query hash does not match query body",
            extensions={"code": "persisted_query_mismatch"},
        )

    await store_persisted_query(digest, body_query)
    return body_query, "store"
