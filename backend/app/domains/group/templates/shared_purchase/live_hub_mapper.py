"""Live hub mapper for Shared Purchase."""
from __future__ import annotations

from app.domains.group import trip_schemas as ts
from app.domains.group.templates.shared_purchase.context import SharedPurchaseContext


def build_live_hub(ctx: SharedPurchaseContext) -> dict:
    return {
        "moment_id": str(ctx.moment.id),
        "selector": {
            "moment_id": str(ctx.moment.id),
            "moment_name": ctx.moment_name,
            "profile_label": ctx.profile_badge,
        },
        "header": ts.TripLiveHubHeader(
            moment_name=ctx.moment_name,
            status_badge=ctx.status_badge,
            profile_badge=ctx.profile_badge,
        ).model_dump(mode="json"),
        "hero": ts.TripLiveHubHero(
            title=ctx.moment_name,
            subtitle="Coordinate the group purchase in one place.",
        ).model_dump(mode="json"),
        "journey_steps": [
            ts.TripLiveHubJourneyStep(id="invite", label="Invite contributors", state="active" if ctx.contributor_count else "upcoming").model_dump(mode="json"),
            ts.TripLiveHubJourneyStep(id="fund", label="Collect funds", state="active" if ctx.contribution_total_minor else "upcoming").model_dump(mode="json"),
            ts.TripLiveHubJourneyStep(id="buy", label="Make the purchase", state="upcoming").model_dump(mode="json"),
        ],
        "insight": ts.TripLiveHubInsight(
            title=ctx.profile.pulse_readiness_title,
            message=ctx.profile.pulse_readiness_narrative,
        ).model_dump(mode="json"),
        "lifecycle_status": (ctx.moment.status or "DRAFT").lower(),
        "orchestration_state": ctx.moment.setup_state,
        "quick_add_modules": ctx.profile.quick_add_modules,
        "activity_feed": ctx.activities[:10],
    }
