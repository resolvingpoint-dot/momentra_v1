"""Team Ops analytics projector — deterministic writes to SQL projection tables."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import (
    BusinessActivityEvents,
    BusinessAttentionItems,
    BusinessDriverFormulaRegistry,
    BusinessHealthDriverScores,
    BusinessMomentMetrics,
    BusinessProgressSnapshots,
    BusinessRecommendedActions,
    BusinessSignalInsights,
    TeamActivities,
    TeamApprovalRequests,
    TeamEscalations,
    TeamIssueRisks,
)
from app.domains.business.templates.team_operations.context import TeamOpsContext

_DRIVER_DEFAULTS: dict[str, tuple[str, Decimal]] = {
    "participation": ("Participation", Decimal("25")),
    "approval_efficiency": ("Approval Efficiency", Decimal("25")),
    "issue_resolution": ("Issue Resolution", Decimal("25")),
    "execution_discipline": ("Execution Discipline", Decimal("25")),
}

_PROGRESS_METRICS: tuple[tuple[str, str, str], ...] = (
    ("participation", "Participation", "participation"),
    ("approval_progress", "Approval Progress", "approval_efficiency"),
    ("escalation_closure", "Escalation Closure", "issue_resolution"),
    ("workload_balance", "Workload Balance", "execution_discipline"),
)


def _pct(numerator: int, denominator: int) -> Decimal:
    if denominator <= 0:
        return Decimal("0")
    return Decimal(str(min(100, round((numerator / denominator) * 100, 2))))


def _driver_status(score: Decimal) -> str:
    value = float(score)
    if value >= 85:
        return "excellent"
    if value >= 70:
        return "good"
    if value >= 50:
        return "moderate"
    return "low"


def _trend(delta: float) -> str:
    if delta > 2:
        return "up"
    if delta < -2:
        return "down"
    return "stable"


def _health_label_band(score: Decimal, ctx: TeamOpsContext) -> tuple[str, str]:
    value = float(score)
    if ctx.member_count <= 0 and ctx.open_issues == 0 and ctx.pending_approvals == 0:
        return "Not started", "empty"
    if ctx.escalation_count > 0 or ctx.open_issues >= 5 or value < 50:
        return "At risk", "at_risk"
    if ctx.open_issues > 0 or ctx.pending_approvals > 3 or value < 70:
        return "Needs attention", "needs_attention"
    if value >= 85:
        return "On track", "healthy"
    return "On track", "healthy"


@dataclass
class TeamOpsProjectionBundle:
    health_score: Decimal
    health_label: str
    health_band: str
    health_drivers: list[dict]
    attention_items: list[dict]
    signal_items: list[dict]
    recommended_action: dict | None
    progress_snapshots: list[dict]
    highlights: list[dict]


class TeamOpsProjector:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def refresh(
        self, ctx: TeamOpsContext, *, persist: bool = False
    ) -> TeamOpsProjectionBundle:
        """Compute in-memory projection bundle.

        ``persist=False`` (default) keeps HTTP/Celery Redis paths fast — Redis is SoT.
        SQL table writes are optional and only when explicitly requested.
        """
        moment_id = ctx.moment_id
        # Brand-new / empty moments: skip extra driver/signal SQL (Personal-like cold paint).
        if self._is_sparse_ctx(ctx):
            bundle = self._sparse_bundle(ctx)
            if persist:
                await self._persist(
                    moment_id,
                    ctx,
                    bundle.health_score,
                    bundle.health_drivers,
                    bundle.attention_items,
                    bundle.signal_items,
                    bundle.recommended_action,
                    bundle.progress_snapshots,
                )
            return bundle

        weights = await self._load_weights()
        driver_scores = await self._compute_drivers(ctx, weights)
        health_score = self._weighted_health(driver_scores, weights)
        health_label, health_band = _health_label_band(health_score, ctx)
        attention = self._build_attention(ctx)
        signals = await self._build_signals(ctx)
        recommended = self._build_recommended_action(ctx)
        progress = self._build_progress(driver_scores)
        highlights = self._build_highlights(ctx)

        if persist:
            await self._persist(
                moment_id,
                ctx,
                health_score,
                driver_scores,
                attention,
                signals,
                recommended,
                progress,
            )

        return TeamOpsProjectionBundle(
            health_score=health_score,
            health_label=health_label,
            health_band=health_band,
            health_drivers=driver_scores,
            attention_items=attention,
            signal_items=signals,
            recommended_action=recommended,
            progress_snapshots=progress,
            highlights=highlights,
        )

    @staticmethod
    def _is_sparse_ctx(ctx: TeamOpsContext) -> bool:
        return (
            int(ctx.activity_count or 0) == 0
            and int(ctx.open_issues or 0) == 0
            and int(ctx.pending_approvals or 0) == 0
            and int(ctx.escalation_count or 0) == 0
            and int(ctx.recognition_count or 0) == 0
            and int(ctx.meeting_count or 0) == 0
            and int(ctx.participation_count or 0) == 0
            and not (ctx.activities or [])
        )

    def _sparse_bundle(self, ctx: TeamOpsContext) -> TeamOpsProjectionBundle:
        health_score = Decimal("0")
        health_label, health_band = _health_label_band(health_score, ctx)
        driver_scores = [
            {
                "driver_code": code,
                "driver_name": name,
                "score": float(Decimal("0")),
                "weight": float(weight),
                "status": _driver_status(Decimal("0")),
                "trend": "stable",
                "delta": 0.0,
            }
            for code, (name, weight) in _DRIVER_DEFAULTS.items()
        ]
        return TeamOpsProjectionBundle(
            health_score=health_score,
            health_label=health_label,
            health_band=health_band,
            health_drivers=driver_scores,
            attention_items=[],
            signal_items=[],
            recommended_action=self._build_recommended_action(ctx),
            progress_snapshots=self._build_progress(driver_scores),
            highlights=[],
        )

    async def _load_weights(self) -> dict[str, Decimal]:
        result = await self.session.execute(
            select(BusinessDriverFormulaRegistry).where(
                BusinessDriverFormulaRegistry.moment_type == "team_operations",
                BusinessDriverFormulaRegistry.active_flag.is_(True),
            )
        )
        rows = list(result.scalars().all())
        weights: dict[str, Decimal] = {}
        for row in rows:
            weights[row.driver_code] = row.driver_weight
        for code, (_, default_weight) in _DRIVER_DEFAULTS.items():
            weights.setdefault(code, default_weight)
        return weights

    async def _compute_drivers(
        self, ctx: TeamOpsContext, weights: dict[str, Decimal]
    ) -> list[dict]:
        moment_id = ctx.moment_id

        participation_total = await self._scalar_count(
            select(func.count()).select_from(TeamActivities).where(
                TeamActivities.moment_id == moment_id,
                TeamActivities.is_voided.is_(False),
                TeamActivities.archived_at.is_(None),
            )
        )
        participation_done = await self._scalar_count(
            select(func.count()).select_from(TeamActivities).where(
                TeamActivities.moment_id == moment_id,
                TeamActivities.is_voided.is_(False),
                TeamActivities.archived_at.is_(None),
                TeamActivities.activity_status.in_(("completed", "in_progress")),
            )
        )
        if participation_total == 0 and ctx.participation_count > 0:
            participation_score = _pct(
                ctx.participation_count, max(ctx.member_count, 1)
            )
        else:
            participation_score = _pct(participation_done, max(participation_total, 1))

        approval_total = await self._scalar_count(
            select(func.count()).select_from(TeamApprovalRequests).where(
                TeamApprovalRequests.moment_id == moment_id,
                TeamApprovalRequests.is_voided.is_(False),
            )
        )
        approval_done = await self._scalar_count(
            select(func.count()).select_from(TeamApprovalRequests).where(
                TeamApprovalRequests.moment_id == moment_id,
                TeamApprovalRequests.is_voided.is_(False),
                TeamApprovalRequests.approval_status.in_(("approved", "rejected")),
            )
        )
        approval_score = (
            _pct(approval_done, approval_total) if approval_total > 0 else Decimal("100")
        )

        issue_total = await self._scalar_count(
            select(func.count()).select_from(TeamIssueRisks).where(
                TeamIssueRisks.moment_id == moment_id,
                TeamIssueRisks.is_voided.is_(False),
            )
        )
        issue_resolved = await self._scalar_count(
            select(func.count()).select_from(TeamIssueRisks).where(
                TeamIssueRisks.moment_id == moment_id,
                TeamIssueRisks.is_voided.is_(False),
                TeamIssueRisks.resolution_status == "resolved",
            )
        )
        issue_score = (
            _pct(issue_resolved, issue_total) if issue_total > 0 else Decimal("100")
        )

        execution_score = participation_score

        raw: dict[str, Decimal] = {
            "participation": participation_score,
            "approval_efficiency": approval_score,
            "issue_resolution": issue_score,
            "execution_discipline": execution_score,
        }

        drivers: list[dict] = []
        for code, (name, _) in _DRIVER_DEFAULTS.items():
            score = raw[code]
            prev = await self._driver_delta(moment_id, code, float(score))
            drivers.append(
                {
                    "driver_code": code,
                    "driver_name": name,
                    "score": float(score),
                    "status": _driver_status(score),
                    "delta": prev,
                    "trend": _trend(prev),
                    "weight": float(weights.get(code, Decimal("25"))),
                }
            )
        return drivers

    async def _driver_delta(self, moment_id: UUID, driver_code: str, current: float) -> float:
        result = await self.session.execute(
            select(BusinessHealthDriverScores.driver_score)
            .where(
                BusinessHealthDriverScores.moment_id == moment_id,
                BusinessHealthDriverScores.driver_code == driver_code,
            )
            .order_by(BusinessHealthDriverScores.calculated_at.desc())
            .limit(1)
        )
        prior = result.scalar_one_or_none()
        if prior is None:
            return 0.0
        return round(current - float(prior), 2)

    def _weighted_health(
        self, drivers: list[dict], weights: dict[str, Decimal]
    ) -> Decimal:
        total_weight = Decimal("0")
        weighted = Decimal("0")
        for driver in drivers:
            code = driver["driver_code"]
            weight = weights.get(code, Decimal("25"))
            total_weight += weight
            weighted += Decimal(str(driver["score"])) * weight
        if total_weight <= 0:
            return Decimal("0")
        return Decimal(str(min(100, round(float(weighted / total_weight), 2))))

    def _build_attention(self, ctx: TeamOpsContext) -> list[dict]:
        items: list[dict] = []
        if ctx.pending_approvals > 0:
            items.append(
                {
                    "attention_type": "pending_approvals",
                    "severity": "high" if ctx.pending_approvals >= 3 else "medium",
                    "title": f"{ctx.pending_approvals} pending approval"
                    f"{'s' if ctx.pending_approvals != 1 else ''}",
                    "description": "Approvals waiting for review",
                    "kind": "pending_approvals",
                    "count": ctx.pending_approvals,
                }
            )
        if ctx.open_issues > 0:
            items.append(
                {
                    "attention_type": "open_issues",
                    "severity": "high" if ctx.open_issues >= 3 else "medium",
                    "title": f"{ctx.open_issues} open issue"
                    f"{'s' if ctx.open_issues != 1 else ''}",
                    "description": "Issues need triage",
                    "kind": "open_issues",
                    "count": ctx.open_issues,
                }
            )
        if ctx.escalation_count > 0:
            items.append(
                {
                    "attention_type": "escalations",
                    "severity": "high",
                    "title": f"{ctx.escalation_count} escalation"
                    f"{'s' if ctx.escalation_count != 1 else ''}",
                    "description": "Escalations require leadership review",
                    "kind": "escalations",
                    "count": ctx.escalation_count,
                }
            )
        return items

    async def _build_signals(self, ctx: TeamOpsContext) -> list[dict]:
        moment_id = ctx.moment_id
        now = datetime.now(timezone.utc)
        current_start = now - timedelta(days=7)
        prior_start = now - timedelta(days=14)

        signals: list[dict] = []
        for action_type, label, impact in (
            ("APPROVAL_REQUEST", "Approval requests", "medium"),
            ("PARTICIPATION", "Team participation", "low"),
            ("ESCALATION", "Escalations", "high"),
        ):
            current = await self._event_window_count(
                moment_id, action_type, current_start, now
            )
            prior = await self._event_window_count(
                moment_id, action_type, prior_start, current_start
            )
            if current == 0 and prior == 0:
                continue
            change = self._change_percent(current, prior)
            direction = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
            signals.append(
                {
                    "signal_type": action_type.lower(),
                    "title": f"{label} {direction}",
                    "summary": f"{current} in last 7 days vs {prior} prior week",
                    "change_percent": change,
                    "impact_level": impact,
                }
            )
        return signals[:3]

    async def _event_window_count(
        self,
        moment_id: UUID,
        action_type: str,
        start: datetime,
        end: datetime,
    ) -> int:
        return await self._scalar_count(
            select(func.count()).select_from(BusinessActivityEvents).where(
                BusinessActivityEvents.business_moment_id == moment_id,
                BusinessActivityEvents.is_voided.is_(False),
                BusinessActivityEvents.action_type == action_type,
                BusinessActivityEvents.occurred_at >= start,
                BusinessActivityEvents.occurred_at < end,
            )
        )

    def _change_percent(self, current: int, prior: int) -> float:
        if prior <= 0:
            return float(current * 100) if current > 0 else 0.0
        return round(((current - prior) / prior) * 100, 2)

    def _build_recommended_action(self, ctx: TeamOpsContext) -> dict | None:
        if ctx.pending_approvals > 0:
            return {
                "action_id": "approval",
                "label": f"Review {ctx.pending_approvals} pending approval"
                f"{'s' if ctx.pending_approvals != 1 else ''}",
                "reason": "pending_approvals",
                "cta_label": "Take Action",
                "target_screen": "action_center",
                "priority": "high",
            }
        if ctx.open_issues > 0:
            return {
                "action_id": "issue",
                "label": "Triage open issues",
                "reason": "open_issues",
                "cta_label": "Take Action",
                "target_screen": "action_center",
                "priority": "high",
            }
        if ctx.member_count > 0:
            return {
                "action_id": "team_update",
                "label": "Post a team update",
                "reason": "keep_rhythm",
                "cta_label": "Take Action",
                "target_screen": "action_center",
                "priority": "medium",
            }
        return None

    def _build_progress(self, drivers: list[dict]) -> list[dict]:
        by_code = {d["driver_code"]: d for d in drivers}
        items: list[dict] = []
        for metric_code, metric_name, driver_code in _PROGRESS_METRICS:
            driver = by_code.get(driver_code, {})
            items.append(
                {
                    "metric_code": metric_code,
                    "metric_name": metric_name,
                    "score": driver.get("score", 0),
                    "delta": driver.get("delta", 0),
                    "status": driver.get("status", "stable"),
                    "trend": driver.get("trend", "stable"),
                }
            )
        return items

    def _build_highlights(self, ctx: TeamOpsContext) -> list[dict]:
        wins = [
            a
            for a in ctx.activities
            if (a.get("action_type") or "").upper()
            in ("RECOGNITION", "APPROVAL_REQUEST", "MEETING", "PARTICIPATION", "TEAM_UPDATE")
        ]
        items: list[dict] = []
        for activity in wins[:4]:
            items.append(
                {
                    "event_id": activity.get("event_id", ""),
                    "action_type": activity.get("action_type", ""),
                    "title": activity.get("title", ""),
                    "subtitle": activity.get("subtitle"),
                    "occurred_at": activity.get("occurred_at"),
                }
            )
        return items

    async def _persist(
        self,
        moment_id: UUID,
        ctx: TeamOpsContext,
        health_score: Decimal,
        drivers: list[dict],
        attention: list[dict],
        signals: list[dict],
        recommended: dict | None,
        progress: list[dict],
    ) -> None:
        await self.session.execute(
            delete(BusinessHealthDriverScores).where(
                BusinessHealthDriverScores.moment_id == moment_id
            )
        )
        for driver in drivers:
            self.session.add(
                BusinessHealthDriverScores(
                    moment_id=moment_id,
                    driver_code=driver["driver_code"],
                    driver_name=driver["driver_name"],
                    driver_score=Decimal(str(driver["score"])),
                    driver_status=driver["status"],
                    score_delta=Decimal(str(driver["delta"])),
                    trend_direction=driver["trend"],
                    source_table="team_operations_projector",
                )
            )

        await self.session.execute(
            delete(BusinessAttentionItems).where(
                BusinessAttentionItems.moment_id == moment_id,
                BusinessAttentionItems.generated_by == "system",
            )
        )
        for item in attention:
            self.session.add(
                BusinessAttentionItems(
                    moment_id=moment_id,
                    attention_type=item["attention_type"],
                    severity=item["severity"],
                    title=item["title"],
                    description=item.get("description"),
                    status="open",
                    generated_by="system",
                )
            )

        await self.session.execute(
            delete(BusinessSignalInsights).where(
                BusinessSignalInsights.moment_id == moment_id
            )
        )
        for signal in signals:
            self.session.add(
                BusinessSignalInsights(
                    moment_id=moment_id,
                    signal_type=signal["signal_type"],
                    signal_title=signal["title"],
                    signal_summary=signal["summary"],
                    impact_level=signal["impact_level"],
                    change_percent=Decimal(str(signal["change_percent"])),
                    lookback_days=7,
                    signal_status="active",
                )
            )

        await self.session.execute(
            delete(BusinessRecommendedActions).where(
                BusinessRecommendedActions.moment_id == moment_id,
                BusinessRecommendedActions.source_rule == "team_ops_projector",
            )
        )
        if recommended:
            self.session.add(
                BusinessRecommendedActions(
                    moment_id=moment_id,
                    action_title=recommended["label"],
                    action_reason=recommended["reason"],
                    priority=recommended["priority"],
                    cta_label=recommended["cta_label"],
                    target_screen=recommended.get("target_screen"),
                    source_rule="team_ops_projector",
                    status="active",
                )
            )

        today = date.today()
        await self.session.execute(
            delete(BusinessProgressSnapshots).where(
                BusinessProgressSnapshots.moment_id == moment_id,
                BusinessProgressSnapshots.snapshot_date == today,
            )
        )
        for snap in progress:
            self.session.add(
                BusinessProgressSnapshots(
                    moment_id=moment_id,
                    metric_code=snap["metric_code"],
                    metric_name=snap["metric_name"],
                    metric_score=Decimal(str(snap["score"])),
                    metric_delta=Decimal(str(snap["delta"])),
                    metric_status=snap.get("status"),
                    snapshot_date=today,
                )
            )

        metrics = await self.session.execute(
            select(BusinessMomentMetrics).where(
                BusinessMomentMetrics.moment_id == moment_id
            )
        )
        row = metrics.scalar_one_or_none()
        if row is None:
            self.session.add(
                BusinessMomentMetrics(
                    moment_id=moment_id,
                    members_count=ctx.member_count,
                    activities_count=ctx.activity_count,
                    pending_approvals=ctx.pending_approvals,
                    open_risks=ctx.open_issues,
                    progress_score=health_score,
                    progress_status=_driver_status(health_score),
                    continue_cta_label=recommended["cta_label"] if recommended else None,
                )
            )
        else:
            row.members_count = ctx.member_count
            row.activities_count = ctx.activity_count
            row.pending_approvals = ctx.pending_approvals
            row.open_risks = ctx.open_issues
            row.progress_score = health_score
            row.progress_status = _driver_status(health_score)
            row.continue_cta_label = recommended["cta_label"] if recommended else None
            row.last_updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    async def _scalar_count(self, stmt) -> int:
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)


async def refresh_team_ops_projections(
    session: AsyncSession,
    ctx: TeamOpsContext,
    *,
    persist: bool = False,
) -> TeamOpsProjectionBundle:
    return await TeamOpsProjector(session).refresh(ctx, persist=persist)
