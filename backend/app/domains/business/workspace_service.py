"""Company workspace service — multi-company Business auth/home boundary."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domains.business.models import (
    BusinessMoments,
    BusinessWorkspaceInvitations,
    BusinessWorkspaceMembers,
    BusinessWorkspaces,
)
from app.domains.preferences.models import UserPreferencesModel

WORKSPACE_ROLES = frozenset({"OWNER", "MANAGER", "MEMBER"})


def company_invite_link(token: str) -> str:
    """Build shareable/QR company invite URL: {base}/company-invite/{token}."""
    base = (settings.invite_link_base_url or "https://www.momentra.tech/invite").rstrip("/")
    if "://" in base:
        scheme, rest = base.split("://", 1)
        if scheme.lower() in ("http", "https"):
            if rest.endswith("/invite"):
                rest = f"{rest[: -len('/invite')]}/company-invite"
            elif "/invite" in rest:
                rest = rest.replace("/invite", "/company-invite", 1)
            else:
                rest = f"{rest.rstrip('/')}/company-invite"
            return f"{scheme}://{rest}/{token}"
        # Custom scheme e.g. momentra://invite → momentra://company-invite/{token}
        return f"{scheme}://company-invite/{token}"
    return f"https://www.momentra.tech/company-invite/{token}"

MODULE_TILES = [
    {
        "key": "finance",
        "label": "Finance",
        "status": "coming_soon",
        "description": "Cash, expenses, and P&L for this company.",
    },
    {
        "key": "inventory",
        "label": "Inventory",
        "status": "coming_soon",
        "description": "Stock levels, SKUs, and warehouse moves.",
    },
    {
        "key": "sales",
        "label": "Sales",
        "status": "coming_soon",
        "description": "Orders, invoices, and revenue tracking.",
    },
    {
        "key": "gst",
        "label": "GST",
        "status": "coming_soon",
        "description": "Returns, invoices, and tax compliance.",
    },
]


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WorkspacePermissionError(HTTPException):
    def __init__(self, detail_code: str, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": detail_code, "message": message},
        )


class BusinessWorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_memberships(
        self, user_id: UUID
    ) -> list[tuple[BusinessWorkspaces, BusinessWorkspaceMembers]]:
        result = await self.session.execute(
            select(BusinessWorkspaces, BusinessWorkspaceMembers)
            .join(
                BusinessWorkspaceMembers,
                BusinessWorkspaceMembers.workspace_id == BusinessWorkspaces.workspace_id,
            )
            .where(
                BusinessWorkspaceMembers.user_id == user_id,
                BusinessWorkspaceMembers.status == "ACTIVE",
                BusinessWorkspaces.status == "ACTIVE",
            )
            .order_by(BusinessWorkspaces.name.asc())
        )
        return list(result.all())

    async def count_active_members(self, workspace_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(BusinessWorkspaceMembers)
            .where(
                BusinessWorkspaceMembers.workspace_id == workspace_id,
                BusinessWorkspaceMembers.status == "ACTIVE",
            )
        )
        return int(result.scalar_one() or 0)

    async def get_member(
        self, workspace_id: UUID, user_id: UUID
    ) -> BusinessWorkspaceMembers | None:
        result = await self.session.execute(
            select(BusinessWorkspaceMembers).where(
                BusinessWorkspaceMembers.workspace_id == workspace_id,
                BusinessWorkspaceMembers.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def require_member(
        self, workspace_id: UUID, user_id: UUID, *, min_role: str | None = None
    ) -> tuple[BusinessWorkspaces, BusinessWorkspaceMembers]:
        ws = await self.get_workspace(workspace_id)
        if ws is None or (ws.status or "").upper() != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "workspace_not_found", "message": "Company not found."},
            )
        member = await self.get_member(workspace_id, user_id)
        if member is None or (member.status or "").upper() != "ACTIVE":
            raise WorkspacePermissionError(
                "workspace_permission_denied",
                "You are not a member of this company.",
            )
        if min_role:
            order = {"MEMBER": 0, "MANAGER": 1, "OWNER": 2}
            if order.get((member.role or "").upper(), -1) < order.get(min_role.upper(), 99):
                raise WorkspacePermissionError(
                    "workspace_permission_denied",
                    f"Requires {min_role} role or higher.",
                )
        return ws, member

    async def get_workspace(self, workspace_id: UUID) -> BusinessWorkspaces | None:
        result = await self.session.execute(
            select(BusinessWorkspaces).where(BusinessWorkspaces.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def get_selected_preference(self, user_id: UUID) -> UUID | None:
        result = await self.session.execute(
            select(UserPreferencesModel).where(UserPreferencesModel.user_id == user_id)
        )
        pref = result.scalar_one_or_none()
        if pref is None:
            return None
        return getattr(pref, "selected_business_workspace_id", None)

    async def set_selected_preference(self, user_id: UUID, workspace_id: UUID | None) -> None:
        result = await self.session.execute(
            select(UserPreferencesModel).where(UserPreferencesModel.user_id == user_id)
        )
        pref = result.scalar_one_or_none()
        if pref is None:
            return
        pref.selected_business_workspace_id = workspace_id
        pref.updated_at = datetime.now(timezone.utc)

    async def resolve_selected(
        self,
        user_id: UUID,
        *,
        workspace_id: UUID | None = None,
        memberships: list[tuple[BusinessWorkspaces, BusinessWorkspaceMembers]] | None = None,
    ) -> tuple[BusinessWorkspaces, BusinessWorkspaceMembers] | None:
        pairs = (
            memberships
            if memberships is not None
            else await self.list_memberships(user_id)
        )
        if not pairs:
            return None

        if workspace_id is not None:
            for ws, member in pairs:
                if ws.workspace_id == workspace_id:
                    return ws, member
            raise WorkspacePermissionError(
                "workspace_permission_denied",
                "You are not a member of this company.",
            )

        preferred = await self.get_selected_preference(user_id)
        if preferred is not None:
            for ws, member in pairs:
                if ws.workspace_id == preferred:
                    return ws, member

        return pairs[0]

    def map_workspace(
        self, ws: BusinessWorkspaces, member: BusinessWorkspaceMembers
    ) -> dict:
        return {
            "id": str(ws.workspace_id),
            "name": ws.name,
            "logo": ws.logo_url,
            "role": (member.role or "MEMBER").upper(),
            "currency": getattr(ws, "currency_code", None) or "INR",
            "timezone": getattr(ws, "timezone", None) or "Asia/Kolkata",
            "industry": getattr(ws, "industry", None),
            "status": ws.status,
        }

    async def create_workspace(
        self,
        user_id: UUID,
        *,
        name: str,
        currency_code: str = "INR",
        timezone_name: str = "Asia/Kolkata",
        industry: str | None = None,
        logo_url: str | None = None,
    ) -> dict:
        clean = (name or "").strip()
        if not clean:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Company name is required.",
            )
        now = _now()
        ws = BusinessWorkspaces(
            workspace_id=uuid4(),
            owned_by=user_id,
            created_by=user_id,
            name=clean[:255],
            status="ACTIVE",
            logo_url=logo_url,
            industry=(industry or None),
            currency_code=(currency_code or "INR")[:3].upper(),
            timezone=(timezone_name or "Asia/Kolkata")[:64],
            created_at=now,
            updated_at=now,
        )
        self.session.add(ws)
        await self.session.flush()

        member = BusinessWorkspaceMembers(
            member_id=uuid4(),
            workspace_id=ws.workspace_id,
            user_id=user_id,
            role="OWNER",
            status="ACTIVE",
            created_at=now,
            updated_at=now,
        )
        self.session.add(member)
        await self.set_selected_preference(user_id, ws.workspace_id)
        await self.session.flush()
        return self.map_workspace(ws, member)

    async def update_workspace(
        self,
        user_id: UUID,
        workspace_id: UUID,
        *,
        name: str | None = None,
        logo_url: str | None = None,
        industry: str | None = None,
        currency_code: str | None = None,
        timezone_name: str | None = None,
        status: str | None = None,
    ) -> dict:
        ws, member = await self.require_member(workspace_id, user_id, min_role="MANAGER")
        if status is not None and (member.role or "").upper() != "OWNER":
            raise WorkspacePermissionError(
                "workspace_permission_denied",
                "Only the owner can archive or delete a company.",
            )
        if name is not None:
            clean = name.strip()
            if not clean:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Company name is required.",
                )
            ws.name = clean[:255]
        if logo_url is not None:
            ws.logo_url = logo_url or None
        if industry is not None:
            ws.industry = industry or None
        if currency_code is not None:
            ws.currency_code = currency_code[:3].upper()
        if timezone_name is not None:
            ws.timezone = timezone_name[:64]
        if status is not None:
            ws.status = status.upper()
        ws.updated_at = _now()
        await self.session.flush()
        return self.map_workspace(ws, member)

    async def select_workspace(self, user_id: UUID, workspace_id: UUID) -> dict:
        ws, member = await self.require_member(workspace_id, user_id)
        await self.set_selected_preference(user_id, workspace_id)
        await self.session.flush()
        return self.map_workspace(ws, member)

    async def list_members(self, user_id: UUID, workspace_id: UUID) -> list[dict]:
        await self.require_member(workspace_id, user_id)
        result = await self.session.execute(
            select(BusinessWorkspaceMembers).where(
                BusinessWorkspaceMembers.workspace_id == workspace_id,
            )
        )
        rows = list(result.scalars().all())
        return [
            {
                "member_id": str(m.member_id),
                "user_id": str(m.user_id),
                "role": (m.role or "MEMBER").upper(),
                "status": (m.status or "ACTIVE").upper(),
            }
            for m in rows
            if (m.status or "ACTIVE").upper() != "REMOVED"
        ]

    async def invite_member(
        self,
        user_id: UUID,
        workspace_id: UUID,
        *,
        email: str,
        role: str = "MEMBER",
    ) -> dict:
        await self.require_member(workspace_id, user_id, min_role="MANAGER")
        role_u = (role or "MEMBER").upper()
        if role_u not in WORKSPACE_ROLES or role_u == "OWNER":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invite role must be MANAGER or MEMBER.",
            )
        clean_email = (email or "").strip().lower()
        if not clean_email or "@" not in clean_email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Valid invitee email is required.",
            )
        now = _now()
        token = secrets.token_urlsafe(24)
        invite = BusinessWorkspaceInvitations(
            invitation_id=uuid4(),
            workspace_id=workspace_id,
            invited_by=user_id,
            invitee_email=clean_email,
            role=role_u,
            token=token,
            status="PENDING",
            created_at=now,
        )
        self.session.add(invite)
        await self.session.flush()
        link = company_invite_link(token)
        return {
            "invitation_id": str(invite.invitation_id),
            "workspace_id": str(workspace_id),
            "invitee_email": clean_email,
            "role": role_u,
            "token": token,
            "invite_link": link,
            "qr_payload": link,
            "status": "PENDING",
        }

    async def upsert_member_from_invite(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
        role: str = "MEMBER",
    ) -> BusinessWorkspaceMembers:
        """Create or reactivate workspace membership (opaque company invite)."""
        existing = await self.get_member(workspace_id, user_id)
        now = _now()
        role_u = (role or "MEMBER").upper()
        if existing is None:
            member = BusinessWorkspaceMembers(
                member_id=uuid4(),
                workspace_id=workspace_id,
                user_id=user_id,
                role=role_u,
                status="ACTIVE",
                created_at=now,
                updated_at=now,
            )
            self.session.add(member)
            await self.session.flush()
            return member
        existing.status = "ACTIVE"
        existing.role = role_u or (existing.role or "MEMBER").upper()
        existing.updated_at = now
        await self.session.flush()
        return existing

    async def accept_invite(self, user_id: UUID, token: str) -> dict:
        result = await self.session.execute(
            select(BusinessWorkspaceInvitations).where(
                BusinessWorkspaceInvitations.token == token
            )
        )
        invite = result.scalar_one_or_none()
        if invite is None or (invite.status or "").upper() not in ("PENDING", "SENT"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found or already used.",
            )
        ws = await self.get_workspace(invite.workspace_id)
        if ws is None or (ws.status or "").upper() != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found.",
            )
        existing = await self.get_member(invite.workspace_id, user_id)
        now = _now()
        if existing is None:
            member = BusinessWorkspaceMembers(
                member_id=uuid4(),
                workspace_id=invite.workspace_id,
                user_id=user_id,
                role=(invite.role or "MEMBER").upper(),
                status="ACTIVE",
                created_at=now,
                updated_at=now,
            )
            self.session.add(member)
        else:
            existing.status = "ACTIVE"
            existing.role = (invite.role or existing.role or "MEMBER").upper()
            existing.updated_at = now
            member = existing
        invite.status = "ACCEPTED"
        invite.invitee_user_id = user_id
        invite.accepted_at = now
        await self.set_selected_preference(user_id, invite.workspace_id)
        await self.session.flush()
        return self.map_workspace(ws, member)

    async def ensure_owner_membership(
        self, workspace_id: UUID, owner_user_id: UUID
    ) -> None:
        """Ensure OWNER row exists (legacy workspace create path)."""
        existing = await self.get_member(workspace_id, owner_user_id)
        if existing is not None:
            if (existing.status or "").upper() != "ACTIVE":
                existing.status = "ACTIVE"
                existing.role = "OWNER"
                existing.updated_at = _now()
            return
        now = _now()
        self.session.add(
            BusinessWorkspaceMembers(
                member_id=uuid4(),
                workspace_id=workspace_id,
                user_id=owner_user_id,
                role="OWNER",
                status="ACTIVE",
                created_at=now,
                updated_at=now,
            )
        )
        await self.session.flush()

    async def dashboard_summary(
        self,
        workspace_id: UUID,
        *,
        open_moments: int | None = None,
    ) -> dict:
        member_count = await self.count_active_members(workspace_id)
        if open_moments is None:
            moments = await self.session.execute(
                select(BusinessMoments).where(
                    BusinessMoments.workspace_id == workspace_id,
                )
            )
            moment_rows = list(moments.scalars().all())
            open_moments = sum(
                1
                for m in moment_rows
                if (m.status or "").lower() in ("active", "configured", "draft")
            )
        return {
            "open_moments": open_moments,
            "pending_approvals": 0,
            "member_count": member_count,
            "revenue_today": None,
            "cash_balance": None,
        }

    def module_tiles(self) -> list[dict]:
        return list(MODULE_TILES)

    async def moment_ids_for_workspace(self, workspace_id: UUID) -> set[UUID]:
        result = await self.session.execute(
            select(BusinessMoments.moment_id).where(
                BusinessMoments.workspace_id == workspace_id
            )
        )
        return {row[0] for row in result.all()}
