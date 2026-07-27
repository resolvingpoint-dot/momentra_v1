"""Extend team specialty tables + create missing typed runtime tables.

Revision ID: mom_25_team_operations_runtime
Revises: mom_24_business_activity_core
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "mom_25_team_operations_runtime"
down_revision: Union[str, Sequence[str], None] = "mom_24_business_activity_core"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_event_bridge(table: str) -> None:
    op.add_column(table, sa.Column("event_id", sa.Uuid(), nullable=True))
    op.add_column(
        table,
        sa.Column("amount_minor", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        table,
        sa.Column("is_voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_foreign_key(
        f"fk_{table}_event",
        table,
        "business_activity_events",
        ["event_id"],
        ["event_id"],
    )
    op.create_index(f"idx_{table}_event", table, ["event_id"])


def upgrade() -> None:
    for table in (
        "team_activities",
        "team_approval_requests",
        "team_issue_risks",
        "team_updates",
    ):
        _add_event_bridge(table)

    op.create_table(
        "team_recognitions",
        sa.Column("recognition_id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("moment_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("recipient_member_id", sa.Uuid(), nullable=True),
        sa.Column("recognition_type", sa.String(64), nullable=False, server_default="kudos"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("is_voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_rec_moment"),
        sa.ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_rec_event"),
    )
    op.create_index("idx_team_recognitions_moment", "team_recognitions", ["moment_id"])

    op.create_table(
        "team_meetings",
        sa.Column("meeting_id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("moment_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("meeting_at", sa.DateTime(), nullable=True),
        sa.Column("attendees", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("is_voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_meet_moment"),
        sa.ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_meet_event"),
    )
    op.create_index("idx_team_meetings_moment", "team_meetings", ["moment_id"])

    op.create_table(
        "team_escalations",
        sa.Column("escalation_id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("moment_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("is_voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_esc_moment"),
        sa.ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_esc_event"),
    )
    op.create_index("idx_team_escalations_moment", "team_escalations", ["moment_id"])

    op.create_table(
        "team_participation",
        sa.Column("participation_id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("moment_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=True),
        sa.Column("participation_type", sa.String(64), nullable=False, server_default="check_in"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("is_voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_part_moment"),
        sa.ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_part_event"),
    )
    op.create_index("idx_team_participation_moment", "team_participation", ["moment_id"])

    op.create_table(
        "team_member_updates",
        sa.Column("member_update_id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("moment_id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=True),
        sa.Column("update_kind", sa.String(64), nullable=False, server_default="status"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("is_voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["moment_id"], ["business_moments.moment_id"], name="fk_team_mu_moment"),
        sa.ForeignKeyConstraint(["event_id"], ["business_activity_events.event_id"], name="fk_team_mu_event"),
    )
    op.create_index("idx_team_member_updates_moment", "team_member_updates", ["moment_id"])


def downgrade() -> None:
    for table, idx in (
        ("team_member_updates", "idx_team_member_updates_moment"),
        ("team_participation", "idx_team_participation_moment"),
        ("team_escalations", "idx_team_escalations_moment"),
        ("team_meetings", "idx_team_meetings_moment"),
        ("team_recognitions", "idx_team_recognitions_moment"),
    ):
        op.drop_index(idx, table_name=table)
        op.drop_table(table)

    for table in ("team_updates", "team_issue_risks", "team_approval_requests", "team_activities"):
        op.drop_index(f"idx_{table}_event", table_name=table)
        op.drop_constraint(f"fk_{table}_event", table, type_="foreignkey")
        op.drop_column(table, "is_voided")
        op.drop_column(table, "amount_minor")
        op.drop_column(table, "event_id")
