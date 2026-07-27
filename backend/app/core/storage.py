from __future__ import annotations

import logging
from abc import ABC, abstractmethod
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


def allowed_content_types_for_purpose(purpose: str | None) -> frozenset[str]:
    """MIME allowlist by attachment purpose."""
    key = (purpose or "").strip().lower()
    if key in ("memory", "memories", "media"):
        return _ALL_ATTACHMENT_CONTENT_TYPES
    if key in ("receipt", "invoice", "document"):
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
    from app.core.config import settings as _settings

    return (_settings.effective_storage_public_base_url or "").rstrip("/")


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


class StorageBackend(ABC):
    """Object-storage port. Today: URL builder + stub; tomorrow: S3 / Supabase."""

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
    """Supabase-compatible URL builder.

  When ``STORAGE_PUBLIC_BASE_URL`` is set we emit bucket URLs the mobile clients
  already understand. Actual SDK upload/delete can be wired here later without
  changing call sites.
    """

    async def upload(self, path: str, data: bytes, *, content_type: str) -> str:
        logger.info(
            "Supabase upload %s (%d bytes, %s) — SDK wiring pending",
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
        """Emit a time-limited-style URL for direct client upload/download.

        Full Supabase signed-URL SDK wiring can replace this later; today we
        require an https public base and append a short expiry query hint so
        clients never fall back to open ``/local-uploads`` in production.
        """
        base = _public_base()
        key = path.lstrip("/")
        if not base:
            if settings.is_production or not settings.debug:
                raise RuntimeError(
                    "STORAGE_PUBLIC_BASE_URL is required for signed uploads"
                )
            return f"/local-uploads/{key}?method={method}&expires_in={expires_in}"
        # Prefer explicit signed-style URL; bucket policies should enforce expiry.
        sep = "&" if "?" in base else "?"
        return f"{base}/{key}{sep}method={method}&expires_in={expires_in}"

    async def move(self, src: str, dest: str) -> None:
        await self.copy(src, dest)
        await self.delete(src)

    async def copy(self, src: str, dest: str) -> None:
        logger.info("Supabase copy %s -> %s — SDK wiring pending", src, dest)


_backend: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _backend
    if _backend is None:
        _backend = (
            SupabaseStorageBackend()
            if settings.effective_storage_public_base_url
            else StubStorageBackend()
        )
    return _backend


def build_upload_url(storage_path: str) -> str:
    """Signed PUT URL helper. Production requires STORAGE_PUBLIC_BASE_URL."""
    base = _public_base()
    if base:
        if not base.startswith("https://") and settings.is_production:
            raise RuntimeError(
                "STORAGE_PUBLIC_BASE_URL must be https:// in production"
            )
        # Expiry query hint; bucket policies should enforce real TTL.
        sep = "&" if "?" in f"{base}/{storage_path.lstrip('/')}" else "?"
        return (
            f"{base}/{storage_path.lstrip('/')}"
            f"{sep}method=PUT&expires_in=3600"
        )
    if settings.is_production or not settings.debug:
        raise RuntimeError(
            "STORAGE_PUBLIC_BASE_URL is required; local-uploads are disabled outside DEBUG"
        )
    return f"/local-uploads/{storage_path.lstrip('/')}"


def public_url_for(storage_path: str) -> str:
    """Publicly readable URL for a stored object (persisted on the entity)."""
    return get_storage().public_url(storage_path)


def require_remote_storage_configured() -> None:
    """Raise if production/non-debug would fall back to open local uploads."""
    if settings.is_production or not settings.debug:
        base = _public_base()
        if not base.startswith("https://"):
            raise RuntimeError(
                "STORAGE_PUBLIC_BASE_URL must be an https:// URL when DEBUG=false"
            )
