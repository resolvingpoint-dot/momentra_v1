"""Sparse signals for Business Runway template."""
from __future__ import annotations

from app.domains.business.templates.business_runway.context import RunwayContext


def derive_signals(ctx: RunwayContext) -> list[dict]:
    signals: list[dict] = []
    threshold = float(ctx.alert_threshold_months or 6)
    if ctx.runway_months is not None and ctx.runway_months < threshold:
        signals.append({
            "signal_type": "low_runway",
            "label": f"{ctx.runway_months:.1f} months runway remaining",
            "title": f"{ctx.runway_months:.1f} months runway remaining",
            "severity": "critical" if ctx.runway_months < 1 else "high",
        })
    if ctx.risk_count > 0:
        signals.append({
            "signal_type": "runway_risks",
            "label": f"{ctx.risk_count} open risk{'s' if ctx.risk_count != 1 else ''}",
            "title": f"{ctx.risk_count} open risk{'s' if ctx.risk_count != 1 else ''}",
            "severity": "medium",
        })
    if ctx.collection_rate_percent is not None and ctx.collection_rate_percent < 70:
        signals.append({
            "signal_type": "collection_rate",
            "label": f"Collection rate {ctx.collection_rate_percent}%",
            "title": f"Collection rate {ctx.collection_rate_percent}%",
            "severity": "medium",
        })
    return signals
