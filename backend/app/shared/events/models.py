"""ORM models for domain event persistence."""
from __future__ import annotations

import datetime
import uuid
from typing import Any, Optional

from sqlalchemy import DateTime, Index, String, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.users.models import Base


class DomainEventLog(Base):
    __tablename__ = "domain_event_log"
    __table_args__ = (
        Index("idx_domain_event_log_moment", "moment_id"),
        Index("idx_domain_event_log_user", "user_id"),
        Index("idx_domain_event_log_name", "name"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    context: Mapped[str] = mapped_column(String(50), nullable=False)
    moment_type: Mapped[Optional[str]] = mapped_column(String(50))
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
