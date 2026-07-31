"""Invite service — JWT links + persisted invite rows in moment runtime store.

Rows live under ``runtime.invites`` (see ``moment_store``) so MockSession tests
and production share the same path. Tokens remain signed JWTs; only a SHA-256
hash is stored on the row.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_invite_token,
    decode_invite_token,
    invite_expires_at,
)
from app.domains.group import moment_store as store
from app.domains.invites import schemas as s
from app.domains.invites.email import send_group_invite_email
from app.domains.moments.repository import MomentRepository

_ACTIVE_STATUSES = {"sent", "opened", "pending"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _invite_link(token: str) -> str:
    base = settings.invite_link_base_url.rstrip("/")
    return f"{base}/{token}"


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _short_code() -> str:
    return secrets.token_hex(4).upper()


def _copy_ready(name: str, link: str) -> tuple[str, str, str, str]:
    subject = f"You're invited to join {name}"
    body = (
        f"You're invited to join \"{name}\" on Momentra.\n\n"
        f"Open this link to accept:\n{link}\n"
    )
    whatsapp = f"Join our shared experience on Momentra: {name}\n{link}"
    sms = f"Join our shared experience on Momentra: {name} {link}"
    return subject, body, whatsapp, sms


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _is_expired(row: dict) -> bool:
    exp = _parse_iso(row.get("expires_at"))
    if exp is None:
        return False
    now = datetime.now(timezone.utc)
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return exp <= now


class InviteService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)

    async def _require_owned_moment(self, user_id: UUID, moment_id: UUID):
        moment = await self.moments.get_by_user_and_id(user_id, moment_id)
        if moment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
            )
        return moment

    def _find_active(
        self,
        moment,
        *,
        participant_id: str | None = None,
        email: str | None = None,
    ) -> dict | None:
        for row in store.list_items(moment, "invites"):
            if row.get("deleted"):
                continue
            status_val = str(row.get("status") or "").lower()
            if status_val in {"accepted", "revoked", "expired"}:
                continue
            if _is_expired(row):
                store.update_item(moment, "invites", row["id"], {"status": "expired"})
                continue
            if participant_id:
                if str(row.get("participant_id") or "") != str(participant_id):
                    continue
            elif email:
                if str(row.get("invitee_email") or "").lower() != str(email).lower():
                    continue
            elif row.get("participant_id") or row.get("invitee_email"):
                # Generic draft: only reuse unbound invites
                continue
            if status_val in _ACTIVE_STATUSES or not status_val:
                return row
        return None

    def _revoke_active(
        self,
        moment,
        *,
        participant_id: str | None = None,
        email: str | None = None,
    ) -> None:
        for row in store.list_items(moment, "invites"):
            if row.get("deleted"):
                continue
            status_val = str(row.get("status") or "").lower()
            if status_val in {"accepted", "revoked", "expired"}:
                continue
            if participant_id and str(row.get("participant_id") or "") != str(participant_id):
                continue
            if email and str(row.get("invitee_email") or "").lower() != str(email).lower():
                continue
            if participant_id is None and email is None:
                if row.get("participant_id") or row.get("invitee_email"):
                    continue
            store.update_item(moment, "invites", row["id"], {"status": "revoked"})

    def _mint_row(
        self,
        moment,
        *,
        participant_id: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        channel: str = "draft",
    ) -> tuple[dict, str]:
        invite_id = store.new_id()
        code = _short_code()
        token = create_invite_token(
            str(moment.id),
            email,
            participant_id=participant_id,
            invite_id=invite_id,
        )
        expires = invite_expires_at()
        row = {
            "id": invite_id,
            "moment_id": str(moment.id),
            "participant_id": participant_id,
            "invitee_email": email,
            "invitee_phone": phone,
            "token_hash": _token_hash(token),
            "invite_code": code,
            "channel": channel,
            "status": "sent",
            "expires_at": expires,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        }
        store.append_item(moment, "invites", row)
        return row, token

    def _draft_payload(
        self,
        moment,
        row: dict,
        token: str | None = None,
        *,
        mark_opened: bool = False,
    ) -> dict:
        name = moment.title or "Your moment"
        # Prefer regenerating link from a fresh token when provided; otherwise
        # rebuild a JWT that still validates against the stored invite id.
        if token is None:
            token = create_invite_token(
                str(moment.id),
                row.get("invitee_email"),
                participant_id=row.get("participant_id"),
                invite_id=row.get("id"),
            )
            # Keep hash in sync when we re-issue for an existing row
            store.update_item(
                moment,
                "invites",
                row["id"],
                {"token_hash": _token_hash(token)},
            )
            row = {**row, "token_hash": _token_hash(token)}
        link = _invite_link(token)
        subject, body, whatsapp, sms = _copy_ready(name, link)
        if mark_opened and str(row.get("status") or "").lower() == "sent":
            store.update_item(moment, "invites", row["id"], {"status": "opened"})
            row = {**row, "status": "opened"}
        return s.InviteDraftResponse(
            invite_link=link,
            invite_code=str(row.get("invite_code") or _short_code()),
            qr_payload=link,
            email_subject=subject,
            email_body=body,
            whatsapp_text=whatsapp,
            sms_text=sms,
            experience_name=name,
            expires_at=row.get("expires_at") or invite_expires_at(),
            invite_id=str(row.get("id") or ""),
            participant_id=row.get("participant_id"),
            status=str(row.get("status") or "sent"),
        ).model_dump(mode="json")

    def _guest_contact(self, moment, participant_id: str | None) -> tuple[str | None, str | None]:
        if not participant_id:
            return None, None
        for g in store.list_items(moment, "guests"):
            if g.get("deleted"):
                continue
            if str(g.get("id") or "") == str(participant_id):
                return g.get("email"), g.get("phone")
        return None, None

    async def invite_draft(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        participant_id: str | None = None,
    ) -> dict:
        from app.domains.invites.platform_service import (
            PlatformInviteService,
            opaque_creates_enabled,
        )

        if opaque_creates_enabled():
            minted = await PlatformInviteService(self.session).create_group_invite(
                user_id,
                moment_id,
                metadata={"participant_id": participant_id} if participant_id else {},
            )
            moment = await self._require_owned_moment(user_id, moment_id)
            name = moment.title or "Your moment"
            link = minted["invite_url"]
            subject, body, whatsapp, sms = _copy_ready(name, link)
            return s.InviteDraftResponse(
                invite_link=link,
                invite_code=minted["code"],
                qr_payload=link,
                email_subject=subject,
                email_body=body,
                whatsapp_text=whatsapp,
                sms_text=sms,
                experience_name=name,
                expires_at=minted["expires_at"],
                invite_id=minted["invite_id"],
                participant_id=participant_id,
                status="sent",
            ).model_dump(mode="json")

        moment = await self._require_owned_moment(user_id, moment_id)
        email, phone = self._guest_contact(moment, participant_id)
        existing = self._find_active(moment, participant_id=participant_id)
        if existing is not None:
            return self._draft_payload(moment, existing, mark_opened=True)
        row, token = self._mint_row(
            moment,
            participant_id=participant_id,
            email=email,
            phone=phone,
            channel="draft",
        )
        return self._draft_payload(moment, row, token, mark_opened=True)

    async def refresh_invite_draft(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        participant_id: str | None = None,
    ) -> dict:
        from app.domains.invites.platform_service import (
            PlatformInviteService,
            opaque_creates_enabled,
        )

        if opaque_creates_enabled():
            return await self.invite_draft(
                user_id, moment_id, participant_id=participant_id
            )

        moment = await self._require_owned_moment(user_id, moment_id)
        email, phone = self._guest_contact(moment, participant_id)
        self._revoke_active(moment, participant_id=participant_id)
        row, token = self._mint_row(
            moment,
            participant_id=participant_id,
            email=email,
            phone=phone,
            channel="draft",
        )
        return self._draft_payload(moment, row, token)

    async def record_channel(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        channel: str,
        participant_id: str | None = None,
        invite_id: str | None = None,
    ) -> dict:
        moment = await self._require_owned_moment(user_id, moment_id)
        row = None
        if invite_id:
            for item in store.list_items(moment, "invites"):
                if str(item.get("id")) == str(invite_id) and not item.get("deleted"):
                    row = item
                    break
        if row is None:
            row = self._find_active(moment, participant_id=participant_id)
        if row is None:
            draft = await self.invite_draft(
                user_id, moment_id, participant_id=participant_id
            )
            return {"ok": True, "invite_id": draft.get("invite_id"), "channel": channel}
        store.update_item(
            moment,
            "invites",
            row["id"],
            {"channel": channel, "status": "sent"},
        )
        return {"ok": True, "invite_id": row["id"], "channel": channel}

    async def create_email_invite(
        self,
        user_id: UUID,
        moment_id: UUID,
        email: str,
        *,
        participant_id: str | None = None,
    ) -> dict:
        moment = await self._require_owned_moment(user_id, moment_id)
        existing = self._find_active(
            moment, participant_id=participant_id, email=email if not participant_id else None
        )
        if existing is not None:
            payload = self._draft_payload(moment, existing)
            token_link = payload["invite_link"]
            subject = payload["email_subject"]
            body = payload["email_body"]
            invite_id = existing["id"]
            expires = existing.get("expires_at") or invite_expires_at()
            created = existing.get("created_at") or _now_iso()
        else:
            row, token = self._mint_row(
                moment,
                participant_id=participant_id,
                email=email,
                channel="email",
            )
            invite_id = row["id"]
            expires = row["expires_at"]
            created = row["created_at"]
            token_link = _invite_link(token)
            name = moment.title or "Your moment"
            subject, body, _w, _s = _copy_ready(name, token_link)

        send_result = await send_group_invite_email(email, subject, body)
        store.update_item(
            moment,
            "invites",
            invite_id,
            {
                "channel": "email",
                "invitee_email": email,
                "status": "sent" if send_result.get("sent") else "sent",
                "send_error": send_result.get("error"),
            },
        )
        return s.EmailInviteResponse(
            id=invite_id,
            moment_id=str(moment_id),
            invitee_email=email,
            status="pending",
            expires_at=expires,
            created_at=created,
            sent=bool(send_result.get("sent")),
            invite_link=token_link,
            email_subject=subject,
            email_body=body,
            send_error=send_result.get("error"),
        ).model_dump(mode="json")

    async def list_email_invites(
        self, user_id: UUID, moment_id: UUID, status_filter: str
    ) -> list[dict]:
        moment = await self._require_owned_moment(user_id, moment_id)
        out: list[dict] = []
        needle = (status_filter or "pending").lower()
        for row in store.list_items(moment, "invites"):
            if row.get("deleted"):
                continue
            if not row.get("invitee_email"):
                continue
            status_val = str(row.get("status") or "").lower()
            if needle == "pending" and status_val in {"accepted", "revoked", "expired"}:
                continue
            if needle not in {"pending", "all", ""} and status_val != needle:
                continue
            out.append(
                s.EmailInviteResponse(
                    id=str(row.get("id")),
                    moment_id=str(moment_id),
                    invitee_email=str(row.get("invitee_email")),
                    status="pending" if status_val in _ACTIVE_STATUSES else status_val,
                    expires_at=str(row.get("expires_at") or invite_expires_at()),
                    created_at=str(row.get("created_at") or _now_iso()),
                    sent=True,
                    invite_link=None,
                    email_subject=None,
                    email_body=None,
                    send_error=row.get("send_error"),
                ).model_dump(mode="json")
            )
        return out

    async def share_invite(self, user_id: UUID, moment_id: UUID) -> dict:
        draft = await self.invite_draft(user_id, moment_id)
        return s.ShareInviteResponse(
            invite_url=draft["invite_link"],
            trip_name=draft.get("experience_name") or "Your moment",
            expires_at=draft.get("expires_at") or invite_expires_at(),
            share_message=draft.get("whatsapp_text"),
        ).model_dump(mode="json")

    def _attach_accepter(
        self,
        moment,
        user_id: UUID,
        *,
        participant_id: str | None,
        email: str | None,
        display_name: str = "Member",
    ) -> str | None:
        uid = str(user_id)
        state = store.read_state(moment)
        rt = state.setdefault("runtime", store._empty_runtime())  # noqa: SLF001
        members = rt.setdefault("members", [])
        guests = rt.setdefault("guests", [])

        # Already a member?
        for m in members:
            if m.get("deleted"):
                continue
            if str(m.get("user_id") or m.get("id") or "") == uid:
                return str(m.get("id") or uid)

        guest = None
        if participant_id:
            guest = next(
                (
                    g
                    for g in guests
                    if not g.get("deleted") and str(g.get("id") or "") == str(participant_id)
                ),
                None,
            )
        if guest is None and email:
            guest = next(
                (
                    g
                    for g in guests
                    if not g.get("deleted")
                    and str(g.get("email") or "").lower() == str(email).lower()
                ),
                None,
            )

        name = display_name
        if guest is not None:
            guest["status"] = "confirmed"
            guest["user_id"] = uid
            guest["updated_at"] = _now_iso()
            name = str(guest.get("full_name") or name)

        member_id = str(guest.get("id") if guest else uid)
        members.append(
            {
                "id": member_id,
                "member_id": member_id,
                "user_id": uid,
                "display_name": name,
                "role_code": "PARTICIPANT",
                "status": "ACTIVE",
                "created_at": _now_iso(),
            }
        )
        store.write_state(moment, state)
        return member_id

    async def _upsert_group_roster_member(
        self,
        moment,
        user_id: UUID,
        *,
        display_name: str = "Member",
        member_id: str | None = None,
    ) -> None:
        """Best-effort ACTIVE row in ``group_moment_members`` (+ stub ``group_moments``).

        Shared Group moments live primarily on ``moments`` + runtime JSON. Relational
        roster FKs ``group_moments``; we upsert a stub when missing so inventory and
        access gates that query ``GroupMomentMembers`` can see invitees. Failures are
        ignored — runtime.members remains the canonical shared-moment roster.
        """
        from uuid import UUID as _UUID
        from uuid import uuid4

        from app.domains.group.models import GroupMomentMembers, GroupMoments

        mid = moment.id
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        try:
            gm_result = await self.session.execute(
                select(GroupMoments).where(GroupMoments.moment_id == mid)
            )
            group_row = gm_result.scalar_one_or_none()
        except Exception:
            group_row = None

        if group_row is None:
            try:
                self.session.add(
                    GroupMoments(
                        moment_id=mid,
                        moment_type=str(moment.moment_type or "TRIP"),
                        moment_profile="DEFAULT",
                        moment_name=str(moment.title or "Group moment"),
                        status=str(moment.status or "ACTIVE"),
                        stage="CREATED",
                        created_by=moment.user_id,
                        created_at=now,
                        updated_at=now,
                    )
                )
            except Exception:
                return

        try:
            mem_result = await self.session.execute(
                select(GroupMomentMembers).where(
                    GroupMomentMembers.moment_id == mid,
                    GroupMomentMembers.user_id == user_id,
                )
            )
            existing = list(mem_result.scalars().all())
        except Exception:
            existing = []

        active = next(
            (
                m
                for m in existing
                if (m.status or "").upper() not in {"LEFT", "REMOVED", "DECLINED"}
                and m.left_at is None
            ),
            None,
        )
        if active is not None:
            active.status = "ACTIVE"
            active.joined_at = active.joined_at or now
            active.display_name = display_name or active.display_name
            return

        try:
            roster_id = (
                _UUID(str(member_id))
                if member_id
                else uuid4()
            )
        except (ValueError, TypeError):
            roster_id = uuid4()

        try:
            self.session.add(
                GroupMomentMembers(
                    member_id=roster_id,
                    moment_id=mid,
                    display_name=display_name or "Member",
                    role_code="PARTICIPANT",
                    status="ACTIVE",
                    created_at=now,
                    joined_at=now,
                    user_id=user_id,
                )
            )
        except Exception:
            return

    async def _is_business_moment(self, moment) -> bool:
        from app.domains.business.models import BusinessMoments
        from app.domains.business.setup.invites import is_business_moment_type

        if is_business_moment_type(getattr(moment, "moment_type", None)):
            return True
        result = await self.session.execute(
            select(BusinessMoments).where(BusinessMoments.moment_id == moment.id)
        )
        try:
            return result.scalar_one_or_none() is not None
        except Exception:
            return False

    async def _accept_business(
        self,
        user_id: UUID,
        moment,
        *,
        token: str,
        invite_id: Any,
        participant_id: Any,
        email: Any,
        token_hash: str,
    ) -> dict:
        from app.domains.business.models import (
            BusinessMomentInvitations,
            BusinessMomentMembers,
        )
        from app.domains.business.setup.invites import invite_token_hash as _biz_hash

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        mid = moment.id

        # Already an active business member?
        mem_result = await self.session.execute(
            select(BusinessMomentMembers).where(
                BusinessMomentMembers.moment_id == mid,
                BusinessMomentMembers.user_id == user_id,
            )
        )
        try:
            existing_members = list(mem_result.scalars().all())
        except Exception:
            existing_members = []
        active = next(
            (
                m
                for m in existing_members
                if (m.member_status or "").lower() not in {"removed"}
            ),
            None,
        )
        if active is not None or moment.user_id == user_id:
            return s.InviteAcceptResponse(
                moment_id=str(moment.id),
                moment_name=moment.title or "Your moment",
                moment_type=moment.moment_type,
                already_member=True,
                participant_id=str(active.member_id) if active else None,
            ).model_dump(mode="json")

        inv_result = await self.session.execute(
            select(BusinessMomentInvitations).where(
                BusinessMomentInvitations.moment_id == mid
            )
        )
        try:
            invites = list(inv_result.scalars().all())
        except Exception:
            invites = []

        matched = None
        invite_id_str = str(invite_id) if invite_id else None
        for row in invites:
            status_val = str(row.invite_status or "").lower()
            if status_val in {"cancelled", "expired"}:
                continue
            if invite_id_str and str(row.invite_id) == invite_id_str:
                matched = row
                break
            if row.qr_token and str(row.qr_token) == token_hash:
                matched = row
                break
            if (
                participant_id
                and row.local_id
                and str(row.local_id) == str(participant_id)
                and status_val in {"pending", "sent"}
            ):
                matched = row
                break

        if matched is not None:
            status_val = str(matched.invite_status or "").lower()
            if status_val == "cancelled" or matched.revoked_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invite has been revoked",
                )
            if status_val == "expired" or (
                matched.expires_at is not None and matched.expires_at <= now
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invite has expired",
                )

            # Email-bound invites must be accepted by the intended address.
            target = str(matched.invite_target or "").strip().lower()
            jwt_email = str(email or "").strip().lower()
            if (matched.invite_method or "").lower() == "email" or (
                matched.channel or ""
            ).upper() == "EMAIL":
                from app.domains.users.models import UserModel

                u_result = await self.session.execute(
                    select(UserModel).where(UserModel.id == user_id)
                )
                user = u_result.scalar_one_or_none()
                user_email = str((user.email if user else None) or "").strip().lower()
                expected = jwt_email or target
                if expected and user_email and user_email != expected:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Signed-in email does not match this invitation",
                    )

            member = None
            if matched.member_id is not None:
                m_result = await self.session.execute(
                    select(BusinessMomentMembers).where(
                        BusinessMomentMembers.member_id == matched.member_id
                    )
                )
                member = m_result.scalar_one_or_none()

            if member is None and participant_id:
                m_result = await self.session.execute(
                    select(BusinessMomentMembers).where(
                        BusinessMomentMembers.moment_id == mid,
                        BusinessMomentMembers.local_id == str(participant_id),
                    )
                )
                try:
                    candidates = list(m_result.scalars().all())
                except Exception:
                    candidates = []
                member = candidates[0] if candidates else None

            if member is None:
                from app.domains.business.setup.team_ops_permissions import (
                    member_permission_flags,
                )

                flags = member_permission_flags("MEMBER")
                member = BusinessMomentMembers(
                    moment_id=mid,
                    name=str(email or "Guest")[:255],
                    role="Team Member",
                    member_status="active",
                    added_by=moment.user_id or user_id,
                    user_id=user_id,
                    email=str(email) if email else None,
                    local_id=str(participant_id) if participant_id else None,
                    can_manage_operations_settings=False,
                    created_at=now,
                    updated_at=now,
                    **flags,
                )
                self.session.add(member)
                await self.session.flush()
            else:
                if member.user_id is not None and member.user_id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="This invitation belongs to another user",
                    )
                member.user_id = user_id
                member.member_status = "active"
                member.updated_at = now
                if email and not member.email:
                    member.email = str(email)

            matched.invite_status = "accepted"
            matched.accepted_at = now
            matched.updated_at = now
            matched.member_id = member.member_id
            if not matched.qr_token:
                matched.qr_token = token_hash
            await self.session.flush()

            return s.InviteAcceptResponse(
                moment_id=str(moment.id),
                moment_name=moment.title or "Your moment",
                moment_type=moment.moment_type,
                already_member=False,
                participant_id=str(member.member_id),
            ).model_dump(mode="json")

        # Open QR / unbound draft JWT: only when this token was never revoked and
        # the invite_id (if a real UUID) does not point at a dead invite row.
        for row in invites:
            if row.qr_token and str(row.qr_token) == token_hash:
                status_val = str(row.invite_status or "").lower()
                if status_val in {"cancelled", "expired"} or row.revoked_at is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invite has been revoked",
                    )

        if invite_id_str:
            try:
                invite_uuid_probe = UUID(invite_id_str)
            except (ValueError, TypeError):
                invite_uuid_probe = None
            if invite_uuid_probe is not None:
                for row in invites:
                    if row.invite_id == invite_uuid_probe:
                        status_val = str(row.invite_status or "").lower()
                        if status_val in {"cancelled", "expired"} or row.revoked_at is not None:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invite has been revoked",
                            )
                        # Row exists but wasn't matched above — treat as failure.
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invite is not acceptable in its current state",
                        )

        # Open QR / unbound draft JWT: create guest member + accepted invite row.
        from app.domains.business.setup.team_ops_permissions import member_permission_flags

        flags = member_permission_flags("MEMBER")
        member = BusinessMomentMembers(
            moment_id=mid,
            name=str(email or "Guest")[:255],
            role="Team Member",
            member_status="active",
            added_by=moment.user_id or user_id,
            user_id=user_id,
            email=str(email) if email else None,
            local_id=str(participant_id) if participant_id else None,
            can_manage_operations_settings=False,
            created_at=now,
            updated_at=now,
            **flags,
        )
        self.session.add(member)
        await self.session.flush()

        invite_uuid = None
        if invite_id_str:
            try:
                invite_uuid = UUID(invite_id_str)
            except (ValueError, TypeError):
                invite_uuid = None

        invitation = BusinessMomentInvitations(
            invite_id=invite_uuid or None,
            moment_id=mid,
            invite_method="qr",
            invite_status="accepted",
            invite_target=str(email or participant_id or user_id)[:255],
            send_on_activation=False,
            member_id=member.member_id,
            qr_token=token_hash or _biz_hash(token),
            accepted_at=now,
            local_id=str(participant_id) if participant_id else None,
            channel="QR",
            created_at=now,
            updated_at=now,
        )
        self.session.add(invitation)
        await self.session.flush()

        return s.InviteAcceptResponse(
            moment_id=str(moment.id),
            moment_name=moment.title or "Your moment",
            moment_type=moment.moment_type,
            already_member=False,
            participant_id=str(member.member_id),
        ).model_dump(mode="json")

    async def accept(self, user_id: UUID, token: str) -> dict:
        from app.domains.invites import codes as invite_codes
        from app.domains.invites.platform_service import (
            PlatformInviteService,
            legacy_jwt_accept_enabled,
        )

        raw = (token or "").strip()
        # Opaque codes must not fall through to JWT decode.
        if invite_codes.is_opaque_code_shape(raw):
            result = await PlatformInviteService(self.session).accept(user_id, raw)
            # Normalize group opaque accept to InviteAcceptResponse shape when present.
            if result.get("moment_id"):
                already = bool(
                    result.get("already_member")
                    or result.get("result") in {"ALREADY_MEMBER", "ALREADY_ACCEPTED"}
                )
                outcome = str(
                    result.get("result")
                    or ("ALREADY_MEMBER" if already else "ACCEPTED")
                )
                payload = s.InviteAcceptResponse(
                    moment_id=str(result["moment_id"]),
                    moment_name=result.get("moment_name") or "Your moment",
                    moment_type=result.get("moment_type"),
                    already_member=already,
                    participant_id=result.get("participant_id"),
                ).model_dump(mode="json")
                payload["result"] = outcome
                payload["invite_type"] = result.get("invite_type") or "GROUP"
                payload["target_id"] = str(result["moment_id"])
                return payload
            return result

        if not legacy_jwt_accept_enabled():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired invite",
            )

        try:
            payload = decode_invite_token(token)
        except jwt.PyJWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired invite",
            ) from exc
        moment_id_raw = payload.get("sub")
        try:
            moment_id = UUID(str(moment_id_raw))
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid invite",
            ) from exc
        moment = await self.moments.get_by_id(moment_id)
        if moment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
            )

        invite_id = payload.get("invite_id")
        participant_id = payload.get("participant_id")
        email = payload.get("email")
        th = _token_hash(token)

        if await self._is_business_moment(moment):
            return await self._accept_business(
                user_id,
                moment,
                token=token,
                invite_id=invite_id,
                participant_id=participant_id,
                email=email,
                token_hash=th,
            )

        # Mark matching invite accepted / reject revoked
        matched = None
        for row in store.list_items(moment, "invites"):
            if row.get("deleted"):
                continue
            if invite_id and str(row.get("id")) == str(invite_id):
                matched = row
                break
            if str(row.get("token_hash") or "") == th:
                matched = row
                break

        if matched is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite not found or has been revoked",
            )

        status_val = str(matched.get("status") or "").lower()
        if status_val == "revoked":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite has been revoked",
            )
        if _is_expired(matched) or status_val == "expired":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite has expired",
            )
        if not participant_id:
            participant_id = matched.get("participant_id")
        if not email:
            email = matched.get("invitee_email")

        # Email-bound invites require the signed-in user to match.
        invitee_email = str(email or matched.get("invitee_email") or "").strip().lower()
        if invitee_email:
            from app.domains.users.models import UserModel

            u_result = await self.session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = u_result.scalar_one_or_none()
            user_email = str((user.email if user else None) or "").strip().lower()
            if user_email and user_email != invitee_email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Signed-in email does not match this invitation",
                )

        already = moment.user_id == user_id
        attached_id = None
        if not already:
            attached_id = self._attach_accepter(
                moment,
                user_id,
                participant_id=str(participant_id) if participant_id else None,
                email=str(email) if email else None,
            )
            await self._upsert_group_roster_member(
                moment,
                user_id,
                display_name="Member",
                member_id=attached_id,
            )

        store.update_item(
            moment,
            "invites",
            matched["id"],
            {"status": "accepted", "accepted_by": str(user_id)},
        )

        return s.InviteAcceptResponse(
            moment_id=str(moment.id),
            moment_name=moment.title or "Your moment",
            moment_type=moment.moment_type,
            already_member=already,
            participant_id=attached_id or (str(participant_id) if participant_id else None),
        ).model_dump(mode="json")
