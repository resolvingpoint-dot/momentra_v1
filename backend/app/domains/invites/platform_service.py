"""Opaque platform invite lifecycle (create / preview / accept / revoke)."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.invites import codes as invite_codes
from app.domains.invites import events as invite_events
from app.domains.invites.models import PlatformInviteModel
from app.domains.users.models import UserModel
from app.shared.events.publisher import get_event_publisher

logger = logging.getLogger(__name__)

_ROLE_LABELS = {
    "MEMBER": "Member",
    "MANAGER": "Manager",
    "OWNER": "Owner",
    "PARTICIPANT": "Participant",
}
_MAX_USES_CAP = 50
_MIN_EXPIRY = timedelta(minutes=5)
_COLLISION_RETRIES = 8


class InviteOutcomeError(HTTPException):
    """HTTPException carrying a stable result_code."""

    def __init__(self, result_code: str, detail: str, status_code: int = 400) -> None:
        super().__init__(status_code=status_code, detail={"code": result_code, "message": detail})
        self.result_code = result_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def opaque_creates_enabled() -> bool:
    return bool(getattr(settings, "invite_opaque_codes_enabled", True))


def legacy_jwt_accept_enabled() -> bool:
    return bool(getattr(settings, "invite_legacy_jwt_accept_enabled", True))


def legacy_workspace_token_accept_enabled() -> bool:
    return bool(getattr(settings, "invite_legacy_workspace_token_accept_enabled", True))


class PlatformInviteService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _expiry_delta(self, expires_in_days: int | None) -> timedelta:
        default_days = int(getattr(settings, "invite_default_expiry_days", 7) or 7)
        max_days = int(getattr(settings, "invite_max_expiry_days", 30) or 30)
        days = default_days if expires_in_days is None else int(expires_in_days)
        days = max(1, min(max_days, days))
        delta = timedelta(days=days)
        return delta if delta >= _MIN_EXPIRY else _MIN_EXPIRY

    def _clamp_max_uses(self, max_uses: int) -> int:
        return max(1, min(_MAX_USES_CAP, int(max_uses or 1)))

    async def _mint_unique_code(self) -> tuple[str, str, str]:
        for _ in range(_COLLISION_RETRIES):
            code = invite_codes.generate_opaque_code()
            code_hash = invite_codes.hash_invite_code(code)
            existing = await self.session.execute(
                select(PlatformInviteModel.id).where(
                    PlatformInviteModel.code_hash == code_hash
                )
            )
            if existing.scalar_one_or_none() is None:
                return code, code_hash, invite_codes.code_suffix(code)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not allocate invite code",
        )

    def _effective_status(self, row: PlatformInviteModel) -> str:
        status_val = (row.status or "ACTIVE").upper()
        if status_val == "REVOKED":
            return "REVOKED"
        if status_val == "EXHAUSTED":
            return "EXHAUSTED"
        expires = _as_aware(row.expires_at)
        if expires is not None and expires <= _now():
            return "EXPIRED"
        if row.use_count >= row.max_uses:
            return "EXHAUSTED"
        return status_val

    async def get_by_code(self, code: str) -> PlatformInviteModel | None:
        code_hash = invite_codes.hash_invite_code(code)
        result = await self.session.execute(
            select(PlatformInviteModel).where(PlatformInviteModel.code_hash == code_hash)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, invite_id: UUID) -> PlatformInviteModel | None:
        result = await self.session.execute(
            select(PlatformInviteModel).where(PlatformInviteModel.id == invite_id)
        )
        return result.scalar_one_or_none()

    async def create_company_invite(
        self,
        user_id: UUID,
        workspace_id: UUID,
        *,
        role_code: str = "MEMBER",
        expires_in_days: int | None = None,
        max_uses: int = 1,
    ) -> dict:
        from app.domains.business.workspace_service import (
            WORKSPACE_ROLES,
            BusinessWorkspaceService,
        )

        ws_svc = BusinessWorkspaceService(self.session)
        await ws_svc.require_member(workspace_id, user_id, min_role="MANAGER")
        ws = await ws_svc.get_workspace(workspace_id)
        if ws is None or (ws.status or "").upper() != "ACTIVE":
            raise InviteOutcomeError(
                "COMPANY_INACTIVE", "Company is inactive or not found", 404
            )

        role_u = (role_code or "MEMBER").upper()
        if role_u not in WORKSPACE_ROLES or role_u == "OWNER":
            raise InviteOutcomeError(
                "ROLE_INVALID", "Invite role must be MANAGER or MEMBER", 422
            )

        code, code_hash, suffix = await self._mint_unique_code()
        now = _now()
        row = PlatformInviteModel(
            id=uuid4(),
            code_hash=code_hash,
            code_suffix=suffix,
            invite_type="COMPANY",
            target_context="BUSINESS",
            target_id=workspace_id,
            workspace_id=workspace_id,
            moment_id=None,
            role_code=role_u,
            status="ACTIVE",
            created_by_user_id=user_id,
            created_at=now,
            expires_at=now + self._expiry_delta(expires_in_days),
            max_uses=self._clamp_max_uses(max_uses),
            use_count=0,
            metadata_json={"legacy_or_opaque": "OPAQUE_CODE"},
        )
        self.session.add(row)
        await self.session.flush()

        url = invite_codes.canonical_invite_url(code)
        try:
            await get_event_publisher().publish(
                invite_events.company_invite_created(
                    user_id=user_id,
                    invite_id=row.id,
                    workspace_id=workspace_id,
                    role_code=role_u,
                    max_uses=row.max_uses,
                )
            )
        except Exception:  # noqa: BLE001
            logger.debug("company_invite.created publish failed", exc_info=True)

        return {
            "invite_id": str(row.id),
            "code": code,
            "invite_url": url,
            "expires_at": row.expires_at.isoformat(),
            "role_code": role_u,
            "max_uses": row.max_uses,
            "qr_payload": url,
        }

    async def mint_opaque_moment_invite(
        self,
        user_id: UUID,
        moment,
        *,
        role_code: str = "PARTICIPANT",
        expires_in_days: int | None = None,
        max_uses: int = 1,
        metadata: dict | None = None,
    ) -> dict:
        """Mint an opaque invite for a moment already authorized by the caller."""
        code, code_hash, suffix = await self._mint_unique_code()
        now = _now()
        meta = dict(metadata or {})
        meta["legacy_or_opaque"] = "OPAQUE_CODE"
        moment_id = moment.id
        row = PlatformInviteModel(
            id=uuid4(),
            code_hash=code_hash,
            code_suffix=suffix,
            invite_type="GROUP",
            target_context=(moment.context_type or "GROUP").upper(),
            target_id=moment_id,
            workspace_id=None,
            moment_id=moment_id,
            role_code=(role_code or "PARTICIPANT").upper(),
            status="ACTIVE",
            created_by_user_id=user_id,
            created_at=now,
            expires_at=now + self._expiry_delta(expires_in_days),
            max_uses=self._clamp_max_uses(max_uses),
            use_count=0,
            metadata_json=meta,
        )
        self.session.add(row)
        await self.session.flush()
        url = invite_codes.canonical_invite_url(code)
        try:
            await get_event_publisher().publish(
                invite_events.group_invite_created(
                    user_id=user_id,
                    invite_id=row.id,
                    moment_id=moment_id,
                    role_code=row.role_code,
                )
            )
        except Exception:  # noqa: BLE001
            logger.debug("group_invite.created publish failed", exc_info=True)
        return {
            "invite_id": str(row.id),
            "code": code,
            "invite_url": url,
            "invite_link": url,
            "qr_payload": url,
            "invite_code": code,
            "expires_at": row.expires_at.isoformat(),
            "role_code": row.role_code,
            "max_uses": row.max_uses,
            "experience_name": moment.title,
            "moment_id": str(moment_id),
            "moment_type": moment.moment_type,
        }

    async def create_group_invite(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        role_code: str = "PARTICIPANT",
        expires_in_days: int | None = None,
        max_uses: int = 1,
        metadata: dict | None = None,
    ) -> dict:
        from app.domains.moments.repository import MomentRepository

        moment = await MomentRepository(self.session).get_by_user_and_id(user_id, moment_id)
        if moment is None:
            raise HTTPException(status_code=404, detail="Moment not found")
        return await self.mint_opaque_moment_invite(
            user_id,
            moment,
            role_code=role_code,
            expires_in_days=expires_in_days,
            max_uses=max_uses,
            metadata=metadata,
        )

    async def list_workspace_invites(
        self, user_id: UUID, workspace_id: UUID
    ) -> list[dict]:
        from app.domains.business.workspace_service import BusinessWorkspaceService

        await BusinessWorkspaceService(self.session).require_member(
            workspace_id, user_id, min_role="MANAGER"
        )
        result = await self.session.execute(
            select(PlatformInviteModel)
            .where(
                PlatformInviteModel.workspace_id == workspace_id,
                PlatformInviteModel.invite_type == "COMPANY",
            )
            .order_by(PlatformInviteModel.created_at.desc())
        )
        rows = list(result.scalars().all())
        out: list[dict] = []
        for row in rows:
            eff = self._effective_status(row)
            out.append(
                {
                    "invite_id": str(row.id),
                    "code_suffix": row.code_suffix,
                    "invite_type": row.invite_type,
                    "role_code": row.role_code,
                    "status": eff,
                    "created_at": row.created_at.isoformat() if row.created_at else "",
                    "expires_at": row.expires_at.isoformat() if row.expires_at else "",
                    "max_uses": row.max_uses,
                    "use_count": row.use_count,
                    "invite_url": None,
                }
            )
        return out

    async def preview(self, code: str) -> dict:
        if not invite_codes.is_opaque_code_shape(code):
            raise InviteOutcomeError("INVALID", "Invite not found", 404)
        row = await self.get_by_code(code)
        if row is None:
            raise InviteOutcomeError("INVALID", "Invite not found", 404)
        eff = self._effective_status(row)
        if row.invite_type == "COMPANY":
            return await self._preview_company(row, eff)
        return await self._preview_group(row, eff)

    async def _preview_company(self, row: PlatformInviteModel, eff: str) -> dict:
        from app.domains.business.workspace_service import BusinessWorkspaceService

        ws = await BusinessWorkspaceService(self.session).get_workspace(row.workspace_id)
        inviter = await self._user_display(row.created_by_user_id)
        role = (row.role_code or "MEMBER").upper()
        return {
            "invite_type": "COMPANY",
            "company": {
                "display_name": (ws.name if ws else "Company"),
                "logo_url": getattr(ws, "logo_url", None) if ws else None,
            },
            "inviter": {"display_name": inviter},
            "role": {"code": role, "display_name": _ROLE_LABELS.get(role, role.title())},
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
            "status": eff,
            "requires_authentication": True,
            "result_code": None if eff == "ACTIVE" else eff,
        }

    async def _preview_group(self, row: PlatformInviteModel, eff: str) -> dict:
        from app.domains.moments.repository import MomentRepository

        moment = (
            await MomentRepository(self.session).get_by_id(row.moment_id)
            if row.moment_id
            else None
        )
        inviter = await self._user_display(row.created_by_user_id)
        return {
            "invite_type": "GROUP",
            "company": {
                "display_name": (moment.title if moment else "Group moment"),
                "logo_url": None,
            },
            "inviter": {"display_name": inviter},
            "role": {
                "code": row.role_code or "PARTICIPANT",
                "display_name": "Participant",
            },
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
            "status": eff,
            "requires_authentication": True,
            "result_code": None if eff == "ACTIVE" else eff,
            "moment_id": str(row.moment_id) if row.moment_id else None,
            "moment_type": moment.moment_type if moment else None,
        }

    async def _user_display(self, user_id: UUID) -> str:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return "Someone"
        return (user.display_name or user.email or "Someone").strip() or "Someone"

    async def accept(self, user_id: UUID, code: str) -> dict:
        if not invite_codes.is_opaque_code_shape(code):
            raise InviteOutcomeError("INVALID", "Invite not found", 404)

        code_hash = invite_codes.hash_invite_code(code)
        # Prefer row lock when the dialect supports it (Postgres).
        try:
            result = await self.session.execute(
                select(PlatformInviteModel)
                .where(PlatformInviteModel.code_hash == code_hash)
                .with_for_update()
            )
        except Exception:
            result = await self.session.execute(
                select(PlatformInviteModel).where(
                    PlatformInviteModel.code_hash == code_hash
                )
            )
        row = result.scalar_one_or_none()
        if row is None:
            raise InviteOutcomeError("INVALID", "Invite not found", 404)

        eff = self._effective_status(row)
        if eff == "REVOKED":
            raise InviteOutcomeError("REVOKED", "Invite has been revoked", 400)
        if eff == "EXPIRED":
            row.status = "EXPIRED"
            raise InviteOutcomeError("EXPIRED", "Invite has expired", 400)

        # Already-member must win over EXHAUSTED so retries stay idempotent.
        if row.invite_type == "COMPANY":
            from app.domains.business.workspace_service import BusinessWorkspaceService

            ws_svc = BusinessWorkspaceService(self.session)
            existing = await ws_svc.get_member(row.workspace_id, user_id)
            already = (
                existing is not None and (existing.status or "").upper() != "REMOVED"
            )
            if already:
                return await self._accept_company(user_id, row)

        if eff == "EXHAUSTED":
            row.status = "EXHAUSTED"
            raise InviteOutcomeError("EXHAUSTED", "Invite has no remaining uses", 400)
        if eff not in {"ACTIVE", "ACCEPTED"}:
            raise InviteOutcomeError("INVALID", "Invite cannot be accepted", 400)

        if row.invite_type == "COMPANY":
            return await self._accept_company(user_id, row)
        return await self._accept_group(user_id, row)

    async def _accept_company(self, user_id: UUID, row: PlatformInviteModel) -> dict:
        from app.domains.business.workspace_service import BusinessWorkspaceService

        ws_svc = BusinessWorkspaceService(self.session)
        ws = await ws_svc.get_workspace(row.workspace_id)
        if ws is None or (ws.status or "").upper() != "ACTIVE":
            raise InviteOutcomeError(
                "COMPANY_INACTIVE", "Company is inactive or not found", 404
            )

        existing = await ws_svc.get_member(row.workspace_id, user_id)
        already = existing is not None and (existing.status or "").upper() != "REMOVED"
        if already:
            await ws_svc.set_selected_preference(user_id, row.workspace_id)
            await AppBootstrapService(self.session).invalidate_cache(user_id)
            mapped = ws_svc.map_workspace(ws, existing)
            session_payload = await self._company_session_slice(user_id, row.workspace_id)
            try:
                await get_event_publisher().publish(
                    invite_events.company_invite_accepted(
                        user_id=user_id,
                        invite_id=row.id,
                        workspace_id=row.workspace_id,
                        result="ALREADY_MEMBER",
                    )
                )
            except Exception:  # noqa: BLE001
                pass
            return {
                "result": "ALREADY_MEMBER",
                "workspace_id": str(row.workspace_id),
                "company_id": str(row.workspace_id),
                "membership": {
                    "role_code": mapped.get("role"),
                    "status": "ACTIVE",
                },
                "selected_workspace": mapped,
                "selected_company": mapped,
                "session": session_payload,
            }

        if row.use_count >= row.max_uses:
            row.status = "EXHAUSTED"
            raise InviteOutcomeError("EXHAUSTED", "Invite has no remaining uses", 400)

        member = await ws_svc.upsert_member_from_invite(
            workspace_id=row.workspace_id,
            user_id=user_id,
            role=(row.role_code or "MEMBER").upper(),
        )
        row.use_count += 1
        row.last_used_at = _now()
        if row.use_count >= row.max_uses:
            row.status = "EXHAUSTED"
        elif row.max_uses == 1:
            row.status = "ACCEPTED"
        await ws_svc.set_selected_preference(user_id, row.workspace_id)
        await self.session.flush()
        await AppBootstrapService(self.session).invalidate_cache(user_id)

        mapped = ws_svc.map_workspace(ws, member)
        session_payload = await self._company_session_slice(user_id, row.workspace_id)
        try:
            await get_event_publisher().publish(
                invite_events.company_invite_accepted(
                    user_id=user_id,
                    invite_id=row.id,
                    workspace_id=row.workspace_id,
                    result="ACCEPTED",
                )
            )
        except Exception:  # noqa: BLE001
            pass
        return {
            "result": "ACCEPTED",
            "workspace_id": str(row.workspace_id),
            "company_id": str(row.workspace_id),
            "membership": {
                "role_code": mapped.get("role"),
                "status": "ACTIVE",
            },
            "selected_workspace": mapped,
            "selected_company": mapped,
            "session": session_payload,
        }

    async def _company_session_slice(self, user_id: UUID, workspace_id: UUID) -> dict:
        from app.domains.business.app_service import BusinessAppService

        try:
            boot = await BusinessAppService(self.session).get_session(
                user_id, workspace_id=workspace_id
            )
            return boot
        except Exception:  # noqa: BLE001
            return {"workspace_id": str(workspace_id)}

    async def _accept_group(self, user_id: UUID, row: PlatformInviteModel) -> dict:
        from app.domains.invites.service import InviteService
        from app.domains.moments.repository import MomentRepository

        if row.moment_id is None:
            raise InviteOutcomeError("INVALID", "Invite not found", 404)
        moment = await MomentRepository(self.session).get_by_id(row.moment_id)
        if moment is None:
            raise InviteOutcomeError("INVALID", "Moment not found", 404)

        meta = dict(row.metadata_json or {})
        is_business = bool(meta.get("business_moment")) or (
            str(row.target_context or "").upper() == "BUSINESS"
        )
        if is_business:
            return await self._accept_business_moment(user_id, row, moment)

        already = moment.user_id == user_id
        attached_id = None
        if not already:
            # Runtime membership check
            from app.domains.group import moment_store as store

            uid = str(user_id)
            for member in store.list_accepted_members(moment):
                if str(member.get("user_id") or "") == uid:
                    already = True
                    attached_id = str(member.get("id") or uid)
                    break

        if already:
            await AppBootstrapService(self.session).invalidate_cache(user_id)
            return {
                "result": "ALREADY_MEMBER",
                "moment_id": str(moment.id),
                "moment_name": moment.title or "Your moment",
                "moment_type": moment.moment_type,
                "already_member": True,
                "participant_id": attached_id,
            }

        if row.use_count >= row.max_uses:
            row.status = "EXHAUSTED"
            raise InviteOutcomeError("EXHAUSTED", "Invite has no remaining uses", 400)

        invite_svc = InviteService(self.session)
        attached_id = invite_svc._attach_accepter(  # noqa: SLF001
            moment,
            user_id,
            participant_id=None,
            email=None,
        )
        await invite_svc._upsert_group_roster_member(  # noqa: SLF001
            moment,
            user_id,
            display_name="Member",
            member_id=attached_id,
        )
        row.use_count += 1
        row.last_used_at = _now()
        if row.use_count >= row.max_uses:
            row.status = "EXHAUSTED"
        await self.session.flush()
        await AppBootstrapService(self.session).invalidate_cache(user_id)
        try:
            await get_event_publisher().publish(
                invite_events.group_invite_accepted(
                    user_id=user_id,
                    invite_id=row.id,
                    moment_id=moment.id,
                    result="ACCEPTED",
                )
            )
        except Exception:  # noqa: BLE001
            pass
        return {
            "result": "ACCEPTED",
            "moment_id": str(moment.id),
            "moment_name": moment.title or "Your moment",
            "moment_type": moment.moment_type,
            "already_member": False,
            "participant_id": attached_id,
        }

    async def _accept_business_moment(
        self, user_id: UUID, row: PlatformInviteModel, moment
    ) -> dict:
        """Accept opaque invite into a business moment with role from invite row."""
        from datetime import datetime, timezone
        from uuid import uuid4

        from app.domains.business.models import BusinessMomentMembers, BusinessMoments
        from app.domains.business.setup.member_roles import to_db_member_role
        from app.domains.business.setup.team_ops_permissions import (
            default_profile_for_role,
            member_permission_flags,
        )
        from app.domains.users.models import UserModel

        mid = moment.id
        meta = dict(row.metadata_json or {})
        local_id = str(meta.get("local_id") or "").strip() or None
        role_api = (row.role_code or "MEMBER").upper()
        if role_api == "OWNER":
            role_api = "MEMBER"

        # Already a member?
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
            return {
                "result": "ALREADY_MEMBER",
                "moment_id": str(moment.id),
                "moment_name": moment.title or "Your moment",
                "moment_type": moment.moment_type,
                "already_member": True,
                "participant_id": str(active.member_id) if active else None,
            }

        if row.use_count >= row.max_uses:
            row.status = "EXHAUSTED"
            raise InviteOutcomeError("EXHAUSTED", "Invite has no remaining uses", 400)

        bm = await self.session.execute(
            select(BusinessMoments).where(BusinessMoments.moment_id == mid)
        )
        if bm.scalar_one_or_none() is None:
            raise InviteOutcomeError("INVALID", "Business moment not found", 404)

        pending = None
        if local_id:
            p_result = await self.session.execute(
                select(BusinessMomentMembers).where(
                    BusinessMomentMembers.moment_id == mid,
                    BusinessMomentMembers.local_id == local_id,
                )
            )
            try:
                pending_rows = list(p_result.scalars().all())
            except Exception:
                pending_rows = []
            pending = next(
                (
                    m
                    for m in pending_rows
                    if (m.member_status or "").lower() in {"invited", "configured"}
                    and m.user_id is None
                ),
                pending_rows[0] if pending_rows else None,
            )

        user_row = (
            await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        ).scalar_one_or_none()
        display = (
            (user_row.display_name or user_row.email or "Teammate")
            if user_row
            else "Teammate"
        )
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        db_role = to_db_member_role(role_api, template_code=moment.moment_type or "")
        flags = member_permission_flags(role_api)

        if pending is not None:
            if pending.user_id is not None and pending.user_id != user_id:
                raise InviteOutcomeError(
                    "INVALID", "This invitation belongs to another user", 403
                )
            pending.user_id = user_id
            pending.name = str(display)[:255]
            pending.role = db_role
            pending.member_status = "active"
            pending.permission_profile = default_profile_for_role(role_api)
            pending.permission_version = 1
            pending.updated_at = now
            if user_row and user_row.email and not pending.email:
                pending.email = user_row.email
            for k, v in flags.items():
                setattr(pending, k, v)
            member_id = str(pending.member_id)
        else:
            member = BusinessMomentMembers(
                member_id=uuid4(),
                moment_id=mid,
                name=str(display)[:255],
                role=db_role,
                member_status="active",
                added_by=moment.user_id or user_id,
                user_id=user_id,
                email=user_row.email if user_row else None,
                local_id=local_id,
                permission_profile=default_profile_for_role(role_api),
                permission_version=1,
                created_at=now,
                updated_at=now,
                can_manage_operations_settings=False,
                **flags,
            )
            self.session.add(member)
            await self.session.flush()
            member_id = str(member.member_id)

        row.use_count += 1
        row.last_used_at = _now()
        if row.use_count >= row.max_uses:
            row.status = "EXHAUSTED"
        elif row.max_uses == 1:
            row.status = "ACCEPTED"
        await self.session.flush()
        await AppBootstrapService(self.session).invalidate_cache(user_id)
        try:
            await get_event_publisher().publish(
                invite_events.group_invite_accepted(
                    user_id=user_id,
                    invite_id=row.id,
                    moment_id=moment.id,
                    result="ACCEPTED",
                )
            )
        except Exception:  # noqa: BLE001
            pass
        return {
            "result": "ACCEPTED",
            "moment_id": str(moment.id),
            "moment_name": moment.title or "Your moment",
            "moment_type": moment.moment_type,
            "already_member": False,
            "participant_id": member_id,
            "role_code": role_api,
            "invite_type": "BUSINESS",
        }

    async def decline(self, user_id: UUID, code: str) -> dict:
        row = await self.get_by_code(code)
        if row is None:
            raise InviteOutcomeError("INVALID", "Invite not found", 404)
        try:
            await get_event_publisher().publish(
                invite_events.company_invite_declined(
                    user_id=user_id,
                    invite_id=row.id,
                    workspace_id=row.workspace_id,
                )
            )
        except Exception:  # noqa: BLE001
            pass
        return {"result": "DECLINED", "invite_id": str(row.id)}

    async def revoke(self, user_id: UUID, invite_id: UUID) -> dict:
        from app.domains.business.workspace_service import BusinessWorkspaceService

        row = await self.get_by_id(invite_id)
        if row is None:
            raise InviteOutcomeError("INVALID", "Invite not found", 404)
        if row.invite_type == "COMPANY" and row.workspace_id is not None:
            await BusinessWorkspaceService(self.session).require_member(
                row.workspace_id, user_id, min_role="MANAGER"
            )
        elif row.created_by_user_id != user_id:
            raise InviteOutcomeError("UNAUTHORIZED", "Not allowed to revoke", 403)

        if (row.status or "").upper() == "REVOKED":
            return {"result": "REVOKED", "invite_id": str(row.id)}

        row.status = "REVOKED"
        row.revoked_at = _now()
        row.revoked_by_user_id = user_id
        await self.session.flush()
        try:
            await get_event_publisher().publish(
                invite_events.company_invite_revoked(
                    user_id=user_id,
                    invite_id=row.id,
                    workspace_id=row.workspace_id,
                )
            )
        except Exception:  # noqa: BLE001
            pass
        return {"result": "REVOKED", "invite_id": str(row.id)}
