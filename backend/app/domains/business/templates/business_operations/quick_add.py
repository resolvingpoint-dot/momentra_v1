"""Quick-add / Action Center catalog for Business Operations."""
from __future__ import annotations

from app.domains.business.action_catalog import build_action_catalog_payload
from app.domains.business.templates.business_operations.context import OpsContext


def build_quick_add(ctx: OpsContext) -> dict:
    return build_action_catalog_payload(
        moment_id=str(ctx.moment_id),
        moment_type=ctx.moment_type or "BUSINESS_OPERATIONS",
        members=getattr(ctx, "member_picker", None) or [],
    )
