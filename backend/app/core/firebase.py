from __future__ import annotations

import hashlib
import logging
import time
from typing import Any

import base64
import json

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings

logger = logging.getLogger(__name__)

_firebase_app: firebase_admin.App | None = None
_VERIFIED_TOKEN_TTL_SEC = 60.0
_VERIFIED_TOKEN_CACHE_MAX = 2048
_verified_token_cache: dict[str, tuple[dict[str, Any], float]] = {}


def init_firebase() -> None:
    global _firebase_app
    if _firebase_app is not None:
        return
    if settings.firebase_credentials_path:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin initialized from credentials file")
    elif settings.firebase_service_account_json_b64:
        decoded = base64.b64decode(settings.firebase_service_account_json_b64).decode("utf-8")
        service_account_info = json.loads(decoded)
        cred = credentials.Certificate(service_account_info)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin initialized from service account JSON")
    elif (
        settings.firebase_project_id
        and settings.firebase_client_email
        and settings.firebase_private_key
    ):
        service_account_info = {
            "type": "service_account",
            "project_id": settings.firebase_project_id,
            "client_email": settings.firebase_client_email,
            # Env vars carry the newlines escaped as "\n"; restore them.
            "private_key": settings.firebase_private_key.replace("\\n", "\n"),
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        cred = credentials.Certificate(service_account_info)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin initialized from client_email/private_key env vars")
    elif settings.firebase_project_id:
        _firebase_app = firebase_admin.initialize_app()
        logger.info(
            "Firebase Admin initialized from project ID (ADC)"
        )
    else:
        logger.warning(
            "No Firebase credentials configured — auth endpoints will fail"
        )


def verify_firebase_token(token: str) -> dict[str, Any]:
    if _firebase_app is None:
        raise RuntimeError("Firebase not initialized")
    cache_key = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = time.monotonic()
    cached = _verified_token_cache.get(cache_key)
    if cached is not None and cached[1] > now:
        return cached[0].copy()

    decoded = auth.verify_id_token(token, app=_firebase_app)
    if len(_verified_token_cache) >= _VERIFIED_TOKEN_CACHE_MAX:
        expired = [key for key, (_, expires_at) in _verified_token_cache.items() if expires_at <= now]
        for key in expired:
            _verified_token_cache.pop(key, None)
        if len(_verified_token_cache) >= _VERIFIED_TOKEN_CACHE_MAX:
            _verified_token_cache.pop(next(iter(_verified_token_cache)))
    _verified_token_cache[cache_key] = (decoded.copy(), now + _VERIFIED_TOKEN_TTL_SEC)
    return decoded
