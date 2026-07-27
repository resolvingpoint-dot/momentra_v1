"""Moments projection mapper for Team Operations — distinct from Pulse timeline."""
from __future__ import annotations

from app.domains.business.templates.team_operations.context import TeamOpsContext
from app.domains.business.templates.team_operations.section_helpers import (
    event_item,
    filter_actions,
    section_state,
)

_MEETING = {"MEETING"}
_APPROVAL = {"APPROVAL_REQUEST"}
_RECOGNITION = {"RECOGNITION"}
_ISSUES = {"ISSUE", "ESCALATION"}
_TEAM_CHANGES = {"MEMBER_UPDATE", "TEAM_UPDATE", "PARTICIPATION"}
_MILESTONES = {"REVIEW", "MEETING", "RECOGNITION"}


def build_moments(ctx: TeamOpsContext) -> dict:
    activities = list(getattr(ctx, "activities", None) or [])
    meetings = filter_actions(activities, _MEETING)
    approvals = filter_actions(activities, _APPROVAL)
    recognition = filter_actions(activities, _RECOGNITION)
    issues = filter_actions(activities, _ISSUES)
    team_changes = filter_actions(activities, _TEAM_CHANGES)
    milestones = filter_actions(activities, _MILESTONES)
    timeline = [event_item(a) for a in activities]
    recent = [event_item(a) for a in activities[:10]]
    member_count = int(getattr(ctx, "member_count", 0) or 0)
    open_issues = int(getattr(ctx, "open_issues", 0) or 0)
    pending_approvals = int(getattr(ctx, "pending_approvals", 0) or 0)
    escalation_count = int(getattr(ctx, "escalation_count", 0) or 0)
    recognition_count = int(getattr(ctx, "recognition_count", 0) or 0)
    meeting_count = int(getattr(ctx, "meeting_count", 0) or 0)
    activity_count = int(getattr(ctx, "activity_count", 0) or 0)
    team_name = getattr(ctx, "team_name", None)
    moment_name = getattr(ctx, "moment_name", None)

    projection = getattr(ctx, "projection", None)
    progress_snapshot = (
        projection.progress_snapshots if projection is not None else []
    )
    highlights = projection.highlights if projection is not None else recent[:4]

    return {
        "moment_id": str(ctx.moment_id),
        "moment_type": ctx.moment_type,
        "moment_name": moment_name,
        "team_name": team_name,
        "status": ctx.status,
        "operations_hub": {
            "member_count": member_count,
            "open_issues": open_issues,
            "pending_approvals": pending_approvals,
            "escalations": escalation_count,
        },
        "journey_hero": {
            "state": section_state(count=1 if (team_name or moment_name) else 0),
            "title": team_name or moment_name or "Team Operations",
            "subtitle": "Team journey",
            "member_count": member_count,
            "activity_count": activity_count,
            "is_active": ctx.is_active,
        },
        "progress_snapshot": {
            "state": section_state(count=len(progress_snapshot)),
            "items": progress_snapshot,
        },
        "highlights": {
            "state": section_state(count=len(highlights)),
            "items": highlights,
        },
        "milestones": {
            "state": section_state(count=len(milestones)),
            "items": milestones[:20],
        },
        "meetings": {
            "state": section_state(count=meeting_count + len(meetings)),
            "count": meeting_count,
            "items": meetings[:20],
        },
        "approvals": {
            "state": section_state(
                count=pending_approvals + len(approvals),
                has_attention=pending_approvals > 0,
            ),
            "pending_count": pending_approvals,
            "items": approvals[:20],
        },
        "recognition": {
            "state": section_state(count=recognition_count + len(recognition)),
            "count": recognition_count,
            "items": recognition[:20],
        },
        "issues": {
            "state": section_state(
                count=open_issues + len(issues),
                has_attention=open_issues > 0,
            ),
            "open_count": open_issues,
            "items": issues[:20],
        },
        "team_changes": {
            "state": section_state(count=len(team_changes)),
            "items": team_changes[:20],
        },
        "timeline": {
            "state": section_state(count=len(timeline)),
            "items": timeline,
        },
        "recent_activity": {
            "state": section_state(count=len(recent)),
            "items": recent,
        },
    }
