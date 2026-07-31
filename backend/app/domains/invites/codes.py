"""Opaque invite code generation and keyed hashing."""
from __future__ import annotations

import hashlib
import hmac
import logging
import secrets

from app.core.config import settings

logger = logging.getLogger(__name__)

# Exclude 0/O, 1/I/L for visual clarity.
OPAQUE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def invite_code_length() -> int:
    return max(6, min(16, int(getattr(settings, "invite_code_length", 8) or 8)))


def _pepper() -> bytes:
    pepper = (getattr(settings, "invite_code_pepper", None) or "").strip()
    if pepper:
        return pepper.encode("utf-8")
    # Derive a dedicated key from session secret when pepper unset.
    secret = (settings.effective_session_secret or "momentra-dev").encode("utf-8")
    return hmac.new(secret, b"invite-code-pepper-v1", hashlib.sha256).digest()


def hash_invite_code(code: str) -> str:
    normalized = (code or "").strip().upper()
    digest = hmac.new(_pepper(), normalized.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest


def codes_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(hash_invite_code(a), hash_invite_code(b))


def generate_opaque_code(length: int | None = None) -> str:
    n = length or invite_code_length()
    return "".join(secrets.choice(OPAQUE_ALPHABET) for _ in range(n))


def code_suffix(code: str, n: int = 4) -> str:
    raw = (code or "").strip().upper()
    return raw[-n:] if len(raw) >= n else raw


def is_opaque_code_shape(raw: str) -> bool:
    """True when string looks like a platform opaque code (not JWT)."""
    s = (raw or "").strip().upper()
    if not s or "." in s:
        return False
    if not (6 <= len(s) <= 16):
        return False
    return all(ch in OPAQUE_ALPHABET for ch in s)


def looks_like_jwt(raw: str) -> bool:
    s = (raw or "").strip()
    if s.count(".") < 2:
        return False
    return len(s) >= 20


def canonical_invite_url(code: str) -> str:
    base = (getattr(settings, "invite_canonical_base_url", None) or "").strip().rstrip("/")
    if not base:
        base = (settings.invite_link_base_url or "https://www.momentra.tech/invite").rstrip(
            "/"
        )
        # If scheme link, rewrite to https canonical for QR/share.
        if base.startswith("momentra://"):
            base = "https://www.momentra.tech/invite"
        elif "/invite" not in base and base.startswith("https://"):
            base = base.rstrip("/") + "/invite"
    # Ensure path ends at /invite
    if base.endswith("/invite"):
        return f"{base}/{code}"
    if "/invite/" in base:
        return f"{base.rstrip('/')}/{code}"
    return f"{base.rstrip('/')}/invite/{code}"


def redact_invite_path(path: str) -> str:
    """Redact invite path segments for logs."""
    parts = (path or "").split("/")
    out: list[str] = []
    redact_next = False
    for p in parts:
        if redact_next and p:
            out.append("[REDACTED]")
            redact_next = False
            continue
        out.append(p)
        if p.lower() in {"invite", "company-invite", "company-invites"}:
            redact_next = True
    return "/".join(out)
