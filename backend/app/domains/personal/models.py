"""Personal domain SQLAlchemy models (personal_* tables, including personal life, lifestyle and memory sub-features).

Auto-generated from the Alembic migrations via reflection.
"""
from __future__ import annotations

from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, Time, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.users.models import Base


class PersonalAccounts(Base):
    __tablename__ = 'personal_accounts'
    __table_args__ = (
        CheckConstraint("account_type::text = ANY (ARRAY['SAVINGS'::character varying, 'CURRENT'::character varying, 'CREDIT_CARD'::character varying, 'INVESTMENT'::character varying, 'WALLET'::character varying, 'CASH'::character varying, 'CUSTOM'::character varying]::text[])", name='chk_personal_account_type'),
        CheckConstraint('opening_balance IS NULL OR opening_balance >= 0::numeric', name='chk_personal_account_opening_balance'),
        PrimaryKeyConstraint('account_id', name='personal_accounts_pkey'),
        Index('idx_personal_accounts_user', 'user_id'),
        Index('uq_personal_default_account', 'user_id', postgresql_where='(is_default = true)', unique=True)
    )

    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    account_name: Mapped[str] = mapped_column(String(120), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    current_balance: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    opening_balance: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2), server_default=text('0'))

    personal_user_preferences: Mapped[list['PersonalUserPreferences']] = relationship('PersonalUserPreferences', back_populates='default_account')
    personal_money_events: Mapped[list['PersonalMoneyEvents']] = relationship('PersonalMoneyEvents', back_populates='account')


class PersonalActivityTimeline(Base):
    __tablename__ = 'personal_activity_timeline'
    __table_args__ = (
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_activity_timeline_moment_type_code_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_activity_timeline_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_activity_timeline_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('timeline_id', name='personal_activity_timeline_pkey'),
        Index('idx_personal_timeline_event_type', 'moment_type_code', 'event_type'),
        Index('idx_personal_timeline_moment_date', 'moment_id', 'event_occurred_at'),
        Index('idx_personal_timeline_user', 'user_id')
    )

    timeline_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    display_title: Mapped[str] = mapped_column(String(150), nullable=False)
    event_occurred_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    is_editable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    display_subtitle: Mapped[Optional[str]] = mapped_column(String(250))
    display_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))
    impact_labels_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_activity_timeline')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_activity_timeline')


class PersonalAiInterpretationRuns(Base):
    __tablename__ = 'personal_ai_interpretation_runs'
    __table_args__ = (
        CheckConstraint("moment_type_code IS NULL OR (moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[]))", name='personal_ai_interpretation_runs_moment_type_code_check'),
        CheckConstraint("run_type::text = ANY (ARRAY['SIGNAL_REFRESH'::character varying, 'RECOMMENDATION_REFRESH'::character varying, 'MEMORY_REFRESH'::character varying, 'FULL_REFRESH'::character varying]::text[])", name='personal_ai_interpretation_runs_run_type_check'),
        CheckConstraint("status::text = ANY (ARRAY['QUEUED'::character varying, 'RUNNING'::character varying, 'COMPLETED'::character varying, 'FAILED'::character varying, 'SKIPPED'::character varying]::text[])", name='personal_ai_interpretation_runs_status_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_ai_interpretation_runs_moment_id_fkey'),
        PrimaryKeyConstraint('run_id', name='personal_ai_interpretation_runs_pkey'),
        Index('idx_personal_ai_runs_moment', 'moment_id'),
        Index('idx_personal_ai_runs_status', 'status'),
        Index('idx_personal_ai_runs_type', 'run_type'),
        Index('idx_personal_ai_runs_user', 'user_id')
    )

    run_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    run_type: Mapped[str] = mapped_column(String(80), nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'QUEUED'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    moment_type_code: Mapped[Optional[str]] = mapped_column(String(50))
    output_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    records_created_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped[Optional['PersonalMoments']] = relationship('PersonalMoments', back_populates='personal_ai_interpretation_runs')


class PersonalCategories(Base):
    __tablename__ = 'personal_categories'
    __table_args__ = (
        CheckConstraint("moment_type_code::text = ANY (ARRAY['ALL'::character varying, 'LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='chk_personal_category_moment_type'),
        PrimaryKeyConstraint('category_id', name='personal_categories_pkey'),
        Index('idx_personal_categories_scope', 'moment_type_code', 'category_group'),
        Index('uq_personal_categories_code_scope', 'moment_type_code', 'category_group', 'category_code', unique=True)
    )

    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    category_group: Mapped[str] = mapped_column(String(80), nullable=False)
    category_code: Mapped[str] = mapped_column(String(80), nullable=False)
    category_name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_money_category: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    display_order: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))


class PersonalEventEdits(Base):
    __tablename__ = 'personal_event_edits'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_event_edits_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_event_edits_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('edit_id', name='personal_event_edits_pkey'),
        Index('idx_personal_event_edits_event', 'quick_add_event_id'),
        Index('idx_personal_event_edits_moment', 'moment_id')
    )

    edit_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    edited_table_name: Mapped[str] = mapped_column(String(120), nullable=False)
    edited_record_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    before_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    after_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    requires_recalculation: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    changed_fields: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))
    edit_reason: Mapped[Optional[str]] = mapped_column(String(250))
    recalculated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_event_edits')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_event_edits')


class PersonalEventVoids(Base):
    __tablename__ = 'personal_event_voids'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_event_voids_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_event_voids_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('void_id', name='personal_event_voids_pkey'),
        Index('idx_personal_event_voids_event', 'quick_add_event_id'),
        Index('idx_personal_event_voids_moment', 'moment_id')
    )

    void_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    voided_table_name: Mapped[str] = mapped_column(String(120), nullable=False)
    voided_record_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    void_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reversal_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    requires_recalculation: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    void_reason: Mapped[Optional[str]] = mapped_column(String(250))
    undo_expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    restored_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    recalculated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_event_voids')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_event_voids')


class PersonalFutureBuildingProfile(Base):
    __tablename__ = 'personal_future_building_profile'
    __table_args__ = (
        CheckConstraint('array_length(friction_sources, 1) >= 1', name='chk_future_friction_sources_not_empty'),
        CheckConstraint('array_length(future_values, 1) >= 1', name='chk_future_values_not_empty'),
        CheckConstraint('array_length(momentum_drivers, 1) >= 1', name='chk_future_momentum_drivers_not_empty'),
        CheckConstraint("breakthrough_potential IS NULL OR (breakthrough_potential::text = ANY (ARRAY['LOW'::character varying, 'MODERATE'::character varying, 'HIGH'::character varying]::text[]))", name='chk_future_breakthrough_potential'),
        CheckConstraint("future_confidence::text = ANY (ARRAY['Exciting'::character varying, 'Hopeful'::character varying, 'Confident'::character varying, 'Unclear'::character varying, 'Stuck'::character varying, 'Overwhelming'::character varying]::text[])", name='chk_future_confidence'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_future_building_profile_moment_id_fkey'),
        PrimaryKeyConstraint('future_profile_id', name='personal_future_building_profile_pkey'),
        Index('idx_future_profile_moment', 'moment_id'),
        Index('idx_future_profile_user', 'user_id')
    )

    future_profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    future_theme: Mapped[str] = mapped_column(String(80), nullable=False)
    current_momentum_state: Mapped[str] = mapped_column(String(80), nullable=False)
    future_values: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    friction_sources: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    momentum_drivers: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    future_confidence: Mapped[str] = mapped_column(String(50), nullable=False)
    future_identity: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    largest_friction_label: Mapped[Optional[str]] = mapped_column(String(100))
    primary_opportunity_label: Mapped[Optional[str]] = mapped_column(String(150))
    breakthrough_potential: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_future_building_profile')


class PersonalFutureLearningEvents(Base):
    __tablename__ = 'personal_future_learning_events'
    __table_args__ = (
        CheckConstraint("application_status IS NULL OR (application_status::text = ANY (ARRAY['Will Use Soon'::character varying, 'Already Applying'::character varying, 'Future Use'::character varying]::text[]))", name='chk_future_learning_application'),
        CheckConstraint('capability_score_delta IS NULL OR capability_score_delta >= 0::numeric AND capability_score_delta <= 100::numeric', name='chk_future_learning_capability_score'),
        CheckConstraint('confidence_boost_score IS NULL OR confidence_boost_score >= 0::numeric AND confidence_boost_score <= 100::numeric', name='chk_future_learning_confidence_score'),
        CheckConstraint("learning_type::text = ANY (ARRAY['Skill'::character varying, 'Knowledge'::character varying, 'Insight'::character varying, 'Experience'::character varying, 'Mentorship'::character varying, 'Mistake'::character varying]::text[])", name='chk_future_learning_type'),
        CheckConstraint("relevance_level::text = ANY (ARRAY['Useful'::character varying, 'Important'::character varying, 'High Leverage'::character varying, 'Transformational'::character varying]::text[])", name='chk_future_learning_relevance'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_future_learning_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_future_learning_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('learning_event_id', name='personal_future_learning_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_future_learning_events_quick_add_event_id_key'),
        Index('idx_future_learning_date', 'event_date'),
        Index('idx_future_learning_moment', 'moment_id'),
        Index('idx_future_learning_user', 'user_id')
    )

    learning_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    learning_type: Mapped[str] = mapped_column(String(50), nullable=False)
    relevance_level: Mapped[str] = mapped_column(String(50), nullable=False)
    readiness_signal_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    application_status: Mapped[Optional[str]] = mapped_column(String(50))
    note: Mapped[Optional[str]] = mapped_column(Text)
    capability_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    confidence_boost_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_future_learning_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_future_learning_events')


class PersonalFutureMilestoneEvents(Base):
    __tablename__ = 'personal_future_milestone_events'
    __table_args__ = (
        CheckConstraint('achievement_score_delta IS NULL OR achievement_score_delta >= 0::numeric AND achievement_score_delta <= 100::numeric', name='chk_future_milestone_score'),
        CheckConstraint("celebration_level IS NULL OR (celebration_level::text = ANY (ARRAY['Personal Win'::character varying, 'Shared Win'::character varying, 'Life Moment'::character varying]::text[]))", name='chk_future_milestone_celebration'),
        CheckConstraint("impact_level::text = ANY (ARRAY['Minor'::character varying, 'Meaningful'::character varying, 'Major'::character varying, 'Transformational'::character varying]::text[])", name='chk_future_milestone_impact'),
        CheckConstraint("milestone_nature::text = ANY (ARRAY['Achievement'::character varying, 'Recognition'::character varying, 'Completion'::character varying, 'Launch'::character varying, 'Certification'::character varying, 'Promotion'::character varying, 'Revenue Event'::character varying, 'Breakthrough'::character varying]::text[])", name='chk_future_milestone_nature'),
        CheckConstraint("outcome_value IS NULL OR (outcome_value::text = ANY (ARRAY['Income Increase'::character varying, 'Savings Increase'::character varying, 'Revenue Increase'::character varying, 'Cost Reduction'::character varying, 'No Financial Impact'::character varying]::text[]))", name='chk_future_milestone_outcome'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_future_milestone_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_future_milestone_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('milestone_event_id', name='personal_future_milestone_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_future_milestone_events_quick_add_event_id_key'),
        Index('idx_future_milestone_date', 'event_date'),
        Index('idx_future_milestone_moment', 'moment_id'),
        Index('idx_future_milestone_user', 'user_id')
    )

    milestone_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    milestone_nature: Mapped[str] = mapped_column(String(80), nullable=False)
    impact_level: Mapped[str] = mapped_column(String(50), nullable=False)
    breakthrough_signal_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    outcome_value: Mapped[Optional[str]] = mapped_column(String(80))
    celebration_level: Mapped[Optional[str]] = mapped_column(String(50))
    note: Mapped[Optional[str]] = mapped_column(Text)
    achievement_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    future_return_signal: Mapped[Optional[str]] = mapped_column(String(80))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_future_milestone_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_future_milestone_events')


class PersonalFutureOpportunityEvents(Base):
    __tablename__ = 'personal_future_opportunity_events'
    __table_args__ = (
        CheckConstraint('opportunity_score_delta IS NULL OR opportunity_score_delta >= 0::numeric AND opportunity_score_delta <= 100::numeric', name='chk_future_opportunity_score'),
        CheckConstraint("opportunity_source::text = ANY (ARRAY['New Connection'::character varying, 'New Skill'::character varying, 'New Resource'::character varying, 'New Funding'::character varying, 'New Role'::character varying, 'New Client'::character varying, 'New Market'::character varying, 'New Idea'::character varying, 'New Partnership'::character varying, 'New Exposure'::character varying, 'Unexpected Event'::character varying, 'Other'::character varying]::text[])", name='chk_future_opportunity_source'),
        CheckConstraint("opportunity_status::text = ANY (ARRAY['Exploring'::character varying, 'Considering'::character varying, 'Acting'::character varying, 'Captured'::character varying]::text[])", name='chk_future_opportunity_status'),
        CheckConstraint("potential_level::text = ANY (ARRAY['Low'::character varying, 'Moderate'::character varying, 'High'::character varying, 'Game-Changing'::character varying]::text[])", name='chk_future_opportunity_potential'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_future_opportunity_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_future_opportunity_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('opportunity_event_id', name='personal_future_opportunity_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_future_opportunity_events_quick_add_event_id_key'),
        Index('idx_future_opportunity_date', 'event_date'),
        Index('idx_future_opportunity_moment', 'moment_id'),
        Index('idx_future_opportunity_user', 'user_id')
    )

    opportunity_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    opportunity_source: Mapped[str] = mapped_column(String(80), nullable=False)
    potential_level: Mapped[str] = mapped_column(String(50), nullable=False)
    opportunity_status: Mapped[str] = mapped_column(String(50), nullable=False)
    acceleration_signal_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    best_opportunity_candidate_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    note: Mapped[Optional[str]] = mapped_column(Text)
    opportunity_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_future_opportunity_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_future_opportunity_events')


class PersonalFuturePivotEvents(Base):
    __tablename__ = 'personal_future_pivot_events'
    __table_args__ = (
        CheckConstraint('adaptability_score_delta IS NULL OR adaptability_score_delta >= 0::numeric AND adaptability_score_delta <= 100::numeric', name='chk_future_pivot_adaptability_score'),
        CheckConstraint("adjustment_type::text = ANY (ARRAY['New Priority'::character varying, 'New Goal'::character varying, 'Reduce Scope'::character varying, 'Increase Focus'::character varying, 'Change Timeline'::character varying, 'Change Direction'::character varying]::text[])", name='chk_future_pivot_adjustment'),
        CheckConstraint("confidence_level::text = ANY (ARRAY['Low'::character varying, 'Medium'::character varying, 'High'::character varying]::text[])", name='chk_future_pivot_confidence'),
        CheckConstraint('direction_shift_score IS NULL OR direction_shift_score >= 0::numeric AND direction_shift_score <= 100::numeric', name='chk_future_pivot_direction_score'),
        CheckConstraint("pivot_reason::text = ANY (ARRAY['New Information'::character varying, 'Opportunity'::character varying, 'Constraint'::character varying, 'Personal Decision'::character varying, 'Market Change'::character varying]::text[])", name='chk_future_pivot_reason'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_future_pivot_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_future_pivot_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('pivot_event_id', name='personal_future_pivot_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_future_pivot_events_quick_add_event_id_key'),
        Index('idx_future_pivot_date', 'event_date'),
        Index('idx_future_pivot_moment', 'moment_id'),
        Index('idx_future_pivot_user', 'user_id')
    )

    pivot_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    adjustment_type: Mapped[str] = mapped_column(String(80), nullable=False)
    pivot_reason: Mapped[str] = mapped_column(String(80), nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(30), nullable=False)
    future_horizon_update_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    note: Mapped[Optional[str]] = mapped_column(Text)
    direction_shift_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    adaptability_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_future_pivot_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_future_pivot_events')


class PersonalFutureProgressEvents(Base):
    __tablename__ = 'personal_future_progress_events'
    __table_args__ = (
        CheckConstraint("effort_level IS NULL OR (effort_level::text = ANY (ARRAY['Low'::character varying, 'Medium'::character varying, 'High'::character varying, 'Exceptional'::character varying]::text[]))", name='chk_future_progress_effort'),
        CheckConstraint('momentum_score_delta IS NULL OR momentum_score_delta >= 0::numeric AND momentum_score_delta <= 100::numeric', name='chk_future_progress_momentum_score'),
        CheckConstraint('money_invested_amount IS NULL OR money_invested_amount >= 0::numeric', name='chk_future_progress_money'),
        CheckConstraint("progress_level::text = ANY (ARRAY['Small Step'::character varying, 'Moderate Progress'::character varying, 'Major Progress'::character varying, 'Breakthrough'::character varying]::text[])", name='chk_future_progress_level'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_future_progress_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_future_progress_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('progress_event_id', name='personal_future_progress_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_future_progress_events_quick_add_event_id_key'),
        Index('idx_future_progress_date', 'event_date'),
        Index('idx_future_progress_moment', 'moment_id'),
        Index('idx_future_progress_user', 'user_id')
    )

    progress_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    progress_type: Mapped[str] = mapped_column(String(80), nullable=False)
    progress_level: Mapped[str] = mapped_column(String(50), nullable=False)
    velocity_signal_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    money_invested_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))
    time_invested_bucket: Mapped[Optional[str]] = mapped_column(String(30))
    effort_level: Mapped[Optional[str]] = mapped_column(String(30))
    note: Mapped[Optional[str]] = mapped_column(Text)
    momentum_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    investment_weight_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_future_progress_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_future_progress_events')


class PersonalInsights(Base):
    __tablename__ = 'personal_insights'
    __table_args__ = (
        CheckConstraint("insight_scope::text = ANY (ARRAY['PULSE'::character varying, 'LIVE'::character varying, 'MEMORY'::character varying, 'DETAIL'::character varying, 'GLOBAL'::character varying]::text[])", name='personal_insights_insight_scope_check'),
        CheckConstraint("moment_type_code IS NULL OR (moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[]))", name='personal_insights_moment_type_code_check'),
        CheckConstraint("severity_level IS NULL OR (severity_level::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'POSITIVE'::character varying]::text[]))", name='personal_insights_severity_level_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_insights_moment_id_fkey'),
        PrimaryKeyConstraint('insight_id', name='personal_insights_pkey'),
        Index('idx_personal_insights_moment_scope', 'moment_id', 'insight_scope', 'is_active')
    )

    insight_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    insight_scope: Mapped[str] = mapped_column(String(50), nullable=False)
    insight_type: Mapped[str] = mapped_column(String(80), nullable=False)
    insight_title: Mapped[str] = mapped_column(String(150), nullable=False)
    insight_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    moment_type_code: Mapped[Optional[str]] = mapped_column(String(50))
    severity_level: Mapped[Optional[str]] = mapped_column(String(30))
    recommended_action: Mapped[Optional[str]] = mapped_column(String(150))
    source_metric_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped[Optional['PersonalMoments']] = relationship('PersonalMoments', back_populates='personal_insights')


class PersonalLifeAdjustEvents(Base):
    __tablename__ = 'personal_life_adjust_events'
    __table_args__ = (
        CheckConstraint('array_length(adjustment_areas, 1) >= 1', name='chk_adjustment_area_not_empty'),
        CheckConstraint("focus_signal IS NULL OR (focus_signal::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[]))", name='chk_focus_signal'),
        CheckConstraint("momentum_signal IS NULL OR (momentum_signal::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[]))", name='chk_momentum_signal'),
        CheckConstraint("pressure_signal IS NULL OR (pressure_signal::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[]))", name='chk_pressure_signal'),
        CheckConstraint("recovery_signal IS NULL OR (recovery_signal::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[]))", name='chk_recovery_signal'),
        CheckConstraint('runtime_shift_score IS NULL OR runtime_shift_score >= 0::numeric AND runtime_shift_score <= 100::numeric', name='chk_runtime_shift_score'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_life_adjust_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_life_adjust_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('adjust_event_id', name='personal_life_adjust_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_life_adjust_events_quick_add_event_id_key'),
        Index('idx_life_adjust_area', 'adjustment_areas', postgresql_using='gin'),
        Index('idx_life_adjust_moment', 'moment_id'),
        Index('idx_life_adjust_user', 'user_id')
    )

    adjust_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    adjustment_areas: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    pressure_signal: Mapped[Optional[str]] = mapped_column(String(20))
    recovery_signal: Mapped[Optional[str]] = mapped_column(String(20))
    focus_signal: Mapped[Optional[str]] = mapped_column(String(20))
    momentum_signal: Mapped[Optional[str]] = mapped_column(String(20))
    note: Mapped[Optional[str]] = mapped_column(Text)
    runtime_shift_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    recommended_runtime_priority: Mapped[Optional[str]] = mapped_column(String(150))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_life_adjust_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_life_adjust_events')


class PersonalLifeAggregateSnapshots(Base):
    __tablename__ = 'personal_life_aggregate_snapshots'
    __table_args__ = (
        CheckConstraint('capacity_score >= 0::numeric AND capacity_score <= 100::numeric', name='personal_life_aggregate_snapshots_capacity_score_check'),
        CheckConstraint('dominant_emotion_pct IS NULL OR dominant_emotion_pct >= 0::numeric AND dominant_emotion_pct <= 100::numeric', name='personal_life_aggregate_snapshots_dominant_emotion_pct_check'),
        CheckConstraint('drift_score IS NULL OR drift_score >= 0::numeric', name='personal_life_aggregate_snapshots_drift_score_check'),
        CheckConstraint("drift_status IS NULL OR (drift_status::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying]::text[]))", name='personal_life_aggregate_snapshots_drift_status_check'),
        CheckConstraint("emotional_momentum_score IS NULL OR emotional_momentum_score >= '-100'::integer::numeric AND emotional_momentum_score <= 100::numeric", name='personal_life_aggregate_snapshot_emotional_momentum_score_check'),
        CheckConstraint('fulfillment_dimension_score >= 0::numeric AND fulfillment_dimension_score <= 100::numeric', name='personal_life_aggregate_snaps_fulfillment_dimension_score_check'),
        CheckConstraint('fulfillment_score >= 0::numeric AND fulfillment_score <= 100::numeric', name='personal_life_aggregate_snapshots_fulfillment_score_check'),
        CheckConstraint('growth_dimension_score >= 0::numeric AND growth_dimension_score <= 100::numeric', name='personal_life_aggregate_snapshots_growth_dimension_score_check'),
        CheckConstraint('growth_score >= 0::numeric AND growth_score <= 100::numeric', name='personal_life_aggregate_snapshots_growth_score_check'),
        CheckConstraint('happiness_driver_score IS NULL OR happiness_driver_score >= 0::numeric', name='personal_life_aggregate_snapshots_happiness_driver_score_check'),
        CheckConstraint('leverage_score IS NULL OR leverage_score >= 0::numeric', name='personal_life_aggregate_snapshots_leverage_score_check'),
        CheckConstraint('life_health_score >= 0::numeric AND life_health_score <= 100::numeric', name='personal_life_aggregate_snapshots_life_health_score_check'),
        CheckConstraint('relationship_health_score >= 0::numeric AND relationship_health_score <= 100::numeric', name='personal_life_aggregate_snapsho_relationship_health_score_check'),
        CheckConstraint('stability_score >= 0::numeric AND stability_score <= 100::numeric', name='personal_life_aggregate_snapshots_stability_score_check'),
        CheckConstraint('stress_score >= 0::numeric AND stress_score <= 100::numeric', name='personal_life_aggregate_snapshots_stress_score_check'),
        PrimaryKeyConstraint('life_aggregate_snapshot_id', name='personal_life_aggregate_snapshots_pkey'),
        Index('idx_life_aggregate_user_current', 'user_id', 'is_current'),
        Index('idx_life_aggregate_user_month', 'user_id', 'snapshot_month')
    )

    life_aggregate_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    life_health_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    stability_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    growth_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    fulfillment_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    relationship_health_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    stress_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    capacity_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    growth_dimension_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    fulfillment_dimension_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    dominant_emotion: Mapped[Optional[str]] = mapped_column(String(50))
    dominant_emotion_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    emotional_momentum_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    drift_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    drift_status: Mapped[Optional[str]] = mapped_column(String(50))
    leverage_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    leverage_area: Mapped[Optional[str]] = mapped_column(String(100))
    happiness_driver: Mapped[Optional[str]] = mapped_column(String(100))
    happiness_driver_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))
    life_stage: Mapped[Optional[str]] = mapped_column(String(100))
    life_intelligence_summary: Mapped[Optional[str]] = mapped_column(Text)


class PersonalLifeAttentionEvents(Base):
    __tablename__ = 'personal_life_attention_events'
    __table_args__ = (
        CheckConstraint('focus_load_score IS NULL OR focus_load_score >= 0::numeric AND focus_load_score <= 100::numeric', name='chk_attention_focus_load'),
        CheckConstraint("intensity_level::text = ANY (ARRAY['LIGHT'::character varying, 'MODERATE'::character varying, 'HEAVY'::character varying]::text[])", name='chk_attention_intensity'),
        CheckConstraint("status::text = ANY (ARRAY['COMPLETED'::character varying, 'IN_PROGRESS'::character varying, 'DELAYED'::character varying]::text[])", name='chk_attention_status'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_life_attention_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_life_attention_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('attention_event_id', name='personal_life_attention_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_life_attention_events_quick_add_event_id_key'),
        Index('idx_life_attention_moment', 'moment_id'),
        Index('idx_life_attention_user', 'user_id')
    )

    attention_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    attention_category: Mapped[str] = mapped_column(String(100), nullable=False)
    intensity_level: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    note: Mapped[Optional[str]] = mapped_column(Text)
    pressure_weight: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    focus_load_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_life_attention_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_life_attention_events')


class PersonalLifeConnections(Base):
    __tablename__ = 'personal_life_connections'
    __table_args__ = (
        CheckConstraint('connection_strength_pct IS NULL OR connection_strength_pct >= 0::numeric AND connection_strength_pct <= 100::numeric', name='personal_life_connections_connection_strength_pct_check'),
        CheckConstraint("source_moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_life_connections_source_moment_type_code_check'),
        CheckConstraint("target_moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_life_connections_target_moment_type_code_check'),
        PrimaryKeyConstraint('life_connection_id', name='personal_life_connections_pkey'),
        Index('idx_life_connections_user_current', 'user_id', 'is_current'),
        Index('idx_life_connections_user_month', 'user_id', 'snapshot_month')
    )

    life_connection_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    target_moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    connection_title: Mapped[str] = mapped_column(String(150), nullable=False)
    connection_summary: Mapped[str] = mapped_column(Text, nullable=False)
    signal_label: Mapped[str] = mapped_column(String(80), nullable=False)
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    connection_strength_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))


class PersonalLifeDimensionScores(Base):
    __tablename__ = 'personal_life_dimension_scores'
    __table_args__ = (
        CheckConstraint("dimension_code::text = ANY (ARRAY['STRESS'::character varying, 'CAPACITY'::character varying, 'GROWTH'::character varying, 'FULFILLMENT'::character varying]::text[])", name='personal_life_dimension_scores_dimension_code_check'),
        CheckConstraint('dimension_score >= 0::numeric AND dimension_score <= 100::numeric', name='personal_life_dimension_scores_dimension_score_check'),
        CheckConstraint("trend_direction IS NULL OR (trend_direction::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[]))", name='personal_life_dimension_scores_trend_direction_check'),
        PrimaryKeyConstraint('life_dimension_score_id', name='personal_life_dimension_scores_pkey'),
        Index('idx_life_dimension_current_month', 'user_id', 'snapshot_month', 'is_current'),
        Index('idx_life_dimension_user_current', 'user_id', 'dimension_code', 'is_current'),
        Index('idx_life_dimension_user_month', 'user_id', 'snapshot_month')
    )

    life_dimension_score_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    dimension_code: Mapped[str] = mapped_column(String(50), nullable=False)
    dimension_label: Mapped[str] = mapped_column(String(100), nullable=False)
    dimension_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    status_label: Mapped[str] = mapped_column(String(100), nullable=False)
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    driver_summary: Mapped[Optional[str]] = mapped_column(Text)
    trend_direction: Mapped[Optional[str]] = mapped_column(String(20))


class PersonalLifeDriftAlerts(Base):
    __tablename__ = 'personal_life_drift_alerts'
    __table_args__ = (
        CheckConstraint("falling_dimension_code IS NULL OR (falling_dimension_code::text = ANY (ARRAY['STRESS'::character varying, 'CAPACITY'::character varying, 'GROWTH'::character varying, 'FULFILLMENT'::character varying]::text[]))", name='personal_life_drift_alerts_falling_dimension_code_check'),
        CheckConstraint("rising_dimension_code IS NULL OR (rising_dimension_code::text = ANY (ARRAY['STRESS'::character varying, 'CAPACITY'::character varying, 'GROWTH'::character varying, 'FULFILLMENT'::character varying]::text[]))", name='personal_life_drift_alerts_rising_dimension_code_check'),
        CheckConstraint("severity_level::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying]::text[])", name='personal_life_drift_alerts_severity_level_check'),
        PrimaryKeyConstraint('life_drift_alert_id', name='personal_life_drift_alerts_pkey'),
        Index('idx_life_drift_user_active', 'user_id', 'is_active')
    )

    life_drift_alert_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    drift_title: Mapped[str] = mapped_column(String(150), nullable=False)
    drift_message: Mapped[str] = mapped_column(Text, nullable=False)
    severity_level: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    rising_dimension_code: Mapped[Optional[str]] = mapped_column(String(50))
    falling_dimension_code: Mapped[Optional[str]] = mapped_column(String(50))
    recommended_action: Mapped[Optional[str]] = mapped_column(String(200))


class PersonalLifeHealthSnapshots(Base):
    __tablename__ = 'personal_life_health_snapshots'
    __table_args__ = (
        CheckConstraint('life_health_score >= 0::numeric AND life_health_score <= 100::numeric', name='personal_life_health_snapshots_life_health_score_check'),
        CheckConstraint("monthly_delta_score IS NULL OR monthly_delta_score >= '-100'::integer::numeric AND monthly_delta_score <= 100::numeric", name='personal_life_health_snapshots_monthly_delta_score_check'),
        PrimaryKeyConstraint('life_health_snapshot_id', name='personal_life_health_snapshots_pkey'),
        Index('idx_life_health_current_month', 'user_id', 'snapshot_month', 'is_current'),
        Index('idx_life_health_user_current', 'user_id', 'is_current'),
        Index('idx_life_health_user_month', 'user_id', 'snapshot_month')
    )

    life_health_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    life_health_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    health_status_label: Mapped[str] = mapped_column(String(100), nullable=False)
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    monthly_delta_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    summary_text: Mapped[Optional[str]] = mapped_column(Text)


class PersonalLifeJourneyEvents(Base):
    __tablename__ = 'personal_life_journey_events'
    __table_args__ = (
        CheckConstraint('importance_score IS NULL OR importance_score >= 0::numeric AND importance_score <= 100::numeric', name='personal_life_journey_events_importance_score_check'),
        CheckConstraint("source_dimension_code IS NULL OR (source_dimension_code::text = ANY (ARRAY['STRESS'::character varying, 'CAPACITY'::character varying, 'GROWTH'::character varying, 'FULFILLMENT'::character varying]::text[]))", name='personal_life_journey_events_source_dimension_code_check'),
        CheckConstraint("source_moment_type_code IS NULL OR (source_moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[]))", name='personal_life_journey_events_source_moment_type_code_check'),
        PrimaryKeyConstraint('life_journey_event_id', name='personal_life_journey_events_pkey'),
        Index('idx_life_journey_user_month', 'user_id', 'journey_month')
    )

    life_journey_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    journey_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    journey_title: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    journey_description: Mapped[Optional[str]] = mapped_column(Text)
    source_moment_type_code: Mapped[Optional[str]] = mapped_column(String(50))
    source_dimension_code: Mapped[Optional[str]] = mapped_column(String(50))
    importance_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))


class PersonalLifeMonthlyChanges(Base):
    __tablename__ = 'personal_life_monthly_changes'
    __table_args__ = (
        CheckConstraint("change_value_pct >= '-100'::integer::numeric AND change_value_pct <= 100::numeric", name='personal_life_monthly_changes_change_value_pct_check'),
        CheckConstraint("dimension_code IS NULL OR (dimension_code::text = ANY (ARRAY['STRESS'::character varying, 'CAPACITY'::character varying, 'GROWTH'::character varying, 'FULFILLMENT'::character varying]::text[]))", name='personal_life_monthly_changes_dimension_code_check'),
        CheckConstraint("direction::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[])", name='personal_life_monthly_changes_direction_check'),
        CheckConstraint("moment_type_code IS NULL OR (moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[]))", name='personal_life_monthly_changes_moment_type_code_check'),
        PrimaryKeyConstraint('life_monthly_change_id', name='personal_life_monthly_changes_pkey'),
        Index('idx_life_monthly_changes_user_month', 'user_id', 'snapshot_month')
    )

    life_monthly_change_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    change_label: Mapped[str] = mapped_column(String(150), nullable=False)
    change_value_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_type_code: Mapped[Optional[str]] = mapped_column(String(50))
    dimension_code: Mapped[Optional[str]] = mapped_column(String(50))


class PersonalLifeMoodEvents(Base):
    __tablename__ = 'personal_life_mood_events'
    __table_args__ = (
        CheckConstraint('mood_score IS NULL OR mood_score >= 0::numeric AND mood_score <= 100::numeric', name='chk_mood_score'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_life_mood_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_life_mood_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('mood_event_id', name='personal_life_mood_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_life_mood_events_quick_add_event_id_key'),
        Index('idx_life_mood_moment', 'moment_id'),
        Index('idx_life_mood_tags', 'mood_tags', postgresql_using='gin'),
        Index('idx_life_mood_user', 'user_id')
    )

    mood_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    mood_state: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    reflection_text: Mapped[Optional[str]] = mapped_column(Text)
    mood_tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))
    mood_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    pressure_context_flag: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_life_mood_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_life_mood_events')


class PersonalLifeOperationsProfile(Base):
    __tablename__ = 'personal_life_operations_profile'
    __table_args__ = (
        CheckConstraint('array_length(desired_directions, 1) >= 1', name='chk_life_desired_directions_not_empty'),
        CheckConstraint('array_length(pressure_sources, 1) >= 1', name='chk_life_pressure_sources_not_empty'),
        CheckConstraint('array_length(recovery_supports, 1) >= 1', name='chk_life_recovery_supports_not_empty'),
        CheckConstraint("pressure_load_level IS NULL OR (pressure_load_level::text = ANY (ARRAY['LOW'::character varying, 'MODERATE'::character varying, 'HIGH'::character varying]::text[]))", name='chk_life_pressure_load_level'),
        CheckConstraint('recovery_integrity_score IS NULL OR recovery_integrity_score >= 0::numeric AND recovery_integrity_score <= 100::numeric', name='chk_life_recovery_integrity_score'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_life_operations_profile_moment_id_fkey'),
        PrimaryKeyConstraint('life_profile_id', name='personal_life_operations_profile_pkey'),
        Index('idx_life_ops_profile_moment', 'moment_id'),
        Index('idx_life_ops_profile_user', 'user_id')
    )

    life_profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    current_life_state: Mapped[str] = mapped_column(String(50), nullable=False)
    desired_directions: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    pressure_sources: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    recovery_supports: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    runtime_identity: Mapped[str] = mapped_column(String(100), nullable=False)
    initial_runtime_focus: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    recovery_integrity_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    pressure_load_level: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_life_operations_profile')


class PersonalLifeRecoveryEvents(Base):
    __tablename__ = 'personal_life_recovery_events'
    __table_args__ = (
        CheckConstraint("energy_impact::text = ANY (ARRAY['LOW'::character varying, 'MODERATE'::character varying, 'HIGH'::character varying]::text[])", name='chk_recovery_energy'),
        CheckConstraint('recovery_score IS NULL OR recovery_score >= 0::numeric AND recovery_score <= 100::numeric', name='chk_recovery_score'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_life_recovery_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_life_recovery_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('recovery_event_id', name='personal_life_recovery_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_life_recovery_events_quick_add_event_id_key'),
        Index('idx_life_recovery_moment', 'moment_id'),
        Index('idx_life_recovery_user', 'user_id')
    )

    recovery_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    recovery_type: Mapped[str] = mapped_column(String(100), nullable=False)
    energy_impact: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    duration_bucket: Mapped[Optional[str]] = mapped_column(String(50))
    note: Mapped[Optional[str]] = mapped_column(Text)
    recovery_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    anchor_candidate_flag: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_life_recovery_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_life_recovery_events')


class PersonalLifestyleAdjustEvents(Base):
    __tablename__ = 'personal_lifestyle_adjust_events'
    __table_args__ = (
        CheckConstraint("adjustment_area::text = ANY (ARRAY['More Rest'::character varying, 'More Travel'::character varying, 'More Creativity'::character varying, 'More Social Time'::character varying, 'More Exercise'::character varying, 'More Personal Time'::character varying, 'More Exploration'::character varying, 'More Balance'::character varying, 'More Presence'::character varying]::text[])", name='chk_lifestyle_adjustment_area'),
        CheckConstraint('change_readiness_score IS NULL OR change_readiness_score >= 0::numeric AND change_readiness_score <= 100::numeric', name='chk_lifestyle_change_readiness_score'),
        CheckConstraint("confidence_level::text = ANY (ARRAY['Not Sure'::character varying, 'Somewhat Sure'::character varying, 'Very Sure'::character varying]::text[])", name='chk_lifestyle_adjust_confidence'),
        CheckConstraint('lifestyle_gap_score IS NULL OR lifestyle_gap_score >= 0::numeric AND lifestyle_gap_score <= 100::numeric', name='chk_lifestyle_gap_score'),
        CheckConstraint("priority_level::text = ANY (ARRAY['Low'::character varying, 'Medium'::character varying, 'High'::character varying]::text[])", name='chk_lifestyle_adjust_priority'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_lifestyle_adjust_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_lifestyle_adjust_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('lifestyle_adjust_event_id', name='personal_lifestyle_adjust_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_lifestyle_adjust_events_quick_add_event_id_key'),
        Index('idx_lifestyle_adjust_date', 'event_date'),
        Index('idx_lifestyle_adjust_moment', 'moment_id'),
        Index('idx_lifestyle_adjust_user', 'user_id')
    )

    lifestyle_adjust_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    adjustment_area: Mapped[str] = mapped_column(String(100), nullable=False)
    priority_level: Mapped[str] = mapped_column(String(30), nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(30), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    note: Mapped[Optional[str]] = mapped_column(Text)
    lifestyle_gap_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    change_readiness_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    recommended_action_label: Mapped[Optional[str]] = mapped_column(String(150))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_lifestyle_adjust_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_lifestyle_adjust_events')


class PersonalLifestyleDiscoveryEvents(Base):
    __tablename__ = 'personal_lifestyle_discovery_events'
    __table_args__ = (
        CheckConstraint("curiosity_level::text = ANY (ARRAY['Low'::character varying, 'Moderate'::character varying, 'High'::character varying]::text[])", name='chk_lifestyle_curiosity_level'),
        CheckConstraint("discovery_type::text = ANY (ARRAY['Place'::character varying, 'Idea'::character varying, 'Activity'::character varying, 'Person'::character varying, 'Skill'::character varying, 'Experience'::character varying, 'Opportunity'::character varying, 'Other'::character varying]::text[])", name='chk_lifestyle_discovery_type'),
        CheckConstraint('expansion_signal_score IS NULL OR expansion_signal_score >= 0::numeric AND expansion_signal_score <= 100::numeric', name='chk_lifestyle_expansion_score'),
        CheckConstraint('exploration_score_delta IS NULL OR exploration_score_delta >= 0::numeric AND exploration_score_delta <= 100::numeric', name='chk_lifestyle_exploration_score'),
        CheckConstraint("impact_level::text = ANY (ARRAY['Interesting'::character varying, 'Useful'::character varying, 'Inspiring'::character varying, 'Life-Changing'::character varying]::text[])", name='chk_lifestyle_discovery_impact'),
        CheckConstraint('money_invested_amount IS NULL OR money_invested_amount >= 0::numeric', name='chk_lifestyle_discovery_money'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_lifestyle_discovery_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_lifestyle_discovery_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('discovery_event_id', name='personal_lifestyle_discovery_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_lifestyle_discovery_events_quick_add_event_id_key'),
        Index('idx_lifestyle_discovery_date', 'event_date'),
        Index('idx_lifestyle_discovery_moment', 'moment_id'),
        Index('idx_lifestyle_discovery_user', 'user_id')
    )

    discovery_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    discovery_type: Mapped[str] = mapped_column(String(80), nullable=False)
    impact_level: Mapped[str] = mapped_column(String(50), nullable=False)
    curiosity_level: Mapped[str] = mapped_column(String(30), nullable=False)
    curiosity_driver_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    money_invested_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))
    note: Mapped[Optional[str]] = mapped_column(Text)
    exploration_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    expansion_signal_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_lifestyle_discovery_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_lifestyle_discovery_events')


class PersonalLifestyleExperienceEvents(Base):
    __tablename__ = 'personal_lifestyle_experience_events'
    __table_args__ = (
        CheckConstraint('cost_amount IS NULL OR cost_amount >= 0::numeric', name='chk_lifestyle_cost_amount'),
        CheckConstraint("energy_impact::text = ANY (ARRAY['Drained'::character varying, 'Neutral'::character varying, 'Refreshed'::character varying, 'Energized'::character varying]::text[])", name='chk_lifestyle_energy_impact'),
        CheckConstraint("experience_quality::text = ANY (ARRAY['Ordinary'::character varying, 'Enjoyable'::character varying, 'Memorable'::character varying, 'Exceptional'::character varying]::text[])", name='chk_lifestyle_experience_quality'),
        CheckConstraint("experience_type::text = ANY (ARRAY['Travel'::character varying, 'Food'::character varying, 'Nature'::character varying, 'Adventure'::character varying, 'Entertainment'::character varying, 'Social'::character varying, 'Family'::character varying, 'Personal'::character varying, 'Wellbeing'::character varying, 'Hobby'::character varying, 'Other'::character varying]::text[])", name='chk_lifestyle_experience_type'),
        CheckConstraint('fulfillment_score_delta IS NULL OR fulfillment_score_delta >= 0::numeric AND fulfillment_score_delta <= 100::numeric', name='chk_lifestyle_fulfillment_score'),
        CheckConstraint('lifestyle_roi_score IS NULL OR lifestyle_roi_score >= 0::numeric AND lifestyle_roi_score <= 100::numeric', name='chk_lifestyle_roi_score'),
        CheckConstraint("location_context IS NULL OR (location_context::text = ANY (ARRAY['Home'::character varying, 'Local'::character varying, 'Outing'::character varying, 'Travel'::character varying]::text[]))", name='chk_lifestyle_location_context'),
        CheckConstraint("people_context IS NULL OR (people_context::text = ANY (ARRAY['Alone'::character varying, 'Partner'::character varying, 'Friends'::character varying, 'Family'::character varying, 'Group'::character varying]::text[]))", name='chk_lifestyle_people_context'),
        CheckConstraint("spend_category IS NULL OR (spend_category::text = ANY (ARRAY['Travel'::character varying, 'Food & Dining'::character varying, 'Entertainment'::character varying, 'Wellbeing'::character varying, 'Fitness'::character varying, 'Learning'::character varying, 'Shopping'::character varying, 'Hobbies'::character varying, 'Experiences'::character varying, 'Other'::character varying]::text[]))", name='chk_lifestyle_spend_category'),
        CheckConstraint("value_received IS NULL OR (value_received::text = ANY (ARRAY['Not Worth It'::character varying, 'Okay'::character varying, 'Worth It'::character varying, 'Excellent Value'::character varying, 'Life Enriching'::character varying]::text[]))", name='chk_lifestyle_value_received'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_lifestyle_experience_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_lifestyle_experience_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('experience_event_id', name='personal_lifestyle_experience_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_lifestyle_experience_events_quick_add_event_id_key'),
        Index('idx_lifestyle_experience_date', 'event_date'),
        Index('idx_lifestyle_experience_moment', 'moment_id'),
        Index('idx_lifestyle_experience_user', 'user_id')
    )

    experience_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    experience_type: Mapped[str] = mapped_column(String(80), nullable=False)
    experience_quality: Mapped[str] = mapped_column(String(50), nullable=False)
    energy_impact: Mapped[str] = mapped_column(String(50), nullable=False)
    best_day_candidate_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    people_context: Mapped[Optional[str]] = mapped_column(String(50))
    location_context: Mapped[Optional[str]] = mapped_column(String(50))
    cost_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))
    spend_category: Mapped[Optional[str]] = mapped_column(String(80))
    value_received: Mapped[Optional[str]] = mapped_column(String(80))
    note: Mapped[Optional[str]] = mapped_column(Text)
    fulfillment_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    lifestyle_roi_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_lifestyle_experience_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_lifestyle_experience_events')


class PersonalLifestyleExpressionEvents(Base):
    __tablename__ = 'personal_lifestyle_expression_events'
    __table_args__ = (
        CheckConstraint("creation_type::text = ANY (ARRAY['Writing'::character varying, 'Art'::character varying, 'Music'::character varying, 'Design'::character varying, 'Content'::character varying, 'Photography'::character varying, 'Problem Solving'::character varying, 'Planning'::character varying, 'Other'::character varying]::text[])", name='chk_lifestyle_creation_type'),
        CheckConstraint('creativity_score_delta IS NULL OR creativity_score_delta >= 0::numeric AND creativity_score_delta <= 100::numeric', name='chk_lifestyle_creativity_score'),
        CheckConstraint('expression_energy_score IS NULL OR expression_energy_score >= 0::numeric AND expression_energy_score <= 100::numeric', name='chk_lifestyle_expression_energy_score'),
        CheckConstraint('money_invested_amount IS NULL OR money_invested_amount >= 0::numeric', name='chk_lifestyle_expression_money'),
        CheckConstraint("satisfaction_level::text = ANY (ARRAY['Low'::character varying, 'Moderate'::character varying, 'High'::character varying, 'Exceptional'::character varying]::text[])", name='chk_lifestyle_satisfaction_level'),
        CheckConstraint("time_invested_bucket IS NULL OR (time_invested_bucket::text = ANY (ARRAY['<30'::character varying, '30_60'::character varying, '1_2_HOURS'::character varying, '2_PLUS_HOURS'::character varying]::text[]))", name='chk_lifestyle_expression_time'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_lifestyle_expression_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_lifestyle_expression_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('expression_event_id', name='personal_lifestyle_expression_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_lifestyle_expression_events_quick_add_event_id_key'),
        Index('idx_lifestyle_expression_date', 'event_date'),
        Index('idx_lifestyle_expression_moment', 'moment_id'),
        Index('idx_lifestyle_expression_user', 'user_id')
    )

    expression_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    creation_type: Mapped[str] = mapped_column(String(80), nullable=False)
    satisfaction_level: Mapped[str] = mapped_column(String(50), nullable=False)
    inspiration_source_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    time_invested_bucket: Mapped[Optional[str]] = mapped_column(String(30))
    money_invested_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))
    note: Mapped[Optional[str]] = mapped_column(Text)
    creativity_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    expression_energy_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_lifestyle_expression_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_lifestyle_expression_events')


class PersonalLifestyleProfile(Base):
    __tablename__ = 'personal_lifestyle_profile'
    __table_args__ = (
        CheckConstraint('array_length(best_day_drivers, 1) >= 1', name='chk_lifestyle_best_day_drivers_not_empty'),
        CheckConstraint('array_length(desired_lifestyle_vectors, 1) >= 1', name='chk_lifestyle_desired_vectors_not_empty'),
        CheckConstraint('array_length(lifestyle_enrichment_factors, 1) >= 1', name='chk_lifestyle_enrichment_factors_not_empty'),
        CheckConstraint('array_length(neglected_lifestyle_areas, 1) >= 1', name='chk_lifestyle_neglected_areas_not_empty'),
        CheckConstraint("lifestyle_potential IS NULL OR (lifestyle_potential::text = ANY (ARRAY['LOW'::character varying, 'MODERATE'::character varying, 'HIGH'::character varying]::text[]))", name='chk_lifestyle_potential'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_lifestyle_profile_moment_id_fkey'),
        PrimaryKeyConstraint('lifestyle_profile_id', name='personal_lifestyle_profile_pkey'),
        Index('idx_lifestyle_profile_moment', 'moment_id'),
        Index('idx_lifestyle_profile_user', 'user_id')
    )

    lifestyle_profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lifestyle_style: Mapped[str] = mapped_column(String(80), nullable=False)
    current_lifestyle_state: Mapped[str] = mapped_column(String(50), nullable=False)
    desired_lifestyle_vectors: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    neglected_lifestyle_areas: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    best_day_drivers: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    lifestyle_enrichment_factors: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    lifestyle_identity: Mapped[str] = mapped_column(String(100), nullable=False)
    lifestyle_energy: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    primary_lifestyle_gap: Mapped[Optional[str]] = mapped_column(String(100))
    primary_lifestyle_opportunity: Mapped[Optional[str]] = mapped_column(String(150))
    lifestyle_potential: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_lifestyle_profile')


class PersonalLifestyleWellbeingEvents(Base):
    __tablename__ = 'personal_lifestyle_wellbeing_events'
    __table_args__ = (
        CheckConstraint('array_length(wellbeing_areas, 1) >= 1', name='chk_lifestyle_wellbeing_areas_not_empty'),
        CheckConstraint("energy_signal_score IS NULL OR energy_signal_score >= '-100'::integer::numeric AND energy_signal_score <= 100::numeric", name='chk_lifestyle_energy_signal_score'),
        CheckConstraint("wellbeing_score_delta IS NULL OR wellbeing_score_delta >= '-100'::integer::numeric AND wellbeing_score_delta <= 100::numeric", name='chk_lifestyle_wellbeing_score'),
        CheckConstraint("wellbeing_state::text = ANY (ARRAY['Low'::character varying, 'Moderate'::character varying, 'Good'::character varying, 'Excellent'::character varying]::text[])", name='chk_lifestyle_wellbeing_state'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_lifestyle_wellbeing_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_lifestyle_wellbeing_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('wellbeing_event_id', name='personal_lifestyle_wellbeing_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_lifestyle_wellbeing_events_quick_add_event_id_key'),
        Index('idx_lifestyle_wellbeing_areas', 'wellbeing_areas', postgresql_using='gin'),
        Index('idx_lifestyle_wellbeing_contributors', 'contributors', postgresql_using='gin'),
        Index('idx_lifestyle_wellbeing_date', 'event_date'),
        Index('idx_lifestyle_wellbeing_moment', 'moment_id'),
        Index('idx_lifestyle_wellbeing_user', 'user_id')
    )

    wellbeing_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    wellbeing_areas: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    wellbeing_state: Mapped[str] = mapped_column(String(50), nullable=False)
    balance_driver_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    contributors: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text()))
    note: Mapped[Optional[str]] = mapped_column(Text)
    wellbeing_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    energy_signal_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_lifestyle_wellbeing_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_lifestyle_wellbeing_events')


class PersonalLivePriorities(Base):
    __tablename__ = 'personal_live_priorities'
    __table_args__ = (
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_live_priorities_moment_type_code_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_live_priorities_moment_id_fkey'),
        PrimaryKeyConstraint('live_priority_id', name='personal_live_priorities_pkey'),
        Index('uq_personal_live_priorities_current', 'moment_id', postgresql_where='(is_current = true)', unique=True)
    )

    live_priority_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    priority_title: Mapped[str] = mapped_column(String(150), nullable=False)
    recommended_action_label: Mapped[str] = mapped_column(String(150), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    priority_reason: Mapped[Optional[str]] = mapped_column(Text)
    expected_impact_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    recent_activity_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    quick_actions_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_live_priorities')


class PersonalMemoryDriverRankings(Base):
    __tablename__ = 'personal_memory_driver_rankings'
    __table_args__ = (
        CheckConstraint("driver_category::text = ANY (ARRAY['POSITIVE'::character varying, 'NEGATIVE'::character varying, 'HIGHEST_RETURN'::character varying, 'FULFILLMENT_DRIVER'::character varying, 'GROWTH_DRIVER'::character varying, 'CONNECTION_DRIVER'::character varying, 'CAPACITY_DRIVER'::character varying]::text[])", name='personal_memory_driver_rankings_driver_category_check'),
        CheckConstraint('driver_rank > 0', name='personal_memory_driver_rankings_driver_rank_check'),
        CheckConstraint('impact_pct IS NULL OR impact_pct >= 0::numeric AND impact_pct <= 100::numeric', name='personal_memory_driver_rankings_impact_pct_check'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_memory_driver_rankings_moment_type_code_check'),
        CheckConstraint('return_multiplier IS NULL OR return_multiplier >= 0::numeric', name='personal_memory_driver_rankings_return_multiplier_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_memory_driver_rankings_moment_id_fkey'),
        PrimaryKeyConstraint('driver_ranking_id', name='personal_memory_driver_rankings_pkey'),
        Index('idx_memory_driver_current_month', 'user_id', 'snapshot_month', 'is_current'),
        Index('idx_memory_driver_moment', 'moment_id'),
        Index('idx_memory_driver_user_type_current', 'user_id', 'moment_type_code', 'driver_category', 'is_current')
    )

    driver_ranking_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    driver_category: Mapped[str] = mapped_column(String(50), nullable=False)
    driver_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    driver_name: Mapped[str] = mapped_column(String(100), nullable=False)
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    impact_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    impact_description: Mapped[Optional[str]] = mapped_column(Text)
    return_multiplier: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_memory_driver_rankings')


class PersonalMemoryEmotionalDna(Base):
    __tablename__ = 'personal_memory_emotional_dna'
    __table_args__ = (
        CheckConstraint('emotion_pct >= 0::numeric AND emotion_pct <= 100::numeric', name='personal_memory_emotional_dna_emotion_pct_check'),
        CheckConstraint('emotion_rank > 0', name='personal_memory_emotional_dna_emotion_rank_check'),
        CheckConstraint("moment_type_code IS NULL OR (moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[]))", name='personal_memory_emotional_dna_moment_type_code_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_memory_emotional_dna_moment_id_fkey'),
        PrimaryKeyConstraint('emotional_dna_id', name='personal_memory_emotional_dna_pkey'),
        Index('idx_memory_emotional_current_month', 'user_id', 'snapshot_month', 'is_current'),
        Index('idx_memory_emotional_moment', 'moment_id'),
        Index('idx_memory_emotional_user_current', 'user_id', 'moment_type_code', 'is_current')
    )

    emotional_dna_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    emotion_name: Mapped[str] = mapped_column(String(50), nullable=False)
    emotion_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    emotion_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    moment_type_code: Mapped[Optional[str]] = mapped_column(String(50))
    dna_summary: Mapped[Optional[str]] = mapped_column(Text)

    moment: Mapped[Optional['PersonalMoments']] = relationship('PersonalMoments', back_populates='personal_memory_emotional_dna')


class PersonalMemoryEvolutionSnapshots(Base):
    __tablename__ = 'personal_memory_evolution_snapshots'
    __table_args__ = (
        CheckConstraint('evolution_confidence_pct IS NULL OR evolution_confidence_pct >= 0::numeric AND evolution_confidence_pct <= 100::numeric', name='personal_memory_evolution_snapsh_evolution_confidence_pct_check'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_memory_evolution_snapshots_moment_type_code_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_memory_evolution_snapshots_moment_id_fkey'),
        PrimaryKeyConstraint('evolution_snapshot_id', name='personal_memory_evolution_snapshots_pkey'),
        Index('idx_memory_evolution_current_month', 'user_id', 'snapshot_month', 'is_current'),
        Index('idx_memory_evolution_moment', 'moment_id'),
        Index('idx_memory_evolution_user_type_current', 'user_id', 'moment_type_code', 'is_current')
    )

    evolution_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_stage: Mapped[str] = mapped_column(String(100), nullable=False)
    current_stage: Mapped[str] = mapped_column(String(100), nullable=False)
    transition_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    emerging_stage: Mapped[Optional[str]] = mapped_column(String(100))
    evolution_confidence_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_memory_evolution_snapshots')


class PersonalMemoryIdentitySnapshots(Base):
    __tablename__ = 'personal_memory_identity_snapshots'
    __table_args__ = (
        CheckConstraint('confidence_pct >= 0::numeric AND confidence_pct <= 100::numeric', name='personal_memory_identity_snapshots_confidence_pct_check'),
        CheckConstraint("confidence_trend_pct IS NULL OR confidence_trend_pct >= '-100'::integer::numeric AND confidence_trend_pct <= 100::numeric", name='personal_memory_identity_snapshots_confidence_trend_pct_check'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_memory_identity_snapshots_moment_type_code_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_memory_identity_snapshots_moment_id_fkey'),
        PrimaryKeyConstraint('identity_snapshot_id', name='personal_memory_identity_snapshots_pkey'),
        Index('idx_memory_identity_current_month', 'user_id', 'snapshot_month', 'is_current'),
        Index('idx_memory_identity_moment', 'moment_id'),
        Index('idx_memory_identity_user_type_current', 'user_id', 'moment_type_code', 'is_current')
    )

    identity_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    identity_title: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    confidence_trend_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    identity_summary: Mapped[Optional[str]] = mapped_column(Text)
    identity_visual_type: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_memory_identity_snapshots')


class PersonalMemoryPatterns(Base):
    __tablename__ = 'personal_memory_patterns'
    __table_args__ = (
        CheckConstraint('confidence_score >= 0::numeric AND confidence_score <= 100::numeric', name='personal_memory_patterns_confidence_score_check'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_memory_patterns_moment_type_code_check'),
        CheckConstraint('pattern_confidence_pct IS NULL OR pattern_confidence_pct >= 0::numeric AND pattern_confidence_pct <= 100::numeric', name='chk_personal_memory_pattern_confidence_pct'),
        CheckConstraint('supporting_event_count >= 0', name='personal_memory_patterns_supporting_event_count_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_memory_patterns_moment_id_fkey'),
        PrimaryKeyConstraint('memory_pattern_id', name='personal_memory_patterns_pkey'),
        Index('idx_memory_patterns_moment_active', 'moment_id', 'is_active')
    )

    memory_pattern_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    pattern_type: Mapped[str] = mapped_column(String(80), nullable=False)
    pattern_title: Mapped[str] = mapped_column(String(150), nullable=False)
    pattern_description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    supporting_event_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    contribution_breakdown_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    pattern_confidence_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    pattern_explanation: Mapped[Optional[str]] = mapped_column(Text)

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_memory_patterns')
    personal_recommendations: Mapped[list['PersonalRecommendations']] = relationship('PersonalRecommendations', back_populates='source_pattern')


class PersonalMetricSnapshots(Base):
    __tablename__ = 'personal_metric_snapshots'
    __table_args__ = (
        CheckConstraint("measurement_period::text = ANY (ARRAY['DAILY'::character varying, 'WEEKLY'::character varying, 'MONTHLY'::character varying]::text[])", name='personal_metric_snapshots_measurement_period_check'),
        CheckConstraint('metric_value >= 0::numeric AND metric_value <= 100::numeric', name='personal_metric_snapshots_metric_value_check'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_metric_snapshots_moment_type_code_check'),
        CheckConstraint("trend_direction IS NULL OR (trend_direction::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[]))", name='personal_metric_snapshots_trend_direction_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_metric_snapshots_moment_id_fkey'),
        PrimaryKeyConstraint('metric_snapshot_id', name='personal_metric_snapshots_pkey'),
        Index('idx_metric_snapshots_moment_metric_date', 'moment_id', 'metric_code', 'snapshot_date')
    )

    metric_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_code: Mapped[str] = mapped_column(String(80), nullable=False)
    metric_label: Mapped[str] = mapped_column(String(120), nullable=False)
    metric_value: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    measurement_period: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DAILY'::character varying"))
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    metric_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    trend_direction: Mapped[Optional[str]] = mapped_column(String(30))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_metric_snapshots')


class PersonalMomentHighlights(Base):
    __tablename__ = 'personal_moment_highlights'
    __table_args__ = (
        CheckConstraint('amount IS NULL OR amount >= 0::numeric', name='personal_moment_highlights_amount_check'),
        CheckConstraint('impact_score IS NULL OR impact_score >= 0::numeric AND impact_score <= 100::numeric', name='personal_moment_highlights_impact_score_check'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_moment_highlights_moment_type_code_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_moment_highlights_moment_id_fkey'),
        PrimaryKeyConstraint('moment_highlight_id', name='personal_moment_highlights_pkey'),
        Index('idx_moment_highlights_moment_current', 'moment_id', 'is_current'),
        Index('idx_moment_highlights_occurred_at', 'occurred_at'),
        Index('idx_moment_highlights_user_type', 'user_id', 'moment_type_code')
    )

    moment_highlight_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    highlight_title: Mapped[str] = mapped_column(String(150), nullable=False)
    highlight_type: Mapped[str] = mapped_column(String(80), nullable=False)
    occurred_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    source_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    source_event_type: Mapped[Optional[str]] = mapped_column(String(100))
    impact_label: Mapped[Optional[str]] = mapped_column(String(150))
    impact_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_moment_highlights')


class PersonalMomentProfiles(Base):
    __tablename__ = 'personal_moment_profiles'
    __table_args__ = (
        CheckConstraint("horizon_potential_label IS NULL OR (horizon_potential_label::text = ANY (ARRAY['LOW'::character varying, 'MODERATE'::character varying, 'HIGH'::character varying]::text[]))", name='chk_horizon_potential_label'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_moment_profiles_moment_id_fkey'),
        PrimaryKeyConstraint('profile_id', name='personal_moment_profiles_pkey'),
        Index('idx_personal_moment_profiles_moment', 'moment_id'),
        Index('idx_personal_moment_profiles_user', 'user_id'),
        Index('uq_personal_moment_profiles_current', 'moment_id', postgresql_where='(is_current = true)', unique=True)
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    identity_label: Mapped[str] = mapped_column(String(100), nullable=False)
    identity_description: Mapped[str] = mapped_column(Text, nullable=False)
    primary_focus_label: Mapped[str] = mapped_column(String(100), nullable=False)
    setup_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    energy_label: Mapped[Optional[str]] = mapped_column(String(100))
    primary_gap_label: Mapped[Optional[str]] = mapped_column(String(100))
    primary_opportunity_label: Mapped[Optional[str]] = mapped_column(String(150))
    horizon_current_label: Mapped[Optional[str]] = mapped_column(String(100))
    horizon_target_label: Mapped[Optional[str]] = mapped_column(String(100))
    horizon_gap_label: Mapped[Optional[str]] = mapped_column(String(100))
    horizon_potential_label: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_moment_profiles')


class PersonalMomentTurningPoints(Base):
    __tablename__ = 'personal_moment_turning_points'
    __table_args__ = (
        CheckConstraint('impact_score IS NULL OR impact_score >= 0::numeric AND impact_score <= 100::numeric', name='personal_moment_turning_points_impact_score_check'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_moment_turning_points_moment_type_code_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_moment_turning_points_moment_id_fkey'),
        PrimaryKeyConstraint('turning_point_id', name='personal_moment_turning_points_pkey'),
        Index('idx_moment_turning_points_moment_current', 'moment_id', 'is_current'),
        Index('idx_moment_turning_points_occurred_at', 'occurred_at'),
        Index('idx_moment_turning_points_user_type', 'user_id', 'moment_type_code')
    )

    turning_point_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    turning_point_title: Mapped[str] = mapped_column(String(150), nullable=False)
    turning_point_type: Mapped[str] = mapped_column(String(80), nullable=False)
    detected_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    source_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    source_event_type: Mapped[Optional[str]] = mapped_column(String(100))
    turning_point_description: Mapped[Optional[str]] = mapped_column(Text)
    impact_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    occurred_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_moment_turning_points')


class PersonalMomentTypes(Base):
    __tablename__ = 'personal_moment_types'
    __table_args__ = (
        CheckConstraint('display_order >= 1 AND display_order <= 4', name='personal_moment_types_display_order_check'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='chk_personal_moment_type_code'),
        PrimaryKeyConstraint('moment_type_id', name='personal_moment_types_pkey'),
        UniqueConstraint('moment_type_code', name='personal_moment_types_moment_type_code_key'),
        UniqueConstraint('moment_type_name', name='personal_moment_types_moment_type_name_key')
    )

    moment_type_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    moment_type_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    personal_moments: Mapped[list['PersonalMoments']] = relationship('PersonalMoments', back_populates='moment_type')


class PersonalMoments(Base):
    __tablename__ = 'personal_moments'
    __table_args__ = (
        CheckConstraint("status::text <> 'ACTIVE'::text OR activated_at IS NOT NULL", name='chk_personal_moment_activation'),
        CheckConstraint("status::text = ANY (ARRAY['DRAFT'::character varying, 'ACTIVE'::character varying, 'PAUSED'::character varying, 'ARCHIVED'::character varying]::text[])", name='chk_personal_moment_status'),
        ForeignKeyConstraint(['moment_type_id'], ['personal_moment_types.moment_type_id'], name='personal_moments_moment_type_id_fkey'),
        PrimaryKeyConstraint('moment_id', name='personal_moments_pkey'),
        Index('idx_personal_moments_type_status', 'moment_type_id', 'status'),
        Index('idx_personal_moments_user', 'user_id')
    )

    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DRAFT'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    activated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    current_identity_label: Mapped[Optional[str]] = mapped_column(String(100))
    current_state_label: Mapped[Optional[str]] = mapped_column(String(100))
    last_activity_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment_type: Mapped['PersonalMomentTypes'] = relationship('PersonalMomentTypes', back_populates='personal_moments')
    personal_ai_interpretation_runs: Mapped[list['PersonalAiInterpretationRuns']] = relationship('PersonalAiInterpretationRuns', back_populates='moment')
    personal_future_building_profile: Mapped[list['PersonalFutureBuildingProfile']] = relationship('PersonalFutureBuildingProfile', back_populates='moment')
    personal_insights: Mapped[list['PersonalInsights']] = relationship('PersonalInsights', back_populates='moment')
    personal_life_operations_profile: Mapped[list['PersonalLifeOperationsProfile']] = relationship('PersonalLifeOperationsProfile', back_populates='moment')
    personal_lifestyle_profile: Mapped[list['PersonalLifestyleProfile']] = relationship('PersonalLifestyleProfile', back_populates='moment')
    personal_live_priorities: Mapped[list['PersonalLivePriorities']] = relationship('PersonalLivePriorities', back_populates='moment')
    personal_memory_driver_rankings: Mapped[list['PersonalMemoryDriverRankings']] = relationship('PersonalMemoryDriverRankings', back_populates='moment')
    personal_memory_emotional_dna: Mapped[list['PersonalMemoryEmotionalDna']] = relationship('PersonalMemoryEmotionalDna', back_populates='moment')
    personal_memory_evolution_snapshots: Mapped[list['PersonalMemoryEvolutionSnapshots']] = relationship('PersonalMemoryEvolutionSnapshots', back_populates='moment')
    personal_memory_identity_snapshots: Mapped[list['PersonalMemoryIdentitySnapshots']] = relationship('PersonalMemoryIdentitySnapshots', back_populates='moment')
    personal_memory_patterns: Mapped[list['PersonalMemoryPatterns']] = relationship('PersonalMemoryPatterns', back_populates='moment')
    personal_metric_snapshots: Mapped[list['PersonalMetricSnapshots']] = relationship('PersonalMetricSnapshots', back_populates='moment')
    personal_moment_highlights: Mapped[list['PersonalMomentHighlights']] = relationship('PersonalMomentHighlights', back_populates='moment')
    personal_moment_profiles: Mapped[list['PersonalMomentProfiles']] = relationship('PersonalMomentProfiles', back_populates='moment')
    personal_moment_turning_points: Mapped[list['PersonalMomentTurningPoints']] = relationship('PersonalMomentTurningPoints', back_populates='moment')
    personal_notification_queue: Mapped[list['PersonalNotificationQueue']] = relationship('PersonalNotificationQueue', back_populates='moment')
    personal_pulse_snapshots: Mapped[list['PersonalPulseSnapshots']] = relationship('PersonalPulseSnapshots', back_populates='moment')
    personal_quick_add_events: Mapped[list['PersonalQuickAddEvents']] = relationship('PersonalQuickAddEvents', back_populates='moment')
    personal_relationships_profile: Mapped[list['PersonalRelationshipsProfile']] = relationship('PersonalRelationshipsProfile', back_populates='moment')
    personal_runtime_snapshots: Mapped[list['PersonalRuntimeSnapshots']] = relationship('PersonalRuntimeSnapshots', back_populates='moment')
    personal_signals: Mapped[list['PersonalSignals']] = relationship('PersonalSignals', back_populates='moment')
    personal_activity_timeline: Mapped[list['PersonalActivityTimeline']] = relationship('PersonalActivityTimeline', back_populates='moment')
    personal_event_edits: Mapped[list['PersonalEventEdits']] = relationship('PersonalEventEdits', back_populates='moment')
    personal_event_voids: Mapped[list['PersonalEventVoids']] = relationship('PersonalEventVoids', back_populates='moment')
    personal_future_learning_events: Mapped[list['PersonalFutureLearningEvents']] = relationship('PersonalFutureLearningEvents', back_populates='moment')
    personal_future_milestone_events: Mapped[list['PersonalFutureMilestoneEvents']] = relationship('PersonalFutureMilestoneEvents', back_populates='moment')
    personal_future_opportunity_events: Mapped[list['PersonalFutureOpportunityEvents']] = relationship('PersonalFutureOpportunityEvents', back_populates='moment')
    personal_future_pivot_events: Mapped[list['PersonalFuturePivotEvents']] = relationship('PersonalFuturePivotEvents', back_populates='moment')
    personal_future_progress_events: Mapped[list['PersonalFutureProgressEvents']] = relationship('PersonalFutureProgressEvents', back_populates='moment')
    personal_life_adjust_events: Mapped[list['PersonalLifeAdjustEvents']] = relationship('PersonalLifeAdjustEvents', back_populates='moment')
    personal_life_attention_events: Mapped[list['PersonalLifeAttentionEvents']] = relationship('PersonalLifeAttentionEvents', back_populates='moment')
    personal_life_mood_events: Mapped[list['PersonalLifeMoodEvents']] = relationship('PersonalLifeMoodEvents', back_populates='moment')
    personal_life_recovery_events: Mapped[list['PersonalLifeRecoveryEvents']] = relationship('PersonalLifeRecoveryEvents', back_populates='moment')
    personal_lifestyle_adjust_events: Mapped[list['PersonalLifestyleAdjustEvents']] = relationship('PersonalLifestyleAdjustEvents', back_populates='moment')
    personal_lifestyle_discovery_events: Mapped[list['PersonalLifestyleDiscoveryEvents']] = relationship('PersonalLifestyleDiscoveryEvents', back_populates='moment')
    personal_lifestyle_experience_events: Mapped[list['PersonalLifestyleExperienceEvents']] = relationship('PersonalLifestyleExperienceEvents', back_populates='moment')
    personal_lifestyle_expression_events: Mapped[list['PersonalLifestyleExpressionEvents']] = relationship('PersonalLifestyleExpressionEvents', back_populates='moment')
    personal_lifestyle_wellbeing_events: Mapped[list['PersonalLifestyleWellbeingEvents']] = relationship('PersonalLifestyleWellbeingEvents', back_populates='moment')
    personal_money_events: Mapped[list['PersonalMoneyEvents']] = relationship('PersonalMoneyEvents', back_populates='moment')
    personal_recommendations: Mapped[list['PersonalRecommendations']] = relationship('PersonalRecommendations', back_populates='moment')
    personal_relationship_adjust_events: Mapped[list['PersonalRelationshipAdjustEvents']] = relationship('PersonalRelationshipAdjustEvents', back_populates='moment')
    personal_relationship_connection_events: Mapped[list['PersonalRelationshipConnectionEvents']] = relationship('PersonalRelationshipConnectionEvents', back_populates='moment')
    personal_relationship_experience_events: Mapped[list['PersonalRelationshipExperienceEvents']] = relationship('PersonalRelationshipExperienceEvents', back_populates='moment')
    personal_relationship_investment_events: Mapped[list['PersonalRelationshipInvestmentEvents']] = relationship('PersonalRelationshipInvestmentEvents', back_populates='moment')
    personal_relationship_support_events: Mapped[list['PersonalRelationshipSupportEvents']] = relationship('PersonalRelationshipSupportEvents', back_populates='moment')


class PersonalMoneyEvents(Base):
    __tablename__ = 'personal_money_events'
    __table_args__ = (
        CheckConstraint('amount >= 0::numeric', name='chk_personal_money_amount'),
        CheckConstraint("direction::text = ANY (ARRAY['CREDIT'::character varying, 'DEBIT'::character varying, 'NEUTRAL'::character varying]::text[])", name='chk_personal_money_direction'),
        CheckConstraint('financial_pressure_score IS NULL OR financial_pressure_score >= 0::numeric AND financial_pressure_score <= 100::numeric', name='chk_personal_money_financial_pressure_score'),
        CheckConstraint('investment_score IS NULL OR investment_score >= 0::numeric AND investment_score <= 100::numeric', name='chk_personal_money_investment_score'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='chk_personal_money_moment_type'),
        CheckConstraint("money_event_type::text = ANY (ARRAY['EXPENSE'::character varying, 'INCOME'::character varying, 'TRANSFER'::character varying, 'CONTRIBUTION'::character varying, 'SAVINGS'::character varying, 'INVESTMENT'::character varying, 'SUPPORT'::character varying, 'GIFT'::character varying, 'SHARED_EXPERIENCE_COST'::character varying]::text[])", name='chk_personal_money_event_type'),
        CheckConstraint('roi_signal_score IS NULL OR roi_signal_score >= 0::numeric AND roi_signal_score <= 100::numeric', name='chk_personal_money_roi_score'),
        ForeignKeyConstraint(['account_id'], ['personal_accounts.account_id'], name='personal_money_events_account_id_fkey'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_money_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_money_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('money_event_id', name='personal_money_events_pkey'),
        Index('idx_personal_money_events_account', 'account_id'),
        Index('idx_personal_money_events_date', 'event_date'),
        Index('idx_personal_money_events_moment', 'moment_id'),
        Index('idx_personal_money_events_quick_add', 'quick_add_event_id'),
        Index('idx_personal_money_events_type', 'moment_type_code', 'money_event_type'),
        Index('idx_personal_money_events_user', 'user_id')
    )

    money_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    source_event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    linked_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    money_event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False, server_default=text("''"))
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text('0'))
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    exchange_rate_to_user_currency: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 8))
    amount_user_currency_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    category_code: Mapped[str] = mapped_column(String(80), nullable=False)
    subcategory_code: Mapped[Optional[str]] = mapped_column(String(80))
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    impact_label: Mapped[Optional[str]] = mapped_column(String(80))
    value_received_label: Mapped[Optional[str]] = mapped_column(String(80))
    financial_pressure_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    investment_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    roi_signal_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    account: Mapped[Optional['PersonalAccounts']] = relationship('PersonalAccounts', back_populates='personal_money_events')
    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_money_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_money_events')


class PersonalNotificationQueue(Base):
    __tablename__ = 'personal_notification_queue'
    __table_args__ = (
        CheckConstraint("moment_type_code IS NULL OR (moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[]))", name='personal_notification_queue_moment_type_code_check'),
        CheckConstraint("priority_level::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying]::text[])", name='personal_notification_queue_priority_level_check'),
        CheckConstraint("status::text = ANY (ARRAY['QUEUED'::character varying, 'SENT'::character varying, 'FAILED'::character varying, 'CANCELLED'::character varying]::text[])", name='personal_notification_queue_status_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_notification_queue_moment_id_fkey'),
        PrimaryKeyConstraint('notification_id', name='personal_notification_queue_pkey'),
        Index('idx_personal_notification_scheduled', 'scheduled_for', 'status'),
        Index('idx_personal_notification_user_status', 'user_id', 'status')
    )

    notification_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    priority_level: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'MEDIUM'::character varying"))
    scheduled_for: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'QUEUED'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    moment_type_code: Mapped[Optional[str]] = mapped_column(String(50))
    deep_link_target: Mapped[Optional[str]] = mapped_column(String(150))
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped[Optional['PersonalMoments']] = relationship('PersonalMoments', back_populates='personal_notification_queue')


class PersonalPulseSnapshots(Base):
    __tablename__ = 'personal_pulse_snapshots'
    __table_args__ = (
        CheckConstraint("moment_type_code IS NULL OR (moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[]))", name='personal_pulse_snapshots_moment_type_code_check'),
        CheckConstraint('primary_metric_value >= 0::numeric AND primary_metric_value <= 100::numeric', name='personal_pulse_snapshots_primary_metric_value_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_pulse_snapshots_moment_id_fkey'),
        PrimaryKeyConstraint('pulse_snapshot_id', name='personal_pulse_snapshots_pkey'),
        Index('idx_pulse_snapshots_moment', 'moment_id'),
        Index('idx_pulse_snapshots_user_date', 'user_id', 'snapshot_date')
    )

    pulse_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    pulse_title: Mapped[str] = mapped_column(String(150), nullable=False)
    primary_metric_label: Mapped[str] = mapped_column(String(100), nullable=False)
    primary_metric_value: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    moment_type_code: Mapped[Optional[str]] = mapped_column(String(50))
    pulse_summary: Mapped[Optional[str]] = mapped_column(Text)
    secondary_metrics: Mapped[Optional[dict]] = mapped_column(JSONB)
    emerging_signal_label: Mapped[Optional[str]] = mapped_column(String(150))
    opportunity_label: Mapped[Optional[str]] = mapped_column(String(150))

    moment: Mapped[Optional['PersonalMoments']] = relationship('PersonalMoments', back_populates='personal_pulse_snapshots')


class PersonalQuickAddEvents(Base):
    __tablename__ = 'personal_quick_add_events'
    __table_args__ = (
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='chk_personal_quick_add_moment_type'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_quick_add_events_moment_id_fkey'),
        PrimaryKeyConstraint('quick_add_event_id', name='personal_quick_add_events_pkey'),
        Index('idx_personal_quick_add_events_date', 'event_occurred_at'),
        Index('idx_personal_quick_add_events_moment', 'moment_id'),
        Index('idx_personal_quick_add_events_type', 'moment_type_code'),
        Index('idx_personal_quick_add_events_user', 'user_id')
    )

    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    quick_add_tab_code: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    event_occurred_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    client_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_quick_add_events')
    personal_activity_timeline: Mapped[list['PersonalActivityTimeline']] = relationship('PersonalActivityTimeline', back_populates='quick_add_event')
    personal_event_edits: Mapped[list['PersonalEventEdits']] = relationship('PersonalEventEdits', back_populates='quick_add_event')
    personal_event_voids: Mapped[list['PersonalEventVoids']] = relationship('PersonalEventVoids', back_populates='quick_add_event')
    personal_future_learning_events: Mapped['PersonalFutureLearningEvents'] = relationship('PersonalFutureLearningEvents', uselist=False, back_populates='quick_add_event')
    personal_future_milestone_events: Mapped['PersonalFutureMilestoneEvents'] = relationship('PersonalFutureMilestoneEvents', uselist=False, back_populates='quick_add_event')
    personal_future_opportunity_events: Mapped['PersonalFutureOpportunityEvents'] = relationship('PersonalFutureOpportunityEvents', uselist=False, back_populates='quick_add_event')
    personal_future_pivot_events: Mapped['PersonalFuturePivotEvents'] = relationship('PersonalFuturePivotEvents', uselist=False, back_populates='quick_add_event')
    personal_future_progress_events: Mapped['PersonalFutureProgressEvents'] = relationship('PersonalFutureProgressEvents', uselist=False, back_populates='quick_add_event')
    personal_life_adjust_events: Mapped['PersonalLifeAdjustEvents'] = relationship('PersonalLifeAdjustEvents', uselist=False, back_populates='quick_add_event')
    personal_life_attention_events: Mapped['PersonalLifeAttentionEvents'] = relationship('PersonalLifeAttentionEvents', uselist=False, back_populates='quick_add_event')
    personal_life_mood_events: Mapped['PersonalLifeMoodEvents'] = relationship('PersonalLifeMoodEvents', uselist=False, back_populates='quick_add_event')
    personal_life_recovery_events: Mapped['PersonalLifeRecoveryEvents'] = relationship('PersonalLifeRecoveryEvents', uselist=False, back_populates='quick_add_event')
    personal_lifestyle_adjust_events: Mapped['PersonalLifestyleAdjustEvents'] = relationship('PersonalLifestyleAdjustEvents', uselist=False, back_populates='quick_add_event')
    personal_lifestyle_discovery_events: Mapped['PersonalLifestyleDiscoveryEvents'] = relationship('PersonalLifestyleDiscoveryEvents', uselist=False, back_populates='quick_add_event')
    personal_lifestyle_experience_events: Mapped['PersonalLifestyleExperienceEvents'] = relationship('PersonalLifestyleExperienceEvents', uselist=False, back_populates='quick_add_event')
    personal_lifestyle_expression_events: Mapped['PersonalLifestyleExpressionEvents'] = relationship('PersonalLifestyleExpressionEvents', uselist=False, back_populates='quick_add_event')
    personal_lifestyle_wellbeing_events: Mapped['PersonalLifestyleWellbeingEvents'] = relationship('PersonalLifestyleWellbeingEvents', uselist=False, back_populates='quick_add_event')
    personal_money_events: Mapped[list['PersonalMoneyEvents']] = relationship('PersonalMoneyEvents', back_populates='quick_add_event')
    personal_relationship_adjust_events: Mapped['PersonalRelationshipAdjustEvents'] = relationship('PersonalRelationshipAdjustEvents', uselist=False, back_populates='quick_add_event')
    personal_relationship_connection_events: Mapped['PersonalRelationshipConnectionEvents'] = relationship('PersonalRelationshipConnectionEvents', uselist=False, back_populates='quick_add_event')
    personal_relationship_experience_events: Mapped['PersonalRelationshipExperienceEvents'] = relationship('PersonalRelationshipExperienceEvents', uselist=False, back_populates='quick_add_event')
    personal_relationship_investment_events: Mapped['PersonalRelationshipInvestmentEvents'] = relationship('PersonalRelationshipInvestmentEvents', uselist=False, back_populates='quick_add_event')
    personal_relationship_support_events: Mapped['PersonalRelationshipSupportEvents'] = relationship('PersonalRelationshipSupportEvents', uselist=False, back_populates='quick_add_event')


class PersonalRecommendations(Base):
    __tablename__ = 'personal_recommendations'
    __table_args__ = (
        CheckConstraint('confidence_score >= 0::numeric AND confidence_score <= 100::numeric', name='personal_recommendations_confidence_score_check'),
        CheckConstraint('growth_edge_confidence_pct IS NULL OR growth_edge_confidence_pct >= 0::numeric AND growth_edge_confidence_pct <= 100::numeric', name='chk_personal_growth_edge_confidence'),
        CheckConstraint('growth_edge_multiplier IS NULL OR growth_edge_multiplier >= 0::numeric', name='chk_personal_growth_edge_multiplier'),
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_recommendations_moment_type_code_check'),
        CheckConstraint('priority_score >= 0::numeric AND priority_score <= 100::numeric', name='personal_recommendations_priority_score_check'),
        CheckConstraint("recommendation_scope::text = ANY (ARRAY['MOMENT'::character varying, 'PULSE'::character varying, 'MEMORY'::character varying, 'LIFE'::character varying]::text[])", name='chk_personal_recommendation_scope'),
        CheckConstraint("status::text = ANY (ARRAY['ACTIVE'::character varying, 'DONE'::character varying, 'DISMISSED'::character varying, 'EXPIRED'::character varying]::text[])", name='personal_recommendations_status_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_recommendations_moment_id_fkey'),
        ForeignKeyConstraint(['source_pattern_id'], ['personal_memory_patterns.memory_pattern_id'], name='personal_recommendations_source_pattern_id_fkey'),
        ForeignKeyConstraint(['source_signal_id'], ['personal_signals.signal_id'], name='personal_recommendations_source_signal_id_fkey'),
        PrimaryKeyConstraint('recommendation_id', name='personal_recommendations_pkey'),
        Index('idx_personal_recommendations_life_scope', 'user_id', 'recommendation_scope', postgresql_where="((recommendation_scope)::text = 'LIFE'::text)"),
        Index('idx_personal_recommendations_moment_status', 'moment_id', 'status'),
        Index('idx_personal_recommendations_priority', 'priority_score'),
        Index('idx_personal_recommendations_scope', 'user_id', 'recommendation_scope', 'status'),
        Index('idx_personal_recommendations_user_status', 'user_id', 'status')
    )

    recommendation_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation_title: Mapped[str] = mapped_column(String(150), nullable=False)
    recommendation_description: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(String(200), nullable=False)
    confidence_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    priority_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    recommendation_scope: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'MOMENT'::character varying"))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    moment_type_code: Mapped[Optional[str]] = mapped_column(String(50))
    expected_impact_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    source_signal_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    source_pattern_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    acted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    dismissed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    growth_edge_multiplier: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))
    growth_edge_confidence_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    life_impact_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped[Optional['PersonalMoments']] = relationship('PersonalMoments', back_populates='personal_recommendations')
    source_pattern: Mapped[Optional['PersonalMemoryPatterns']] = relationship('PersonalMemoryPatterns', back_populates='personal_recommendations')
    source_signal: Mapped[Optional['PersonalSignals']] = relationship('PersonalSignals', back_populates='personal_recommendations')


class PersonalRelationshipAdjustEvents(Base):
    __tablename__ = 'personal_relationship_adjust_events'
    __table_args__ = (
        CheckConstraint("adjustment_area::text = ANY (ARRAY['More Time Together'::character varying, 'Better Communication'::character varying, 'More Presence'::character varying, 'More Support'::character varying, 'More Fun'::character varying, 'More Shared Experiences'::character varying, 'More Appreciation'::character varying, 'More Consistency'::character varying]::text[])", name='chk_relationship_adjust_area'),
        CheckConstraint("confidence_level::text = ANY (ARRAY['Not Sure'::character varying, 'Somewhat Sure'::character varying, 'Very Sure'::character varying]::text[])", name='chk_relationship_adjust_confidence'),
        CheckConstraint('connection_gap_score IS NULL OR connection_gap_score >= 0::numeric AND connection_gap_score <= 100::numeric', name='chk_relationship_gap_score'),
        CheckConstraint("desired_outcome IS NULL OR (desired_outcome::text = ANY (ARRAY['Closer'::character varying, 'More Trust'::character varying, 'More Support'::character varying, 'More Fun'::character varying, 'More Consistency'::character varying, 'Better Communication'::character varying]::text[]))", name='chk_relationship_desired_outcome'),
        CheckConstraint("priority_level::text = ANY (ARRAY['Low'::character varying, 'Medium'::character varying, 'High'::character varying]::text[])", name='chk_relationship_adjust_priority'),
        CheckConstraint("relationship_focus::text = ANY (ARRAY['Partner'::character varying, 'Family'::character varying, 'Friend'::character varying, 'Parent'::character varying, 'Child'::character varying]::text[])", name='chk_relationship_adjust_focus'),
        CheckConstraint('relationship_readiness_score IS NULL OR relationship_readiness_score >= 0::numeric AND relationship_readiness_score <= 100::numeric', name='chk_relationship_readiness_score'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_relationship_adjust_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_relationship_adjust_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('relationship_adjust_event_id', name='personal_relationship_adjust_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_relationship_adjust_events_quick_add_event_id_key'),
        Index('idx_relationship_adjust_date', 'event_date'),
        Index('idx_relationship_adjust_moment', 'moment_id'),
        Index('idx_relationship_adjust_user', 'user_id')
    )

    relationship_adjust_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    relationship_focus: Mapped[str] = mapped_column(String(80), nullable=False)
    adjustment_area: Mapped[str] = mapped_column(String(100), nullable=False)
    priority_level: Mapped[str] = mapped_column(String(30), nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(30), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    desired_outcome: Mapped[Optional[str]] = mapped_column(String(100))
    note: Mapped[Optional[str]] = mapped_column(Text)
    connection_gap_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    relationship_readiness_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    recommended_connection_action: Mapped[Optional[str]] = mapped_column(String(150))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_relationship_adjust_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_relationship_adjust_events')


class PersonalRelationshipConnectionEvents(Base):
    __tablename__ = 'personal_relationship_connection_events'
    __table_args__ = (
        CheckConstraint("connection_quality::text = ANY (ARRAY['Routine'::character varying, 'Meaningful'::character varying, 'Deep'::character varying, 'Memorable'::character varying]::text[])", name='chk_relationship_connection_quality'),
        CheckConstraint('connection_score_delta IS NULL OR connection_score_delta >= 0::numeric AND connection_score_delta <= 100::numeric', name='chk_relationship_connection_score'),
        CheckConstraint("connection_type::text = ANY (ARRAY['Conversation'::character varying, 'Call'::character varying, 'Message'::character varying, 'Visit'::character varying, 'Shared Time'::character varying, 'Meal Together'::character varying, 'Celebration'::character varying, 'Check-In'::character varying, 'Other'::character varying]::text[])", name='chk_relationship_connection_type'),
        CheckConstraint("emotional_tone IS NULL OR (emotional_tone::text = ANY (ARRAY['Positive'::character varying, 'Neutral'::character varying, 'Difficult'::character varying, 'Supportive'::character varying, 'Celebratory'::character varying]::text[]))", name='chk_relationship_emotional_tone'),
        CheckConstraint("relationship_type::text = ANY (ARRAY['Partner'::character varying, 'Family'::character varying, 'Friend'::character varying, 'Parent'::character varying, 'Child'::character varying, 'Mentor'::character varying, 'Professional'::character varying, 'Community'::character varying]::text[])", name='chk_relationship_connection_relationship_type'),
        CheckConstraint("time_invested_bucket IS NULL OR (time_invested_bucket::text = ANY (ARRAY['<15'::character varying, '15_30'::character varying, '30_60'::character varying, '1_2_HOURS'::character varying, '2_PLUS_HOURS'::character varying]::text[]))", name='chk_relationship_connection_time'),
        CheckConstraint("trust_score_delta IS NULL OR trust_score_delta >= '-100'::integer::numeric AND trust_score_delta <= 100::numeric", name='chk_relationship_trust_score'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_relationship_connection_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_relationship_connection_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('connection_event_id', name='personal_relationship_connection_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_relationship_connection_events_quick_add_event_id_key'),
        Index('idx_relationship_connection_date', 'event_date'),
        Index('idx_relationship_connection_moment', 'moment_id'),
        Index('idx_relationship_connection_user', 'user_id')
    )

    connection_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    connection_type: Mapped[str] = mapped_column(String(80), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(80), nullable=False)
    connection_quality: Mapped[str] = mapped_column(String(50), nullable=False)
    presence_signal_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    emotional_tone: Mapped[Optional[str]] = mapped_column(String(50))
    time_invested_bucket: Mapped[Optional[str]] = mapped_column(String(30))
    note: Mapped[Optional[str]] = mapped_column(Text)
    connection_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    trust_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_relationship_connection_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_relationship_connection_events')


class PersonalRelationshipExperienceEvents(Base):
    __tablename__ = 'personal_relationship_experience_events'
    __table_args__ = (
        CheckConstraint('connection_score_delta IS NULL OR connection_score_delta >= 0::numeric AND connection_score_delta <= 100::numeric', name='chk_relationship_experience_connection_score'),
        CheckConstraint('cost_amount IS NULL OR cost_amount >= 0::numeric', name='chk_relationship_experience_cost'),
        CheckConstraint("experience_type::text = ANY (ARRAY['Dining'::character varying, 'Travel'::character varying, 'Celebration'::character varying, 'Entertainment'::character varying, 'Activity'::character varying, 'Learning'::character varying, 'Family Event'::character varying, 'Milestone'::character varying, 'Other'::character varying]::text[])", name='chk_relationship_experience_type'),
        CheckConstraint('relationship_roi_score IS NULL OR relationship_roi_score >= 0::numeric AND relationship_roi_score <= 100::numeric', name='chk_relationship_experience_roi_score'),
        CheckConstraint("relationship_type::text = ANY (ARRAY['Partner'::character varying, 'Family'::character varying, 'Friend'::character varying, 'Child'::character varying, 'Parent'::character varying, 'Group'::character varying]::text[])", name='chk_relationship_experience_relationship_type'),
        CheckConstraint("spend_category IS NULL OR (spend_category::text = ANY (ARRAY['Dining'::character varying, 'Travel'::character varying, 'Gift'::character varying, 'Event'::character varying, 'Support'::character varying, 'Experience'::character varying, 'Other'::character varying]::text[]))", name='chk_relationship_experience_spend_category'),
        CheckConstraint("value_received::text = ANY (ARRAY['Okay'::character varying, 'Worth It'::character varying, 'Excellent Value'::character varying, 'Relationship Building'::character varying, 'Life Enriching'::character varying]::text[])", name='chk_relationship_experience_value'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_relationship_experience_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_relationship_experience_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('relationship_experience_event_id', name='personal_relationship_experience_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_relationship_experience_events_quick_add_event_id_key'),
        Index('idx_relationship_experience_date', 'event_date'),
        Index('idx_relationship_experience_moment', 'moment_id'),
        Index('idx_relationship_experience_user', 'user_id')
    )

    relationship_experience_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    experience_type: Mapped[str] = mapped_column(String(80), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(80), nullable=False)
    value_received: Mapped[str] = mapped_column(String(80), nullable=False)
    meaningful_moment_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    cost_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))
    spend_category: Mapped[Optional[str]] = mapped_column(String(80))
    note: Mapped[Optional[str]] = mapped_column(Text)
    connection_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    relationship_roi_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_relationship_experience_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_relationship_experience_events')


class PersonalRelationshipInvestmentEvents(Base):
    __tablename__ = 'personal_relationship_investment_events'
    __table_args__ = (
        CheckConstraint('amount >= 0::numeric', name='chk_relationship_investment_amount'),
        CheckConstraint('connection_roi_score IS NULL OR connection_roi_score >= 0::numeric AND connection_roi_score <= 100::numeric', name='chk_relationship_connection_roi_score'),
        CheckConstraint("investment_purpose::text = ANY (ARRAY['Care'::character varying, 'Growth'::character varying, 'Support'::character varying, 'Celebration'::character varying, 'Responsibility'::character varying, 'Shared Future'::character varying]::text[])", name='chk_relationship_investment_purpose'),
        CheckConstraint('investment_score_delta IS NULL OR investment_score_delta >= 0::numeric AND investment_score_delta <= 100::numeric', name='chk_relationship_investment_score'),
        CheckConstraint("investment_type::text = ANY (ARRAY['Gift'::character varying, 'Support'::character varying, 'Education'::character varying, 'Travel'::character varying, 'Celebration'::character varying, 'Shared Goal'::character varying, 'Family Expense'::character varying, 'Contribution'::character varying, 'Other'::character varying]::text[])", name='chk_relationship_investment_type'),
        CheckConstraint("perceived_value::text = ANY (ARRAY['Low'::character varying, 'Moderate'::character varying, 'High'::character varying, 'Exceptional'::character varying]::text[])", name='chk_relationship_investment_perceived_value'),
        CheckConstraint("relationship_type::text = ANY (ARRAY['Partner'::character varying, 'Family'::character varying, 'Friend'::character varying, 'Child'::character varying, 'Parent'::character varying, 'Group'::character varying]::text[])", name='chk_relationship_investment_relationship_type'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_relationship_investment_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_relationship_investment_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('investment_event_id', name='personal_relationship_investment_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_relationship_investment_events_quick_add_event_id_key'),
        Index('idx_relationship_investment_date', 'event_date'),
        Index('idx_relationship_investment_moment', 'moment_id'),
        Index('idx_relationship_investment_user', 'user_id')
    )

    investment_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    investment_type: Mapped[str] = mapped_column(String(80), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(80), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    investment_purpose: Mapped[str] = mapped_column(String(80), nullable=False)
    perceived_value: Mapped[str] = mapped_column(String(50), nullable=False)
    financial_support_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    note: Mapped[Optional[str]] = mapped_column(Text)
    investment_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    connection_roi_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_relationship_investment_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_relationship_investment_events')


class PersonalRelationshipSupportEvents(Base):
    __tablename__ = 'personal_relationship_support_events'
    __table_args__ = (
        CheckConstraint("impact_level::text = ANY (ARRAY['Small'::character varying, 'Meaningful'::character varying, 'Important'::character varying, 'Transformational'::character varying]::text[])", name='chk_relationship_support_impact'),
        CheckConstraint("relationship_type::text = ANY (ARRAY['Partner'::character varying, 'Family'::character varying, 'Friend'::character varying, 'Parent'::character varying, 'Child'::character varying, 'Mentor'::character varying, 'Professional'::character varying, 'Community'::character varying]::text[])", name='chk_relationship_support_relationship_type'),
        CheckConstraint('resilience_score_delta IS NULL OR resilience_score_delta >= 0::numeric AND resilience_score_delta <= 100::numeric', name='chk_relationship_resilience_score'),
        CheckConstraint("support_balance_side IS NULL OR (support_balance_side::text = ANY (ARRAY['GIVEN'::character varying, 'RECEIVED'::character varying, 'MUTUAL'::character varying]::text[]))", name='chk_relationship_support_balance_side'),
        CheckConstraint("support_direction::text = ANY (ARRAY['Given'::character varying, 'Received'::character varying, 'Mutual'::character varying]::text[])", name='chk_relationship_support_direction'),
        CheckConstraint('support_score_delta IS NULL OR support_score_delta >= 0::numeric AND support_score_delta <= 100::numeric', name='chk_relationship_support_score'),
        CheckConstraint("support_type::text = ANY (ARRAY['Emotional'::character varying, 'Practical'::character varying, 'Financial'::character varying, 'Advice'::character varying, 'Encouragement'::character varying, 'Care'::character varying, 'Celebration'::character varying, 'Other'::character varying]::text[])", name='chk_relationship_support_type'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], name='personal_relationship_support_events_moment_id_fkey'),
        ForeignKeyConstraint(['quick_add_event_id'], ['personal_quick_add_events.quick_add_event_id'], ondelete='CASCADE', name='personal_relationship_support_events_quick_add_event_id_fkey'),
        PrimaryKeyConstraint('support_event_id', name='personal_relationship_support_events_pkey'),
        UniqueConstraint('quick_add_event_id', name='personal_relationship_support_events_quick_add_event_id_key'),
        Index('idx_relationship_support_date', 'event_date'),
        Index('idx_relationship_support_moment', 'moment_id'),
        Index('idx_relationship_support_user', 'user_id')
    )

    support_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    quick_add_event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    support_type: Mapped[str] = mapped_column(String(80), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(80), nullable=False)
    support_direction: Mapped[str] = mapped_column(String(30), nullable=False)
    impact_level: Mapped[str] = mapped_column(String(50), nullable=False)
    event_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    note: Mapped[Optional[str]] = mapped_column(Text)
    support_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    resilience_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    support_balance_side: Mapped[Optional[str]] = mapped_column(String(30))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_relationship_support_events')
    quick_add_event: Mapped['PersonalQuickAddEvents'] = relationship('PersonalQuickAddEvents', back_populates='personal_relationship_support_events')


class PersonalRelationshipsProfile(Base):
    __tablename__ = 'personal_relationships_profile'
    __table_args__ = (
        CheckConstraint('array_length(desired_connection_types, 1) >= 1', name='chk_relationship_desired_connection_not_empty'),
        CheckConstraint('array_length(neglected_relationship_areas, 1) >= 1', name='chk_relationship_neglected_areas_not_empty'),
        CheckConstraint('array_length(relationship_investment_areas, 1) >= 1', name='chk_relationship_investment_areas_not_empty'),
        CheckConstraint('array_length(relationship_strength_factors, 1) >= 1', name='chk_relationship_strength_factors_not_empty'),
        CheckConstraint("relationship_potential IS NULL OR (relationship_potential::text = ANY (ARRAY['LOW'::character varying, 'MODERATE'::character varying, 'HIGH'::character varying]::text[]))", name='chk_relationship_potential'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_relationships_profile_moment_id_fkey'),
        PrimaryKeyConstraint('relationship_profile_id', name='personal_relationships_profile_pkey'),
        Index('idx_relationships_profile_moment', 'moment_id'),
        Index('idx_relationships_profile_user', 'user_id')
    )

    relationship_profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    relationship_focus: Mapped[str] = mapped_column(String(80), nullable=False)
    current_relationship_state: Mapped[str] = mapped_column(String(50), nullable=False)
    desired_connection_types: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    neglected_relationship_areas: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    relationship_strength_factors: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    relationship_investment_areas: Mapped[list[str]] = mapped_column(ARRAY(Text()), nullable=False)
    relationship_identity: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship_energy: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    primary_relationship_gap: Mapped[Optional[str]] = mapped_column(String(100))
    primary_relationship_opportunity: Mapped[Optional[str]] = mapped_column(String(150))
    relationship_potential: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_relationships_profile')


class PersonalRuntimeSnapshots(Base):
    __tablename__ = 'personal_runtime_snapshots'
    __table_args__ = (
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_runtime_snapshots_moment_type_code_check'),
        CheckConstraint('primary_score >= 0::numeric AND primary_score <= 100::numeric', name='personal_runtime_snapshots_primary_score_check'),
        CheckConstraint('secondary_score IS NULL OR secondary_score >= 0::numeric AND secondary_score <= 100::numeric', name='personal_runtime_snapshots_secondary_score_check'),
        CheckConstraint("trend_direction::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[])", name='personal_runtime_snapshots_trend_direction_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_runtime_snapshots_moment_id_fkey'),
        PrimaryKeyConstraint('runtime_snapshot_id', name='personal_runtime_snapshots_pkey'),
        Index('idx_runtime_snapshots_moment_date', 'moment_id', 'snapshot_date')
    )

    runtime_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    runtime_state_label: Mapped[str] = mapped_column(String(120), nullable=False)
    primary_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    trend_direction: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'STABLE'::character varying"))
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    runtime_summary: Mapped[Optional[str]] = mapped_column(Text)
    secondary_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    risk_or_gap_label: Mapped[Optional[str]] = mapped_column(String(150))

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_runtime_snapshots')


class PersonalSignals(Base):
    __tablename__ = 'personal_signals'
    __table_args__ = (
        CheckConstraint("moment_type_code::text = ANY (ARRAY['LIFE_OPERATIONS'::character varying, 'FUTURE_BUILDING'::character varying, 'LIFESTYLE'::character varying, 'RELATIONSHIPS'::character varying]::text[])", name='personal_signals_moment_type_code_check'),
        CheckConstraint("severity_level::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'POSITIVE'::character varying, 'WARNING'::character varying]::text[])", name='personal_signals_severity_level_check'),
        CheckConstraint('signal_score >= 0::numeric AND signal_score <= 100::numeric', name='personal_signals_signal_score_check'),
        CheckConstraint("signal_window::text = ANY (ARRAY['7D'::character varying, '14D'::character varying, '30D'::character varying, '90D'::character varying]::text[])", name='personal_signals_signal_window_check'),
        CheckConstraint('source_event_count >= 0', name='personal_signals_source_event_count_check'),
        CheckConstraint("trend_direction IS NULL OR (trend_direction::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying]::text[]))", name='personal_signals_trend_direction_check'),
        ForeignKeyConstraint(['moment_id'], ['personal_moments.moment_id'], ondelete='CASCADE', name='personal_signals_moment_id_fkey'),
        PrimaryKeyConstraint('signal_id', name='personal_signals_pkey'),
        Index('idx_personal_signals_moment_active', 'moment_id', 'is_active'),
        Index('idx_personal_signals_type', 'moment_type_code', 'signal_type'),
        Index('idx_personal_signals_user_active', 'user_id', 'is_active')
    )

    signal_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_title: Mapped[str] = mapped_column(String(150), nullable=False)
    signal_description: Mapped[str] = mapped_column(Text, nullable=False)
    signal_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    severity_level: Mapped[str] = mapped_column(String(30), nullable=False)
    source_event_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    signal_window: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'30D'::character varying"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    trend_direction: Mapped[Optional[str]] = mapped_column(String(30))
    source_metric_code: Mapped[Optional[str]] = mapped_column(String(100))
    source_metric_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))
    source_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['PersonalMoments'] = relationship('PersonalMoments', back_populates='personal_signals')
    personal_recommendations: Mapped[list['PersonalRecommendations']] = relationship('PersonalRecommendations', back_populates='source_signal')


class PersonalUserPreferences(Base):
    __tablename__ = 'personal_user_preferences'
    __table_args__ = (
        CheckConstraint("week_start_day::text = ANY (ARRAY['MONDAY'::character varying, 'SUNDAY'::character varying]::text[])", name='personal_user_preferences_week_start_day_check'),
        ForeignKeyConstraint(['default_account_id'], ['personal_accounts.account_id'], name='personal_user_preferences_default_account_id_fkey'),
        PrimaryKeyConstraint('preference_id', name='personal_user_preferences_pkey'),
        UniqueConstraint('user_id', name='personal_user_preferences_user_id_key'),
        Index('idx_personal_user_preferences_user', 'user_id')
    )

    preference_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    default_currency_code: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    timezone_name: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("'Asia/Kolkata'::character varying"))
    notification_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    quick_add_reminder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    daily_summary_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    privacy_mode_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    week_start_day: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'MONDAY'::character varying"))
    default_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    preferred_summary_time: Mapped[Optional[datetime.time]] = mapped_column(Time)

    default_account: Mapped[Optional['PersonalAccounts']] = relationship('PersonalAccounts', back_populates='personal_user_preferences')
