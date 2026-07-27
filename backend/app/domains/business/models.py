"""Business domain SQLAlchemy models (business_*, operations_*, runway_*, team_* tables, including business life and memory sub-features).

Auto-generated from the Alembic migrations via reflection.
"""
from __future__ import annotations

from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.users.models import Base


class BusinessWorkspaces(Base):
    """Company workspace — Business auth/home boundary (multi-company)."""

    __tablename__ = "business_workspaces"
    __table_args__ = (
        PrimaryKeyConstraint("workspace_id", name="business_workspaces_pkey"),
        Index("idx_business_workspaces_owned_by", "owned_by"),
        Index("idx_business_workspaces_status", "status"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    owned_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'"))
    logo_url: Mapped[Optional[str]] = mapped_column(Text)
    industry: Mapped[Optional[str]] = mapped_column(String(128))
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'INR'"))
    timezone: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default=text("'Asia/Kolkata'")
    )
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class BusinessWorkspaceMembers(Base):
    __tablename__ = "business_workspace_members"
    __table_args__ = (
        PrimaryKeyConstraint("member_id", name="business_workspace_members_pkey"),
        ForeignKeyConstraint(
            ["workspace_id"],
            ["business_workspaces.workspace_id"],
            name="fk_workspace_members_workspace",
            ondelete="CASCADE",
        ),
        Index("uq_workspace_members_workspace_user", "workspace_id", "user_id", unique=True),
        Index("idx_workspace_members_user", "user_id"),
        CheckConstraint("role IN ('OWNER', 'MANAGER', 'MEMBER')", name="chk_workspace_member_role"),
        CheckConstraint(
            "status IN ('ACTIVE', 'INVITED', 'REMOVED')",
            name="chk_workspace_member_status",
        ),
    )

    member_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'MEMBER'"))
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'ACTIVE'"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class BusinessWorkspaceInvitations(Base):
    __tablename__ = "business_workspace_invitations"
    __table_args__ = (
        PrimaryKeyConstraint("invitation_id", name="business_workspace_invitations_pkey"),
        ForeignKeyConstraint(
            ["workspace_id"],
            ["business_workspaces.workspace_id"],
            name="fk_workspace_invites_workspace",
            ondelete="CASCADE",
        ),
        Index("uq_workspace_invite_token", "token", unique=True),
        Index("idx_workspace_invites_workspace", "workspace_id"),
        CheckConstraint("role IN ('OWNER', 'MANAGER', 'MEMBER')", name="chk_workspace_invite_role"),
        CheckConstraint(
            "status IN ('PENDING', 'SENT', 'ACCEPTED', 'REVOKED', 'EXPIRED')",
            name="chk_workspace_invite_status",
        ),
    )

    invitation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    invited_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    invitee_email: Mapped[Optional[str]] = mapped_column(String(255))
    invitee_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    role: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'MEMBER'"))
    token: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'PENDING'"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    accepted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)



class BusinessActivityCenterItems(Base):
    __tablename__ = 'business_activity_center_items'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_activity_center_items_moment_id_fkey'),
        PrimaryKeyConstraint('activity_center_item_id', name='business_activity_center_items_pkey'),
        Index('idx_activity_center_moment', 'moment_id'),
        Index('idx_activity_center_occurred', 'occurred_at')
    )

    activity_center_item_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    occurred_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    source_table: Mapped[Optional[str]] = mapped_column(String(100))
    source_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    activity_type: Mapped[Optional[str]] = mapped_column(String(100))
    activity_title: Mapped[Optional[str]] = mapped_column(String(255))
    activity_summary: Mapped[Optional[str]] = mapped_column(Text)
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    actor_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actor_name: Mapped[Optional[str]] = mapped_column(String(255))
    activity_status: Mapped[Optional[str]] = mapped_column(String(50))
    permission_badge: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_activity_center_items')


class BusinessActivityPermissions(Base):
    __tablename__ = 'business_activity_permissions'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_activity_permissions_moment_id_fkey'),
        PrimaryKeyConstraint('permission_id', name='business_activity_permissions_pkey'),
        {'comment': 'Derived permission cache for Activity Center rendering.'}
    )

    permission_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_record_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    granted_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    can_view: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    can_edit: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    can_delete: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    can_approve: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    permission_reason: Mapped[Optional[str]] = mapped_column(Text)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_activity_permissions')


class BusinessActivitySourceMapping(Base):
    __tablename__ = 'business_activity_source_mapping'
    __table_args__ = (
        PrimaryKeyConstraint('mapping_id', name='business_activity_source_mapping_pkey'),
    )

    mapping_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    title_field: Mapped[str] = mapped_column(String(100), nullable=False)
    description_field: Mapped[Optional[str]] = mapped_column(String(100))
    status_field: Mapped[Optional[str]] = mapped_column(String(100))
    date_field: Mapped[Optional[str]] = mapped_column(String(100))
    amount_field: Mapped[Optional[str]] = mapped_column(String(100))
    active_flag: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))


class BusinessAttachmentFiles(Base):
    __tablename__ = 'business_attachment_files'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_attachment_moment'),
        PrimaryKeyConstraint('file_id', name='business_attachment_files_pkey'),
        Index('idx_attachment_moment', 'moment_id'),
        Index('idx_attachment_source', 'source_table', 'source_record_id')
    )

    file_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_record_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_attachment_files')


class BusinessAttentionItems(Base):
    __tablename__ = 'business_attention_items'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_attention_items_moment_id_fkey'),
        PrimaryKeyConstraint('attention_id', name='business_attention_items_pkey'),
        Index('idx_attention_moment', 'moment_id'),
        Index('idx_attention_status', 'status')
    )

    attention_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    attention_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'open'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    source_table: Mapped[Optional[str]] = mapped_column(String(100))
    source_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    generated_by: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'system'::character varying"))
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_attention_items')


class BusinessAuditHistory(Base):
    __tablename__ = 'business_audit_history'
    __table_args__ = (
        CheckConstraint("change_type::text = ANY (ARRAY['create'::character varying, 'edit'::character varying, 'delete'::character varying, 'restore'::character varying, 'approve'::character varying, 'reject'::character varying, 'resolve'::character varying]::text[])", name='chk_audit_change_type'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_audit_moment'),
        PrimaryKeyConstraint('audit_id', name='business_audit_history_pkey'),
        Index('idx_audit_changed_at', 'changed_at'),
        Index('idx_audit_moment', 'moment_id'),
        Index('idx_audit_source', 'source_table', 'source_record_id')
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_record_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    new_value: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    changed_by_name: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    change_reason: Mapped[Optional[str]] = mapped_column(Text)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_audit_history')


class BusinessDriverFormulaRegistry(Base):
    __tablename__ = 'business_driver_formula_registry'
    __table_args__ = (
        PrimaryKeyConstraint('driver_formula_id', name='business_driver_formula_registry_pkey'),
        Index('idx_driver_formula_moment_type', 'moment_type'),
        Index('uq_driver_formula_registry', 'moment_type', 'driver_code', postgresql_where='(active_flag = true)', unique=True)
    )

    driver_formula_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    driver_code: Mapped[str] = mapped_column(String(100), nullable=False)
    driver_name: Mapped[str] = mapped_column(String(255), nullable=False)
    driver_weight: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    source_table: Mapped[str] = mapped_column(String(255), nullable=False)
    formula_description: Mapped[str] = mapped_column(Text, nullable=False)
    source_column: Mapped[Optional[str]] = mapped_column(String(255))
    active_flag: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class BusinessHealthDriverScores(Base):
    __tablename__ = 'business_health_driver_scores'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_health_driver_scores_moment_id_fkey'),
        PrimaryKeyConstraint('score_id', name='business_health_driver_scores_pkey'),
        Index('idx_health_driver_code', 'driver_code'),
        Index('idx_health_driver_moment', 'moment_id')
    )

    score_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    driver_code: Mapped[str] = mapped_column(String(100), nullable=False)
    driver_name: Mapped[str] = mapped_column(String(255), nullable=False)
    driver_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('0'))
    driver_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'stable'::character varying"))
    calculated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    trend_direction: Mapped[Optional[str]] = mapped_column(String(30))
    source_table: Mapped[Optional[str]] = mapped_column(String(100))
    source_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_health_driver_scores')


class BusinessLifeConnections(Base):
    __tablename__ = 'business_life_connections'
    __table_args__ = (
        PrimaryKeyConstraint('connection_id', name='business_life_connections_pkey'),
        Index('idx_life_connection_workspace', 'workspace_id')
    )

    connection_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    source_dimension: Mapped[Optional[str]] = mapped_column(String(100))
    source_label: Mapped[Optional[str]] = mapped_column(String(255))
    source_change: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))
    influence_type: Mapped[Optional[str]] = mapped_column(String(50))
    influence_strength: Mapped[Optional[str]] = mapped_column(String(50))
    target_dimension: Mapped[Optional[str]] = mapped_column(String(100))
    target_label: Mapped[Optional[str]] = mapped_column(String(255))
    target_change: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))


class BusinessLifeDimensions(Base):
    __tablename__ = 'business_life_dimensions'
    __table_args__ = (
        PrimaryKeyConstraint('dimension_id', name='business_life_dimensions_pkey'),
        Index('idx_life_dimension_workspace', 'workspace_id')
    )

    dimension_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    dimension_type: Mapped[str] = mapped_column(String(100), nullable=False)
    dimension_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dimension_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    dimension_status: Mapped[Optional[str]] = mapped_column(String(50))
    trend_direction: Mapped[Optional[str]] = mapped_column(String(30))
    trend_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    active_moment_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))


class BusinessLifeInsights(Base):
    __tablename__ = 'business_life_insights'
    __table_args__ = (
        PrimaryKeyConstraint('life_insight_id', name='business_life_insights_pkey'),
        Index('idx_life_insights_type', 'insight_type'),
        Index('idx_life_insights_workspace', 'workspace_id')
    )

    life_insight_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    insight_type: Mapped[str] = mapped_column(String(100), nullable=False)
    insight_title: Mapped[str] = mapped_column(String(255), nullable=False)
    insight_body: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    insight_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    priority: Mapped[Optional[str]] = mapped_column(String(30))
    source_dimension: Mapped[Optional[str]] = mapped_column(String(100))
    insight_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'active'::character varying"))


class BusinessLifeSnapshots(Base):
    __tablename__ = 'business_life_snapshots'
    __table_args__ = (
        PrimaryKeyConstraint('snapshot_id', name='business_life_snapshots_pkey'),
        Index('idx_life_snapshot_workspace', 'workspace_id')
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    life_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    life_status: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    people_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    finance_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    operations_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    vendor_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    growth_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    active_moment_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    strongest_dimension: Mapped[Optional[str]] = mapped_column(String(100))
    weakest_dimension: Mapped[Optional[str]] = mapped_column(String(100))
    leverage_dimension: Mapped[Optional[str]] = mapped_column(String(100))
    drift_detected: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    life_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    included_moment_types: Mapped[Optional[dict]] = mapped_column(JSONB)


class BusinessLiveFeed(Base):
    __tablename__ = 'business_live_feed'
    __table_args__ = (
        CheckConstraint("priority IS NULL OR (priority::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[]))", name='chk_live_priority'),
        CheckConstraint("visibility::text = ANY (ARRAY['team_only'::character varying, 'leadership'::character varying, 'organization'::character varying, 'runway_roles'::character varying, 'runway_owners'::character varying, 'finance_leads'::character varying, 'all_runway_participants'::character varying, 'operations_roles'::character varying, 'operations_owners'::character varying, 'operations_leads'::character varying, 'budget_controllers'::character varying, 'all_operations_participants'::character varying]::text[])", name='chk_live_visibility'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_live_feed_moment'),
        PrimaryKeyConstraint('feed_id', name='business_live_feed_pkey'),
        Index('idx_business_live_feed_operations_source', 'source_table', 'source_record_id'),
        Index('idx_business_live_feed_runway_source', 'source_table', 'source_record_id'),
        Index('idx_live_feed_event_type', 'event_type'),
        Index('idx_live_feed_moment_business_live_feed', 'moment_id'),
        Index('idx_live_feed_source', 'source_table', 'source_record_id'),
        Index('idx_live_feed_timestamp', 'event_timestamp')
    )

    feed_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_record_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    actor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    event_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    visibility: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'team_only'::character varying"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    activity_center_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    detail_message: Mapped[Optional[str]] = mapped_column(Text)
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 2))
    priority: Mapped[Optional[str]] = mapped_column(String(20))
    edit_mode: Mapped[Optional[str]] = mapped_column(String(50))
    permission_badge: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_live_feed')


class BusinessMemoryLearnings(Base):
    __tablename__ = 'business_memory_learnings'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_memory_learnings_moment_id_fkey'),
        PrimaryKeyConstraint('learning_id', name='business_memory_learnings_pkey')
    )

    learning_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    learning_type: Mapped[Optional[str]] = mapped_column(String(100))
    learning_title: Mapped[Optional[str]] = mapped_column(String(255))
    learning_summary: Mapped[Optional[str]] = mapped_column(Text)
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    derived_from_count: Mapped[Optional[int]] = mapped_column(Integer)
    learning_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'active'::character varying"))

    moment: Mapped[Optional['BusinessMoments']] = relationship('BusinessMoments', back_populates='business_memory_learnings')
    business_memory_snapshots: Mapped[list['BusinessMemorySnapshots']] = relationship('BusinessMemorySnapshots', back_populates='strongest_learning')


class BusinessMemoryPatterns(Base):
    __tablename__ = 'business_memory_patterns'
    __table_args__ = (
        CheckConstraint("pattern_status::text = ANY (ARRAY['active'::character varying, 'archived'::character varying]::text[])", name='chk_pattern_status'),
        CheckConstraint("pattern_type::text = ANY (ARRAY['vendor'::character varying, 'vendor_pattern'::character varying, 'spend_pattern'::character varying, 'approval_pattern'::character varying, 'risk_pattern'::character varying, 'ownership_pattern'::character varying, 'cash_inflow_pattern'::character varying, 'burn_pattern'::character varying, 'runway_risk_pattern'::character varying, 'decision_pattern'::character varying, 'financial_update_pattern'::character varying, 'net_burn_pattern'::character varying, 'operations_budget_pattern'::character varying, 'operations_vendor_pattern'::character varying, 'operations_approval_pattern'::character varying, 'operations_issue_pattern'::character varying, 'operations_improvement_pattern'::character varying]::text[])", name='chk_business_memory_pattern_type'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_memory_pattern_moment'),
        PrimaryKeyConstraint('pattern_id', name='business_memory_patterns_pkey'),
        Index('idx_business_memory_patterns_operations_type', 'moment_id', 'pattern_type'),
        Index('idx_business_memory_patterns_runway_type', 'moment_id', 'pattern_type'),
        Index('idx_memory_pattern_moment', 'moment_id'),
        Index('idx_memory_pattern_strength', 'pattern_strength'),
        Index('idx_memory_pattern_type', 'pattern_type'),
        Index('idx_memory_pattern_workspace', 'workspace_id')
    )

    pattern_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    pattern_type: Mapped[str] = mapped_column(String(100), nullable=False)
    pattern_title: Mapped[str] = mapped_column(String(255), nullable=False)
    observation_text: Mapped[str] = mapped_column(Text, nullable=False)
    first_observed_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    last_observed_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    pattern_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'active'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    display_priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('100'))
    source_metric: Mapped[Optional[str]] = mapped_column(String(255))
    confidence_level: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    pattern_strength: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_memory_patterns')


class BusinessMemorySnapshots(Base):
    __tablename__ = 'business_memory_snapshots'
    __table_args__ = (
        ForeignKeyConstraint(['strongest_learning_id'], ['business_memory_learnings.learning_id'], name='fk_memory_snapshot_learning'),
        ForeignKeyConstraint(['strongest_wisdom_id'], ['business_wisdom.wisdom_id'], name='fk_memory_snapshot_wisdom'),
        PrimaryKeyConstraint('snapshot_id', name='business_memory_snapshots_pkey'),
        Index('idx_memory_snapshot_workspace', 'workspace_id')
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    memory_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    memory_status: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    learning_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    playbook_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    risk_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    strongest_learning_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    strongest_wisdom_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    memory_score_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    success_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    wisdom_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))

    strongest_learning: Mapped[Optional['BusinessMemoryLearnings']] = relationship('BusinessMemoryLearnings', back_populates='business_memory_snapshots')
    strongest_wisdom: Mapped[Optional['BusinessWisdom']] = relationship('BusinessWisdom', back_populates='business_memory_snapshots')


class BusinessMomentGovernance(Base):
    __tablename__ = 'business_moment_governance'
    __table_args__ = (
        CheckConstraint("operational_visibility::text = ANY (ARRAY['private'::character varying, 'leadership'::character varying, 'organization'::character varying]::text[])", name='chk_operational_visibility'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_governance_moment'),
        PrimaryKeyConstraint('governance_id', name='business_moment_governance_pkey'),
        Index('uq_business_moment_governance', 'moment_id', unique=True)
    )

    governance_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    send_invites_on_activation: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    operational_visibility: Mapped[str] = mapped_column(String(50), nullable=False)
    notify_approvals: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    notify_spending_activity: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    notify_issues_risks: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    notify_team_updates: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    approval_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    activation_ready: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    runway_approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    operations_approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    activation_ready_reason: Mapped[Optional[str]] = mapped_column(Text)
    activated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    activated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    runway_visibility_roles: Mapped[Optional[dict]] = mapped_column(JSONB)
    runway_alert_roles: Mapped[Optional[dict]] = mapped_column(JSONB)
    runway_alert_conditions: Mapped[Optional[dict]] = mapped_column(JSONB)
    runway_approval_rules: Mapped[Optional[dict]] = mapped_column(JSONB)
    operations_visibility_roles: Mapped[Optional[dict]] = mapped_column(JSONB)
    operations_alert_roles: Mapped[Optional[dict]] = mapped_column(JSONB)
    operations_alert_conditions: Mapped[Optional[dict]] = mapped_column(JSONB)
    operations_approval_rules: Mapped[Optional[dict]] = mapped_column(JSONB)
    operations_monitoring_level: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_moment_governance')


class BusinessMomentHighlights(Base):
    __tablename__ = 'business_moment_highlights'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_moment_highlights_moment_id_fkey'),
        PrimaryKeyConstraint('highlight_id', name='business_moment_highlights_pkey'),
        Index('idx_moment_highlight_moment', 'moment_id')
    )

    highlight_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    highlight_type: Mapped[str] = mapped_column(String(100), nullable=False)
    highlight_title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    highlight_summary: Mapped[Optional[str]] = mapped_column(Text)
    source_table: Mapped[Optional[str]] = mapped_column(String(100))
    source_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    impact_level: Mapped[Optional[str]] = mapped_column(String(50))
    highlight_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'active'::character varying"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_moment_highlights')


class BusinessMomentInvitations(Base):
    __tablename__ = 'business_moment_invitations'
    __table_args__ = (
        CheckConstraint("invite_method::text = ANY (ARRAY['email'::character varying, 'mobile'::character varying, 'username'::character varying, 'qr'::character varying]::text[])", name='chk_invite_method'),
        CheckConstraint("invite_status::text = ANY (ARRAY['pending'::character varying, 'sent'::character varying, 'accepted'::character varying, 'expired'::character varying, 'cancelled'::character varying]::text[])", name='chk_invite_status'),
        ForeignKeyConstraint(['member_id'], ['business_moment_members.member_id'], name='fk_invitation_member'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_invitation_moment'),
        PrimaryKeyConstraint('invite_id', name='business_moment_invitations_pkey'),
        Index('idx_business_invitation_moment', 'moment_id'),
        Index('idx_business_invitation_status', 'invite_status')
    )

    invite_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    invite_method: Mapped[str] = mapped_column(String(50), nullable=False)
    invite_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'pending'::character varying"))
    invite_target: Mapped[str] = mapped_column(String(255), nullable=False)
    send_on_activation: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    qr_token: Mapped[Optional[str]] = mapped_column(String(500))
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    accepted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    local_id: Mapped[Optional[str]] = mapped_column(String(64))
    channel: Mapped[Optional[str]] = mapped_column(String(32))
    revoked_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    send_idempotency_key: Mapped[Optional[str]] = mapped_column(String(128))

    member: Mapped[Optional['BusinessMomentMembers']] = relationship('BusinessMomentMembers', back_populates='business_moment_invitations')
    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_moment_invitations')


class BusinessMomentMembers(Base):
    __tablename__ = 'business_moment_members'
    __table_args__ = (
        CheckConstraint("member_status::text = ANY (ARRAY['configured'::character varying, 'invited'::character varying, 'active'::character varying, 'removed'::character varying]::text[])", name='chk_member_status'),
        CheckConstraint("role::text = ANY (ARRAY['Team Member'::character varying, 'Team Lead'::character varying, 'Budget Owner'::character varying, 'Approver'::character varying, 'Observer'::character varying, 'Runway Owner'::character varying, 'Finance Lead'::character varying, 'Operations Lead'::character varying, 'Financial Contributor'::character varying, 'Viewer'::character varying, 'Operations Owner'::character varying, 'Budget Controller'::character varying, 'Contributor'::character varying]::text[])", name='chk_member_role'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_member_moment'),
        PrimaryKeyConstraint('member_id', name='business_moment_members_pkey'),
        Index('idx_business_members_moment', 'moment_id'),
        Index('idx_business_members_role', 'role'),
        Index('idx_business_members_status', 'member_status'),
        Index('idx_member_operations_permissions', 'can_add_operations_records', 'can_edit_operations_records'),
        Index('idx_member_runway_permissions', 'can_add_runway_transactions', 'can_edit_financial_entries')
    )

    member_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    member_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'configured'::character varying"))
    is_team_lead: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    is_budget_owner: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_edit_own_entries: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    can_edit_team_entries: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_edit_expense_entries: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    added_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    can_add_runway_transactions: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_edit_financial_entries: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_manage_runway_settings: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_approve_runway_changes: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_add_operations_records: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_edit_operations_records: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_edit_own_operations_records: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_approve_operations_requests: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_delete_operations_records: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_manage_operations_settings: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    mobile: Mapped[Optional[str]] = mapped_column(String(50))
    username: Mapped[Optional[str]] = mapped_column(String(100))
    local_id: Mapped[Optional[str]] = mapped_column(String(64))
    permission_profile: Mapped[Optional[str]] = mapped_column(String(64))
    permission_version: Mapped[Optional[int]] = mapped_column(Integer)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_moment_members')
    business_moment_invitations: Mapped[list['BusinessMomentInvitations']] = relationship('BusinessMomentInvitations', back_populates='member')
    team_activities: Mapped[list['TeamActivities']] = relationship('TeamActivities', back_populates='activity_owner')
    team_approval_requests_approver: Mapped[list['TeamApprovalRequests']] = relationship('TeamApprovalRequests', foreign_keys='[TeamApprovalRequests.approver_id]', back_populates='approver')
    team_approval_requests_requested_by: Mapped[list['TeamApprovalRequests']] = relationship('TeamApprovalRequests', foreign_keys='[TeamApprovalRequests.requested_by]', back_populates='business_moment_members')
    team_issue_risks: Mapped[list['TeamIssueRisks']] = relationship('TeamIssueRisks', back_populates='owner')


class BusinessMomentMetrics(Base):
    __tablename__ = 'business_moment_metrics'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_moment_metrics_moment'),
        PrimaryKeyConstraint('metric_id', name='business_moment_metrics_pkey'),
        Index('idx_business_moment_metrics_operations', 'moment_id'),
        Index('idx_business_moment_metrics_runway', 'moment_id'),
        Index('uq_moment_metrics', 'moment_id', unique=True)
    )

    metric_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    members_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    activities_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    pending_approvals: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    open_risks: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    spend_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    last_updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    cash_available: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    estimated_runway_months: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    cash_inflow_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    expense_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    risk_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    decision_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    net_burn: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    budget_category_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    operations_budget_used_total: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    operations_active_issue_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    operations_approval_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    operations_improvement_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    recent_wins_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    timeline_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    last_activity_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    operating_currency: Mapped[Optional[str]] = mapped_column(String(10), server_default=text("'INR'::character varying"))
    last_operations_activity_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    latest_spend_title: Mapped[Optional[str]] = mapped_column(String(255))
    latest_issue_title: Mapped[Optional[str]] = mapped_column(String(255))
    latest_approval_status: Mapped[Optional[str]] = mapped_column(String(50))
    latest_improvement_title: Mapped[Optional[str]] = mapped_column(String(255))
    operations_operating_currency: Mapped[Optional[str]] = mapped_column(String(10), server_default=text("'INR'::character varying"))
    progress_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    progress_status: Mapped[Optional[str]] = mapped_column(String(50))
    continue_cta_label: Mapped[Optional[str]] = mapped_column(String(100))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_moment_metrics')


class BusinessMomentSetup(Base):
    __tablename__ = 'business_moment_setup'
    __table_args__ = (
        CheckConstraint('monthly_budget IS NULL OR monthly_budget >= 0::numeric', name='chk_budget'),
        CheckConstraint("team_size::text = ANY (ARRAY['just_me'::character varying, '2_5'::character varying, '6_15'::character varying, '16_50'::character varying, '50_plus'::character varying]::text[])", name='chk_team_size'),
        CheckConstraint("visibility::text = ANY (ARRAY['team_only'::character varying, 'leadership'::character varying, 'organization'::character varying]::text[])", name='chk_visibility'),
        CheckConstraint("work_style::text = ANY (ARRAY['planned'::character varying, 'mixed'::character varying, 'fast_response'::character varying]::text[])", name='chk_work_style'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_setup_moment'),
        PrimaryKeyConstraint('setup_id', name='business_moment_setup_pkey'),
        Index('uq_business_moment_setup', 'moment_id', unique=True)
    )

    setup_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)
    team_size: Mapped[str] = mapped_column(String(50), nullable=False)
    budget_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    work_style: Mapped[Optional[str]] = mapped_column(String(50))
    visibility: Mapped[Optional[str]] = mapped_column(String(50))
    team_owner_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    custom_purpose: Mapped[Optional[str]] = mapped_column(String(255))
    monthly_budget: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 2))
    team_name: Mapped[Optional[str]] = mapped_column(String(255))
    country_code: Mapped[Optional[str]] = mapped_column(String(8))
    locale: Mapped[Optional[str]] = mapped_column(String(32))
    timezone: Mapped[Optional[str]] = mapped_column(String(64))
    review_cycle: Mapped[Optional[str]] = mapped_column(String(32))
    monthly_budget_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    setup_extras: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_moment_setup')


class BusinessMomentStructure(Base):
    __tablename__ = 'business_moment_structure'
    __table_args__ = (
        CheckConstraint('approval_threshold >= 0::numeric', name='chk_approval_threshold'),
        CheckConstraint("coordination_style::text = ANY (ARRAY['independent'::character varying, 'cross_functional'::character varying, 'leadership_driven'::character varying, 'shared_ownership'::character varying]::text[])", name='chk_coordination_style'),
        CheckConstraint("monitoring_level::text = ANY (ARRAY['basic'::character varying, 'standard'::character varying, 'high_visibility'::character varying]::text[])", name='chk_monitoring_level'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_structure_moment'),
        PrimaryKeyConstraint('structure_id', name='business_moment_structure_pkey'),
        Index('uq_business_moment_structure', 'moment_id', unique=True)
    )

    structure_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    roles_supported: Mapped[dict] = mapped_column(JSONB, nullable=False)
    approver_role: Mapped[str] = mapped_column(String(100), nullable=False)
    approval_threshold: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    escalation_contact_role: Mapped[str] = mapped_column(String(100), nullable=False)
    coordination_style: Mapped[str] = mapped_column(String(50), nullable=False)
    monitoring_level: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    custom_approver_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    approval_threshold_label: Mapped[Optional[str]] = mapped_column(String(100))
    custom_escalation_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    approval_threshold_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    structure_extras: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_moment_structure')


class BusinessMoments(Base):
    __tablename__ = 'business_moments'
    __table_args__ = (
        CheckConstraint("moment_type::text = ANY (ARRAY['team_operations'::character varying, 'business_runway'::character varying, 'business_operations'::character varying, 'project_operations'::character varying, 'event_operations'::character varying, 'department_operations'::character varying, 'vendor_operations'::character varying, 'custom_operational_moment'::character varying]::text[])", name='chk_business_moment_type'),
        CheckConstraint("status::text = ANY (ARRAY['draft'::character varying, 'configured'::character varying, 'active'::character varying, 'completed'::character varying, 'archived'::character varying]::text[])", name='chk_business_moment_status'),
        PrimaryKeyConstraint('moment_id', name='business_moments_pkey'),
        Index('idx_business_moments_status', 'status'),
        Index('idx_business_moments_type', 'moment_type'),
        Index('idx_business_moments_workspace', 'workspace_id')
    )

    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    moment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=text("'draft'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    activated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    ai_signals: Mapped[list['AiSignals']] = relationship('AiSignals', back_populates='moment')
    business_activity_center_items: Mapped[list['BusinessActivityCenterItems']] = relationship('BusinessActivityCenterItems', back_populates='moment')
    business_activity_permissions: Mapped[list['BusinessActivityPermissions']] = relationship('BusinessActivityPermissions', back_populates='moment')
    business_attachment_files: Mapped[list['BusinessAttachmentFiles']] = relationship('BusinessAttachmentFiles', back_populates='moment')
    business_attention_items: Mapped[list['BusinessAttentionItems']] = relationship('BusinessAttentionItems', back_populates='moment')
    business_audit_history: Mapped[list['BusinessAuditHistory']] = relationship('BusinessAuditHistory', back_populates='moment')
    business_health_driver_scores: Mapped[list['BusinessHealthDriverScores']] = relationship('BusinessHealthDriverScores', back_populates='moment')
    business_live_feed: Mapped[list['BusinessLiveFeed']] = relationship('BusinessLiveFeed', back_populates='moment')
    business_memory_learnings: Mapped[list['BusinessMemoryLearnings']] = relationship('BusinessMemoryLearnings', back_populates='moment')
    business_memory_patterns: Mapped[list['BusinessMemoryPatterns']] = relationship('BusinessMemoryPatterns', back_populates='moment')
    business_moment_governance: Mapped[list['BusinessMomentGovernance']] = relationship('BusinessMomentGovernance', back_populates='moment')
    business_moment_highlights: Mapped[list['BusinessMomentHighlights']] = relationship('BusinessMomentHighlights', back_populates='moment')
    business_moment_members: Mapped[list['BusinessMomentMembers']] = relationship('BusinessMomentMembers', back_populates='moment')
    business_moment_metrics: Mapped[list['BusinessMomentMetrics']] = relationship('BusinessMomentMetrics', back_populates='moment')
    business_moment_setup: Mapped[list['BusinessMomentSetup']] = relationship('BusinessMomentSetup', back_populates='moment')
    business_moment_structure: Mapped[list['BusinessMomentStructure']] = relationship('BusinessMomentStructure', back_populates='moment')
    business_notifications: Mapped[list['BusinessNotifications']] = relationship('BusinessNotifications', back_populates='moment')
    business_operations_budget_categories: Mapped[list['BusinessOperationsBudgetCategories']] = relationship('BusinessOperationsBudgetCategories', back_populates='moment')
    business_operations_governance_rules: Mapped[list['BusinessOperationsGovernanceRules']] = relationship('BusinessOperationsGovernanceRules', back_populates='moment')
    business_operations_setup: Mapped[list['BusinessOperationsSetup']] = relationship('BusinessOperationsSetup', back_populates='moment')
    business_operations_snapshots: Mapped[list['BusinessOperationsSnapshots']] = relationship('BusinessOperationsSnapshots', back_populates='moment')
    business_operations_structure: Mapped[list['BusinessOperationsStructure']] = relationship('BusinessOperationsStructure', back_populates='moment')
    business_orchestration_jobs: Mapped[list['BusinessOrchestrationJobs']] = relationship('BusinessOrchestrationJobs', back_populates='moment')
    business_playbooks: Mapped[list['BusinessPlaybooks']] = relationship('BusinessPlaybooks', back_populates='moment')
    business_progress_snapshots: Mapped[list['BusinessProgressSnapshots']] = relationship('BusinessProgressSnapshots', back_populates='moment')
    business_quick_add_drafts: Mapped[list['BusinessQuickAddDrafts']] = relationship('BusinessQuickAddDrafts', back_populates='moment')
    business_recommended_actions: Mapped[list['BusinessRecommendedActions']] = relationship('BusinessRecommendedActions', back_populates='moment')
    business_risk_memory: Mapped[list['BusinessRiskMemory']] = relationship('BusinessRiskMemory', back_populates='moment')
    business_runway_governance_rules: Mapped[list['BusinessRunwayGovernanceRules']] = relationship('BusinessRunwayGovernanceRules', back_populates='moment')
    business_runway_setup: Mapped[list['BusinessRunwaySetup']] = relationship('BusinessRunwaySetup', back_populates='moment')
    business_runway_snapshots: Mapped[list['BusinessRunwaySnapshots']] = relationship('BusinessRunwaySnapshots', back_populates='moment')
    business_runway_structure: Mapped[list['BusinessRunwayStructure']] = relationship('BusinessRunwayStructure', back_populates='moment')
    business_signal_insights: Mapped[list['BusinessSignalInsights']] = relationship('BusinessSignalInsights', back_populates='moment')
    business_success_memory: Mapped[list['BusinessSuccessMemory']] = relationship('BusinessSuccessMemory', back_populates='moment')
    business_transaction_permissions: Mapped[list['BusinessTransactionPermissions']] = relationship('BusinessTransactionPermissions', back_populates='moment')
    business_wisdom: Mapped[list['BusinessWisdom']] = relationship('BusinessWisdom', back_populates='moment')
    operations_improvements: Mapped[list['OperationsImprovements']] = relationship('OperationsImprovements', back_populates='moment')
    operations_issues: Mapped[list['OperationsIssues']] = relationship('OperationsIssues', back_populates='moment')
    operations_vendor_updates: Mapped[list['OperationsVendorUpdates']] = relationship('OperationsVendorUpdates', back_populates='moment')
    runway_cash_inflows: Mapped[list['RunwayCashInflows']] = relationship('RunwayCashInflows', back_populates='moment')
    runway_expense_burns: Mapped[list['RunwayExpenseBurns']] = relationship('RunwayExpenseBurns', back_populates='moment')
    runway_financial_updates: Mapped[list['RunwayFinancialUpdates']] = relationship('RunwayFinancialUpdates', back_populates='moment')
    runway_risks: Mapped[list['RunwayRisks']] = relationship('RunwayRisks', back_populates='moment')
    runway_strategic_decisions: Mapped[list['RunwayStrategicDecisions']] = relationship('RunwayStrategicDecisions', back_populates='moment')
    team_updates: Mapped[list['TeamUpdates']] = relationship('TeamUpdates', back_populates='moment')
    business_moment_invitations: Mapped[list['BusinessMomentInvitations']] = relationship('BusinessMomentInvitations', back_populates='moment')
    business_pulse_snapshots: Mapped[list['BusinessPulseSnapshots']] = relationship('BusinessPulseSnapshots', back_populates='moment')
    operations_spend_entries: Mapped[list['OperationsSpendEntries']] = relationship('OperationsSpendEntries', back_populates='moment')
    team_activities: Mapped[list['TeamActivities']] = relationship('TeamActivities', back_populates='moment')
    team_approval_requests: Mapped[list['TeamApprovalRequests']] = relationship('TeamApprovalRequests', back_populates='moment')
    team_issue_risks: Mapped[list['TeamIssueRisks']] = relationship('TeamIssueRisks', back_populates='moment')
    operations_approval_requests: Mapped[list['OperationsApprovalRequests']] = relationship('OperationsApprovalRequests', back_populates='moment')


class BusinessNotifications(Base):
    __tablename__ = 'business_notifications'
    __table_args__ = (
        CheckConstraint("delivery_channel::text = ANY (ARRAY['in_app'::character varying, 'email'::character varying, 'push'::character varying]::text[])", name='chk_delivery_channel'),
        CheckConstraint("notification_status::text = ANY (ARRAY['queued'::character varying, 'sent'::character varying, 'read'::character varying, 'failed'::character varying, 'archived'::character varying]::text[])", name='chk_notification_status'),
        CheckConstraint("priority::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])", name='chk_notification_priority'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_notification_moment'),
        PrimaryKeyConstraint('notification_id', name='business_notifications_pkey'),
        Index('idx_notification_created', 'created_at'),
        Index('idx_notification_recipient', 'recipient_user_id'),
        Index('idx_notification_status', 'notification_status')
    )

    notification_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    recipient_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_record_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'medium'::character varying"))
    delivery_channel: Mapped[str] = mapped_column(String(50), nullable=False)
    notification_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'queued'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    read_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_notifications')


class BusinessOperationsBudgetCategories(Base):
    __tablename__ = 'business_operations_budget_categories'
    __table_args__ = (
        CheckConstraint('allocated_budget >= 0::numeric', name='chk_operations_budget_allocated'),
        CheckConstraint("category_status::text = ANY (ARRAY['active'::character varying, 'archived'::character varying]::text[])", name='chk_operations_budget_category_status'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_operations_budget_category_moment'),
        PrimaryKeyConstraint('budget_category_id', name='business_operations_budget_categories_pkey'),
        Index('idx_operations_budget_categories_moment', 'moment_id'),
        Index('idx_operations_budget_categories_status', 'category_status')
    )

    budget_category_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category_name: Mapped[Optional[str]] = mapped_column(String(100))
    allocated_budget: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    category_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'active'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    custom_category_name: Mapped[Optional[str]] = mapped_column(String(255))
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    alert_threshold_percent: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2), server_default=text('80'))
    allocation_id: Mapped[Optional[str]] = mapped_column(String(64))
    allocated_budget_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    percentage: Mapped[Optional[int]] = mapped_column(Integer)
    category_code: Mapped[Optional[str]] = mapped_column(String(64))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_operations_budget_categories')
    operations_spend_entries: Mapped[list['OperationsSpendEntries']] = relationship('OperationsSpendEntries', back_populates='budget_category')


class BusinessOperationsGovernanceRules(Base):
    __tablename__ = 'business_operations_governance_rules'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_business_operations_governance_moment'),
        PrimaryKeyConstraint('operations_governance_id', name='business_operations_governance_rules_pkey'),
        Index('uq_business_operations_governance', 'moment_id', unique=True)
    )

    operations_governance_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    visibility_roles: Mapped[dict] = mapped_column(JSONB, nullable=False)
    alert_conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    alert_recipient_roles: Mapped[dict] = mapped_column(JSONB, nullable=False)
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    monitoring_level: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'standard'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    approval_rules: Mapped[Optional[dict]] = mapped_column(JSONB)
    approval_threshold_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    secondary_approver_ids: Mapped[Optional[dict]] = mapped_column(JSONB)
    alert_recipient_ids: Mapped[Optional[dict]] = mapped_column(JSONB)
    visibility: Mapped[Optional[str]] = mapped_column(String(32))
    governance_extras: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_operations_governance_rules')


class BusinessOperationsSetup(Base):
    __tablename__ = 'business_operations_setup'
    __table_args__ = (
        CheckConstraint('monthly_operating_budget >= 0::numeric', name='chk_business_operations_monthly_budget'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_business_operations_setup_moment'),
        PrimaryKeyConstraint('operations_setup_id', name='business_operations_setup_pkey'),
        Index('uq_business_operations_setup', 'moment_id', unique=True)
    )

    operations_setup_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    operations_type: Mapped[Optional[str]] = mapped_column(String(100))
    operating_model: Mapped[Optional[str]] = mapped_column(String(100))
    operational_owner_role: Mapped[Optional[str]] = mapped_column(String(100))
    operating_currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    monthly_operating_budget: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    operations_name: Mapped[Optional[str]] = mapped_column(String(255))
    operations_scope: Mapped[Optional[str]] = mapped_column(String(64))
    operating_model_canonical: Mapped[Optional[str]] = mapped_column(String(64))
    monthly_budget_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    review_cycle: Mapped[Optional[str]] = mapped_column(String(32))
    financial_year_start: Mapped[Optional[str]] = mapped_column(String(32))
    country_code: Mapped[Optional[str]] = mapped_column(String(8))
    locale: Mapped[Optional[str]] = mapped_column(String(32))
    timezone: Mapped[Optional[str]] = mapped_column(String(64))
    setup_extras: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_operations_setup')


class BusinessOperationsSnapshots(Base):
    __tablename__ = 'business_operations_snapshots'
    __table_args__ = (
        CheckConstraint("operations_health_status::text = ANY (ARRAY['healthy'::character varying, 'attention'::character varying, 'at_risk'::character varying]::text[])", name='chk_business_operations_health_status'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_business_operations_snapshot_moment'),
        PrimaryKeyConstraint('operations_snapshot_id', name='business_operations_snapshots_pkey'),
        Index('idx_business_operations_snapshot_date', 'snapshot_date'),
        Index('idx_business_operations_snapshot_moment', 'moment_id'),
        Index('uq_business_operations_snapshot_day', 'moment_id', 'snapshot_date', unique=True)
    )

    operations_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    monthly_budget: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    allocated_budget: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    budget_used: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    budget_remaining: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    budget_alert_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    vendor_activity_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    open_approval_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    active_issue_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    critical_issue_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    improvement_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    operations_health_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'healthy'::character varying"))
    operating_currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_operations_snapshots')


class BusinessOperationsStructure(Base):
    __tablename__ = 'business_operations_structure'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_business_operations_structure_moment'),
        PrimaryKeyConstraint('operations_structure_id', name='business_operations_structure_pkey'),
        Index('uq_business_operations_structure', 'moment_id', unique=True)
    )

    operations_structure_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    vendor_dependency: Mapped[Optional[str]] = mapped_column(String(50))
    approval_model: Mapped[Optional[str]] = mapped_column(String(100))
    issue_sensitivity: Mapped[Optional[str]] = mapped_column(String(100))
    performance_review_cycle: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    kpi_tracking: Mapped[Optional[dict]] = mapped_column(JSONB)
    vendor_dependency_level: Mapped[Optional[str]] = mapped_column(String(32))
    monitoring_level_canonical: Mapped[Optional[str]] = mapped_column(String(32))
    allocation_mode: Mapped[Optional[str]] = mapped_column(String(32))
    budget_allocations: Mapped[Optional[dict]] = mapped_column(JSONB)
    budget_categories: Mapped[Optional[dict]] = mapped_column(JSONB)
    alert_conditions: Mapped[Optional[dict]] = mapped_column(JSONB)
    structure_extras: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_operations_structure')


class BusinessOrchestrationJobs(Base):
    __tablename__ = 'business_orchestration_jobs'
    __table_args__ = (
        CheckConstraint("job_status::text = ANY (ARRAY['queued'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying]::text[])", name='chk_job_status'),
        CheckConstraint("job_type::text = ANY (ARRAY['pulse_refresh'::character varying, 'moments_refresh'::character varying, 'life_refresh'::character varying, 'memory_refresh'::character varying, 'activity_refresh'::character varying, 'workspace_refresh'::character varying, 'business_360_refresh'::character varying]::text[])", name='chk_business_orchestration_job_type'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_job_moment'),
        PrimaryKeyConstraint('job_id', name='business_orchestration_jobs_pkey'),
        Index('idx_job_moment', 'moment_id'),
        Index('idx_job_status', 'job_status'),
        Index('idx_job_type', 'job_type'),
        Index('idx_orchestration_scope', 'orchestration_scope'),
        Index('idx_orchestration_workspace', 'workspace_id')
    )

    job_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    job_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'queued'::character varying"))
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    queued_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    source_table: Mapped[Optional[str]] = mapped_column(String(100))
    source_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    workspace_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    orchestration_scope: Mapped[Optional[str]] = mapped_column(String(50))
    priority: Mapped[Optional[str]] = mapped_column(String(30), server_default=text("'medium'::character varying"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_orchestration_jobs')


class BusinessPlaybooks(Base):
    __tablename__ = 'business_playbooks'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_playbooks_moment_id_fkey'),
        PrimaryKeyConstraint('playbook_id', name='business_playbooks_pkey')
    )

    playbook_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    playbook_title: Mapped[Optional[str]] = mapped_column(String(255))
    playbook_summary: Mapped[Optional[str]] = mapped_column(Text)
    success_rate: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    playbook_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'active'::character varying"))

    moment: Mapped[Optional['BusinessMoments']] = relationship('BusinessMoments', back_populates='business_playbooks')


class BusinessProgressSnapshots(Base):
    __tablename__ = 'business_progress_snapshots'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_progress_snapshots_moment_id_fkey'),
        PrimaryKeyConstraint('progress_id', name='business_progress_snapshots_pkey'),
        Index('idx_progress_snapshot_moment', 'moment_id')
    )

    progress_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    metric_code: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    metric_delta: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    metric_status: Mapped[Optional[str]] = mapped_column(String(50))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_progress_snapshots')


class BusinessPulseSnapshots(Base):
    __tablename__ = 'business_pulse_snapshots'
    __table_args__ = (
        CheckConstraint("health_status::text = ANY (ARRAY['stable'::character varying, 'attention'::character varying, 'at_risk'::character varying, 'critical'::character varying]::text[])", name='chk_business_pulse_health_status'),
        CheckConstraint("operations_health_status IS NULL OR (operations_health_status::text = ANY (ARRAY['healthy'::character varying, 'attention'::character varying, 'at_risk'::character varying]::text[]))", name='chk_business_pulse_operations_health_status'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_pulse_snapshot_moment'),
        ForeignKeyConstraint(['next_best_action_id'], ['business_recommended_actions.action_id'], name='fk_business_pulse_next_action'),
        PrimaryKeyConstraint('snapshot_id', name='business_pulse_snapshots_pkey'),
        Index('idx_business_pulse_operations_snapshot', 'moment_id', 'snapshot_date'),
        Index('idx_business_pulse_runway_snapshot', 'moment_id', 'snapshot_date'),
        Index('idx_pulse_next_action', 'next_best_action_id'),
        Index('idx_pulse_snapshot_date', 'snapshot_date'),
        Index('idx_pulse_snapshot_moment', 'moment_id')
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    activities_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    completed_activities: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    in_progress_activities: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    planned_activities: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    pending_approvals: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    open_risks: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    critical_risks: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    monthly_spend: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    health_score: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('100'))
    health_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'stable'::character varying"))
    cash_available: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    estimated_runway_months: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    cash_inflow_total: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    expense_burn_total: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    net_burn: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    runway_alert_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    runway_risk_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    active_issue_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    open_approval_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    budget_alert_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    improvement_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    budget_used_total: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    budget_remaining_total: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    vendor_activity_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    health_driver_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    attention_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    signal_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    top_spend_category: Mapped[Optional[str]] = mapped_column(String(255))
    health_reason: Mapped[Optional[str]] = mapped_column(Text)
    operating_currency: Mapped[Optional[str]] = mapped_column(String(10), server_default=text("'INR'::character varying"))
    operations_health_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'healthy'::character varying"))
    operations_operating_currency: Mapped[Optional[str]] = mapped_column(String(10), server_default=text("'INR'::character varying"))
    pulse_category: Mapped[Optional[str]] = mapped_column(String(50))
    pulse_description: Mapped[Optional[str]] = mapped_column(Text)
    next_best_action_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_pulse_snapshots')
    next_best_action: Mapped[Optional['BusinessRecommendedActions']] = relationship('BusinessRecommendedActions', back_populates='business_pulse_snapshots')


class BusinessQuickAddDrafts(Base):
    __tablename__ = 'business_quick_add_drafts'
    __table_args__ = (
        CheckConstraint("draft_status::text = ANY (ARRAY['active'::character varying, 'submitted'::character varying, 'discarded'::character varying, 'expired'::character varying]::text[])", name='chk_draft_status'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_draft_moment'),
        PrimaryKeyConstraint('draft_id', name='business_quick_add_drafts_pkey'),
        Index('idx_draft_moment', 'moment_id'),
        Index('idx_draft_user', 'user_id')
    )

    draft_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    tab_type: Mapped[str] = mapped_column(String(50), nullable=False)
    draft_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    draft_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'active'::character varying"))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_quick_add_drafts')


class BusinessRecommendedActions(Base):
    __tablename__ = 'business_recommended_actions'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_recommended_actions_moment_id_fkey'),
        PrimaryKeyConstraint('action_id', name='business_recommended_actions_pkey'),
        Index('idx_recommended_action_moment', 'moment_id'),
        Index('idx_recommended_action_status', 'status')
    )

    action_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action_title: Mapped[str] = mapped_column(String(255), nullable=False)
    action_reason: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(30), nullable=False)
    cta_label: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    target_screen: Mapped[Optional[str]] = mapped_column(String(100))
    target_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    expected_health_impact: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    source_rule: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'active'::character varying"))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_recommended_actions')
    business_pulse_snapshots: Mapped[list['BusinessPulseSnapshots']] = relationship('BusinessPulseSnapshots', back_populates='next_best_action')


class BusinessRiskMemory(Base):
    __tablename__ = 'business_risk_memory'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_risk_memory_moment_id_fkey'),
        PrimaryKeyConstraint('risk_memory_id', name='business_risk_memory_pkey')
    )

    risk_memory_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    risk_title: Mapped[Optional[str]] = mapped_column(String(255))
    risk_summary: Mapped[Optional[str]] = mapped_column(Text)
    observed_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('1'))
    severity: Mapped[Optional[str]] = mapped_column(String(30))

    moment: Mapped[Optional['BusinessMoments']] = relationship('BusinessMoments', back_populates='business_risk_memory')


class BusinessRunwayGovernanceRules(Base):
    __tablename__ = 'business_runway_governance_rules'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_governance_rules_moment'),
        PrimaryKeyConstraint('governance_rule_id', name='business_runway_governance_rules_pkey'),
        Index('uq_business_runway_governance_rules', 'moment_id', unique=True)
    )

    governance_rule_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    visibility_roles: Mapped[dict] = mapped_column(JSONB, nullable=False)
    alert_recipient_roles: Mapped[dict] = mapped_column(JSONB, nullable=False)
    alert_conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    approval_rules: Mapped[Optional[dict]] = mapped_column(JSONB)
    large_expense_threshold_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    visibility: Mapped[Optional[str]] = mapped_column(String(32))
    governance_extras: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_runway_governance_rules')


class BusinessRunwaySetup(Base):
    __tablename__ = 'business_runway_setup'
    __table_args__ = (
        CheckConstraint('cash_available >= 0::numeric', name='chk_runway_cash_available'),
        CheckConstraint('monthly_burn >= 0::numeric', name='chk_runway_monthly_burn'),
        CheckConstraint('monthly_revenue >= 0::numeric', name='chk_runway_monthly_revenue'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_setup_moment'),
        PrimaryKeyConstraint('runway_setup_id', name='business_runway_setup_pkey'),
        Index('idx_business_runway_setup_owner', 'runway_owner_id'),
        Index('uq_business_runway_setup', 'moment_id', unique=True)
    )

    runway_setup_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    business_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    cash_available: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    monthly_burn: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    monthly_revenue: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    operating_currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    estimated_runway_months: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    runway_goal: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    runway_owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    current_cash_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    monthly_burn_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    estimated_monthly_revenue_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    runway_goal_months: Mapped[Optional[int]] = mapped_column(Integer)
    revenue_status: Mapped[Optional[str]] = mapped_column(String(50))
    country_code: Mapped[Optional[str]] = mapped_column(String(8))
    locale: Mapped[Optional[str]] = mapped_column(String(32))
    timezone: Mapped[Optional[str]] = mapped_column(String(64))
    setup_extras: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_runway_setup')


class BusinessRunwaySnapshots(Base):
    __tablename__ = 'business_runway_snapshots'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_snapshot_moment'),
        PrimaryKeyConstraint('snapshot_id', name='business_runway_snapshots_pkey'),
        Index('idx_runway_snapshot_date', 'snapshot_date'),
        Index('idx_runway_snapshot_moment', 'moment_id'),
        Index('uq_business_runway_snapshot_day', 'moment_id', 'snapshot_date', unique=True)
    )

    snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    snapshot_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    cash_available: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    total_cash_inflow: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    total_expense_burn: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    net_burn: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    estimated_runway_months: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('0'))
    open_risks: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    decision_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    operating_currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'INR'::character varying"))
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_runway_snapshots')


class BusinessRunwayStructure(Base):
    __tablename__ = 'business_runway_structure'
    __table_args__ = (
        CheckConstraint('alert_threshold_months > 0::numeric', name='chk_runway_alert_threshold'),
        CheckConstraint("monitoring_level::text = ANY (ARRAY['basic'::character varying, 'standard'::character varying, 'high_visibility'::character varying]::text[])", name='chk_runway_monitoring_level'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_structure_moment'),
        PrimaryKeyConstraint('structure_id', name='business_runway_structure_pkey'),
        Index('uq_business_runway_structure', 'moment_id', unique=True)
    )

    structure_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    burn_categories: Mapped[dict] = mapped_column(JSONB, nullable=False)
    revenue_model: Mapped[Optional[str]] = mapped_column(String(100))
    alert_threshold_months: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default=text('6'))
    funding_structure: Mapped[Optional[str]] = mapped_column(String(100))
    runway_philosophy: Mapped[Optional[str]] = mapped_column(String(100))
    monitoring_level: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'standard'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    hiring_intent: Mapped[Optional[str]] = mapped_column(String(100))
    runway_alert_threshold_months: Mapped[Optional[int]] = mapped_column(Integer)
    collection_rate_percent: Mapped[Optional[int]] = mapped_column(Integer)
    funding_sources: Mapped[Optional[dict]] = mapped_column(JSONB)
    revenue_model_canonical: Mapped[Optional[str]] = mapped_column(String(64))
    structure_extras: Mapped[Optional[dict]] = mapped_column(JSONB)

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_runway_structure')


class BusinessSignalInsights(Base):
    __tablename__ = 'business_signal_insights'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_signal_insights_moment_id_fkey'),
        PrimaryKeyConstraint('signal_id', name='business_signal_insights_pkey'),
        Index('idx_signal_moment', 'moment_id'),
        Index('idx_signal_status', 'signal_status'),
        {'comment': 'Pulse UI signal cache generated from ai_signals and business '
                'analytics.'}
    )

    signal_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_title: Mapped[str] = mapped_column(String(255), nullable=False)
    signal_summary: Mapped[str] = mapped_column(Text, nullable=False)
    impact_level: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    change_percent: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))
    lookback_days: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('7'))
    source_table: Mapped[Optional[str]] = mapped_column(String(100))
    source_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    signal_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'active'::character varying"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_signal_insights')


class BusinessSuccessMemory(Base):
    __tablename__ = 'business_success_memory'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_success_memory_moment_id_fkey'),
        PrimaryKeyConstraint('success_id', name='business_success_memory_pkey')
    )

    success_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    success_title: Mapped[Optional[str]] = mapped_column(String(255))
    success_summary: Mapped[Optional[str]] = mapped_column(Text)
    action_taken: Mapped[Optional[str]] = mapped_column(Text)
    impact_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped[Optional['BusinessMoments']] = relationship('BusinessMoments', back_populates='business_success_memory')


class BusinessTransactionPermissions(Base):
    __tablename__ = 'business_transaction_permissions'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_permission_moment'),
        PrimaryKeyConstraint('permission_id', name='business_transaction_permissions_pkey'),
        Index('idx_business_transaction_permissions_operations', 'moment_id', 'source_table', 'source_record_id', 'role_name'),
        Index('idx_permission_moment', 'moment_id'),
        Index('idx_permission_role', 'role_name'),
        Index('idx_permission_source', 'source_table', 'source_record_id')
    )

    permission_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source_table: Mapped[str] = mapped_column(String(100), nullable=False)
    source_record_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    can_view: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    can_edit: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    can_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    permission_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    granted_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    active_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    can_approve: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='business_transaction_permissions')


class BusinessVendorDirectory(Base):
    __tablename__ = 'business_vendor_directory'
    __table_args__ = (
        CheckConstraint("vendor_status::text = ANY (ARRAY['active'::character varying, 'inactive'::character varying, 'archived'::character varying]::text[])", name='chk_vendor_status'),
        PrimaryKeyConstraint('vendor_id', name='business_vendor_directory_pkey'),
        Index('idx_vendor_name', 'vendor_name'),
        Index('idx_vendor_workspace', 'workspace_id')
    )

    vendor_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'active'::character varying"))
    total_spend: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    vendor_category: Mapped[Optional[str]] = mapped_column(String(100))
    last_transaction_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class BusinessWisdom(Base):
    __tablename__ = 'business_wisdom'
    __table_args__ = (
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='business_wisdom_moment_id_fkey'),
        PrimaryKeyConstraint('wisdom_id', name='business_wisdom_pkey')
    )

    wisdom_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    wisdom_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    moment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    confidence_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    moment: Mapped[Optional['BusinessMoments']] = relationship('BusinessMoments', back_populates='business_wisdom')
    business_memory_snapshots: Mapped[list['BusinessMemorySnapshots']] = relationship('BusinessMemorySnapshots', back_populates='strongest_wisdom')


class OperationsApprovalRequests(Base):
    __tablename__ = 'operations_approval_requests'
    __table_args__ = (
        CheckConstraint('amount IS NULL OR amount >= 0::numeric', name='chk_operations_approval_amount'),
        CheckConstraint("approval_status::text = ANY (ARRAY['pending'::character varying, 'approved'::character varying, 'rejected'::character varying, 'cancelled'::character varying, 'archived'::character varying]::text[])", name='chk_operations_approval_status'),
        CheckConstraint("priority::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])", name='chk_operations_approval_priority'),
        CheckConstraint("request_type::text = ANY (ARRAY['expense_approval'::character varying, 'vendor_approval'::character varying, 'budget_change'::character varying, 'policy_exception'::character varying, 'operational_request'::character varying]::text[])", name='chk_operations_approval_request_type'),
        ForeignKeyConstraint(['linked_spend_entry_id'], ['operations_spend_entries.spend_entry_id'], name='fk_operations_approval_spend'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_operations_approval_moment'),
        PrimaryKeyConstraint('operations_approval_id', name='operations_approval_requests_pkey'),
        Index('idx_operations_approval_approver', 'approver_id'),
        Index('idx_operations_approval_moment', 'moment_id'),
        Index('idx_operations_approval_spend', 'linked_spend_entry_id'),
        Index('idx_operations_approval_status', 'approval_status')
    )

    operations_approval_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    request_type: Mapped[str] = mapped_column(String(100), nullable=False)
    request_title: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'medium'::character varying"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'pending'::character varying"))
    requested_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    linked_spend_entry_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    approver_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    decision_note: Mapped[Optional[str]] = mapped_column(Text)
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    decided_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    linked_spend_entry: Mapped[Optional['OperationsSpendEntries']] = relationship('OperationsSpendEntries', back_populates='operations_approval_requests')
    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='operations_approval_requests')


class OperationsImprovements(Base):
    __tablename__ = 'operations_improvements'
    __table_args__ = (
        CheckConstraint("expected_impact::text = ANY (ARRAY['reduce_cost'::character varying, 'improve_speed'::character varying, 'reduce_issues'::character varying, 'improve_service'::character varying, 'improve_control'::character varying, 'improve_visibility'::character varying]::text[])", name='chk_operations_improvement_expected_impact'),
        CheckConstraint("impact_area::text = ANY (ARRAY['budget'::character varying, 'operations'::character varying, 'customer'::character varying, 'compliance'::character varying, 'inventory'::character varying, 'staff'::character varying, 'approval_flow'::character varying]::text[])", name='chk_operations_improvement_impact_area'),
        CheckConstraint("improvement_status::text = ANY (ARRAY['recorded'::character varying, 'in_follow_up'::character varying, 'completed'::character varying, 'archived'::character varying]::text[])", name='chk_operations_improvement_status'),
        CheckConstraint("improvement_type::text = ANY (ARRAY['process_improvement'::character varying, 'budget_control_improvement'::character varying, 'customer_experience_improvement'::character varying, 'inventory_improvement'::character varying, 'compliance_improvement'::character varying, 'staffing_scheduling_improvement'::character varying, 'approval_flow_improvement'::character varying, 'service_quality_improvement'::character varying, 'operational_control_improvement'::character varying, 'other'::character varying]::text[])", name='chk_operations_improvement_type'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_operations_improvement_moment'),
        PrimaryKeyConstraint('improvement_id', name='operations_improvements_pkey'),
        Index('idx_operations_improvements_moment', 'moment_id'),
        Index('idx_operations_improvements_owner', 'owner_id'),
        Index('idx_operations_improvements_status', 'improvement_status'),
        Index('idx_operations_improvements_type', 'improvement_type')
    )

    improvement_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    improvement_type: Mapped[str] = mapped_column(String(100), nullable=False)
    improvement_title: Mapped[str] = mapped_column(String(255), nullable=False)
    impact_area: Mapped[str] = mapped_column(String(100), nullable=False)
    expected_impact: Mapped[str] = mapped_column(String(100), nullable=False)
    effective_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    improvement_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'recorded'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    description: Mapped[Optional[str]] = mapped_column(Text)
    follow_up_owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    follow_up_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='operations_improvements')


class OperationsIssues(Base):
    __tablename__ = 'operations_issues'
    __table_args__ = (
        CheckConstraint("impact_area::text = ANY (ARRAY['budget'::character varying, 'operations'::character varying, 'vendor'::character varying, 'customer'::character varying, 'compliance'::character varying, 'technology'::character varying]::text[])", name='chk_operations_issue_impact'),
        CheckConstraint("issue_category::text = ANY (ARRAY['operations'::character varying, 'inventory'::character varying, 'vendor'::character varying, 'compliance'::character varying, 'customer'::character varying, 'technology'::character varying, 'other'::character varying]::text[])", name='chk_operations_issue_category'),
        CheckConstraint("issue_status::text = ANY (ARRAY['open'::character varying, 'investigating'::character varying, 'resolved'::character varying, 'archived'::character varying]::text[])", name='chk_operations_issue_status'),
        CheckConstraint("severity::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])", name='chk_operations_issue_severity'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_operations_issue_moment'),
        PrimaryKeyConstraint('operations_issue_id', name='operations_issues_pkey'),
        Index('idx_operations_issues_moment', 'moment_id'),
        Index('idx_operations_issues_owner', 'owner_id'),
        Index('idx_operations_issues_severity', 'severity'),
        Index('idx_operations_issues_status', 'issue_status')
    )

    operations_issue_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    issue_category: Mapped[str] = mapped_column(String(100), nullable=False)
    issue_title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    impact_area: Mapped[str] = mapped_column(String(100), nullable=False)
    issue_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'open'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    target_resolution_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='operations_issues')


class OperationsSpendEntries(Base):
    __tablename__ = 'operations_spend_entries'
    __table_args__ = (
        CheckConstraint('amount > 0::numeric', name='chk_operations_spend_amount'),
        CheckConstraint('amount_in_operating_currency >= 0::numeric', name='chk_operations_spend_amount_operating'),
        CheckConstraint("approval_status::text = ANY (ARRAY['not_required'::character varying, 'pending'::character varying, 'approved'::character varying, 'rejected'::character varying]::text[])", name='chk_operations_spend_approval_status'),
        CheckConstraint('exchange_rate_to_operating_currency > 0::numeric', name='chk_operations_spend_fx'),
        CheckConstraint("priority::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])", name='chk_operations_spend_priority'),
        CheckConstraint("spend_category::text = ANY (ARRAY['purchase'::character varying, 'vendor_payment'::character varying, 'staff_cost'::character varying, 'utility_bill'::character varying, 'maintenance'::character varying, 'marketing_spend'::character varying, 'inventory_refill'::character varying, 'service_charge'::character varying, 'travel_expense'::character varying, 'other'::character varying]::text[])", name='chk_operations_spend_category'),
        ForeignKeyConstraint(['budget_category_id'], ['business_operations_budget_categories.budget_category_id'], name='fk_operations_spend_budget_category'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_operations_spend_moment'),
        PrimaryKeyConstraint('spend_entry_id', name='operations_spend_entries_pkey'),
        Index('idx_operations_spend_approval', 'approval_status'),
        Index('idx_operations_spend_budget_category', 'budget_category_id'),
        Index('idx_operations_spend_date', 'spend_date'),
        Index('idx_operations_spend_moment', 'moment_id')
    )

    spend_entry_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    spend_name: Mapped[str] = mapped_column(String(255), nullable=False)
    budget_category_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    spend_category: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    exchange_rate_to_operating_currency: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 6), nullable=False, server_default=text('1'))
    amount_in_operating_currency: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    spend_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'medium'::character varying"))
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    approval_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'not_required'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    budget_category: Mapped['BusinessOperationsBudgetCategories'] = relationship('BusinessOperationsBudgetCategories', back_populates='operations_spend_entries')
    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='operations_spend_entries')
    operations_approval_requests: Mapped[list['OperationsApprovalRequests']] = relationship('OperationsApprovalRequests', back_populates='linked_spend_entry')


class OperationsVendorUpdates(Base):
    __tablename__ = 'operations_vendor_updates'
    __table_args__ = (
        CheckConstraint("impact_level::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])", name='chk_operations_vendor_impact'),
        CheckConstraint("vendor_category::text = ANY (ARRAY['inventory_vendor'::character varying, 'technology_vendor'::character varying, 'marketing_vendor'::character varying, 'service_vendor'::character varying, 'facility_vendor'::character varying, 'logistics_vendor'::character varying, 'professional_services'::character varying, 'equipment_supplier'::character varying, 'other'::character varying]::text[])", name='chk_operations_vendor_category'),
        CheckConstraint("vendor_event_type::text = ANY (ARRAY['new_vendor'::character varying, 'vendor_evaluation'::character varying, 'vendor_issue'::character varying, 'contract_renewal'::character varying, 'payment_status'::character varying, 'contract_change'::character varying, 'vendor_suspension'::character varying, 'vendor_reactivation'::character varying, 'other'::character varying]::text[])", name='chk_operations_vendor_event_type'),
        CheckConstraint("vendor_status::text = ANY (ARRAY['active'::character varying, 'preferred_vendor'::character varying, 'under_review'::character varying, 'on_hold'::character varying, 'blocked'::character varying, 'terminated'::character varying]::text[])", name='chk_operations_vendor_status'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_operations_vendor_update_moment'),
        PrimaryKeyConstraint('vendor_update_id', name='operations_vendor_updates_pkey'),
        Index('idx_operations_vendor_updates_event', 'vendor_event_type'),
        Index('idx_operations_vendor_updates_moment', 'moment_id'),
        Index('idx_operations_vendor_updates_status', 'vendor_status'),
        Index('idx_operations_vendor_updates_vendor', 'vendor_name')
    )

    vendor_update_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    vendor_event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_category: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor_status: Mapped[str] = mapped_column(String(100), nullable=False)
    impact_level: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'medium'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='operations_vendor_updates')


class RunwayCashInflows(Base):
    __tablename__ = 'runway_cash_inflows'
    __table_args__ = (
        CheckConstraint('amount > 0::numeric', name='chk_runway_cash_inflow_amount'),
        CheckConstraint('amount_in_operating_currency >= 0::numeric', name='chk_runway_cash_inflow_converted_amount'),
        CheckConstraint('exchange_rate_to_operating_currency > 0::numeric', name='chk_runway_cash_inflow_fx'),
        CheckConstraint("inflow_type::text = ANY (ARRAY['revenue_collected'::character varying, 'investor_funding'::character varying, 'owner_contribution'::character varying, 'bank_loan'::character varying, 'government_grant'::character varying, 'customer_advance'::character varying, 'other'::character varying]::text[])", name='chk_runway_cash_inflow_type'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_cash_inflow_moment'),
        PrimaryKeyConstraint('cash_inflow_id', name='runway_cash_inflows_pkey'),
        Index('idx_runway_cash_inflows_date', 'inflow_date'),
        Index('idx_runway_cash_inflows_moment', 'moment_id'),
        Index('idx_runway_cash_inflows_type', 'inflow_type')
    )

    cash_inflow_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    inflow_type: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    exchange_rate_to_operating_currency: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 6), nullable=False, server_default=text('1'))
    amount_in_operating_currency: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    inflow_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    reference: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    currency_code: Mapped[Optional[str]] = mapped_column(String(10))
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='runway_cash_inflows')


class RunwayExpenseBurns(Base):
    __tablename__ = 'runway_expense_burns'
    __table_args__ = (
        CheckConstraint('amount > 0::numeric', name='chk_runway_expense_amount'),
        CheckConstraint('amount_in_operating_currency >= 0::numeric', name='chk_runway_expense_converted_amount'),
        CheckConstraint("approval_status::text = ANY (ARRAY['not_required'::character varying, 'pending'::character varying, 'approved'::character varying, 'rejected'::character varying]::text[])", name='chk_runway_expense_approval_status'),
        CheckConstraint('exchange_rate_to_operating_currency > 0::numeric', name='chk_runway_expense_fx'),
        CheckConstraint("expense_category::text = ANY (ARRAY['salaries'::character varying, 'marketing'::character varying, 'technology'::character varying, 'operations'::character varying, 'vendor'::character varying, 'inventory'::character varying, 'taxes'::character varying, 'other'::character varying]::text[])", name='chk_runway_expense_category'),
        CheckConstraint("priority::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying]::text[])", name='chk_runway_expense_priority'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_expense_moment'),
        PrimaryKeyConstraint('expense_id', name='runway_expense_burns_pkey'),
        Index('idx_runway_expenses_approval', 'approval_status'),
        Index('idx_runway_expenses_category', 'expense_category'),
        Index('idx_runway_expenses_date', 'expense_date'),
        Index('idx_runway_expenses_moment', 'moment_id')
    )

    expense_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    expense_category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    exchange_rate_to_operating_currency: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 6), nullable=False, server_default=text('1'))
    amount_in_operating_currency: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    expense_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    approval_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'not_required'::character varying"))
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'medium'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    currency_code: Mapped[Optional[str]] = mapped_column(String(10))
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='runway_expense_burns')


class RunwayFinancialUpdates(Base):
    __tablename__ = 'runway_financial_updates'
    __table_args__ = (
        CheckConstraint("applied_status::text = ANY (ARRAY['pending'::character varying, 'applied'::character varying, 'rejected'::character varying]::text[])", name='chk_runway_financial_update_applied_status'),
        CheckConstraint("approval_status::text = ANY (ARRAY['not_required'::character varying, 'pending'::character varying, 'approved'::character varying, 'rejected'::character varying]::text[])", name='chk_runway_financial_update_approval_status'),
        CheckConstraint('new_value >= 0::numeric', name='chk_runway_financial_update_new_value'),
        CheckConstraint("update_type::text = ANY (ARRAY['cash_available'::character varying, 'monthly_burn'::character varying, 'revenue_estimate'::character varying, 'runway_threshold'::character varying, 'funding_expectation'::character varying]::text[])", name='chk_runway_financial_update_type'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_financial_update_moment'),
        PrimaryKeyConstraint('financial_update_id', name='runway_financial_updates_pkey'),
        Index('idx_runway_financial_updates_moment', 'moment_id'),
        Index('idx_runway_financial_updates_status', 'applied_status'),
        Index('idx_runway_financial_updates_type', 'update_type')
    )

    financial_update_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    update_type: Mapped[str] = mapped_column(String(100), nullable=False)
    current_value: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    new_value: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    approval_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'not_required'::character varying"))
    applied_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'pending'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    exchange_rate_to_operating_currency: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 6))
    new_value_in_operating_currency: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 2))
    applied_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    currency_code: Mapped[Optional[str]] = mapped_column(String(10))
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='runway_financial_updates')


class RunwayRisks(Base):
    __tablename__ = 'runway_risks'
    __table_args__ = (
        CheckConstraint("affected_metric IS NULL OR (affected_metric::text = ANY (ARRAY['cash_available'::character varying, 'revenue'::character varying, 'monthly_burn'::character varying, 'runway_threshold'::character varying]::text[]))", name='chk_runway_risk_affected_metric'),
        CheckConstraint("expected_impact::text = ANY (ARRAY['lt_1_month'::character varying, '1_3_months'::character varying, '3_6_months'::character varying, '6_plus_months'::character varying]::text[])", name='chk_runway_risk_expected_impact'),
        CheckConstraint("risk_status::text = ANY (ARRAY['open'::character varying, 'investigating'::character varying, 'resolved'::character varying, 'archived'::character varying]::text[])", name='chk_runway_risk_status'),
        CheckConstraint("risk_type::text = ANY (ARRAY['funding_delay'::character varying, 'revenue_drop'::character varying, 'cost_increase'::character varying, 'customer_loss'::character varying, 'loan_risk'::character varying, 'vendor_dependency'::character varying, 'other'::character varying]::text[])", name='chk_runway_risk_type'),
        CheckConstraint("severity::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])", name='chk_runway_risk_severity'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_risk_moment'),
        PrimaryKeyConstraint('risk_id', name='runway_risks_pkey'),
        Index('idx_runway_risks_moment', 'moment_id'),
        Index('idx_runway_risks_owner', 'owner_id'),
        Index('idx_runway_risks_severity', 'severity'),
        Index('idx_runway_risks_status', 'risk_status')
    )

    risk_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    risk_title: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_impact: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'open'::character varying"))
    adjustment_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    target_resolution_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    affected_metric: Mapped[Optional[str]] = mapped_column(String(100))
    current_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 2))
    new_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 2))
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    currency_code: Mapped[Optional[str]] = mapped_column(String(10))
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='runway_risks')


class RunwayStrategicDecisions(Base):
    __tablename__ = 'runway_strategic_decisions'
    __table_args__ = (
        CheckConstraint("decision_status::text = ANY (ARRAY['active'::character varying, 'edited'::character varying, 'archived'::character varying]::text[])", name='chk_runway_decision_status'),
        CheckConstraint("decision_type::text = ANY (ARRAY['hiring'::character varying, 'expansion'::character varying, 'funding'::character varying, 'cost_reduction'::character varying, 'pricing'::character varying, 'operations'::character varying, 'other'::character varying]::text[])", name='chk_runway_decision_type'),
        CheckConstraint("expected_impact::text = ANY (ARRAY['increase_runway'::character varying, 'reduce_runway'::character varying, 'neutral'::character varying, 'unknown'::character varying]::text[])", name='chk_runway_decision_impact'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_runway_decision_moment'),
        PrimaryKeyConstraint('decision_id', name='runway_strategic_decisions_pkey'),
        Index('idx_runway_decisions_created', 'created_at'),
        Index('idx_runway_decisions_moment', 'moment_id'),
        Index('idx_runway_decisions_type', 'decision_type')
    )

    decision_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    decision_type: Mapped[str] = mapped_column(String(100), nullable=False)
    decision_title: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_impact: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'active'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    decision_owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    description: Mapped[Optional[str]] = mapped_column(Text)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    currency_code: Mapped[Optional[str]] = mapped_column(String(10))
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='runway_strategic_decisions')


class TeamActivities(Base):
    __tablename__ = 'team_activities'
    __table_args__ = (
        CheckConstraint("activity_status::text = ANY (ARRAY['planned'::character varying, 'in_progress'::character varying, 'completed'::character varying]::text[])", name='chk_activity_status'),
        CheckConstraint('amount IS NULL OR amount >= 0::numeric', name='chk_activity_amount'),
        CheckConstraint("priority::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying]::text[])", name='chk_activity_priority'),
        ForeignKeyConstraint(['activity_owner_id'], ['business_moment_members.member_id'], name='fk_team_activity_owner_member'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_activity_moment'),
        PrimaryKeyConstraint('activity_id', name='team_activities_pkey'),
        Index('idx_team_activities_moment', 'moment_id'),
        Index('idx_team_activities_owner', 'activity_owner_id'),
        Index('idx_team_activities_recorded', 'recorded_at'),
        Index('idx_team_activities_status', 'activity_status')
    )

    activity_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    activity_title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    activity_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'planned'::character varying"))
    has_spend: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'medium'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    recorded_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    activity_owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 2))
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    receipt_file_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    activity_owner: Mapped[Optional['BusinessMomentMembers']] = relationship('BusinessMomentMembers', back_populates='team_activities')
    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='team_activities')


class TeamApprovalRequests(Base):
    __tablename__ = 'team_approval_requests'
    __table_args__ = (
        CheckConstraint('amount >= 0::numeric', name='chk_approval_amount'),
        CheckConstraint("approval_status::text = ANY (ARRAY['pending'::character varying, 'approved'::character varying, 'rejected'::character varying, 'cancelled'::character varying, 'expired'::character varying]::text[])", name='chk_approval_status'),
        CheckConstraint("priority::text = ANY (ARRAY['normal'::character varying, 'urgent'::character varying]::text[])", name='chk_approval_priority'),
        ForeignKeyConstraint(['approver_id'], ['business_moment_members.member_id'], name='fk_team_approval_approver_member'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_approval_moment'),
        ForeignKeyConstraint(['requested_by'], ['business_moment_members.member_id'], name='fk_team_approval_requested_by_member'),
        PrimaryKeyConstraint('approval_id', name='team_approval_requests_pkey'),
        Index('idx_team_approval_approver', 'approver_id'),
        Index('idx_team_approval_moment', 'moment_id'),
        Index('idx_team_approval_status', 'approval_status')
    )

    approval_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    request_title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    approval_type: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'normal'::character varying"))
    requested_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    approver_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'pending'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    converted_to_spend: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    needed_by: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    decision_note: Mapped[Optional[str]] = mapped_column(Text)
    decided_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    decided_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    converted_activity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    converted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    approver: Mapped['BusinessMomentMembers'] = relationship('BusinessMomentMembers', foreign_keys=[approver_id], back_populates='team_approval_requests_approver')
    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='team_approval_requests')
    business_moment_members: Mapped['BusinessMomentMembers'] = relationship('BusinessMomentMembers', foreign_keys=[requested_by], back_populates='team_approval_requests_requested_by')


class TeamIssueRisks(Base):
    __tablename__ = 'team_issue_risks'
    __table_args__ = (
        CheckConstraint("current_impact::text = ANY (ARRAY['none_yet'::character varying, 'minor'::character varying, 'moderate'::character varying, 'major'::character varying]::text[])", name='chk_issue_impact'),
        CheckConstraint("resolution_status::text = ANY (ARRAY['open'::character varying, 'investigating'::character varying, 'resolved'::character varying]::text[])", name='chk_issue_status'),
        CheckConstraint("severity::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])", name='chk_issue_severity'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_issue_moment'),
        ForeignKeyConstraint(['owner_id'], ['business_moment_members.member_id'], name='fk_team_issue_owner_member'),
        PrimaryKeyConstraint('issue_id', name='team_issue_risks_pkey'),
        Index('idx_team_risks_moment', 'moment_id'),
        Index('idx_team_risks_owner', 'owner_id'),
        Index('idx_team_risks_severity', 'severity'),
        Index('idx_team_risks_status', 'resolution_status')
    )

    issue_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    issue_title: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    current_impact: Mapped[str] = mapped_column(String(50), nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'open'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    target_resolution_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(Text)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='team_issue_risks')
    owner: Mapped[Optional['BusinessMomentMembers']] = relationship('BusinessMomentMembers', back_populates='team_issue_risks')


class TeamUpdates(Base):
    __tablename__ = 'team_updates'
    __table_args__ = (
        CheckConstraint("visibility::text = ANY (ARRAY['team_only'::character varying, 'leadership'::character varying, 'everyone'::character varying]::text[])", name='chk_update_visibility'),
        ForeignKeyConstraint(['moment_id'], ['business_moments.moment_id'], name='fk_team_update_moment'),
        PrimaryKeyConstraint('update_id', name='team_updates_pkey'),
        Index('idx_team_updates_created', 'created_at'),
        Index('idx_team_updates_moment', 'moment_id')
    )

    update_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    update_type: Mapped[str] = mapped_column(String(100), nullable=False)
    update_title: Mapped[str] = mapped_column(String(255), nullable=False)
    visibility: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'team_only'::character varying"))
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    people_involved: Mapped[Optional[dict]] = mapped_column(JSONB)
    description: Mapped[Optional[str]] = mapped_column(Text)
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    amount_minor: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    moment: Mapped['BusinessMoments'] = relationship('BusinessMoments', back_populates='team_updates')


class BusinessActivityEvents(Base):
    """Canonical write-path parent row for Business Quick Add / Activity Center."""

    __tablename__ = "business_activity_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["business_moment_id"],
            ["business_moments.moment_id"],
            name="fk_bae_moment",
        ),
        PrimaryKeyConstraint("event_id", name="business_activity_events_pkey"),
        Index("idx_bae_moment_occurred", "business_moment_id", "occurred_at"),
        Index("idx_bae_moment_action", "business_moment_id", "action_type"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    business_moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    moment_type_code: Mapped[str] = mapped_column(String(64), nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(String(255))
    occurred_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    source: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'quick_add'")
    )
    payload: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    client_request_id: Mapped[Optional[str]] = mapped_column(String(128))
    is_voided: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    voided_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class BusinessActivityAudit(Base):
    __tablename__ = "business_activity_audit"
    __table_args__ = (
        ForeignKeyConstraint(
            ["event_id"],
            ["business_activity_events.event_id"],
            name="fk_baa_event",
        ),
        PrimaryKeyConstraint("audit_id", name="business_activity_audit_pkey"),
        Index("idx_baa_event", "event_id"),
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    before_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    after_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    occurred_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class TeamRecognitions(Base):
    __tablename__ = "team_recognitions"
    __table_args__ = (
        ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_rec_moment"),
        ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_rec_event"),
        PrimaryKeyConstraint("recognition_id", name="team_recognitions_pkey"),
        Index("idx_team_recognitions_moment", "moment_id"),
    )

    recognition_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text("gen_random_uuid()"))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    recognition_type: Mapped[str] = mapped_column(String(64), nullable=False, server_default=text("'kudos'"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class TeamMeetings(Base):
    __tablename__ = "team_meetings"
    __table_args__ = (
        ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_meet_moment"),
        ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_meet_event"),
        PrimaryKeyConstraint("meeting_id", name="team_meetings_pkey"),
        Index("idx_team_meetings_moment", "moment_id"),
    )

    meeting_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text("gen_random_uuid()"))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    meeting_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    attendees: Mapped[Optional[dict]] = mapped_column(JSONB)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class TeamEscalations(Base):
    __tablename__ = "team_escalations"
    __table_args__ = (
        ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_esc_moment"),
        ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_esc_event"),
        PrimaryKeyConstraint("escalation_id", name="team_escalations_pkey"),
        Index("idx_team_escalations_moment", "moment_id"),
    )

    escalation_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text("gen_random_uuid()"))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'medium'"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'open'"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class TeamParticipation(Base):
    __tablename__ = "team_participation"
    __table_args__ = (
        ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_part_moment"),
        ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_part_event"),
        PrimaryKeyConstraint("participation_id", name="team_participation_pkey"),
        Index("idx_team_participation_moment", "moment_id"),
    )

    participation_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text("gen_random_uuid()"))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    participation_type: Mapped[str] = mapped_column(String(64), nullable=False, server_default=text("'check_in'"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class TeamMemberUpdates(Base):
    __tablename__ = "team_member_updates"
    __table_args__ = (
        ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_mu_moment"),
        ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_mu_event"),
        PrimaryKeyConstraint("member_update_id", name="team_member_updates_pkey"),
        Index("idx_team_member_updates_moment", "moment_id"),
    )

    member_update_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text("gen_random_uuid()"))
    moment_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    member_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    update_kind: Mapped[str] = mapped_column(String(64), nullable=False, server_default=text("'status'"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
