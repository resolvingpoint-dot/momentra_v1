"""BUSINESS-safe invite helpers (JWT + Resend) without Group moment_store writes."""
from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_invite_token, invite_expires_at
from app.domains.business.models import BusinessMomentInvitations
from app.domains.invites.email import send_group_invite_email

logger = logging.getLogger(__name__)

_BUSINESS_MOMENT_TYPES = frozenset(
    {
        "TEAM_OPERATIONS",
        "BUSINESS_RUNWAY",
        "BUSINESS_OPERATIONS",
        "PROJECT_OPERATIONS",
        "EVENT_OPERATIONS",
        "DEPARTMENT_OPERATIONS",
        "VENDOR_OPERATIONS",
        "CUSTOM_OPERATIONAL_MOMENT",
    }
)


def is_business_moment_type(moment_type: str | None) -> bool:
    t = (moment_type or "").upper().replace("-", "_")
    if t in _BUSINESS_MOMENT_TYPES:
        return True
    return "BUSINESS" in t or t.startswith("BIZ") or t == "ORG"


def invite_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _invite_link(token: str) -> str:
    base = settings.invite_link_base_url.rstrip("/")
    return f"{base}/{token}"


def _copy_ready(name: str, link: str) -> tuple[str, str, str, str]:
    subject = f"You're invited to join {name}"
    body = f"Join {name} on Momentra:\n{link}"
    whatsapp = f"You're invited to {name}: {link}"
    sms = f"Momentra invite to {name}: {link}"
    return subject, body, whatsapp, sms


def _parse_expires_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


def build_invite_draft_payload(
    *,
    moment_id: str,
    local_id: str,
    channel: str,
    experience_name: str,
    email: str | None = None,
    invite_id: str | None = None,
    raw_token: str | None = None,
) -> dict[str, Any]:
    invite_id = invite_id or secrets.token_hex(8)
    token = raw_token or create_invite_token(
        moment_id,
        email,
        participant_id=local_id,
        invite_id=invite_id,
    )
    link = _invite_link(token)
    subject, body, whatsapp, sms = _copy_ready(experience_name, link)
    return {
        "invite_id": invite_id,
        "local_id": local_id,
        "channel": channel.upper(),
        "invite_link": link,
        "invite_token": token,
        "token_hash": invite_token_hash(token),
        "invite_code": secrets.token_hex(4).upper(),
        "qr_payload": link,
        "email_subject": subject,
        "email_body": body,
        "whatsapp_text": whatsapp,
        "sms_text": sms,
        "expires_at": invite_expires_at(),
    }


def bind_token_to_invitation(
    row: BusinessMomentInvitations,
    *,
    token: str,
    expires_at: str | None = None,
) -> None:
    """Persist SHA-256 of JWT on the invitation row (never the raw token)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    row.qr_token = invite_token_hash(token)
    exp = _parse_expires_at(expires_at) or _parse_expires_at(invite_expires_at())
    if exp is not None:
        row.expires_at = exp
    row.updated_at = now


async def mint_and_bind_invitation(
    session: AsyncSession,
    row: BusinessMomentInvitations,
    *,
    moment_id: UUID,
    experience_name: str,
    mark_sent: bool = False,
) -> dict[str, Any]:
    """Mint a durable JWT bound to the DB invite_id and store qr_token."""
    channel = str(row.channel or row.invite_method or "QR").upper()
    email = None
    if (row.invite_method or "").lower() == "email" or channel == "EMAIL":
        target = str(row.invite_target or "")
        if "@" in target:
            email = target
    draft = build_invite_draft_payload(
        moment_id=str(moment_id),
        local_id=str(row.local_id or row.invite_id),
        channel=channel,
        experience_name=experience_name,
        email=email,
        invite_id=str(row.invite_id),
    )
    bind_token_to_invitation(
        row,
        token=str(draft["invite_token"]),
        expires_at=str(draft.get("expires_at")),
    )
    if mark_sent:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        row.invite_status = "sent"
        row.sent_at = now
        row.updated_at = now
    await session.flush()
    return draft


async def deliver_pending_invites(
    session: AsyncSession,
    *,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    """Send pending EMAIL invites and bind tokens for all channels (idempotent)."""
    name = str(answers.get("team_name") or answers.get("moment_name") or "Team Operations")
    result = await session.execute(
        select(BusinessMomentInvitations).where(
            BusinessMomentInvitations.moment_id == moment_id,
            BusinessMomentInvitations.invite_status.in_(["pending", "sent"]),
        )
    )
    try:
        rows = list(result.scalars().all())
    except Exception:
        return

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for row in rows:
        if row.sent_at is not None and row.qr_token:
            continue
        channel = (row.channel or row.invite_method or "").upper()
        is_email = channel in {"EMAIL", "email"} or row.invite_method == "email"
        if not is_email:
            # Non-email: mint durable JWT, store hash, mark sent (client delivers copy).
            try:
                await mint_and_bind_invitation(
                    session,
                    row,
                    moment_id=moment_id,
                    experience_name=name,
                    mark_sent=True,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to bind QR invite %s: %s", row.invite_id, exc)
            continue

        email = row.invite_target
        if not email or "@" not in str(email):
            continue
        draft = build_invite_draft_payload(
            moment_id=str(moment_id),
            local_id=str(row.local_id or row.invite_id),
            channel="EMAIL",
            experience_name=name,
            email=str(email),
            invite_id=str(row.invite_id),
        )
        bind_token_to_invitation(
            row,
            token=str(draft["invite_token"]),
            expires_at=str(draft.get("expires_at")),
        )
        send_result = await send_group_invite_email(
            str(email),
            draft["email_subject"],
            draft["email_body"],
        )
        if send_result.get("sent"):
            row.invite_status = "sent"
            row.sent_at = now
            row.updated_at = now
        else:
            logger.warning(
                "Invite email not sent for %s: %s",
                row.invite_id,
                send_result.get("error"),
            )
            # Keep pending — activation already committed; retry is safe (no sent_at).
            # Token hash is still stored so QR/link accept works if user has the link.
            row.updated_at = now
