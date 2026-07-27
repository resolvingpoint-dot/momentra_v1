"""Pulse projection mapper for Team Operations — deterministic section tree."""
from __future__ import annotations

from app.domains.business.templates.team_operations.context import TeamOpsContext
from app.domains.business.templates.team_operations.section_helpers import (
    event_item,
    filter_actions,
    rule_based_team_health,
    section_state,
)
from app.domains.business.templates.team_operations.signals import derive_signals

_APPROVAL = {"APPROVAL_REQUEST"}
_PARTICIPATION = {"PARTICIPATION"}
_ISSUES = {"ISSUE", "ESCALATION"}
_RECOGNITION = {"RECOGNITION"}


def _merge_health(ctx: TeamOpsContext, fallback: dict) -> dict:
    projection = getattr(ctx, "projection", None)
    if projection is None:
        return fallback
    merged = dict(fallback)
    merged["label"] = projection.health_label
    merged["band"] = projection.health_band
    merged["score"] = float(projection.health_score)
    merged["max_score"] = 100
    merged["rule"] = "weighted_driver_blend"
    return merged


def build_pulse(ctx: TeamOpsContext) -> dict:
    activities = list(getattr(ctx, "activities", None) or [])
    approvals = filter_actions(activities, _APPROVAL)
    participation = filter_actions(activities, _PARTICIPATION)
    issues = filter_actions(activities, _ISSUES)
    recognition = filter_actions(activities, _RECOGNITION)
    recent = [event_item(a) for a in activities[:20]]
    fallback_signals = derive_signals(ctx)
    member_count = int(getattr(ctx, "member_count", 0) or 0)
    open_issues = int(getattr(ctx, "open_issues", 0) or 0)
    pending_approvals = int(getattr(ctx, "pending_approvals", 0) or 0)
    escalation_count = int(getattr(ctx, "escalation_count", 0) or 0)
    recognition_count = int(getattr(ctx, "recognition_count", 0) or 0)
    meeting_count = int(getattr(ctx, "meeting_count", 0) or 0)
    participation_count = int(getattr(ctx, "participation_count", 0) or 0)
    activity_count = int(getattr(ctx, "activity_count", 0) or 0)
    health = _merge_health(
        ctx,
        rule_based_team_health(
            member_count=member_count,
            open_issues=open_issues,
            pending_approvals=pending_approvals,
            escalation_count=escalation_count,
        ),
    )

    projection = getattr(ctx, "projection", None)
    if projection is not None:
        attention = [
            {
                "kind": item.get("kind") or item.get("attention_type", ""),
                "label": item.get("title", ""),
                "count": item.get("count", 0),
                "severity": item.get("severity"),
                "description": item.get("description"),
            }
            for item in projection.attention_items
        ]
        signals = [
            {
                "signal_type": item.get("signal_type", ""),
                "label": item.get("title", ""),
                "title": item.get("title", ""),
                "summary": item.get("summary"),
                "change_percent": item.get("change_percent"),
                "severity": item.get("impact_level"),
            }
            for item in projection.signal_items
        ]
        health_drivers = projection.health_drivers
        next_action = projection.recommended_action
    else:
        attention = []
        if open_issues > 0:
            attention.append({
                "kind": "open_issues",
                "label": f"{open_issues} open issue{'s' if open_issues != 1 else ''}",
                "count": open_issues,
            })
        if pending_approvals > 0:
            attention.append({
                "kind": "pending_approvals",
                "label": f"{pending_approvals} pending approval{'s' if pending_approvals != 1 else ''}",
                "count": pending_approvals,
            })
        if escalation_count > 0:
            attention.append({
                "kind": "escalations",
                "label": f"{escalation_count} escalation{'s' if escalation_count != 1 else ''}",
                "count": escalation_count,
            })
        signals = fallback_signals
        health_drivers = []
        next_action = None
        if pending_approvals > 0:
            next_action = {
                "action_id": "approval",
                "label": "Review pending approvals",
                "reason": "pending_approvals",
            }
        elif open_issues > 0:
            next_action = {
                "action_id": "issue",
                "label": "Triage open issues",
                "reason": "open_issues",
            }
        elif member_count > 0:
            next_action = {
                "action_id": "team_update",
                "label": "Post a team update",
                "reason": "keep_rhythm",
            }

    return {
        "moment_id": str(ctx.moment_id),
        "moment_type": ctx.moment_type,
        "moment_name": getattr(ctx, "moment_name", None),
        "team_name": getattr(ctx, "team_name", None),
        "status": ctx.status,
        "is_active": ctx.is_active,
        "member_count": member_count,
        "activity_count": activity_count,
        "operating_currency": getattr(ctx, "operating_currency", "INR"),
        "stats": {
            "members": member_count,
            "open_issues": open_issues,
            "pending_approvals": pending_approvals,
            "recognitions": recognition_count,
            "meetings": meeting_count,
            "escalations": escalation_count,
            "participation": participation_count,
        },
        "hero": {
            "state": section_state(count=1 if (getattr(ctx, "moment_name", None) or getattr(ctx, "team_name", None)) else 0),
            "title": getattr(ctx, "team_name", None) or getattr(ctx, "moment_name", None) or "Team Operations",
            "subtitle": "Team Operations",
            "status": ctx.status,
            "is_active": ctx.is_active,
            "overall_team_health": health,
        },
        "health_drivers": {
            "state": section_state(count=len(health_drivers)),
            "items": health_drivers,
        },
        "kpis": {
            "state": section_state(
                count=member_count + activity_count,
                has_attention=bool(attention),
            ),
            "members": member_count,
            "open_issues": open_issues,
            "pending_approvals": pending_approvals,
            "recognitions": recognition_count,
            "meetings": meeting_count,
            "escalations": escalation_count,
            "participation": participation_count,
            "overall_team_health": health,
        },
        "approvals": {
            "state": section_state(
                count=pending_approvals + len(approvals),
                has_attention=pending_approvals > 0,
            ),
            "pending_count": pending_approvals,
            "items": approvals[:10],
        },
        "participation": {
            "state": section_state(count=participation_count + len(participation)),
            "count": participation_count,
            "items": participation[:10],
        },
        "issues": {
            "state": section_state(
                count=open_issues + escalation_count + len(issues),
                has_attention=open_issues > 0 or escalation_count > 0,
            ),
            "open_count": open_issues,
            "escalation_count": escalation_count,
            "items": issues[:10],
        },
        "recognition": {
            "state": section_state(count=recognition_count + len(recognition)),
            "count": recognition_count,
            "items": recognition[:10],
        },
        "recent_activity": {
            "state": section_state(count=len(recent)),
            "items": recent,
        },
        "attention": {
            "state": section_state(count=len(attention), has_attention=bool(attention)),
            "items": attention,
        },
        "signals": {
            "state": section_state(count=len(signals), has_attention=bool(signals)),
            "items": signals,
        },
        "next_action": {
            "state": "empty" if next_action is None else "complete",
            "item": next_action,
        },
    }
