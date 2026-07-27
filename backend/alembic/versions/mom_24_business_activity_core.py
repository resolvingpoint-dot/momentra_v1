"""Business activity parent events and audit.

Revision ID: mom_24_business_activity_core
Revises: mom_23_business_operations_setup
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "mom_24_business_activity_core"
down_revision: Union[str, Sequence[str], None] = "mom_23_business_operations_setup"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "business_activity_events",
        sa.Column("event_id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_moment_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("moment_type_code", sa.String(length=64), nullable=False),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subtitle", sa.String(length=255), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="quick_add"),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("client_request_id", sa.String(length=128), nullable=True),
        sa.Column("is_voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("voided_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["business_moment_id"], ["business_moments.moment_id"], name="fk_bae_moment"),
    )
    op.create_index("idx_bae_moment_occurred", "business_activity_events", ["business_moment_id", "occurred_at"])
    op.create_index("idx_bae_moment_action", "business_activity_events", ["business_moment_id", "action_type"])
    op.create_index(
        "uq_bae_moment_client_request",
        "business_activity_events",
        ["business_moment_id", "client_request_id"],
        unique=True,
        postgresql_where=sa.text("client_request_id IS NOT NULL"),
    )

    op.create_table(
        "business_activity_audit",
        sa.Column("audit_id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("before_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_baa_event"),
    )
    op.create_index("idx_baa_event", "business_activity_audit", ["event_id"])


def downgrade() -> None:
    op.drop_index("idx_baa_event", table_name="business_activity_audit")
    op.drop_table("business_activity_audit")
    op.drop_index("uq_bae_moment_client_request", table_name="business_activity_events")
    op.drop_index("idx_bae_moment_action", table_name="business_activity_events")
    op.drop_index("idx_bae_moment_occurred", table_name="business_activity_events")
    op.drop_table("business_activity_events")
