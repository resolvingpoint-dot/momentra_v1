"""Live hub projection mapper for Shared Experience."""
from __future__ import annotations

from app.domains.group import trip_schemas as t
from app.domains.group.templates.shared_experience.context import SharedExperienceContext


def _quick_add_modules(ctx: SharedExperienceContext) -> list[t.TripLiveHubQuickAddModule]:
    icon_map = {
        "EXPENSE": "receipt",
        "PARTICIPANT": "person_add",
        "CONTRIBUTION": "wallet",
        "BOOKING": "event",
        "MEMORY": "photo_camera",
        "PLANNING_ITEM": "map",
        "VENDOR": "store",
        "POLL": "poll",
        "ATTENDANCE": "groups",
        "UPDATE": "campaign",
    }
    label_map = {
        "EXPENSE": "Expense",
        "PARTICIPANT": "Participant",
        "CONTRIBUTION": "Contribution",
        "BOOKING": "Booking",
        "MEMORY": "Memory",
        "PLANNING_ITEM": "Plan",
        "VENDOR": "Vendor",
        "POLL": "Poll",
        "ATTENDANCE": "Attendance",
        "UPDATE": "Update",
    }
    modules: list[t.TripLiveHubQuickAddModule] = []
    for code in ctx.experience_type.quick_add_modules:
        modules.append(
            t.TripLiveHubQuickAddModule(
                module_code=code,
                label=label_map.get(code, code.title()),
                icon=icon_map.get(code, "add"),
            )
        )
    return modules


def build_live_hub(ctx: SharedExperienceContext) -> dict:
    et = ctx.experience_type
    stages = et.timeline_stages or ["Plan", "Live", "Remember"]
    journey = [
        t.TripLiveHubJourneyStep(
            id=s.lower().replace(" ", "_"),
            label=s,
            state="active" if i == 0 else "upcoming",
        )
        for i, s in enumerate(stages)
    ]
    activity_items = [
        t.TripLiveHubActivityItem(
            id=str(a.get("id") or ""),
            activity_type=str(a.get("activity_type") or "UPDATE"),
            title=str(a.get("title") or ""),
            subtitle=str(a.get("subtitle") or ""),
            icon=str(a.get("icon") or "update"),
            occurred_at=str(a.get("occurred_at") or ""),
        )
        for a in ctx.activities[:15]
    ]
    return t.TripLiveHubResponse(
        moment_id=str(ctx.moment.id),
        header=t.TripLiveHubHeader(
            moment_name=ctx.moment_name,
            status_badge=ctx.status_badge,
            profile_badge=ctx.profile_badge,
        ),
        hero=t.TripLiveHubHero(
            title=ctx.moment_name,
            subtitle="Coordinate everything for this experience in one place.",
        ),
        experience_profile=t.TripLiveHubExperienceProfile(
            title=ctx.profile_badge,
            description="Plan, spend and capture together as it happens.",
            capability_chips=list(et.capability_chips),
            profile_icon=et.icon,
        ),
        creation_event=t.TripLiveHubCreationEvent(
            title="Moment created",
            subtitle="Invite your people and start planning.",
        ),
        journey_steps=journey,
        insight=t.TripLiveHubInsight(
            title="You're just getting started" if not ctx.activities else "Your group is active",
            message=et.pulse_readiness_narrative,
        ),
        activity_empty_message="Nothing here yet — activity will show up as your group gets going.",
        lifecycle_status=(ctx.moment.status or "DRAFT").lower(),
        orchestration_state=ctx.moment.setup_state,
        can_open_live_workspace=ctx.is_active,
        quick_add_modules=_quick_add_modules(ctx),
        activity_items=activity_items,
    ).model_dump(mode="json")
