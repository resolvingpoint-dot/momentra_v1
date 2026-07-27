"""Group domain SQLAlchemy models (group_* tables, including group life and memory sub-features).

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


class GroupActivityEdits(Base):
    __tablename__ = 'group_activity_edits'
    __table_args__ = (
        CheckConstraint("edit_status::text = ANY (ARRAY['DRAFT'::character varying, 'SAVED'::character varying, 'REVERTED'::character varying, 'CANCELLED'::character varying]::text[])", name='chk_gae_status'),
        ForeignKeyConstraint(['activity_id'], ['group_live_feed.feed_id'], name='fk_gae_activity'),
        ForeignKeyConstraint(['edited_by'], ['group_moment_members.member_id'], name='fk_gae_edited_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gae_moment'),
        PrimaryKeyConstraint('edit_id', name='group_activity_edits_pkey'),
        Index('idx_gae_edited_by', 'edited_by'),
        Index('idx_gae_entity', 'entity_name', 'entity_id'),
        Index('idx_gae_moment', 'moment_id')
    )

    edit_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    entity_name: Mapped[str] = mapped_column(String(150), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    edit_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'SAVED'::character varying"))
    edited_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    edited_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    activity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    edit_payload_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    edit_reason: Mapped[Optional[str]] = mapped_column(Text)

    activity: Mapped[Optional['GroupLiveFeed']] = relationship('GroupLiveFeed', back_populates='group_activity_edits')
    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_activity_edits')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_activity_edits')


class GroupAiInsights(Base):
    __tablename__ = 'group_ai_insights'
    __table_args__ = (
        CheckConstraint("confidence_level IS NULL OR (confidence_level::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying]::text[]))", name='chk_gai_confidence_v2'),
        CheckConstraint("display_context::text = ANY (ARRAY['PULSE'::character varying, 'MEMORY'::character varying, 'LIFE'::character varying, 'BOTH'::character varying]::text[])", name='chk_gai_display_context'),
        CheckConstraint("insight_layer::text = ANY (ARRAY['PULSE'::character varying, 'MOMENTS'::character varying, 'MEMORY'::character varying, 'LIFE'::character varying]::text[])", name='chk_gai_layer_v2'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gai_moment'),
        ForeignKeyConstraint(['related_life_space_id'], ['group_life_spaces.life_space_id'], name='fk_gai_life_space_v2'),
        PrimaryKeyConstraint('insight_id', name='group_ai_insights_pkey'),
        Index('idx_gai_display_context', 'display_context'),
        Index('idx_gai_moment', 'moment_id'),
        Index('idx_gai_type', 'insight_type')
    )

    insight_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    insight_type: Mapped[str] = mapped_column(String(100), nullable=False)
    insight_title: Mapped[str] = mapped_column(String(250), nullable=False)
    insight_text: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    display_context: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'BOTH'::character varying"))
    insight_layer: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'PULSE'::character varying"))
    insight_body: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    source_snapshot_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    related_life_space_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    confidence_level: Mapped[Optional[str]] = mapped_column(String(30))
    supporting_metrics_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    display_order: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_ai_insights')
    related_life_space: Mapped[Optional['GroupLifeSpaces']] = relationship('GroupLifeSpaces', back_populates='group_ai_insights')


class GroupAttachments(Base):
    __tablename__ = 'group_attachments'
    __table_args__ = (
        CheckConstraint("file_type::text = ANY (ARRAY['IMAGE'::character varying, 'PDF'::character varying, 'AUDIO'::character varying, 'VIDEO'::character varying, 'OTHER'::character varying]::text[])", name='chk_ga_file_type'),
        ForeignKeyConstraint(['event_id'], ['group_quick_add_events.event_id'], name='fk_ga_event'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_ga_moment'),
        PrimaryKeyConstraint('attachment_id', name='group_attachments_pkey'),
        Index('idx_attachments_entity', 'entity_name', 'entity_id'),
        Index('idx_attachments_event', 'event_id'),
        Index('idx_attachments_moment', 'moment_id'),
        Index('idx_ga_asset_category', 'asset_category'),
        Index('idx_ga_attachment_context', 'attachment_context'),
        Index('idx_ga_gallery_group', 'gallery_group'),
        Index('idx_ga_gallery_item', 'is_gallery_item')
    )

    attachment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    entity_name: Mapped[str] = mapped_column(String(150), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_gallery_item: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    attachment_context: Mapped[Optional[str]] = mapped_column(String(100))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    gallery_group: Mapped[Optional[str]] = mapped_column(String(100))
    asset_category: Mapped[Optional[str]] = mapped_column(String(100))

    event: Mapped[Optional['GroupQuickAddEvents']] = relationship('GroupQuickAddEvents', back_populates='group_attachments')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_attachments')
    group_moment_resources: Mapped[list['GroupMomentResources']] = relationship('GroupMomentResources', back_populates='attachment')
    shared_purchase_delivery: Mapped[list['SharedPurchaseDelivery']] = relationship('SharedPurchaseDelivery', back_populates='proof_attachment')


class GroupAttendance(Base):
    __tablename__ = 'group_attendance'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['CONFIRMED'::character varying, 'TENTATIVE'::character varying, 'DECLINED'::character varying, 'ATTENDED'::character varying, 'ABSENT'::character varying]::text[])", name='chk_ga_status'),
        ForeignKeyConstraint(['member_id'], ['group_moment_members.member_id'], name='fk_ga_member'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_ga_moment'),
        PrimaryKeyConstraint('attendance_id', name='group_attendance_pkey'),
        Index('idx_attendance_member', 'member_id'),
        Index('idx_attendance_moment', 'moment_id'),
        Index('idx_attendance_status', 'status')
    )

    attendance_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    attendance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    attendance_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_attendance')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_attendance')


class GroupChangeHistory(Base):
    __tablename__ = 'group_change_history'
    __table_args__ = (
        CheckConstraint("change_type::text = ANY (ARRAY['CREATED'::character varying, 'UPDATED'::character varying, 'DELETED'::character varying]::text[])", name='chk_gch_type'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gch_moment'),
        PrimaryKeyConstraint('change_id', name='group_change_history_pkey'),
        Index('idx_change_history_entity', 'entity_name', 'entity_id'),
        Index('idx_change_history_moment', 'moment_id'),
        Index('idx_change_history_time', 'changed_at'),
        Index('idx_gch_change_category', 'change_category'),
        Index('idx_gch_edit_batch', 'edit_batch_id'),
        Index('idx_gch_source_activity', 'source_activity_id'),
        Index('idx_gch_source_widget', 'source_widget')
    )

    change_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    entity_name: Mapped[str] = mapped_column(String(150), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    changed_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    rollback_supported: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    field_name: Mapped[Optional[str]] = mapped_column(String(150))
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    change_category: Mapped[Optional[str]] = mapped_column(String(100))
    source_widget: Mapped[Optional[str]] = mapped_column(String(100))
    edit_batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    edit_reason: Mapped[Optional[str]] = mapped_column(Text)
    source_activity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_change_history')


class GroupContributions(Base):
    __tablename__ = 'group_contributions'
    __table_args__ = (
        CheckConstraint('amount > 0::numeric', name='chk_gc_amount'),
        CheckConstraint("payment_method IS NULL OR (payment_method::text = ANY (ARRAY['UPI'::character varying, 'BANK_TRANSFER'::character varying, 'CARD'::character varying, 'CASH'::character varying, 'OTHER'::character varying]::text[]))", name='chk_gc_payment_method'),
        CheckConstraint("status::text = ANY (ARRAY['PENDING'::character varying, 'RECEIVED'::character varying]::text[])", name='chk_gc_status'),
        ForeignKeyConstraint(['contributor_member_id'], ['group_moment_members.member_id'], name='fk_gc_member'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gc_moment'),
        PrimaryKeyConstraint('contribution_id', name='group_contributions_pkey'),
        Index('idx_contributions_member', 'contributor_member_id'),
        Index('idx_contributions_moment', 'moment_id'),
        Index('idx_contributions_status', 'status'),
        Index('idx_gc_budget_plan', 'budget_plan_id'),
        Index('idx_gc_budget_split', 'budget_split_id')
    )

    contribution_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    contributor_member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    contribution_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'PENDING'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    reference_number: Mapped[Optional[str]] = mapped_column(String(150))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    budget_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    budget_split_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    target_contribution_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))

    contributor_member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_contributions')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_contributions')


class GroupDecisions(Base):
    __tablename__ = 'group_decisions'
    __table_args__ = (
        CheckConstraint("decision_type::text = ANY (ARRAY['POLL'::character varying, 'VOTE'::character varying, 'APPROVAL'::character varying, 'RESOLUTION'::character varying, 'OWNERSHIP'::character varying, 'RULE'::character varying, 'PRIORITY'::character varying, 'VENDOR'::character varying]::text[])", name='chk_gd_type'),
        CheckConstraint("status::text = ANY (ARRAY['DRAFT'::character varying, 'OPEN'::character varying, 'APPROVED'::character varying, 'REJECTED'::character varying, 'RESOLVED'::character varying, 'CLOSED'::character varying]::text[])", name='chk_gd_status'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_gd_created_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gd_moment'),
        ForeignKeyConstraint(['owner_id'], ['group_moment_members.member_id'], name='fk_gd_owner'),
        PrimaryKeyConstraint('decision_id', name='group_decisions_pkey')
    )

    decision_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DRAFT'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    result: Mapped[Optional[str]] = mapped_column(Text)
    decision_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    source_ref_table: Mapped[Optional[str]] = mapped_column(String(150))
    source_ref_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', foreign_keys=[created_by], back_populates='group_decisions_created_by')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_decisions')
    owner: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', foreign_keys=[owner_id], back_populates='group_decisions_owner')


class GroupExpenseSplits(Base):
    __tablename__ = 'group_expense_splits'
    __table_args__ = (
        CheckConstraint("settlement_status::text = ANY (ARRAY['OPEN'::character varying, 'SETTLED'::character varying, 'WAIVED'::character varying]::text[])", name='chk_ges_settlement'),
        CheckConstraint('split_amount >= 0::numeric', name='chk_ges_amount'),
        CheckConstraint("split_method::text = ANY (ARRAY['EQUAL'::character varying, 'CUSTOM_AMOUNT'::character varying, 'CUSTOM_PERCENTAGE'::character varying, 'ORGANIZER_PAID'::character varying]::text[])", name='chk_ges_method'),
        ForeignKeyConstraint(['expense_id'], ['group_expenses.expense_id'], name='fk_ges_expense'),
        ForeignKeyConstraint(['member_id'], ['group_moment_members.member_id'], name='fk_ges_member'),
        PrimaryKeyConstraint('split_id', name='group_expense_splits_pkey'),
        Index('idx_expense_splits_expense', 'expense_id'),
        Index('idx_expense_splits_member', 'member_id')
    )

    split_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    expense_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    split_method: Mapped[str] = mapped_column(String(50), nullable=False)
    split_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    settlement_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'OPEN'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    split_percentage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    expense: Mapped['GroupExpenses'] = relationship('GroupExpenses', back_populates='group_expense_splits')
    member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_expense_splits')


class GroupExpenses(Base):
    __tablename__ = 'group_expenses'
    __table_args__ = (
        CheckConstraint('amount > 0::numeric', name='chk_ge_amount'),
        CheckConstraint("status::text = ANY (ARRAY['RECORDED'::character varying, 'EDITED'::character varying, 'DELETED'::character varying]::text[])", name='chk_ge_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_ge_moment'),
        ForeignKeyConstraint(['paid_by_member_id'], ['group_moment_members.member_id'], name='fk_ge_paid_by'),
        PrimaryKeyConstraint('expense_id', name='group_expenses_pkey'),
        Index('idx_ge_budget_category', 'budget_category_id'),
        Index('idx_ge_budget_plan', 'budget_plan_id'),
        Index('idx_group_expenses_context', 'module_context'),
        Index('idx_group_expenses_date', 'expense_date'),
        Index('idx_group_expenses_moment', 'moment_id')
    )

    expense_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    module_context: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    expense_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    expense_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    paid_by_member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'RECORDED'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    budget_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    budget_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    budget_variance_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(14, 2))

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_expenses')
    paid_by_member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_expenses')
    group_expense_splits: Mapped[list['GroupExpenseSplits']] = relationship('GroupExpenseSplits', back_populates='expense')
    shared_living_maintenance: Mapped[list['SharedLivingMaintenance']] = relationship('SharedLivingMaintenance', back_populates='linked_expense')


class GroupFieldValueConfig(Base):
    __tablename__ = 'group_field_value_config'
    __table_args__ = (
        PrimaryKeyConstraint('config_value_id', name='group_field_value_config_pkey'),
        Index('idx_field_config_lookup', 'moment_type', 'moment_profile', 'module_code', 'field_name'),
        Index('idx_gfvc_value_group', 'value_group'),
        Index('idx_gfvc_value_subgroup', 'value_subgroup')
    )

    config_value_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    moment_profile: Mapped[str] = mapped_column(String(100), nullable=False)
    module_code: Mapped[str] = mapped_column(String(100), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value_code: Mapped[str] = mapped_column(String(100), nullable=False)
    value_label: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_top_category: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    value_group: Mapped[Optional[str]] = mapped_column(String(100))
    value_subgroup: Mapped[Optional[str]] = mapped_column(String(100))


class GroupHealthSnapshots(Base):
    __tablename__ = 'group_health_snapshots'
    __table_args__ = (
        CheckConstraint('budget_health_score IS NULL OR budget_health_score >= 0::numeric AND budget_health_score <= 100::numeric', name='chk_ghs_budget_health_score'),
        CheckConstraint("health_status::text = ANY (ARRAY['EXCELLENT'::character varying, 'GOOD'::character varying, 'STABLE'::character varying, 'WARNING'::character varying, 'CRITICAL'::character varying]::text[])", name='chk_ghs_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_ghs_moment'),
        PrimaryKeyConstraint('health_snapshot_id', name='group_health_snapshots_pkey'),
        Index('idx_ghs_date', 'snapshot_date'),
        Index('idx_ghs_dimension_breakdown_json', 'dimension_breakdown_json', postgresql_using='gin'),
        Index('idx_ghs_health_driver_json', 'health_driver_breakdown_json', postgresql_using='gin'),
        Index('idx_ghs_moment', 'moment_id')
    )

    health_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    health_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    health_status: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    people_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    money_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    activity_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    health_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2))
    health_delta_period: Mapped[Optional[str]] = mapped_column(String(30))
    health_driver_breakdown_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    budget_health_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    dimension_breakdown_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_health_snapshots')


class GroupJourneyMetrics(Base):
    __tablename__ = 'group_journey_metrics'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gjm_moment'),
        PrimaryKeyConstraint('metric_id', name='group_journey_metrics_pkey'),
        Index('idx_gjm_date', 'metric_date'),
        Index('idx_gjm_moment', 'moment_id')
    )

    metric_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    metric_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    days_in_stage: Mapped[Optional[int]] = mapped_column(Integer)
    completion_percentage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    milestone_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_journey_metrics')


class GroupLifeDimensionScores(Base):
    __tablename__ = 'group_life_dimension_scores'
    __table_args__ = (
        CheckConstraint('score >= 0::numeric AND score <= 100::numeric', name='chk_glds_score'),
        ForeignKeyConstraint(['life_snapshot_id'], ['group_life_snapshots.life_snapshot_id'], name='fk_glds_snapshot'),
        PrimaryKeyConstraint('dimension_score_id', name='group_life_dimension_scores_pkey')
    )

    dimension_score_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    life_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    dimension_code: Mapped[str] = mapped_column(String(100), nullable=False)
    dimension_name: Mapped[str] = mapped_column(String(150), nullable=False)
    score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[Optional[str]] = mapped_column(String(30))
    trend_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2))
    explanation: Mapped[Optional[str]] = mapped_column(Text)

    life_snapshot: Mapped['GroupLifeSnapshots'] = relationship('GroupLifeSnapshots', back_populates='group_life_dimension_scores')


class GroupLifeDriverEffects(Base):
    __tablename__ = 'group_life_driver_effects'
    __table_args__ = (
        CheckConstraint("confidence_level::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying]::text[])", name='chk_glde_confidence'),
        CheckConstraint('rank_no >= 1', name='chk_glde_rank'),
        ForeignKeyConstraint(['life_snapshot_id'], ['group_life_snapshots.life_snapshot_id'], name='fk_glde_snapshot'),
        PrimaryKeyConstraint('driver_effect_id', name='group_life_driver_effects_pkey')
    )

    driver_effect_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    life_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    effect_label: Mapped[str] = mapped_column(String(250), nullable=False)
    impact_pct: Mapped[decimal.Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'MEDIUM'::character varying"))
    rank_no: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    recommended_action: Mapped[Optional[str]] = mapped_column(Text)
    supporting_metrics_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    life_snapshot: Mapped['GroupLifeSnapshots'] = relationship('GroupLifeSnapshots', back_populates='group_life_driver_effects')


class GroupLifeMasterSnapshots(Base):
    __tablename__ = 'group_life_master_snapshots'
    __table_args__ = (
        CheckConstraint('group_life_score >= 0::numeric AND group_life_score <= 100::numeric', name='chk_glms_score'),
        ForeignKeyConstraint(['life_space_id'], ['group_life_spaces.life_space_id'], name='fk_glms_space'),
        PrimaryKeyConstraint('master_snapshot_id', name='group_life_master_snapshots_pkey')
    )

    master_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    life_space_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    group_life_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    participation_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    contribution_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    coordination_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    progress_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    community_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    active_group_moments_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    active_members_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    open_group_actions_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    group_risk_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    dominant_group_driver: Mapped[Optional[str]] = mapped_column(Text)
    dominant_group_risk: Mapped[Optional[str]] = mapped_column(Text)
    highest_group_leverage: Mapped[Optional[str]] = mapped_column(Text)
    source_snapshot_ids_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    life_space: Mapped['GroupLifeSpaces'] = relationship('GroupLifeSpaces', back_populates='group_life_master_snapshots')


class GroupLifeMomentLinks(Base):
    __tablename__ = 'group_life_moment_links'
    __table_args__ = (
        CheckConstraint('included_weight >= 0::numeric', name='chk_glml_weight'),
        ForeignKeyConstraint(['life_space_id'], ['group_life_spaces.life_space_id'], name='fk_glml_space'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_glml_moment'),
        PrimaryKeyConstraint('life_link_id', name='group_life_moment_links_pkey'),
        UniqueConstraint('life_space_id', 'moment_id', name='uq_glml_space_moment')
    )

    life_link_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    life_space_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    included_weight: Mapped[decimal.Decimal] = mapped_column(Numeric(6, 3), nullable=False, server_default=text('1.000'))
    linked_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    life_space: Mapped['GroupLifeSpaces'] = relationship('GroupLifeSpaces', back_populates='group_life_moment_links')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_life_moment_links')


class GroupLifeSnapshots(Base):
    __tablename__ = 'group_life_snapshots'
    __table_args__ = (
        CheckConstraint('group_life_score >= 0::numeric AND group_life_score <= 100::numeric', name='chk_glsnap_score'),
        CheckConstraint("health_status::text = ANY (ARRAY['HEALTHY'::character varying, 'STABLE'::character varying, 'WATCH'::character varying, 'NEEDS_ATTENTION'::character varying, 'CRITICAL'::character varying]::text[])", name='chk_glsnap_status'),
        ForeignKeyConstraint(['life_space_id'], ['group_life_spaces.life_space_id'], name='fk_glsnap_space'),
        PrimaryKeyConstraint('life_snapshot_id', name='group_life_snapshots_pkey')
    )

    life_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    life_space_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    group_life_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    health_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'STABLE'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    dominant_driver: Mapped[Optional[str]] = mapped_column(Text)
    dominant_risk: Mapped[Optional[str]] = mapped_column(Text)
    highest_leverage: Mapped[Optional[str]] = mapped_column(Text)
    trend_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(6, 2))

    life_space: Mapped['GroupLifeSpaces'] = relationship('GroupLifeSpaces', back_populates='group_life_snapshots')
    group_life_dimension_scores: Mapped[list['GroupLifeDimensionScores']] = relationship('GroupLifeDimensionScores', back_populates='life_snapshot')
    group_life_driver_effects: Mapped[list['GroupLifeDriverEffects']] = relationship('GroupLifeDriverEffects', back_populates='life_snapshot')


class GroupLifeSpaces(Base):
    __tablename__ = 'group_life_spaces'
    __table_args__ = (
        CheckConstraint("space_status::text = ANY (ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying]::text[])", name='chk_gls_status'),
        PrimaryKeyConstraint('life_space_id', name='group_life_spaces_pkey')
    )

    life_space_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    space_name: Mapped[str] = mapped_column(String(200), nullable=False, server_default=text("'Group Life'::character varying"))
    space_status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    group_ai_insights: Mapped[list['GroupAiInsights']] = relationship('GroupAiInsights', back_populates='related_life_space')
    group_life_master_snapshots: Mapped[list['GroupLifeMasterSnapshots']] = relationship('GroupLifeMasterSnapshots', back_populates='life_space')
    group_life_moment_links: Mapped[list['GroupLifeMomentLinks']] = relationship('GroupLifeMomentLinks', back_populates='life_space')
    group_life_snapshots: Mapped[list['GroupLifeSnapshots']] = relationship('GroupLifeSnapshots', back_populates='life_space')


class GroupLiveFeed(Base):
    __tablename__ = 'group_live_feed'
    __table_args__ = (
        CheckConstraint("visibility::text = ANY (ARRAY['EVERYONE'::character varying, 'ORGANIZERS'::character varying, 'SELECTED'::character varying]::text[])", name='chk_glf_visibility'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_glf_created_by'),
        ForeignKeyConstraint(['event_id'], ['group_quick_add_events.event_id'], name='fk_glf_event'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_glf_moment'),
        PrimaryKeyConstraint('feed_id', name='group_live_feed_pkey'),
        Index('idx_glf_category_chip', 'category_chip'),
        Index('idx_glf_created_by', 'created_by'),
        Index('idx_glf_entity', 'entity_name', 'entity_id'),
        Index('idx_glf_is_editable', 'is_editable'),
        Index('idx_glf_timeline_display_json', 'timeline_display_json', postgresql_using='gin'),
        Index('idx_live_feed_category', 'feed_category'),
        Index('idx_live_feed_created', 'created_at'),
        Index('idx_live_feed_event', 'event_id'),
        Index('idx_live_feed_moment', 'moment_id')
    )

    feed_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    feed_category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    can_view: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    can_edit: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    visibility: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'EVERYONE'::character varying"))
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    can_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    is_editable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    category_chip: Mapped[Optional[str]] = mapped_column(String(100))
    timeline_display_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    source_widget: Mapped[Optional[str]] = mapped_column(String(100))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    entity_name: Mapped[Optional[str]] = mapped_column(String(150))
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    edit_route: Mapped[Optional[str]] = mapped_column(String(250))

    group_moment_members: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', back_populates='group_live_feed')
    event: Mapped['GroupQuickAddEvents'] = relationship('GroupQuickAddEvents', back_populates='group_live_feed')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_live_feed')
    group_activity_edits: Mapped[list['GroupActivityEdits']] = relationship('GroupActivityEdits', back_populates='activity')


class GroupMemoryEntries(Base):
    __tablename__ = 'group_memory_entries'
    __table_args__ = (
        CheckConstraint('highlight_score IS NULL OR highlight_score >= 0::numeric AND highlight_score <= 100::numeric', name='chk_gme_highlight_score'),
        CheckConstraint("visibility IS NULL OR (visibility::text = ANY (ARRAY['EVERYONE'::character varying, 'ORGANIZERS'::character varying, 'SELECTED'::character varying]::text[]))", name='chk_gme_visibility'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gme_moment'),
        ForeignKeyConstraint(['source_event_id'], ['group_quick_add_events.event_id'], name='fk_gme_event'),
        PrimaryKeyConstraint('memory_id', name='group_memory_entries_pkey'),
        Index('idx_gme_budget_plan', 'budget_plan_id'),
        Index('idx_gme_category', 'category'),
        Index('idx_gme_gallery_item', 'is_gallery_item'),
        Index('idx_gme_highlight_score', 'highlight_score'),
        Index('idx_gme_memory_category', 'memory_category'),
        Index('idx_gme_memory_date', 'memory_date'),
        Index('idx_gme_moment', 'moment_id')
    )

    memory_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    memory_type: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    memory_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_gallery_item: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    memory_category: Mapped[Optional[str]] = mapped_column(String(100))
    media_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    visibility: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'EVERYONE'::character varying"))
    highlight_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    budget_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_memory_entries')
    source_event: Mapped[Optional['GroupQuickAddEvents']] = relationship('GroupQuickAddEvents', back_populates='group_memory_entries')


class GroupMemoryPatterns(Base):
    __tablename__ = 'group_memory_patterns'
    __table_args__ = (
        CheckConstraint('pattern_strength IS NULL OR pattern_strength >= 0::numeric AND pattern_strength <= 100::numeric', name='chk_gmp_pattern_strength'),
        CheckConstraint("status::text = ANY (ARRAY['ACTIVE'::character varying, 'SUPERSEDED'::character varying, 'DISMISSED'::character varying]::text[])", name='chk_gmp_status'),
        CheckConstraint("trend_direction IS NULL OR (trend_direction::text = ANY (ARRAY['UP'::character varying, 'DOWN'::character varying, 'STABLE'::character varying, 'MIXED'::character varying]::text[]))", name='chk_gmp_trend_direction'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gmp_moment'),
        PrimaryKeyConstraint('pattern_id', name='group_memory_patterns_pkey'),
        Index('idx_gmp_identity_label', 'identity_label'),
        Index('idx_gmp_moment', 'moment_id'),
        Index('idx_gmp_status', 'status'),
        Index('idx_gmp_supporting_metrics_json', 'supporting_metrics_json', postgresql_using='gin'),
        Index('idx_gmp_type', 'pattern_type')
    )

    pattern_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    pattern_type: Mapped[str] = mapped_column(String(100), nullable=False)
    pattern_category: Mapped[str] = mapped_column(String(100), nullable=False)
    insight_title: Mapped[str] = mapped_column(String(250), nullable=False)
    confidence_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    insight_text: Mapped[Optional[str]] = mapped_column(Text)
    supporting_event_ids_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    lesson_text: Mapped[Optional[str]] = mapped_column(Text)
    identity_label: Mapped[Optional[str]] = mapped_column(String(150))
    pattern_strength: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    trend_direction: Mapped[Optional[str]] = mapped_column(String(30))
    supporting_metrics_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_memory_patterns')


class GroupMemorySnapshots(Base):
    __tablename__ = 'group_memory_snapshots'
    __table_args__ = (
        CheckConstraint('memory_count >= 0 AND milestone_count >= 0', name='chk_gms_counts'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gms_moment'),
        PrimaryKeyConstraint('snapshot_id', name='group_memory_snapshots_pkey')
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    memory_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    milestone_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    what_changed_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    budget_reflection_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    identity_label: Mapped[Optional[str]] = mapped_column(String(150))

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_memory_snapshots')


class GroupMomentMembers(Base):
    __tablename__ = 'group_moment_members'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gmm_moment'),
        ForeignKeyConstraint(['role_code'], ['group_moment_roles.role_code'], name='fk_gmm_role'),
        PrimaryKeyConstraint('member_id', name='group_moment_members_pkey'),
        Index('idx_gmm_contact_email', 'contact_email'),
        Index('idx_gmm_user_id', 'user_id'),
        Index('idx_group_members_moment', 'moment_id'),
        Index('idx_group_members_status', 'status'),
        Index('uq_gmm_invite_token', 'invite_token', postgresql_where='(invite_token IS NOT NULL)', unique=True)
    )

    member_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role_code: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'INVITED'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    joined_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    left_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(30))
    invite_token: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    invite_sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_moment_members')
    group_moment_roles: Mapped['GroupMomentRoles'] = relationship('GroupMomentRoles', back_populates='group_moment_members')
    community_coordination_details: Mapped[list['CommunityCoordinationDetails']] = relationship('CommunityCoordinationDetails', back_populates='primary_owner')
    group_attendance: Mapped[list['GroupAttendance']] = relationship('GroupAttendance', back_populates='member')
    group_contributions: Mapped[list['GroupContributions']] = relationship('GroupContributions', back_populates='contributor_member')
    group_decisions_created_by: Mapped[list['GroupDecisions']] = relationship('GroupDecisions', foreign_keys='[GroupDecisions.created_by]', back_populates='group_moment_members')
    group_decisions_owner: Mapped[list['GroupDecisions']] = relationship('GroupDecisions', foreign_keys='[GroupDecisions.owner_id]', back_populates='owner')
    group_expenses: Mapped[list['GroupExpenses']] = relationship('GroupExpenses', back_populates='paid_by_member')
    group_live_feed: Mapped[list['GroupLiveFeed']] = relationship('GroupLiveFeed', back_populates='group_moment_members')
    group_moment_work_items_created_by: Mapped[list['GroupMomentWorkItems']] = relationship('GroupMomentWorkItems', foreign_keys='[GroupMomentWorkItems.created_by]', back_populates='group_moment_members')
    group_moment_work_items_owner: Mapped[list['GroupMomentWorkItems']] = relationship('GroupMomentWorkItems', foreign_keys='[GroupMomentWorkItems.owner_id]', back_populates='owner')
    group_people_impact_scores: Mapped[list['GroupPeopleImpactScores']] = relationship('GroupPeopleImpactScores', back_populates='member')
    group_polls: Mapped[list['GroupPolls']] = relationship('GroupPolls', back_populates='group_moment_members')
    group_updates: Mapped[list['GroupUpdates']] = relationship('GroupUpdates', back_populates='group_moment_members')
    shared_experience_budget_splits: Mapped[list['SharedExperienceBudgetSplits']] = relationship('SharedExperienceBudgetSplits', back_populates='member')
    shared_experience_planning_items_created_by: Mapped[list['SharedExperiencePlanningItems']] = relationship('SharedExperiencePlanningItems', foreign_keys='[SharedExperiencePlanningItems.created_by]', back_populates='group_moment_members')
    shared_experience_planning_items_owner_member: Mapped[list['SharedExperiencePlanningItems']] = relationship('SharedExperiencePlanningItems', foreign_keys='[SharedExperiencePlanningItems.owner_member_id]', back_populates='owner_member')
    shared_experience_settlements_payer_member: Mapped[list['SharedExperienceSettlements']] = relationship('SharedExperienceSettlements', foreign_keys='[SharedExperienceSettlements.payer_member_id]', back_populates='payer_member')
    shared_experience_settlements_receiver_member: Mapped[list['SharedExperienceSettlements']] = relationship('SharedExperienceSettlements', foreign_keys='[SharedExperienceSettlements.receiver_member_id]', back_populates='receiver_member')
    shared_goal_details: Mapped[list['SharedGoalDetails']] = relationship('SharedGoalDetails', back_populates='goal_owner')
    shared_living_assets: Mapped[list['SharedLivingAssets']] = relationship('SharedLivingAssets', back_populates='owner_member')
    shared_living_resident_dynamics: Mapped[list['SharedLivingResidentDynamics']] = relationship('SharedLivingResidentDynamics', back_populates='resident_member')
    shared_living_residents: Mapped[list['SharedLivingResidents']] = relationship('SharedLivingResidents', back_populates='member')
    shared_living_rules: Mapped[list['SharedLivingRules']] = relationship('SharedLivingRules', back_populates='group_moment_members')
    shared_living_tasks: Mapped[list['SharedLivingTasks']] = relationship('SharedLivingTasks', back_populates='assigned_to_member')
    shared_purchase_contributors: Mapped[list['SharedPurchaseContributors']] = relationship('SharedPurchaseContributors', back_populates='member')
    shared_purchase_items: Mapped[list['SharedPurchaseItems']] = relationship('SharedPurchaseItems', back_populates='group_moment_members')
    shared_purchase_ownership: Mapped[list['SharedPurchaseOwnership']] = relationship('SharedPurchaseOwnership', back_populates='owner_member')
    group_activity_edits: Mapped[list['GroupActivityEdits']] = relationship('GroupActivityEdits', back_populates='group_moment_members')
    group_expense_splits: Mapped[list['GroupExpenseSplits']] = relationship('GroupExpenseSplits', back_populates='member')
    group_moment_resources_created_by: Mapped[list['GroupMomentResources']] = relationship('GroupMomentResources', foreign_keys='[GroupMomentResources.created_by]', back_populates='group_moment_members')
    group_moment_resources_owner: Mapped[list['GroupMomentResources']] = relationship('GroupMomentResources', foreign_keys='[GroupMomentResources.owner_id]', back_populates='owner')
    shared_living_maintenance_assigned_to_member: Mapped[list['SharedLivingMaintenance']] = relationship('SharedLivingMaintenance', foreign_keys='[SharedLivingMaintenance.assigned_to_member_id]', back_populates='assigned_to_member')
    shared_living_maintenance_reported_by_member: Mapped[list['SharedLivingMaintenance']] = relationship('SharedLivingMaintenance', foreign_keys='[SharedLivingMaintenance.reported_by_member_id]', back_populates='reported_by_member')
    shared_purchase_delivery: Mapped[list['SharedPurchaseDelivery']] = relationship('SharedPurchaseDelivery', back_populates='received_by_member')
    group_poll_votes: Mapped[list['GroupPollVotes']] = relationship('GroupPollVotes', back_populates='voter_member')


class GroupMomentProfiles(Base):
    __tablename__ = 'group_moment_profiles'
    __table_args__ = (
        PrimaryKeyConstraint('profile_id', name='group_moment_profiles_pkey'),
        UniqueConstraint('moment_type', 'profile_code', name='uq_group_profile'),
        Index('idx_group_profiles_type', 'moment_type')
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    profile_code: Mapped[str] = mapped_column(String(100), nullable=False)
    profile_name: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    profile_description: Mapped[Optional[str]] = mapped_column(Text)


class GroupMomentResources(Base):
    __tablename__ = 'group_moment_resources'
    __table_args__ = (
        CheckConstraint("resource_type::text = ANY (ARRAY['DOCUMENT'::character varying, 'TOOL'::character varying, 'VENUE'::character varying, 'EQUIPMENT'::character varying, 'RECEIPT'::character varying, 'TICKET'::character varying, 'BOOKING'::character varying, 'PHOTO'::character varying, 'FILE'::character varying, 'LINK'::character varying, 'REFERENCE'::character varying, 'ASSET'::character varying]::text[])", name='chk_gmr_type'),
        CheckConstraint("status::text = ANY (ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'REMOVED'::character varying, 'EXPIRED'::character varying]::text[])", name='chk_gmr_status'),
        ForeignKeyConstraint(['attachment_id'], ['group_attachments.attachment_id'], name='fk_gmr_attachment'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_gmr_created_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gmr_moment'),
        ForeignKeyConstraint(['owner_id'], ['group_moment_members.member_id'], name='fk_gmr_owner'),
        PrimaryKeyConstraint('resource_id', name='group_moment_resources_pkey')
    )

    resource_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_name: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'::character varying"))
    is_memory_asset: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    attachment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    resource_url: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    attachment: Mapped[Optional['GroupAttachments']] = relationship('GroupAttachments', back_populates='group_moment_resources')
    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', foreign_keys=[created_by], back_populates='group_moment_resources_created_by')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_moment_resources')
    owner: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', foreign_keys=[owner_id], back_populates='group_moment_resources_owner')


class GroupMomentRoles(Base):
    __tablename__ = 'group_moment_roles'
    __table_args__ = (
        PrimaryKeyConstraint('role_code', name='group_moment_roles_pkey'),
        Index('idx_group_roles_type', 'moment_type')
    )

    role_code: Mapped[str] = mapped_column(String(100), primary_key=True)
    moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    role_name: Mapped[str] = mapped_column(String(200), nullable=False)
    permission_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    role_description: Mapped[Optional[str]] = mapped_column(Text)

    group_moment_members: Mapped[list['GroupMomentMembers']] = relationship('GroupMomentMembers', back_populates='group_moment_roles')


class GroupMomentStageHistory(Base):
    __tablename__ = 'group_moment_stage_history'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_stage_history_moment'),
        PrimaryKeyConstraint('stage_history_id', name='group_moment_stage_history_pkey'),
        Index('idx_stage_history_current', 'is_current'),
        Index('idx_stage_history_moment', 'moment_id')
    )

    stage_history_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    new_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    changed_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    old_stage: Mapped[Optional[str]] = mapped_column(String(50))
    change_reason: Mapped[Optional[str]] = mapped_column(Text)
    source_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_moment_stage_history')


class GroupMomentWorkItems(Base):
    __tablename__ = 'group_moment_work_items'
    __table_args__ = (
        CheckConstraint("priority IS NULL OR (priority::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying]::text[]))", name='chk_gmwi_priority'),
        CheckConstraint('progress_pct IS NULL OR progress_pct >= 0::numeric AND progress_pct <= 100::numeric', name='chk_gmwi_progress'),
        CheckConstraint("status::text = ANY (ARRAY['OPEN'::character varying, 'IN_PROGRESS'::character varying, 'COMPLETED'::character varying, 'CANCELLED'::character varying, 'BLOCKED'::character varying, 'RESOLVED'::character varying]::text[])", name='chk_gmwi_status'),
        CheckConstraint("work_item_type::text = ANY (ARRAY['TASK'::character varying, 'MILESTONE'::character varying, 'EVENT'::character varying, 'ISSUE'::character varying, 'ANNOUNCEMENT'::character varying, 'PROGRESS_UPDATE'::character varying, 'ACHIEVEMENT'::character varying, 'BOOKING'::character varying, 'DELIVERY'::character varying, 'MAINTENANCE'::character varying]::text[])", name='chk_gmwi_type'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_gmwi_created_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gmwi_moment'),
        ForeignKeyConstraint(['owner_id'], ['group_moment_members.member_id'], name='fk_gmwi_owner'),
        PrimaryKeyConstraint('work_item_id', name='group_moment_work_items_pkey')
    )

    work_item_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    work_item_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default=text("'OPEN'::character varying"))
    source_quick_add: Mapped[str] = mapped_column(String(100), nullable=False)
    is_milestone: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    category: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    priority: Mapped[Optional[str]] = mapped_column(String(30))
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    event_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    progress_pct: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', foreign_keys=[created_by], back_populates='group_moment_work_items_created_by')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_moment_work_items')
    owner: Mapped[Optional['GroupMomentMembers']] = relationship('GroupMomentMembers', foreign_keys=[owner_id], back_populates='group_moment_work_items_owner')


class GroupMoments(Base):
    __tablename__ = 'group_moments'
    __table_args__ = (
        CheckConstraint("activation_status IS NULL OR (activation_status::text = ANY (ARRAY['PLANNING'::character varying, 'ACTIVE'::character varying, 'COMPLETED'::character varying, 'CANCELLED'::character varying]::text[]))", name='chk_group_moments_activation_status'),
        CheckConstraint("planning_mode IS NULL OR (planning_mode::text = ANY (ARRAY['PLAN_NOW'::character varying, 'FUTURE_PLAN'::character varying]::text[]))", name='chk_group_moments_planning_mode'),
        CheckConstraint("status::text = ANY (ARRAY['DRAFT'::character varying, 'ACTIVE'::character varying, 'COMPLETED'::character varying, 'ARCHIVED'::character varying]::text[])", name='chk_group_moment_status'),
        PrimaryKeyConstraint('moment_id', name='group_moments_pkey'),
        Index('idx_group_moments_activation_status', 'activation_status'),
        Index('idx_group_moments_experience_subtype', 'experience_subtype'),
        Index('idx_group_moments_life_included', 'is_life_included'),
        Index('idx_group_moments_life_space', 'group_life_space_id'),
        Index('idx_group_moments_planning_mode', 'planning_mode'),
        Index('idx_group_moments_stage', 'stage'),
        Index('idx_group_moments_status', 'status'),
        Index('idx_group_moments_type', 'moment_type')
    )

    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    moment_profile: Mapped[str] = mapped_column(String(100), nullable=False)
    moment_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'DRAFT'::character varying"))
    stage: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'CREATED'::character varying"))
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_life_included: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    activated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    experience_subtype: Mapped[Optional[str]] = mapped_column(String(100))
    planning_mode: Mapped[Optional[str]] = mapped_column(String(30), server_default=text("'PLAN_NOW'::character varying"))
    activation_status: Mapped[Optional[str]] = mapped_column(String(30), server_default=text("'ACTIVE'::character varying"))
    planned_activation_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    group_life_space_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    group_ai_insights: Mapped[list['GroupAiInsights']] = relationship('GroupAiInsights', back_populates='moment')
    group_change_history: Mapped[list['GroupChangeHistory']] = relationship('GroupChangeHistory', back_populates='moment')
    group_health_snapshots: Mapped[list['GroupHealthSnapshots']] = relationship('GroupHealthSnapshots', back_populates='moment')
    group_journey_metrics: Mapped[list['GroupJourneyMetrics']] = relationship('GroupJourneyMetrics', back_populates='moment')
    group_life_moment_links: Mapped[list['GroupLifeMomentLinks']] = relationship('GroupLifeMomentLinks', back_populates='moment')
    group_memory_patterns: Mapped[list['GroupMemoryPatterns']] = relationship('GroupMemoryPatterns', back_populates='moment')
    group_memory_snapshots: Mapped[list['GroupMemorySnapshots']] = relationship('GroupMemorySnapshots', back_populates='moment')
    group_moment_members: Mapped[list['GroupMomentMembers']] = relationship('GroupMomentMembers', back_populates='moment')
    group_moment_stage_history: Mapped[list['GroupMomentStageHistory']] = relationship('GroupMomentStageHistory', back_populates='moment')
    group_pulse_snapshots: Mapped[list['GroupPulseSnapshots']] = relationship('GroupPulseSnapshots', back_populates='moment')
    group_quick_add_events: Mapped[list['GroupQuickAddEvents']] = relationship('GroupQuickAddEvents', back_populates='moment')
    group_recommendations: Mapped[list['GroupRecommendations']] = relationship('GroupRecommendations', back_populates='moment')
    group_signals: Mapped[list['GroupSignals']] = relationship('GroupSignals', back_populates='moment')
    shared_experience_budget_plans: Mapped[list['SharedExperienceBudgetPlans']] = relationship('SharedExperienceBudgetPlans', back_populates='moment')
    shared_experience_details: Mapped[list['SharedExperienceDetails']] = relationship('SharedExperienceDetails', back_populates='moment')
    shared_living_details: Mapped[list['SharedLivingDetails']] = relationship('SharedLivingDetails', back_populates='moment')
    shared_living_home_personality: Mapped[list['SharedLivingHomePersonality']] = relationship('SharedLivingHomePersonality', back_populates='moment')
    shared_purchase_details: Mapped[list['SharedPurchaseDetails']] = relationship('SharedPurchaseDetails', back_populates='moment')
    shared_purchase_vendors: Mapped[list['SharedPurchaseVendors']] = relationship('SharedPurchaseVendors', back_populates='moment')
    community_coordination_details: Mapped[list['CommunityCoordinationDetails']] = relationship('CommunityCoordinationDetails', back_populates='moment')
    group_attachments: Mapped[list['GroupAttachments']] = relationship('GroupAttachments', back_populates='moment')
    group_attendance: Mapped[list['GroupAttendance']] = relationship('GroupAttendance', back_populates='moment')
    group_contributions: Mapped[list['GroupContributions']] = relationship('GroupContributions', back_populates='moment')
    group_decisions: Mapped[list['GroupDecisions']] = relationship('GroupDecisions', back_populates='moment')
    group_expenses: Mapped[list['GroupExpenses']] = relationship('GroupExpenses', back_populates='moment')
    group_live_feed: Mapped[list['GroupLiveFeed']] = relationship('GroupLiveFeed', back_populates='moment')
    group_memory_entries: Mapped[list['GroupMemoryEntries']] = relationship('GroupMemoryEntries', back_populates='moment')
    group_moment_work_items: Mapped[list['GroupMomentWorkItems']] = relationship('GroupMomentWorkItems', back_populates='moment')
    group_people_impact_scores: Mapped[list['GroupPeopleImpactScores']] = relationship('GroupPeopleImpactScores', back_populates='moment')
    group_polls: Mapped[list['GroupPolls']] = relationship('GroupPolls', back_populates='moment')
    group_updates: Mapped[list['GroupUpdates']] = relationship('GroupUpdates', back_populates='moment')
    shared_experience_memory_highlights: Mapped[list['SharedExperienceMemoryHighlights']] = relationship('SharedExperienceMemoryHighlights', back_populates='moment')
    shared_experience_planning_items: Mapped[list['SharedExperiencePlanningItems']] = relationship('SharedExperiencePlanningItems', back_populates='moment')
    shared_experience_settlements: Mapped[list['SharedExperienceSettlements']] = relationship('SharedExperienceSettlements', back_populates='moment')
    shared_goal_details: Mapped[list['SharedGoalDetails']] = relationship('SharedGoalDetails', back_populates='moment')
    shared_living_assets: Mapped[list['SharedLivingAssets']] = relationship('SharedLivingAssets', back_populates='moment')
    shared_living_resident_dynamics: Mapped[list['SharedLivingResidentDynamics']] = relationship('SharedLivingResidentDynamics', back_populates='moment')
    shared_living_residents: Mapped[list['SharedLivingResidents']] = relationship('SharedLivingResidents', back_populates='moment')
    shared_living_rules: Mapped[list['SharedLivingRules']] = relationship('SharedLivingRules', back_populates='moment')
    shared_living_tasks: Mapped[list['SharedLivingTasks']] = relationship('SharedLivingTasks', back_populates='moment')
    shared_purchase_contributors: Mapped[list['SharedPurchaseContributors']] = relationship('SharedPurchaseContributors', back_populates='moment')
    shared_purchase_items: Mapped[list['SharedPurchaseItems']] = relationship('SharedPurchaseItems', back_populates='moment')
    shared_purchase_ownership: Mapped[list['SharedPurchaseOwnership']] = relationship('SharedPurchaseOwnership', back_populates='moment')
    group_activity_edits: Mapped[list['GroupActivityEdits']] = relationship('GroupActivityEdits', back_populates='moment')
    group_moment_resources: Mapped[list['GroupMomentResources']] = relationship('GroupMomentResources', back_populates='moment')
    shared_living_maintenance: Mapped[list['SharedLivingMaintenance']] = relationship('SharedLivingMaintenance', back_populates='moment')
    shared_purchase_delivery: Mapped[list['SharedPurchaseDelivery']] = relationship('SharedPurchaseDelivery', back_populates='moment')


class GroupPeopleImpactScores(Base):
    __tablename__ = 'group_people_impact_scores'
    __table_args__ = (
        CheckConstraint('activity_score IS NULL OR activity_score >= 0::numeric AND activity_score <= 100::numeric', name='chk_gpis_activity_score'),
        CheckConstraint('contribution_score IS NULL OR contribution_score >= 0::numeric AND contribution_score <= 100::numeric', name='chk_gpis_contribution_score'),
        CheckConstraint('helpfulness_score IS NULL OR helpfulness_score >= 0::numeric AND helpfulness_score <= 100::numeric', name='chk_gpis_helpfulness_score'),
        CheckConstraint('impact_score >= 0::numeric AND impact_score <= 100::numeric', name='chk_gpis_score'),
        CheckConstraint("impact_type::text = ANY (ARRAY['MOST_ACTIVE'::character varying, 'MOST_HELPFUL'::character varying, 'TOP_CONTRIBUTOR'::character varying, 'MOST_CONSISTENT'::character varying, 'COMMUNITY_BUILDER'::character varying, 'MILESTONE_DRIVER'::character varying]::text[])", name='chk_gpis_type'),
        CheckConstraint('rank_no >= 1', name='chk_gpis_rank'),
        ForeignKeyConstraint(['member_id'], ['group_moment_members.member_id'], name='fk_gpis_member'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gpis_moment'),
        PrimaryKeyConstraint('impact_id', name='group_people_impact_scores_pkey')
    )

    impact_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    impact_type: Mapped[str] = mapped_column(String(100), nullable=False)
    impact_score: Mapped[decimal.Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    rank_no: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    badge_label: Mapped[Optional[str]] = mapped_column(String(150))
    supporting_metrics_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    activity_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    helpfulness_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    contribution_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_people_impact_scores')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_people_impact_scores')


class GroupPollOptions(Base):
    __tablename__ = 'group_poll_options'
    __table_args__ = (
        CheckConstraint('sort_order > 0', name='chk_gpo_sort'),
        ForeignKeyConstraint(['poll_id'], ['group_polls.poll_id'], name='fk_gpo_poll'),
        PrimaryKeyConstraint('option_id', name='group_poll_options_pkey'),
        Index('idx_poll_options_poll', 'poll_id')
    )

    option_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    poll_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    option_text: Mapped[str] = mapped_column(String(250), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    poll: Mapped['GroupPolls'] = relationship('GroupPolls', back_populates='group_poll_options')
    group_poll_votes: Mapped[list['GroupPollVotes']] = relationship('GroupPollVotes', back_populates='option')


class GroupPollVotes(Base):
    __tablename__ = 'group_poll_votes'
    __table_args__ = (
        ForeignKeyConstraint(['option_id'], ['group_poll_options.option_id'], name='fk_gpv_option'),
        ForeignKeyConstraint(['poll_id'], ['group_polls.poll_id'], name='fk_gpv_poll'),
        ForeignKeyConstraint(['voter_member_id'], ['group_moment_members.member_id'], name='fk_gpv_voter'),
        PrimaryKeyConstraint('vote_id', name='group_poll_votes_pkey'),
        Index('idx_poll_votes_poll', 'poll_id'),
        Index('idx_poll_votes_voter', 'voter_member_id')
    )

    vote_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    poll_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    option_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    voter_member_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    voted_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    rank_order: Mapped[Optional[int]] = mapped_column(Integer)

    option: Mapped['GroupPollOptions'] = relationship('GroupPollOptions', back_populates='group_poll_votes')
    poll: Mapped['GroupPolls'] = relationship('GroupPolls', back_populates='group_poll_votes')
    voter_member: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_poll_votes')


class GroupPolls(Base):
    __tablename__ = 'group_polls'
    __table_args__ = (
        CheckConstraint("poll_type::text = ANY (ARRAY['SINGLE_CHOICE'::character varying, 'MULTIPLE_CHOICE'::character varying, 'YES_NO'::character varying, 'RANKING'::character varying]::text[])", name='chk_gp_type'),
        CheckConstraint("status::text = ANY (ARRAY['OPEN'::character varying, 'CLOSED'::character varying, 'CANCELLED'::character varying]::text[])", name='chk_gp_status'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_gp_created_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gp_moment'),
        PrimaryKeyConstraint('poll_id', name='group_polls_pkey'),
        Index('idx_polls_end_date', 'end_date'),
        Index('idx_polls_moment', 'moment_id'),
        Index('idx_polls_status', 'status')
    )

    poll_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    question: Mapped[str] = mapped_column(String(300), nullable=False)
    poll_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    allow_multiple_votes: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'OPEN'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_polls')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_polls')
    group_poll_options: Mapped[list['GroupPollOptions']] = relationship('GroupPollOptions', back_populates='poll')
    group_poll_votes: Mapped[list['GroupPollVotes']] = relationship('GroupPollVotes', back_populates='poll')


class GroupPulseSnapshots(Base):
    __tablename__ = 'group_pulse_snapshots'
    __table_args__ = (
        CheckConstraint('pulse_score >= 0::numeric AND pulse_score <= 100::numeric', name='chk_gps_pulse_score'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gps_moment'),
        PrimaryKeyConstraint('snapshot_id', name='group_pulse_snapshots_pkey'),
        Index('idx_gps_attention_items_json', 'attention_items_json', postgresql_using='gin'),
        Index('idx_gps_budget_snapshot_json', 'budget_snapshot_json', postgresql_using='gin'),
        Index('idx_gps_date', 'snapshot_date'),
        Index('idx_gps_extended_metrics_json', 'extended_metrics_json', postgresql_using='gin'),
        Index('idx_gps_health_driver_json', 'health_driver_json', postgresql_using='gin'),
        Index('idx_gps_hero_snapshot_json', 'hero_snapshot_json', postgresql_using='gin'),
        Index('idx_gps_moment', 'moment_id'),
        Index('idx_gps_next_best_action_json', 'next_best_action_json', postgresql_using='gin')
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    completion_percentage: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    participation_percentage: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    funding_percentage: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    active_members: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    active_tasks: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    open_items: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    pulse_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    hero_snapshot_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    health_driver_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    progress_context_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    budget_snapshot_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    participation_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    timeline_preview_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    insights_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    extended_metrics_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    attention_items_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    next_best_action_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_pulse_snapshots')


class GroupQuickAddConfig(Base):
    __tablename__ = 'group_quick_add_config'
    __table_args__ = (
        PrimaryKeyConstraint('config_id', name='group_quick_add_config_pkey'),
        Index('idx_gqac_moment_type_support', 'moment_type_support'),
        Index('idx_gqac_quick_add_category', 'quick_add_category'),
        Index('idx_quick_add_profile', 'moment_type', 'moment_profile')
    )

    config_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    moment_profile: Mapped[str] = mapped_column(String(100), nullable=False)
    module_code: Mapped[str] = mapped_column(String(100), nullable=False)
    module_label: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    quick_add_category: Mapped[Optional[str]] = mapped_column(String(100))
    moment_type_support: Mapped[Optional[str]] = mapped_column(String(50))


class GroupQuickAddEvents(Base):
    __tablename__ = 'group_quick_add_events'
    __table_args__ = (
        CheckConstraint("event_action::text = ANY (ARRAY['CREATED'::character varying, 'EDITED'::character varying, 'DELETED'::character varying]::text[])", name='chk_qae_action'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_qae_moment'),
        PrimaryKeyConstraint('event_id', name='group_quick_add_events_pkey'),
        Index('idx_qae_module', 'module_code'),
        Index('idx_qae_moment', 'moment_id'),
        Index('idx_qae_time', 'event_time')
    )

    event_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    module_code: Mapped[str] = mapped_column(String(100), nullable=False)
    event_ref_table: Mapped[str] = mapped_column(String(150), nullable=False)
    event_ref_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_action: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'CREATED'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    event_payload_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_quick_add_events')
    group_attachments: Mapped[list['GroupAttachments']] = relationship('GroupAttachments', back_populates='event')
    group_live_feed: Mapped[list['GroupLiveFeed']] = relationship('GroupLiveFeed', back_populates='event')
    group_memory_entries: Mapped[list['GroupMemoryEntries']] = relationship('GroupMemoryEntries', back_populates='source_event')
    shared_experience_memory_highlights: Mapped[list['SharedExperienceMemoryHighlights']] = relationship('SharedExperienceMemoryHighlights', back_populates='source_event')


class GroupRecommendations(Base):
    __tablename__ = 'group_recommendations'
    __table_args__ = (
        CheckConstraint("confidence_level IS NULL OR (confidence_level::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying]::text[]))", name='chk_gr_confidence_level'),
        CheckConstraint('impact_score IS NULL OR impact_score >= 0::numeric AND impact_score <= 100::numeric', name='chk_gr_impact_score'),
        CheckConstraint("priority::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying]::text[])", name='chk_gr_priority'),
        CheckConstraint("status::text = ANY (ARRAY['OPEN'::character varying, 'ACCEPTED'::character varying, 'DISMISSED'::character varying, 'COMPLETED'::character varying]::text[])", name='chk_gr_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gr_moment'),
        PrimaryKeyConstraint('recommendation_id', name='group_recommendations_pkey'),
        Index('idx_gr_action_deep_link', 'action_deep_link'),
        Index('idx_gr_expected_impact_json', 'expected_impact_json', postgresql_using='gin'),
        Index('idx_gr_impact_score', 'impact_score'),
        Index('idx_gr_life_space', 'related_life_space_id'),
        Index('idx_gr_moment', 'moment_id'),
        Index('idx_gr_priority', 'priority'),
        Index('idx_gr_status', 'status')
    )

    recommendation_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation_category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    priority: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'OPEN'::character varying"))
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    recommendation_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    actioned_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expected_impact_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    impact_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    confidence_level: Mapped[Optional[str]] = mapped_column(String(30))
    action_deeplink: Mapped[Optional[str]] = mapped_column(Text)
    related_life_space_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    action_label: Mapped[Optional[str]] = mapped_column(String(100))
    action_deep_link: Mapped[Optional[str]] = mapped_column(String(250))

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_recommendations')


class GroupSignals(Base):
    __tablename__ = 'group_signals'
    __table_args__ = (
        CheckConstraint("priority::text = ANY (ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying]::text[])", name='chk_gs_priority'),
        CheckConstraint("severity IS NULL OR (severity::text = ANY (ARRAY['INFO'::character varying, 'WARN'::character varying, 'CRITICAL'::character varying]::text[]))", name='chk_group_signals_severity'),
        CheckConstraint("signal_status IS NULL OR (signal_status::text = ANY (ARRAY['OPEN'::character varying, 'CLOSED'::character varying, 'DISMISSED'::character varying]::text[]))", name='chk_group_signals_status'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gs_moment'),
        PrimaryKeyConstraint('signal_id', name='group_signals_pkey'),
        Index('idx_gs_active', 'is_active'),
        Index('idx_gs_category', 'signal_category'),
        Index('idx_gs_moment', 'moment_id'),
        Index('idx_gs_related_budget_plan', 'related_budget_plan_id'),
        Index('idx_gs_severity', 'severity'),
        Index('idx_gs_signal_status', 'signal_status')
    )

    signal_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_category: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_title: Mapped[str] = mapped_column(String(250), nullable=False)
    priority: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    signal_description: Mapped[Optional[str]] = mapped_column(Text)
    signal_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    severity: Mapped[Optional[str]] = mapped_column(String(30))
    signal_status: Mapped[Optional[str]] = mapped_column(String(30), server_default=text("'OPEN'::character varying"))
    display_order: Mapped[Optional[int]] = mapped_column(Integer)
    action_ref: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    source_widget: Mapped[Optional[str]] = mapped_column(String(100))
    related_budget_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_signals')


class GroupUpdates(Base):
    __tablename__ = 'group_updates'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['POSTED'::character varying, 'EDITED'::character varying, 'ARCHIVED'::character varying]::text[])", name='chk_gu_status'),
        CheckConstraint("visibility::text = ANY (ARRAY['EVERYONE'::character varying, 'ORGANIZERS'::character varying, 'SELECTED'::character varying]::text[])", name='chk_gu_visibility'),
        ForeignKeyConstraint(['created_by'], ['group_moment_members.member_id'], name='fk_gu_created_by'),
        ForeignKeyConstraint(['moment_id'], ['group_moments.moment_id'], name='fk_gu_moment'),
        PrimaryKeyConstraint('update_id', name='group_updates_pkey'),
        Index('idx_updates_category', 'category'),
        Index('idx_updates_created', 'created_at'),
        Index('idx_updates_moment', 'moment_id')
    )

    update_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    visibility: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'EVERYONE'::character varying"))
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'POSTED'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    group_moment_members: Mapped['GroupMomentMembers'] = relationship('GroupMomentMembers', back_populates='group_updates')
    moment: Mapped['GroupMoments'] = relationship('GroupMoments', back_populates='group_updates')
