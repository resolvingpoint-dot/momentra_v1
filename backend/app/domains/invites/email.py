"""Resend-backed group invite email sender.

Uses ``settings.resend_api_key`` / ``settings.resend_from`` (from
``MOMENTRA_RESEND_*``). Never raises into setup/activate paths — callers get a
``{sent, error?}`` result and decide how to surface it.
"""
from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_group_invite_email(to: str, subject: str, body: str) -> dict:
    """Send invite email via Resend. Returns ``{sent: bool, error?: str}``."""
    api_key = (settings.resend_api_key or "").strip()
    from_addr = (settings.resend_from or "").strip().strip('"')
    if not api_key or not from_addr:
        return {"sent": False, "error": "resend_not_configured"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": from_addr,
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
            )
        if resp.status_code >= 400:
            detail = resp.text[:300]
            logger.warning("Resend invite email failed: %s %s", resp.status_code, detail)
            return {"sent": False, "error": f"resend_{resp.status_code}"}
        return {"sent": True}
    except Exception as exc:  # noqa: BLE001 — never block invite/setup
        logger.warning("Resend invite email error: %s", exc)
        return {"sent": False, "error": "resend_request_failed"}
