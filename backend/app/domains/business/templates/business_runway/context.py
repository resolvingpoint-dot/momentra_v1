"""Business Runway projection context."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from app.domains.business.templates.base import BusinessProjectionContext

if TYPE_CHECKING:
    from app.domains.business.templates.business_runway.projector import RunwayProjectionBundle


@dataclass
class RunwayContext(BusinessProjectionContext):
    operating_currency: str = "INR"
    runway_name: str = ""
    total_inflow_minor: int = 0
    total_burn_minor: int = 0
    net_burn_minor: int = 0
    monthly_burn_setup_minor: int = 0
    monthly_revenue_minor: int = 0
    collection_rate_percent: int | None = None
    runway_goal_months: int | None = None
    alert_threshold_months: float | None = None
    revenue_status: str | None = None
    runway_months: float | None = None
    cash_available_minor: int = 0
    risk_count: int = 0
    decision_count: int = 0
    financial_update_count: int = 0
    projection: RunwayProjectionBundle | None = None
    typed_rows: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
