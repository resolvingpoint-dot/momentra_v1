"""Quick-add / Action Center catalog for Team Operations."""
from __future__ import annotations

from app.domains.business.action_catalog import build_action_catalog_payload
from app.domains.business.templates.team_operations.context import TeamOpsContext


def build_quick_add(ctx: TeamOpsContext) -> dict:
    return build_action_catalog_payload(
        moment_id=str(ctx.moment_id),
        moment_type=ctx.moment_type or "TEAM_OPERATIONS",
        members=getattr(ctx, "member_picker", None) or [],
    )
