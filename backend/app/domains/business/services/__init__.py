"""Modular Business services.

Each feature area (moments, workspace, members, approvals, risks, transactions,
quick-add, notifications, activity feed, pulse, analytics, memory, state engine)
lives in its own module and subclasses :class:`BusinessModuleService`, which
provides membership-based authorization and shared serialization helpers on top
of the generated repositories/schemas. Services return Pydantic schemas only and
contain no HTTP concerns.
"""
from __future__ import annotations

from app.domains.business.services.activity import BusinessActivityFeedModule
from app.domains.business.services.analytics import BusinessAnalyticsModule
from app.domains.business.services.approvals import BusinessApprovalsModule
from app.domains.business.services.departments import BusinessDepartmentsModule
from app.domains.business.services.members import BusinessMembersModule
from app.domains.business.services.memory import BusinessMemoryModule
from app.domains.business.services.moments import BusinessMomentsModule
from app.domains.business.services.notifications import BusinessNotificationsModule
from app.domains.business.services.projects import BusinessProjectsModule
from app.domains.business.services.pulse import BusinessPulseModule
from app.domains.business.services.quick_add import BusinessQuickAddModule
from app.domains.business.services.risks import BusinessRisksModule
from app.domains.business.services.state_engine import BusinessStateEngineModule
from app.domains.business.services.transactions import BusinessTransactionsModule
from app.domains.business.services.workspace import BusinessWorkspaceModule

__all__ = [
    "BusinessActivityFeedModule",
    "BusinessAnalyticsModule",
    "BusinessApprovalsModule",
    "BusinessDepartmentsModule",
    "BusinessMembersModule",
    "BusinessMemoryModule",
    "BusinessMomentsModule",
    "BusinessNotificationsModule",
    "BusinessProjectsModule",
    "BusinessPulseModule",
    "BusinessQuickAddModule",
    "BusinessRisksModule",
    "BusinessStateEngineModule",
    "BusinessTransactionsModule",
    "BusinessWorkspaceModule",
]
