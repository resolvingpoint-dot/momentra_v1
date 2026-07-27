"""SQLAlchemy model for personal_master_expenses."""
from __future__ import annotations

import datetime
import uuid
from typing import Any, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.users.models import Base


class PersonalMasterExpenses(Base):
    __tablename__ = "personal_master_expenses"
    __table_args__ = (
        Index("idx_personal_master_expenses_user", "user_id", "occurred_at"),
    )

    master_expense_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personal_accounts.account_id"), nullable=False
    )
    category_code: Mapped[str] = mapped_column(String(80), nullable=False)
    subcategory_code: Mapped[Optional[str]] = mapped_column(String(80))
    occurred_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    feeling: Mapped[Optional[str]] = mapped_column(String(40))
    meaningfulness: Mapped[Optional[str]] = mapped_column(String(20))
    memorability: Mapped[Optional[str]] = mapped_column(String(20))
    is_shared: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    shared_with: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    relationship_impact: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    context_reason: Mapped[Optional[str]] = mapped_column(String(80))
    notes: Mapped[Optional[str]] = mapped_column(String(200))
    client_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    life_operations_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personal_quick_add_events.quick_add_event_id")
    )
    lifestyle_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personal_quick_add_events.quick_add_event_id")
    )
    relationships_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personal_quick_add_events.quick_add_event_id")
    )
    is_voided: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
