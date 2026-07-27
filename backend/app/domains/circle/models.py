"""Circle domain SQLAlchemy models (circle_* tables).

Auto-generated from the Alembic migrations via reflection.
"""
from __future__ import annotations

from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import Boolean, Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.users.models import Base


class CircleParticipantSources(Base):
    __tablename__ = 'circle_participant_sources'
    __table_args__ = (
        ForeignKeyConstraint(['circle_participant_id'], ['circle_participants.circle_participant_id'], ondelete='CASCADE', name='circle_participant_sources_circle_participant_id_fkey'),
        PrimaryKeyConstraint('source_id', name='circle_participant_sources_pkey'),
        UniqueConstraint('circle_participant_id', 'source_type', 'source_moment_id', name='uq_circle_source')
    )

    source_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    circle_participant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_moment_name: Mapped[Optional[str]] = mapped_column(String(250))
    source_moment_type: Mapped[Optional[str]] = mapped_column(String(100))
    participation_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    is_active_source: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    circle_participant: Mapped['CircleParticipants'] = relationship('CircleParticipants', back_populates='circle_participant_sources')


class CircleParticipantStats(Base):
    __tablename__ = 'circle_participant_stats'
    __table_args__ = (
        ForeignKeyConstraint(['circle_participant_id'], ['circle_participants.circle_participant_id'], ondelete='CASCADE', name='circle_participant_stats_circle_participant_id_fkey'),
        PrimaryKeyConstraint('stats_id', name='circle_participant_stats_pkey'),
        UniqueConstraint('circle_participant_id', name='uq_circle_stats')
    )

    stats_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    circle_participant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    shared_moment_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    active_moment_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    recent_activity_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    participation_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2), server_default=text('0'))
    rank_order: Mapped[Optional[int]] = mapped_column(Integer)
    last_activity_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    circle_participant: Mapped['CircleParticipants'] = relationship('CircleParticipants', back_populates='circle_participant_stats')


class CircleParticipants(Base):
    __tablename__ = 'circle_participants'
    __table_args__ = (
        PrimaryKeyConstraint('circle_participant_id', name='circle_participants_pkey'),
        Index('uq_circle_participant', 'user_id', 'participant_name', unique=True)
    )

    circle_participant_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    participant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    participant_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    participant_phone: Mapped[Optional[str]] = mapped_column(String(30))
    participant_email: Mapped[Optional[str]] = mapped_column(String(200))
    first_seen_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    last_seen_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    circle_participant_sources: Mapped[list['CircleParticipantSources']] = relationship('CircleParticipantSources', back_populates='circle_participant')
    circle_participant_stats: Mapped['CircleParticipantStats'] = relationship('CircleParticipantStats', uselist=False, back_populates='circle_participant')


class CircleSuggestions(Base):
    __tablename__ = 'circle_suggestions'
    __table_args__ = (
        PrimaryKeyConstraint('suggestion_id', name='circle_suggestions_pkey'),
    )

    suggestion_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    suggestion_type: Mapped[str] = mapped_column(String(50), nullable=False)
    participant_ids_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    suggestion_title: Mapped[str] = mapped_column(String(300), nullable=False)
    suggestion_description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2), server_default=text('0'))
    cta_label: Mapped[Optional[str]] = mapped_column(String(100))
    target_create_flow: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
