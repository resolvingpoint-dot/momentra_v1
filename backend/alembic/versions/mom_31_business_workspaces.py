"""Multi-company business workspaces + members + invitations.

Revision ID: mom_31_business_workspaces
Revises: mom_30_fix_ops_ai_signals

- Drop one-ACTIVE-workspace-per-owner unique
- Add branding/currency/timezone/created_by on business_workspaces
- business_workspace_members + business_workspace_invitations
- user_preferences.selected_business_workspace_id
- Backfill OWNER members from owned_by; MEMBER from moment members
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "mom_31_business_workspaces"
down_revision: Union[str, Sequence[str], None] = "mom_30_fix_ops_ai_signals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(
        "uq_business_workspaces_owned_by_active",
        table_name="business_workspaces",
    )

    op.add_column(
        "business_workspaces",
        sa.Column("logo_url", sa.Text(), nullable=True),
    )
    op.add_column(
        "business_workspaces",
        sa.Column("industry", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "business_workspaces",
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="INR"),
    )
    op.add_column(
        "business_workspaces",
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default="Asia/Kolkata"),
    )
    op.add_column(
        "business_workspaces",
        sa.Column("created_by", sa.Uuid(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE business_workspaces
            SET created_by = owned_by
            WHERE created_by IS NULL
            """
        )
    )
    op.alter_column("business_workspaces", "created_by", nullable=False)

    op.create_index(
        "idx_business_workspaces_owned_by",
        "business_workspaces",
        ["owned_by"],
    )
    op.create_index(
        "idx_business_workspaces_status",
        "business_workspaces",
        ["status"],
    )

    op.create_table(
        "business_workspace_members",
        sa.Column(
            "member_id",
            sa.Uuid(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="MEMBER"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="ACTIVE"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["business_workspaces.workspace_id"],
            name="fk_workspace_members_workspace",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "role IN ('OWNER', 'MANAGER', 'MEMBER')",
            name="chk_workspace_member_role",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INVITED', 'REMOVED')",
            name="chk_workspace_member_status",
        ),
    )
    op.create_index(
        "uq_workspace_members_workspace_user",
        "business_workspace_members",
        ["workspace_id", "user_id"],
        unique=True,
    )
    op.create_index(
        "idx_workspace_members_user",
        "business_workspace_members",
        ["user_id"],
    )

    op.create_table(
        "business_workspace_invitations",
        sa.Column(
            "invitation_id",
            sa.Uuid(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("invited_by", sa.Uuid(), nullable=False),
        sa.Column("invitee_email", sa.String(length=255), nullable=True),
        sa.Column("invitee_user_id", sa.Uuid(), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="MEMBER"),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["business_workspaces.workspace_id"],
            name="fk_workspace_invites_workspace",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "role IN ('OWNER', 'MANAGER', 'MEMBER')",
            name="chk_workspace_invite_role",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'SENT', 'ACCEPTED', 'REVOKED', 'EXPIRED')",
            name="chk_workspace_invite_status",
        ),
    )
    op.create_index(
        "uq_workspace_invite_token",
        "business_workspace_invitations",
        ["token"],
        unique=True,
    )
    op.create_index(
        "idx_workspace_invites_workspace",
        "business_workspace_invitations",
        ["workspace_id"],
    )

    # Backfill OWNER from workspace.owned_by
    op.execute(
        sa.text(
            """
            INSERT INTO business_workspace_members (
                member_id, workspace_id, user_id, role, status, created_at, updated_at
            )
            SELECT gen_random_uuid(), w.workspace_id, w.owned_by, 'OWNER', 'ACTIVE',
                   CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            FROM business_workspaces w
            WHERE w.status = 'ACTIVE'
              AND NOT EXISTS (
                SELECT 1 FROM business_workspace_members m
                WHERE m.workspace_id = w.workspace_id AND m.user_id = w.owned_by
              )
            """
        )
    )

    # Backfill MEMBER from moment members (distinct users per workspace)
    op.execute(
        sa.text(
            """
            INSERT INTO business_workspace_members (
                member_id, workspace_id, user_id, role, status, created_at, updated_at
            )
            SELECT gen_random_uuid(), bm.workspace_id, mm.user_id, 'MEMBER', 'ACTIVE',
                   CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            FROM business_moment_members mm
            JOIN business_moments bm ON bm.moment_id = mm.moment_id
            WHERE mm.user_id IS NOT NULL
              AND LOWER(COALESCE(mm.member_status, 'active')) IN ('active', 'configured')
              AND NOT EXISTS (
                SELECT 1 FROM business_workspace_members m
                WHERE m.workspace_id = bm.workspace_id AND m.user_id = mm.user_id
              )
            GROUP BY bm.workspace_id, mm.user_id
            """
        )
    )

    op.add_column(
        "user_preferences",
        sa.Column("selected_business_workspace_id", sa.Uuid(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_preferences", "selected_business_workspace_id")
    op.drop_index("idx_workspace_invites_workspace", table_name="business_workspace_invitations")
    op.drop_index("uq_workspace_invite_token", table_name="business_workspace_invitations")
    op.drop_table("business_workspace_invitations")
    op.drop_index("idx_workspace_members_user", table_name="business_workspace_members")
    op.drop_index("uq_workspace_members_workspace_user", table_name="business_workspace_members")
    op.drop_table("business_workspace_members")
    op.drop_index("idx_business_workspaces_status", table_name="business_workspaces")
    op.drop_index("idx_business_workspaces_owned_by", table_name="business_workspaces")
    op.drop_column("business_workspaces", "created_by")
    op.drop_column("business_workspaces", "timezone")
    op.drop_column("business_workspaces", "currency_code")
    op.drop_column("business_workspaces", "industry")
    op.drop_column("business_workspaces", "logo_url")
    op.create_index(
        "uq_business_workspaces_owned_by_active",
        "business_workspaces",
        ["owned_by"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )
