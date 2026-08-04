from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from uuid import uuid4

from app.core.config import settings

logger = logging.getLogger(__name__)

_EXT_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/webm": ".webm",
    "application/pdf": ".pdf",
}

# 10 MB — matches memory quick-add upload_requirements.max_bytes
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024

_IMAGE_CONTENT_TYPES = frozenset(
    {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/heic",
        "image/gif",
    }
)
_VIDEO_CONTENT_TYPES = frozenset({"video/mp4", "video/quicktime", "video/webm"})
_PDF_CONTENT_TYPES = frozenset({"application/pdf"})
_ALL_ATTACHMENT_CONTENT_TYPES = (
    _IMAGE_CONTENT_TYPES | _VIDEO_CONTENT_TYPES | _PDF_CONTENT_TYPES
)

# Signed gallery GET TTL (seconds)
_SIGNED_GET_EXPIRES_IN = 3600
_SIGNED_UPLOAD_EXPIRES_IN = 3600


def allowed_content_types_for_purpose(purpose: str | None) -> frozenset[str]:
    """MIME allowlist by attachment purpose."""
    key = (purpose or "").strip().lower()
    if key in ("memory", "memories", "media"):
        return _ALL_ATTACHMENT_CONTENT_TYPES
    if key in ("receipt", "invoice", "document", "business_activity", "activity"):
        return _IMAGE_CONTENT_TYPES | _PDF_CONTENT_TYPES
    # Default: images only (legacy receipt-style uploads)
    return _IMAGE_CONTENT_TYPES


def assert_attachment_upload(
    *,
    content_type: str | None,
    byte_size: int | None,
    purpose: str | None = None,
) -> str:
    """Validate content type + size before issuing an upload URL."""
    ct = (content_type or "").strip().lower()
    if not ct or ct not in allowed_content_types_for_purpose(purpose):
        allowed = ", ".join(sorted(allowed_content_types_for_purpose(purpose)))
        raise ValueError(f"Unsupported content_type. Allowed: {allowed}")
    size = int(byte_size or 0)
    if size <= 0:
        raise ValueError("byte_size must be greater than 0")
    if size > MAX_ATTACHMENT_BYTES:
        raise ValueError(
            f"File exceeds the {MAX_ATTACHMENT_BYTES // (1024 * 1024)} MB limit"
        )
    return ct


def _public_base() -> str:
    return (settings.effective_storage_public_base_url or "").rstrip("/")


def _supabase_project_url() -> str:
    return (settings.effective_supabase_url or "").rstrip("/")


def _storage_bucket() -> str:
    return settings.effective_storage_bucket


def _supabase_secret() -> str:
    return (settings.supabase_secret_key or "").strip()


def _extension_for(content_type: str | None) -> str:
    if not content_type:
        return ""
    return _EXT_BY_CONTENT_TYPE.get(content_type.lower(), "")


def build_storage_path(prefix: str, content_type: str | None = None) -> str:
    """Deterministic-ish object key under ``prefix`` for a new upload."""
    return f"{prefix.strip('/')}/{uuid4().hex}{_extension_for(content_type)}"


def assert_storage_path_under(storage_path: str, prefix: str) -> str:
    """Reject confirms that point outside the issued upload prefix (path hijack)."""
    path = (storage_path or "").replace("\\", "/").lstrip("/")
    expected = (prefix or "").strip("/")
    if not path or not expected:
        raise ValueError("Invalid storage path")
    if ".." in path.split("/"):
        raise ValueError("Invalid storage path")
    if path != expected and not path.startswith(expected + "/"):
        raise ValueError("storage_path is outside the allowed upload prefix")
    return path


def _supabase_auth_headers() -> dict[str, str]:
    secret = _supabase_secret()
    if not secret:
        raise RuntimeError(
            "SUPABASE_SECRET_KEY is required to mint signed storage URLs"
        )
    return {
        "Authorization": f"Bearer {secret}",
        "apikey": secret,
        "Content-Type": "application/json",
    }


def _http_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: dict | None = None,
    timeout: float = 20,
) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = Request(url, data=data, method=method.upper())
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 — configured Supabase URL
            raw = resp.read().decode("utf-8") or "{}"
            return json.loads(raw) if raw.strip() else {}
    except HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            detail = str(exc)
        raise RuntimeError(
            f"Supabase storage {method} {url} failed ({exc.code}): {detail[:300]}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"Supabase storage request failed: {exc}") from exc


def _absolute_storage_url(relative_or_absolute: str) -> str:
    value = (relative_or_absolute or "").strip()
    if not value:
        raise RuntimeError("Empty signed URL from Supabase")
    if value.startswith("http://") or value.startswith("https://"):
        return value
    root = _supabase_project_url()
    if not root:
        raise RuntimeError("SUPABASE_URL is required for signed storage URLs")
    if value.startswith("/storage/v1"):
        return f"{root}{value}"
    if value.startswith("/"):
        return f"{root}/storage/v1{value}"
    return f"{root}/storage/v1/{value.lstrip('/')}"


def create_signed_upload_url(storage_path: str, *, expires_in: int = _SIGNED_UPLOAD_EXPIRES_IN) -> str:
    """Mint a time-limited PUT URL for the private attachments bucket."""
    root = _supabase_project_url()
    bucket = _storage_bucket()
    key = storage_path.lstrip("/")
    if not root:
        raise RuntimeError("SUPABASE_URL is required for signed uploads")
    encoded_key = "/".join(quote(part, safe="") for part in key.split("/"))
    api = f"{root}/storage/v1/object/upload/sign/{bucket}/{encoded_key}"
    # Match supabase-js: upsert is requested via header on mint (token embeds upsert=true).
    headers = {**_supabase_auth_headers(), "x-upsert": "true"}
    payload = _http_json(
        "POST",
        api,
        headers=headers,
        body={"expiresIn": expires_in},
    )
    # Supabase returns {"url": "/object/upload/sign/...?token=..."}
    relative = payload.get("url") or payload.get("signedURL") or payload.get("signedUrl")
    if not isinstance(relative, str) or not relative.strip():
        raise RuntimeError(f"Unexpected upload-sign response: {payload!r}")
    return _absolute_storage_url(relative.strip())


def create_signed_get_url(storage_path: str, *, expires_in: int = _SIGNED_GET_EXPIRES_IN) -> str:
    """Mint a time-limited GET URL so private-bucket gallery <img> tags work."""
    root = _supabase_project_url()
    bucket = _storage_bucket()
    key = storage_path.lstrip("/")
    if not root:
        raise RuntimeError("SUPABASE_URL is required for signed downloads")
    encoded_key = "/".join(quote(part, safe="") for part in key.split("/"))
    api = f"{root}/storage/v1/object/sign/{bucket}/{encoded_key}"
    payload = _http_json(
        "POST",
        api,
        headers=_supabase_auth_headers(),
        body={"expiresIn": expires_in},
    )
    relative = payload.get("signedURL") or payload.get("signedUrl") or payload.get("url")
    if not isinstance(relative, str) or not relative.strip():
        raise RuntimeError(f"Unexpected object-sign response: {payload!r}")
    return _absolute_storage_url(relative.strip())


def _extract_storage_key_from_url(url: str) -> str | None:
    """Best-effort extract object key from a Supabase storage URL."""
    s = url.strip()
    bucket = _storage_bucket()
    markers = (
        f"/storage/v1/object/public/{bucket}/",
        f"/storage/v1/object/sign/{bucket}/",
        f"/storage/v1/object/upload/sign/{bucket}/",
        f"/storage/v1/object/{bucket}/",
        # Legacy wrong bucket name from older deploys
        "/storage/v1/object/public/momentra/",
        "/storage/v1/object/momentra/",
    )
    for marker in markers:
        if marker in s:
            rest = s.split(marker, 1)[1]
            return rest.split("?", 1)[0].lstrip("/")
    return None


class StorageBackend(ABC):
    """Object-storage port."""

    @abstractmethod
    async def upload(self, path: str, data: bytes, *, content_type: str) -> str:
        """Store bytes at ``path``; returns the canonical path."""

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Remove an object."""

    @abstractmethod
    async def signed_url(
        self, path: str, *, expires_in: int = 3600, method: str = "GET"
    ) -> str:
        """Time-limited URL for direct client upload or download."""

    @abstractmethod
    async def move(self, src: str, dest: str) -> None:
        """Move an object within the bucket."""

    @abstractmethod
    async def copy(self, src: str, dest: str) -> None:
        """Copy an object within the bucket."""

    def public_url(self, path: str) -> str:
        base = _public_base()
        key = path.lstrip("/")
        if base:
            return f"{base}/{key}"
        if settings.is_production or not settings.debug:
            raise RuntimeError(
                "STORAGE_PUBLIC_BASE_URL is required; local-uploads are disabled outside DEBUG"
            )
        return f"/local-uploads/{key}"


class StubStorageBackend(StorageBackend):
    """Local/dev backend when no bucket is configured."""

    async def upload(self, path: str, data: bytes, *, content_type: str) -> str:
        logger.debug("Stub upload %s (%d bytes, %s)", path, len(data), content_type)
        return path

    async def delete(self, path: str) -> None:
        logger.debug("Stub delete %s", path)

    async def signed_url(
        self, path: str, *, expires_in: int = 3600, method: str = "GET"
    ) -> str:
        _ = expires_in, method
        return self.public_url(path)

    async def move(self, src: str, dest: str) -> None:
        logger.debug("Stub move %s -> %s", src, dest)

    async def copy(self, src: str, dest: str) -> None:
        logger.debug("Stub copy %s -> %s", src, dest)


class SupabaseStorageBackend(StorageBackend):
    """Supabase storage using service-role signed upload/GET URLs."""

    async def upload(self, path: str, data: bytes, *, content_type: str) -> str:
        logger.info(
            "Supabase upload %s (%d bytes, %s) — prefer client signed PUT",
            path,
            len(data),
            content_type,
        )
        return path

    async def delete(self, path: str) -> None:
        logger.info("Supabase delete %s — SDK wiring pending", path)

    async def signed_url(
        self, path: str, *, expires_in: int = 3600, method: str = "PUT"
    ) -> str:
        key = path.lstrip("/")
        method_u = (method or "GET").upper()
        if method_u == "PUT":
            return create_signed_upload_url(key, expires_in=expires_in)
        return create_signed_get_url(key, expires_in=expires_in)

    async def move(self, src: str, dest: str) -> None:
        await self.copy(src, dest)
        await self.delete(src)

    async def copy(self, src: str, dest: str) -> None:
        logger.info("Supabase copy %s -> %s — SDK wiring pending", src, dest)

    def public_url(self, path: str) -> str:
        """Return a signed GET URL for private-bucket display."""
        key = path.lstrip("/")
        if _supabase_secret() and _supabase_project_url():
            try:
                return create_signed_get_url(key)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to mint signed GET for %s; falling back", key)
        return super().public_url(path)


_backend: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _backend
    if _backend is None:
        _backend = (
            SupabaseStorageBackend()
            if settings.effective_storage_public_base_url
            or settings.effective_supabase_url
            else StubStorageBackend()
        )
    return _backend


def build_upload_url(storage_path: str) -> str:
    """Direct-client PUT URL (signed when Supabase is configured)."""
    key = storage_path.lstrip("/")
    if _supabase_project_url() and _supabase_secret():
        return create_signed_upload_url(key)
    if _public_base():
        # Remote base without secret — cannot safely mint uploads.
        raise RuntimeError(
            "SUPABASE_SECRET_KEY is required to mint signed upload URLs for "
            f"bucket {_storage_bucket()!r}"
        )
    if settings.is_production or not settings.debug:
        raise RuntimeError(
            "STORAGE_PUBLIC_BASE_URL / SUPABASE_URL is required; "
            "local-uploads are disabled outside DEBUG"
        )
    return f"/local-uploads/{key}"


def public_url_for(storage_path: str) -> str:
    """Display URL for a stored object (signed GET when using private Supabase)."""
    return get_storage().public_url(storage_path)


def verify_stored_object(storage_path: str) -> None:
    """Raise ``ValueError`` when the uploaded object is missing."""
    key = (storage_path or "").replace("\\", "/").lstrip("/")
    if not key or ".." in key.split("/"):
        raise ValueError("Invalid storage path")

    root = _supabase_project_url()
    secret = _supabase_secret()
    if root and secret:
        bucket = _storage_bucket()
        encoded_key = "/".join(quote(part, safe="") for part in key.split("/"))
        url = f"{root}/storage/v1/object/{bucket}/{encoded_key}"
        headers = _supabase_auth_headers()
        # Prefer HEAD; some gateways only allow GET.
        for method in ("HEAD", "GET"):
            req = Request(url, method=method)
            for hk, hv in headers.items():
                req.add_header(hk, hv)
            if method == "GET":
                req.add_header("Range", "bytes=0-0")
            try:
                with urlopen(req, timeout=15) as resp:  # noqa: S310
                    code = getattr(resp, "status", None) or resp.getcode()
                    if 200 <= int(code) < 300:
                        return
            except HTTPError as exc:
                if exc.code == 404:
                    raise ValueError("Upload not found; retry the upload") from exc
                if exc.code == 405 and method == "HEAD":
                    continue
                raise ValueError(f"Could not verify upload ({exc.code})") from exc
            except URLError as exc:
                raise ValueError("Could not verify upload") from exc
        raise ValueError("Upload not found; retry the upload")

    # DEBUG stub filesystem
    local_root = Path(__file__).resolve().parents[2] / ".local-uploads"
    if not (local_root / key).is_file():
        raise ValueError("Upload not found; retry the upload")


def resolve_media_display_url(value: str | None) -> str | None:
    """Turn a storage key, absolute URL, or relative stub into a displayable URL."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s.startswith(("http://", "https://")):
        # Already signed token URLs are usable as-is.
        if "token=" in s or "/object/sign/" in s or "/upload/sign/" in s:
            return s
        extracted = _extract_storage_key_from_url(s)
        if extracted and _supabase_secret() and _supabase_project_url():
            try:
                return create_signed_get_url(extracted)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to re-sign display URL for %s", extracted)
                return s
        return s
    if s.startswith("/"):
        return s
    return public_url_for(s)


def resolve_memory_image_url(memory: dict) -> str | None:
    """Resolve a gallery/display image URL from a memory store payload."""
    for key in ("image_url", "cover_url", "cover_image_url", "photo_url", "url"):
        val = memory.get(key)
        if isinstance(val, str) and val.strip():
            resolved = resolve_media_display_url(val)
            if resolved:
                return resolved
    paths = memory.get("media_storage_paths") or memory.get("media_urls") or []
    if isinstance(paths, str):
        paths = [paths]
    if not isinstance(paths, list):
        return None
    for path in paths:
        if not path:
            continue
        resolved = resolve_media_display_url(str(path))
        if resolved:
            return resolved
    return None


def require_remote_storage_configured() -> None:
    """Raise if production/non-debug would fall back to open local uploads."""
    if settings.is_production or not settings.debug:
        base = _public_base()
        if not base.startswith("https://") and not _supabase_project_url():
            raise RuntimeError(
                "STORAGE_PUBLIC_BASE_URL or SUPABASE_URL must be set when DEBUG=false"
            )
        if not _supabase_secret():
            raise RuntimeError(
                "SUPABASE_SECRET_KEY is required for signed storage when DEBUG=false"
            )
