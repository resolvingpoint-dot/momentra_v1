"""Live hub mapper for Shared Living."""
from __future__ import annotations

from app.domains.group import trip_schemas as ts
from app.domains.group.templates.shared_living.context import SharedLivingContext


def build_live_hub(ctx: SharedLivingContext) -> dict:
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
            subtitle="Run your shared home together.",
        ).model_dump(mode="json"),
        "journey_steps": [
            ts.TripLiveHubJourneyStep(id="invite", label="Invite residents", state="active" if ctx.resident_count else "upcoming").model_dump(mode="json"),
            ts.TripLiveHubJourneyStep(id="setup", label="Set up expenses & chores", state="active" if ctx.expense_count or ctx.task_count else "upcoming").model_dump(mode="json"),
            ts.TripLiveHubJourneyStep(id="live", label="Run it together", state="active" if ctx.is_active else "upcoming").model_dump(mode="json"),
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
