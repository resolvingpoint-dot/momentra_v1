"""Life360 / shared-experience domain SQLAlchemy models (shared_*, life360_snapshots, community/budget/experience/ai reference tables).

Auto-generated from the Alembic migrations via reflection.
"""
from __future__ import annotations

from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.users.models import Base


class AiSignals(Base):
    __tablename__ = 'ai_signals'
    __table_args__ = (
        CheckConstraint("severity::text = ANY (ARRAY['info'::character varying, 'low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])", name='chk_ai_signal_severity'),
        CheckConstraint("signal_status::text = ANY (ARRAY['active'::character varying, 'dismissed'::character varying, 'resolved'::character varying, 'expired'::character varying, 'archived'::character varying]::text[])", name='chk_ai_signal_status'),
        CheckConstraint("target_screen IS NULL OR (target_screen::text = ANY (ARRAY['pulse'::character varying, 'moments'::character varying, 'live'::character varying, 'memory'::character varying, 'quick_add'::character varying]::text[]))", name='chk_ai_signal_target_screen'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_ai_signal_moment'),
        PrimaryKeyConstraint('signal_id', name='ai_signals_pkey'),
        Index('idx_ai_signals_generated', 'generated_at'),
        Index('idx_ai_signals_moment', 'moment_id'),
        Index('idx_ai_signals_status', 'signal_status'),
        Index('idx_ai_signals_type', 'signal_type')
    )

    signal_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    signal_scope: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'team_operations'::character varying"))
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_title: Mapped[str] = mapped_column(String(255), nullable=False)
    signal_message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'info'::character varying"))
    signal_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'active'::character varying"))
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    source_table: Mapped[Optional[str]] = mapped_column(String(100))
    source_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    recommended_action: Mapped[Optional[str]] = mapped_column(Text)
    target_screen: Mapped[Optional[str]] = mapped_column(String(50))
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='ai_signals')


class BudgetMasterCategories(Base):
    __tablename__ = 'budget_master_categories'
    __table_args__ = (
        PrimaryKeyConstraint('category_id', name='budget_master_categories_pkey'),
        UniqueConstraint('category_code', name='budget_master_categories_category_code_key')
    )

    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    category_code: Mapped[str] = mapped_column(String(100), nullable=False)
    category_name: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    icon_name: Mapped[Optional[str]] = mapped_column(String(100))

    experience_budget_templates: Mapped[list['ExperienceBudgetTemplates']] = relationship('ExperienceBudgetTemplates', back_populates='category')
    shared_experience_budget_allocations: Mapped[list['SharedExperienceBudgetAllocations']] = relationship('SharedExperienceBudgetAllocations', back_populates='category')


class CommunityCoordinationDetails(Base):
    __tablename__ = 'community_coordination_details'
    __table_args__ = (
        CheckConstraint("community_status::text = ANY (ARRAY['DRAFT'::character varying, 'ACTIVE'::character varying, 'COORDINATING'::character varying, 'CLOSED'::character varying]::text[])", name='chk_ccd_status'),
        CheckConstraint("coordination_mode IS NULL OR (coordination_mode::text = ANY (ARRAY['VOTING'::character varying, 'ADMIN_APPROVAL'::character varying, 'CONSENSUS'::character varying, 'MIXED'::character varying]::text[]))", name='chk_ccd_mode'),
        CheckConstraint('member_base_count IS NULL OR member_base_count >= 0', name='chk_ccd_member_count'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_ccd_moment'),
        ForeignKeyConstraint(['primary_owner_id'], ['group_moment_members.member_id'], name='fk_ccd_owner'),
        PrimaryKeyConstraint('community_id', name='community_coordination_details_pkey')
    )

    community_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    community_type: Mapped[str] = mapped_column(String(100), nullable=False)
    community_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DRAFT'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    member_base_count: Mapped[Optional[int]] = mapped_column(Integer)
    coordination_mode: Mapped[Optional[str]] = mapped_column(String(50))
    primary_owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='community_coordination_details')
    primary_owner: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', back_populates='community_coordination_details')


class ExperienceBudgetTemplates(Base):
    __tablename__ = 'experience_budget_templates'
    __table_args__ = (
        CheckConstraint('suggested_percentage >= 0::numeric AND suggested_percentage <= 100::numeric', name='chk_ebt_pct'),
        ForeignKeyConstraint(['category_id'], ['budget_master_categories.category_id'], name='fk_ebt_category'),
        PrimaryKeyConstraint('template_id', name='experience_budget_templates_pkey')
    )

    template_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    experience_subtype: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    suggested_percentage: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    category: Mapped['BudgetMasterCategories'] = relationship('BudgetMasterCategories', back_populates='experience_budget_templates')


class Life360Snapshots(Base):
    __tablename__ = 'life360_snapshots'
    __table_args__ = (
        PrimaryKeyConstraint('life360_snapshot_id', name='life360_snapshots_pkey'),
        UniqueConstraint('user_id', 'snapshot_date', name='uq_life360_user_date')
    )

    life360_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    snapshot_month: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text("(date_trunc('month'::text, (CURRENT_DATE)::timestamp with time zone))::date"))
    life_alignment_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    source_personal_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    source_group_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    source_business_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    personal_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    group_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    business_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    life_phase: Mapped[Optional[str]] = mapped_column(String(50))
    money_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    relationship_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    execution_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    growth_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    personal_energy_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    group_energy_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    business_energy_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    momentum_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2))
    momentum_status: Mapped[Optional[str]] = mapped_column(String(30))
    strongest_driver: Mapped[Optional[str]] = mapped_column(String(100))
    biggest_tension: Mapped[Optional[str]] = mapped_column(String(100))
    money_status: Mapped[Optional[str]] = mapped_column(String(40))
    relationship_status: Mapped[Optional[str]] = mapped_column(String(40))
    execution_status: Mapped[Optional[str]] = mapped_column(String(40))
    growth_status: Mapped[Optional[str]] = mapped_column(String(40))
    reflection_summary: Mapped[Optional[str]] = mapped_column(Text)
    active_dimensions_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    signal_confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class SharedExperienceBudgetAllocations(Base):
    __tablename__ = 'shared_experience_budget_allocations'
    __table_args__ = (
        CheckConstraint('COALESCE(recommended_amount, 0::numeric) >= 0::numeric AND final_amount >= 0::numeric AND actual_amount >= 0::numeric', name='chk_seba_amounts'),
        CheckConstraint('recommended_percentage IS NULL OR recommended_percentage >= 0::numeric AND recommended_percentage <= 100::numeric) AND (final_percentage IS NULL OR final_percentage >= 0::numeric AND final_percentage <= 100::numeric', name='chk_seba_pct'),
        ForeignKeyConstraint(['budget_plan_id'], ['shared_experience_budget_plans.budget_plan_id'], name='fk_seba_plan'),
        ForeignKeyConstraint(['category_id'], ['budget_master_categories.category_id'], name='fk_seba_category'),
        PrimaryKeyConstraint('allocation_id', name='shared_experience_budget_allocations_pkey')
    )

    allocation_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    budget_plan_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    final_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    actual_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    variance_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    recommended_percentage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    recommended_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))
    final_percentage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    budget_plan: Mapped['SharedExperienceBudgetPlans'] = relationship('SharedExperienceBudgetPlans', back_populates='shared_experience_budget_allocations')
    category: Mapped['BudgetMasterCategories'] = relationship('BudgetMasterCategories', back_populates='shared_experience_budget_allocations')


class SharedExperienceBudgetPlans(Base):
    __tablename__ = 'shared_experience_budget_plans'
    __table_args__ = (
        CheckConstraint('funding_readiness_pct >= 0::numeric AND funding_readiness_pct <= 100::numeric', name='chk_sebp_readiness'),
        CheckConstraint('participant_count >= 1', name='chk_sebp_participants'),
        CheckConstraint('planned_total_budget > 0::numeric AND final_total_budget >= 0::numeric', name='chk_sebp_budget'),
        CheckConstraint("split_method::text = ANY (ARRAY['EQUAL_SPLIT'::character varying, 'CUSTOM_SPLIT'::character varying, 'ORGANIZER_PAYS'::character varying, 'SPONSOR_SUPPORTED'::character varying, 'CONTRIBUTION_BASED'::character varying]::text[])", name='chk_sebp_split_method'),
        CheckConstraint("status::text = ANY (ARRAY['DRAFT'::character varying, 'ACTIVE'::character varying, 'LOCKED'::character varying, 'COMPLETED'::character varying, 'CANCELLED'::character varying]::text[])", name='chk_sebp_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_sebp_moment'),
        PrimaryKeyConstraint('budget_plan_id', name='shared_experience_budget_plans_pkey')
    )

    budget_plan_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    planned_total_budget: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    final_total_budget: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    participant_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))
    split_method: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'EQUAL_SPLIT'::character varying"))
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DRAFT'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    funding_readiness_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2), server_default=text('0'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_experience_budget_plans')
    shared_experience_budget_allocations: Mapped[list['SharedExperienceBudgetAllocations']] = relationship('SharedExperienceBudgetAllocations', back_populates='budget_plan')
    shared_experience_budget_splits: Mapped[list['SharedExperienceBudgetSplits']] = relationship('SharedExperienceBudgetSplits', back_populates='budget_plan')


class SharedExperienceBudgetSplits(Base):
    __tablename__ = 'shared_experience_budget_splits'
    __table_args__ = (
        CheckConstraint('planned_share_amount >= 0::numeric AND committed_amount >= 0::numeric AND paid_amount >= 0::numeric AND pending_amount >= 0::numeric', name='chk_sebs_amounts'),
        CheckConstraint("split_status::text = ANY (ARRAY['PENDING'::character varying, 'COMMITTED'::character varying, 'PAID'::character varying, 'OVERDUE'::character varying, 'WAIVED'::character varying]::text[])", name='chk_sebs_status'),
        ForeignKeyConstraint(['budget_plan_id'], ['shared_experience_budget_plans.budget_plan_id'], name='fk_sebs_plan'),
        ForeignKeyConstraint(['member_id'], ['group_moment_members.member_id'], name='fk_sebs_member'),
        PrimaryKeyConstraint('split_id', name='shared_experience_budget_splits_pkey')
    )

    split_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    budget_plan_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    planned_share_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    committed_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    paid_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    pending_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 2), nullable=False, server_default=text('0'))
    split_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'PENDING'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    budget_plan: Mapped['SharedExperienceBudgetPlans'] = relationship('SharedExperienceBudgetPlans', back_populates='shared_experience_budget_splits')
    member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='shared_experience_budget_splits')


class SharedExperienceDetails(Base):
    __tablename__ = 'shared_experience_details'
    __table_args__ = (
        CheckConstraint('expected_participants IS NULL OR expected_participants >= 1', name='chk_sed_expected_participants'),
        CheckConstraint("money_tracking_mode::text = ANY (ARRAY['NO_MONEY'::character varying, 'SHARED_EXPENSES'::character varying, 'CONTRIBUTIONS_AND_EXPENSES'::character varying]::text[])", name='chk_sed_money_mode'),
        CheckConstraint("planning_style::text = ANY (ARRAY['SIMPLE'::character varying, 'STRUCTURED'::character varying, 'FULLY_MANAGED'::character varying]::text[])", name='chk_sed_planning_style'),
        CheckConstraint('start_date IS NULL OR end_date IS NULL OR start_date <= end_date', name='chk_sed_dates'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_sed_moment'),
        PrimaryKeyConstraint('experience_detail_id', name='shared_experience_details_pkey'),
        Index('idx_sed_budget_enabled', 'budget_enabled'),
        Index('idx_sed_default_budget_plan', 'default_budget_plan_id'),
        Index('idx_shared_experience_details_moment', 'moment_id'),
        Index('idx_shared_experience_details_profile', 'experience_profile')
    )

    experience_detail_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    experience_profile: Mapped[str] = mapped_column(String(100), nullable=False)
    planning_style: Mapped[str] = mapped_column(String(50), nullable=False)
    money_tracking_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    budget_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    location: Mapped[Optional[str]] = mapped_column(String(250))
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    expected_participants: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    default_budget_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_experience_details')


class SharedExperienceMemoryHighlights(Base):
    __tablename__ = 'shared_experience_memory_highlights'
    __table_args__ = (
        CheckConstraint('importance_score >= 0::numeric AND importance_score <= 100::numeric', name='chk_semh_importance'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_semh_moment'),
        ForeignKeyConstraint(['source_event_id'], ['group_quick_add_events.event_id'], name='fk_semh_source_event'),
        PrimaryKeyConstraint('highlight_id', name='shared_experience_memory_highlights_pkey'),
        Index('idx_se_memory_highlights_moment', 'moment_id'),
        Index('idx_se_memory_highlights_score', 'importance_score'),
        Index('idx_se_memory_highlights_type', 'highlight_type')
    )

    highlight_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    highlight_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    importance_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('50'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_experience_memory_highlights')
    source_event: Mapped[Optional['GroupQuickAddEvents']] = relationship('GroupQuickAddEvents', back_populates='shared_experience_memory_highlights')


class SharedExperiencePlanningItems(Base):
    __tablename__ = 'shared_experience_planning_items'
    __table_args__ = (
        CheckConstraint('actual_cost IS NULL OR actual_cost >= 0::numeric', name='chk_sepi_actual_cost'),
        CheckConstraint('estimated_cost IS NULL OR estimated_cost >= 0::numeric', name='chk_sepi_estimated_cost'),
        CheckConstraint("item_type::text = ANY (ARRAY['PLANNING_ITEM'::character varying, 'BOOKING'::character varying, 'VENDOR'::character varying, 'TASK'::character varying, 'ACTIVITY'::character varying]::text[])", name='chk_sepi_item_type'),
        CheckConstraint("status::text = ANY (ARRAY['PENDING'::character varying, 'IN_PROGRESS'::character varying, 'CONFIRMED'::character varying, 'COMPLETED'::character varying, 'CANCELLED'::character varying]::text[])", name='chk_sepi_status'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_sepi_created_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_sepi_moment'),
        ForeignKeyConstraint(['owner_member_id'], ['group_moment_members.member_id'], name='fk_sepi_owner'),
        PrimaryKeyConstraint('item_id', name='shared_experience_planning_items_pkey'),
        Index('idx_se_planning_items_due_date', 'due_date'),
        Index('idx_se_planning_items_moment', 'moment_id'),
        Index('idx_se_planning_items_status', 'status'),
        Index('idx_se_planning_items_type', 'item_type'),
        Index('idx_sepi_budget_category', 'budget_category_id'),
        Index('idx_sepi_budget_plan', 'budget_plan_id')
    )

    item_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'PENDING'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    estimated_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    actual_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    provider_name: Mapped[Optional[str]] = mapped_column(String(200))
    booking_reference: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    budget_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    budget_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', foreign_keys=[created_by], back_populates='shared_experience_planning_items_created_by')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_experience_planning_items')
    owner_member: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', foreign_keys=[owner_member_id], back_populates='shared_experience_planning_items_owner_member')


class SharedExperienceSettlements(Base):
    __tablename__ = 'shared_experience_settlements'
    __table_args__ = (
        CheckConstraint('payer_member_id <> receiver_member_id', name='chk_ses_not_same_person'),
        CheckConstraint('settlement_amount > 0::numeric', name='chk_ses_amount'),
        CheckConstraint("settlement_status::text = ANY (ARRAY['OPEN'::character varying, 'SETTLED'::character varying, 'WAIVED'::character varying]::text[])", name='chk_ses_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_ses_moment'),
        ForeignKeyConstraint(['payer_member_id'], ['group_moment_members.member_id'], name='fk_ses_payer'),
        ForeignKeyConstraint(['receiver_member_id'], ['group_moment_members.member_id'], name='fk_ses_receiver'),
        PrimaryKeyConstraint('settlement_id', name='shared_experience_settlements_pkey'),
        Index('idx_se_settlements_moment', 'moment_id'),
        Index('idx_se_settlements_payer', 'payer_member_id'),
        Index('idx_se_settlements_receiver', 'receiver_member_id'),
        Index('idx_se_settlements_status', 'settlement_status')
    )

    settlement_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    payer_member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    receiver_member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    settlement_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    settlement_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'OPEN'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    settled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    source_expense_ids_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_experience_settlements')
    payer_member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', foreign_keys=[payer_member_id], back_populates='shared_experience_settlements_payer_member')
    receiver_member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', foreign_keys=[receiver_member_id], back_populates='shared_experience_settlements_receiver_member')


class SharedGoalDetails(Base):
    __tablename__ = 'shared_goal_details'
    __table_args__ = (
        CheckConstraint("goal_status::text = ANY (ARRAY['DRAFT'::character varying, 'ACTIVE'::character varying, 'ACHIEVED'::character varying, 'PAUSED'::character varying, 'CANCELLED'::character varying]::text[])", name='chk_sgd_status'),
        CheckConstraint('progress_pct >= 0::numeric AND progress_pct <= 100::numeric', name='chk_sgd_progress'),
        CheckConstraint('target_amount IS NULL OR target_amount >= 0::numeric', name='chk_sgd_amount'),
        ForeignKeyConstraint(['goal_owner_id'], ['group_moment_members.member_id'], name='fk_sgd_owner'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_sgd_moment'),
        PrimaryKeyConstraint('goal_id', name='shared_goal_details_pkey')
    )

    goal_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    goal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    goal_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DRAFT'::character varying"))
    progress_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    target_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))
    target_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    goal_owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    goal_owner: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', back_populates='shared_goal_details')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_goal_details')


class SharedLivingAssets(Base):
    __tablename__ = 'shared_living_assets'
    __table_args__ = (
        CheckConstraint('estimated_value IS NULL OR estimated_value >= 0::numeric', name='chk_sla_value'),
        CheckConstraint("status::text = ANY (ARRAY['ACTIVE'::character varying, 'RETIRED'::character varying, 'REMOVED'::character varying]::text[])", name='chk_sla_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_sla_moment'),
        ForeignKeyConstraint(['owner_member_id'], ['group_moment_members.member_id'], name='fk_sla_owner'),
        PrimaryKeyConstraint('asset_id', name='shared_living_assets_pkey'),
        Index('idx_living_assets_moment', 'moment_id'),
        Index('idx_living_assets_owner', 'owner_member_id'),
        Index('idx_living_assets_status', 'status')
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_shared_asset: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    purchase_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    estimated_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    location_in_home: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_living_assets')
    owner_member: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', back_populates='shared_living_assets')


class SharedLivingDetails(Base):
    __tablename__ = 'shared_living_details'
    __table_args__ = (
        CheckConstraint('expected_residents IS NULL OR expected_residents >= 1', name='chk_sld_expected_residents'),
        CheckConstraint("management_style::text = ANY (ARRAY['COLLABORATIVE'::character varying, 'SHARED_RESPONSIBILITY'::character varying, 'HOUSEHOLD_LEAD'::character varying, 'FAMILY_MANAGED'::character varying]::text[])", name='chk_sld_management_style'),
        CheckConstraint('monthly_budget IS NULL OR monthly_budget >= 0::numeric', name='chk_sld_budget'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_sld_moment'),
        PrimaryKeyConstraint('living_detail_id', name='shared_living_details_pkey'),
        Index('idx_shared_living_details_moment', 'moment_id'),
        Index('idx_shared_living_details_type', 'living_type')
    )

    living_detail_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    living_type: Mapped[str] = mapped_column(String(100), nullable=False)
    living_name: Mapped[str] = mapped_column(String(200), nullable=False)
    management_style: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    location: Mapped[Optional[str]] = mapped_column(String(250))
    move_in_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    monthly_budget: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    expected_residents: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_living_details')


class SharedLivingHomePersonality(Base):
    __tablename__ = 'shared_living_home_personality'
    __table_args__ = (
        CheckConstraint('confidence_score >= 0::numeric AND confidence_score <= 100::numeric', name='chk_slhp_confidence'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_slhp_moment'),
        PrimaryKeyConstraint('personality_id', name='shared_living_home_personality_pkey'),
        Index('idx_living_home_personality_moment', 'moment_id'),
        Index('idx_living_home_personality_snapshot', 'snapshot_date')
    )

    personality_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    traits_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    primary_trait: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_living_home_personality')


class SharedLivingMaintenance(Base):
    __tablename__ = 'shared_living_maintenance'
    __table_args__ = (
        CheckConstraint('estimated_cost IS NULL OR estimated_cost >= 0::numeric', name='chk_slm_estimated_cost'),
        CheckConstraint("priority::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'URGENT'::character varying]::text[])", name='chk_slm_priority'),
        CheckConstraint("status::text = ANY (ARRAY['REPORTED'::character varying, 'IN_PROGRESS'::character varying, 'FIXED'::character varying]::text[])", name='chk_slm_status'),
        ForeignKeyConstraint(['assigned_to_member_id'], ['group_moment_members.member_id'], name='fk_slm_assigned_to'),
        ForeignKeyConstraint(['linked_expense_id'], ['group_expenses.expense_id'], name='fk_slm_linked_expense'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_slm_moment'),
        ForeignKeyConstraint(['reported_by_member_id'], ['group_moment_members.member_id'], name='fk_slm_reported_by'),
        PrimaryKeyConstraint('maintenance_id', name='shared_living_maintenance_pkey'),
        Index('idx_living_maintenance_moment', 'moment_id'),
        Index('idx_living_maintenance_priority', 'priority'),
        Index('idx_living_maintenance_status', 'status'),
        Index('idx_living_maintenance_target', 'target_resolution_date'),
        Index('idx_slm_linked_expense', 'linked_expense_id')
    )

    maintenance_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    issue_title: Mapped[str] = mapped_column(String(200), nullable=False)
    reported_by_member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    priority: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'MEDIUM'::character varying"))
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'REPORTED'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to_member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    target_resolution_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    fixed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    estimated_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    linked_expense_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    assigned_to_member: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', foreign_keys=[assigned_to_member_id], back_populates='shared_living_maintenance_assigned_to_member')
    linked_expense: Mapped[Optional['GroupExpenses']] = relationship('GroupExpenses', back_populates='shared_living_maintenance')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_living_maintenance')
    reported_by_member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', foreign_keys=[reported_by_member_id], back_populates='shared_living_maintenance_reported_by_member')


class SharedLivingResidentDynamics(Base):
    __tablename__ = 'shared_living_resident_dynamics'
    __table_args__ = (
        CheckConstraint('activity_score >= 0::numeric AND activity_score <= 100::numeric', name='chk_slrd_activity_score'),
        CheckConstraint('contribution_score IS NULL OR contribution_score >= 0::numeric AND contribution_score <= 100::numeric', name='chk_slrd_contribution_score'),
        CheckConstraint('helpfulness_score IS NULL OR helpfulness_score >= 0::numeric AND helpfulness_score <= 100::numeric', name='chk_slrd_helpfulness_score'),
        CheckConstraint('period_end >= period_start', name='chk_slrd_period'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_slrd_moment'),
        ForeignKeyConstraint(['resident_member_id'], ['group_moment_members.member_id'], name='fk_slrd_resident'),
        PrimaryKeyConstraint('dynamics_id', name='shared_living_resident_dynamics_pkey'),
        Index('idx_living_resident_dynamics_moment', 'moment_id'),
        Index('idx_living_resident_dynamics_period', 'period_start', 'period_end'),
        Index('idx_living_resident_dynamics_resident', 'resident_member_id')
    )

    dynamics_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    resident_member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    activity_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    period_start: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    period_end: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    helpfulness_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    contribution_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    summary_label: Mapped[Optional[str]] = mapped_column(String(150))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_living_resident_dynamics')
    resident_member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='shared_living_resident_dynamics')


class SharedLivingResidents(Base):
    __tablename__ = 'shared_living_residents'
    __table_args__ = (
        CheckConstraint('expected_monthly_contribution IS NULL OR expected_monthly_contribution >= 0::numeric', name='chk_slr_expected_contribution'),
        CheckConstraint('move_in_date IS NULL OR move_out_date IS NULL OR move_out_date >= move_in_date', name='chk_slr_move_dates'),
        CheckConstraint("status::text = ANY (ARRAY['INVITED'::character varying, 'ACTIVE'::character varying, 'PENDING'::character varying, 'MOVED_OUT'::character varying]::text[])", name='chk_slr_status'),
        ForeignKeyConstraint(['member_id'], ['group_moment_members.member_id'], name='fk_slr_member'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_slr_moment'),
        PrimaryKeyConstraint('resident_id', name='shared_living_residents_pkey'),
        Index('idx_living_residents_member', 'member_id'),
        Index('idx_living_residents_moment', 'moment_id'),
        Index('idx_living_residents_status', 'status')
    )

    resident_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    resident_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'INVITED'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    move_in_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    move_out_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    expected_monthly_contribution: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='shared_living_residents')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_living_residents')


class SharedLivingRules(Base):
    __tablename__ = 'shared_living_rules'
    __table_args__ = (
        CheckConstraint("applies_to::text = ANY (ARRAY['EVERYONE'::character varying, 'SELECTED_RESIDENTS'::character varying]::text[])", name='chk_slrules_applies_to'),
        CheckConstraint('review_date IS NULL OR review_date >= effective_date', name='chk_slrules_review_date'),
        CheckConstraint("status::text = ANY (ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying]::text[])", name='chk_slrules_status'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_slrules_created_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_slrules_moment'),
        PrimaryKeyConstraint('rule_id', name='shared_living_rules_pkey'),
        Index('idx_living_rules_effective', 'effective_date'),
        Index('idx_living_rules_moment', 'moment_id'),
        Index('idx_living_rules_status', 'status')
    )

    rule_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_title: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_description: Mapped[str] = mapped_column(Text, nullable=False)
    applies_to: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'EVERYONE'::character varying"))
    effective_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    review_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='shared_living_rules')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_living_rules')


class SharedLivingTasks(Base):
    __tablename__ = 'shared_living_tasks'
    __table_args__ = (
        CheckConstraint("frequency::text = ANY (ARRAY['ONE_TIME'::character varying, 'DAILY'::character varying, 'WEEKLY'::character varying, 'MONTHLY'::character varying, 'CUSTOM'::character varying]::text[])", name='chk_slt_frequency'),
        CheckConstraint("priority IS NULL OR (priority::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying]::text[]))", name='chk_slt_priority'),
        CheckConstraint("status::text = ANY (ARRAY['TO_DO'::character varying, 'IN_PROGRESS'::character varying, 'COMPLETED'::character varying, 'OVERDUE'::character varying]::text[])", name='chk_slt_status'),
        ForeignKeyConstraint(['assigned_to_member_id'], ['group_moment_members.member_id'], name='fk_slt_assignee'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_slt_moment'),
        PrimaryKeyConstraint('task_id', name='shared_living_tasks_pkey'),
        Index('idx_living_tasks_assignee', 'assigned_to_member_id'),
        Index('idx_living_tasks_due_date', 'due_date'),
        Index('idx_living_tasks_moment', 'moment_id'),
        Index('idx_living_tasks_status', 'status'),
        Index('idx_slt_next_due_date', 'next_due_date')
    )

    task_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    frequency: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'ONE_TIME'::character varying"))
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'TO_DO'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    assigned_to_member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    priority: Mapped[Optional[str]] = mapped_column(String(30))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    next_due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    assigned_to_member: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', back_populates='shared_living_tasks')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_living_tasks')


class SharedPurchaseContributors(Base):
    __tablename__ = 'shared_purchase_contributors'
    __table_args__ = (
        CheckConstraint('expected_amount IS NULL OR expected_amount >= 0::numeric', name='chk_spc_expected_amount'),
        CheckConstraint("status::text = ANY (ARRAY['INVITED'::character varying, 'ACTIVE'::character varying, 'PAID'::character varying, 'DROPPED'::character varying]::text[])", name='chk_spc_status'),
        ForeignKeyConstraint(['member_id'], ['group_moment_members.member_id'], name='fk_spc_member'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_spc_moment'),
        PrimaryKeyConstraint('contributor_id', name='shared_purchase_contributors_pkey'),
        Index('idx_purchase_contributors_member', 'member_id'),
        Index('idx_purchase_contributors_moment', 'moment_id'),
        Index('idx_purchase_contributors_status', 'status')
    )

    contributor_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    contributor_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'INVITED'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    expected_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    invited_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='shared_purchase_contributors')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_purchase_contributors')


class SharedPurchaseDelivery(Base):
    __tablename__ = 'shared_purchase_delivery'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['PENDING'::character varying, 'COMPLETED'::character varying, 'DELAYED'::character varying]::text[])", name='chk_spdeli_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_spdeli_moment'),
        ForeignKeyConstraint(['proof_attachment_id'], ['group_attachments.attachment_id'], name='fk_spdeli_attachment'),
        ForeignKeyConstraint(['received_by_member_id'], ['group_moment_members.member_id'], name='fk_spdeli_receiver'),
        PrimaryKeyConstraint('delivery_id', name='shared_purchase_delivery_pkey'),
        Index('idx_purchase_delivery_date', 'delivery_date'),
        Index('idx_purchase_delivery_moment', 'moment_id'),
        Index('idx_purchase_delivery_status', 'status')
    )

    delivery_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    delivery_category: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'PENDING'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    delivery_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    received_by_member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    proof_attachment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_purchase_delivery')
    proof_attachment: Mapped[Optional['GroupAttachments']] = relationship('GroupAttachments', back_populates='shared_purchase_delivery')
    received_by_member: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', back_populates='shared_purchase_delivery')


class SharedPurchaseDetails(Base):
    __tablename__ = 'shared_purchase_details'
    __table_args__ = (
        CheckConstraint('expected_contributors IS NULL OR expected_contributors >= 1', name='chk_spd_expected_contributors'),
        CheckConstraint("funding_style::text = ANY (ARRAY['OPEN'::character varying, 'SUGGESTED'::character varying, 'FIXED'::character varying, 'ORGANIZER_MANAGED'::character varying]::text[])", name='chk_spd_funding_style'),
        CheckConstraint('target_amount > 0::numeric', name='chk_spd_target_amount'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_spd_moment'),
        PrimaryKeyConstraint('purchase_detail_id', name='shared_purchase_details_pkey'),
        Index('idx_shared_purchase_details_moment', 'moment_id'),
        Index('idx_shared_purchase_details_type', 'purchase_type')
    )

    purchase_detail_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    purchase_type: Mapped[str] = mapped_column(String(100), nullable=False)
    purchase_name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    funding_style: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    target_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    purchase_link: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    expected_contributors: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_purchase_details')


class SharedPurchaseItems(Base):
    __tablename__ = 'shared_purchase_items'
    __table_args__ = (
        CheckConstraint("priority IS NULL OR (priority::text = ANY (ARRAY['HIGH'::character varying, 'MEDIUM'::character varying, 'LOW'::character varying]::text[]))", name='chk_spi_priority'),
        CheckConstraint('quantity IS NULL OR quantity >= 1', name='chk_spi_quantity'),
        CheckConstraint("status::text = ANY (ARRAY['PROPOSED'::character varying, 'SHORTLISTED'::character varying, 'SELECTED'::character varying, 'PURCHASED'::character varying, 'DROPPED'::character varying]::text[])", name='chk_spi_status'),
        CheckConstraint('target_price IS NULL OR target_price >= 0::numeric', name='chk_spi_target_price'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_spi_created_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_spi_moment'),
        PrimaryKeyConstraint('item_id', name='shared_purchase_items_pkey'),
        Index('idx_purchase_items_category', 'category'),
        Index('idx_purchase_items_moment', 'moment_id'),
        Index('idx_purchase_items_status', 'status')
    )

    item_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'PROPOSED'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    target_price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    quantity: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('1'))
    purchase_link: Mapped[Optional[str]] = mapped_column(Text)
    priority: Mapped[Optional[str]] = mapped_column(String(30))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='shared_purchase_items')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_purchase_items')


class SharedPurchaseOwnership(Base):
    __tablename__ = 'shared_purchase_ownership'
    __table_args__ = (
        CheckConstraint('ownership_percentage IS NULL OR ownership_percentage >= 0::numeric AND ownership_percentage <= 100::numeric', name='chk_spo_percentage'),
        CheckConstraint("status::text = ANY (ARRAY['DRAFT'::character varying, 'FINALIZED'::character varying, 'REVISED'::character varying]::text[])", name='chk_spo_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_spo_moment'),
        ForeignKeyConstraint(['owner_member_id'], ['group_moment_members.member_id'], name='fk_spo_owner'),
        PrimaryKeyConstraint('ownership_id', name='shared_purchase_ownership_pkey'),
        Index('idx_purchase_ownership_moment', 'moment_id'),
        Index('idx_purchase_ownership_owner', 'owner_member_id'),
        Index('idx_purchase_ownership_status', 'status')
    )

    ownership_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    owner_member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    ownership_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DRAFT'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    ownership_percentage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    usage_rights: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_purchase_ownership')
    owner_member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='shared_purchase_ownership')


class SharedPurchaseOwnershipInsights(Base):
    __tablename__ = 'shared_purchase_ownership_insights'
    __table_args__ = (
        PrimaryKeyConstraint('insight_id', name='shared_purchase_ownership_insights_pkey'),
    )

    insight_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    insight_type: Mapped[Optional[str]] = mapped_column(String(100))
    title: Mapped[Optional[str]] = mapped_column(String(250))
    description: Mapped[Optional[str]] = mapped_column(Text)
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class SharedPurchaseVendors(Base):
    __tablename__ = 'shared_purchase_vendors'
    __table_args__ = (
        CheckConstraint('quoted_price IS NULL OR quoted_price >= 0::numeric', name='chk_spv_quoted_price'),
        CheckConstraint("status::text = ANY (ARRAY['EVALUATING'::character varying, 'SHORTLISTED'::character varying, 'CONFIRMED'::character varying, 'REJECTED'::character varying]::text[])", name='chk_spv_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_spv_moment'),
        PrimaryKeyConstraint('vendor_id', name='shared_purchase_vendors_pkey'),
        Index('idx_purchase_vendors_category', 'vendor_category'),
        Index('idx_purchase_vendors_moment', 'moment_id'),
        Index('idx_purchase_vendors_status', 'status')
    )

    vendor_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    vendor_category: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'EVALUATING'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    contact_person: Mapped[Optional[str]] = mapped_column(String(200))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(200))
    quoted_price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    vendor_link: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='shared_purchase_vendors')
