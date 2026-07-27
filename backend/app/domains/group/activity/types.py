"""Group activity types — canonical write path for group template actions."""
from __future__ import annotations

from enum import Enum


class ActivityType(str, Enum):
    EXPENSE = "EXPENSE"
    BOOKING = "BOOKING"
    PARTICIPANT = "PARTICIPANT"
    CONTRIBUTION = "CONTRIBUTION"
    POLL = "POLL"
    TASK = "TASK"
    MEMORY = "MEMORY"
    VENDOR = "VENDOR"
    ATTENDANCE = "ATTENDANCE"
    UPDATE = "UPDATE"
    PLANNING_ITEM = "PLANNING_ITEM"
    PAYMENT = "PAYMENT"
    INSTALLMENT = "INSTALLMENT"
    OWNERSHIP_UPDATE = "OWNERSHIP_UPDATE"
    DECISION = "DECISION"
    MILESTONE = "MILESTONE"
    NOTE = "NOTE"
    DOCUMENT_PLACEHOLDER = "DOCUMENT_PLACEHOLDER"
    RENT = "RENT"
    UTILITY = "UTILITY"
    GROCERY = "GROCERY"
    HOUSEHOLD_EXPENSE = "HOUSEHOLD_EXPENSE"
    CHORE = "CHORE"
    HOUSEHOLD_PURCHASE = "HOUSEHOLD_PURCHASE"
    MAINTENANCE = "MAINTENANCE"
    SETTLEMENT_NOTE = "SETTLEMENT_NOTE"
    MEMBER_UPDATE = "MEMBER_UPDATE"
    HOME_MEMORY = "HOME_MEMORY"


_COLLECTION_MAP: dict[ActivityType, str] = {
    ActivityType.EXPENSE: "expenses",
    ActivityType.BOOKING: "bookings",
    ActivityType.PARTICIPANT: "guests",
    ActivityType.CONTRIBUTION: "contributions",
    ActivityType.POLL: "polls",
    ActivityType.TASK: "tasks",
    ActivityType.MEMORY: "memories",
    ActivityType.VENDOR: "vendors",
    ActivityType.ATTENDANCE: "attendances",
    ActivityType.UPDATE: "updates",
    ActivityType.PLANNING_ITEM: "plans",
    ActivityType.PAYMENT: "payments",
    ActivityType.INSTALLMENT: "installments",
    ActivityType.OWNERSHIP_UPDATE: "ownership_shares",
    ActivityType.DECISION: "decisions",
    ActivityType.MILESTONE: "milestones",
    ActivityType.NOTE: "notes",
    ActivityType.DOCUMENT_PLACEHOLDER: "documents",
    ActivityType.RENT: "rent",
    ActivityType.UTILITY: "utilities",
    ActivityType.GROCERY: "groceries",
    ActivityType.HOUSEHOLD_EXPENSE: "expenses",
    ActivityType.CHORE: "chores",
    ActivityType.HOUSEHOLD_PURCHASE: "household_purchases",
    ActivityType.MAINTENANCE: "maintenance",
    ActivityType.SETTLEMENT_NOTE: "notes",
    ActivityType.MEMBER_UPDATE: "guests",
    ActivityType.HOME_MEMORY: "memories",
}


def collection_for(activity_type: ActivityType) -> str:
    return _COLLECTION_MAP[activity_type]
