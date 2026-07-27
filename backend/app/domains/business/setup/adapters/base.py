"""Template adapter protocol for Business setup."""
from __future__ import annotations

from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.setup.schemas import SetupPreviewResponse


class BusinessSetupAdapter(Protocol):
    moment_type_code: str
    template_id: str

    def bind(self, session: AsyncSession) -> Any: ...

    def normalize_answers(
        self,
        answers: dict[str, Any],
        *,
        owner_user_id: str | None = None,
        owner_display_name: str | None = None,
    ) -> dict[str, Any]: ...

    def validate_draft(self, answers: dict[str, Any]) -> list[str]: ...

    def build_preview(
        self,
        answers: dict[str, Any],
        *,
        owner_user_id: str | None = None,
    ) -> SetupPreviewResponse: ...

    def validate_activation(
        self,
        answers: dict[str, Any],
        *,
        owner_user_id: str | None = None,
    ) -> list[str]: ...

    async def commit_profile(self, *, moment_id: str, user_id: str, answers: dict[str, Any]) -> None: ...

    async def commit_governance(self, *, moment_id: str, user_id: str, answers: dict[str, Any]) -> None: ...

    async def commit_members(self, *, moment_id: str, user_id: str, answers: dict[str, Any]) -> None: ...
