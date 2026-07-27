"""Team Ops setup bridge: workspaces, extras, minor money, roles.

Revision ID: mom_21_team_ops_setup
Revises: mom_20_expense_subcategory
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "mom_21_team_ops_setup"
down_revision: Union[str, Sequence[str], None] = "mom_20_expense_subcategory"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "business_workspaces",
        sa.Column("workspace_id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owned_by", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index(
        "uq_business_workspaces_owned_by_active",
        "business_workspaces",
        ["owned_by"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )

    op.add_column("business_moment_setup", sa.Column("team_name", sa.String(length=255), nullable=True))
    op.add_column("business_moment_setup", sa.Column("country_code", sa.String(length=8), nullable=True))
    op.add_column("business_moment_setup", sa.Column("locale", sa.String(length=32), nullable=True))
    op.add_column("business_moment_setup", sa.Column("timezone", sa.String(length=64), nullable=True))
    op.add_column("business_moment_setup", sa.Column("review_cycle", sa.String(length=32), nullable=True))
    op.add_column(
        "business_moment_setup",
        sa.Column("monthly_budget_minor", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "business_moment_setup",
        sa.Column("setup_extras", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.alter_column("business_moment_setup", "work_style", existing_type=sa.String(length=50), nullable=True)
    op.alter_column("business_moment_setup", "visibility", existing_type=sa.String(length=50), nullable=True)

    op.add_column(
        "business_moment_structure",
        sa.Column("approval_threshold_minor", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "business_moment_structure",
        sa.Column("structure_extras", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.add_column("business_moment_members", sa.Column("local_id", sa.String(length=64), nullable=True))
    op.add_column(
        "business_moment_members",
        sa.Column("permission_profile", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "business_moment_members",
        sa.Column("permission_version", sa.Integer(), nullable=True),
    )
    op.create_index(
        "uq_business_members_moment_local",
        "business_moment_members",
        ["moment_id", "local_id"],
        unique=True,
        postgresql_where=sa.text("local_id IS NOT NULL"),
    )

    op.drop_constraint("chk_member_role", "business_moment_members", type_="check")
    op.create_check_constraint(
        "chk_member_role",
        "business_moment_members",
        "role::text = ANY (ARRAY["
        "'OWNER','ADMIN','TEAM_LEAD','OPERATIONS_LEAD','FINANCE_LEAD','BUDGET_OWNER',"
        "'APPROVER','CONTRIBUTOR','MEMBER','OBSERVER',"
        "'Team Member','Team Lead','Budget Owner','Approver','Observer',"
        "'Runway Owner','Finance Lead','Operations Lead','Financial Contributor',"
        "'Viewer','Operations Owner','Budget Controller','Contributor'"
        "]::text[])",
    )

    op.add_column("business_moment_invitations", sa.Column("local_id", sa.String(length=64), nullable=True))
    op.add_column("business_moment_invitations", sa.Column("channel", sa.String(length=32), nullable=True))
    op.add_column("business_moment_invitations", sa.Column("revoked_at", sa.DateTime(), nullable=True))
    op.add_column(
        "business_moment_invitations",
        sa.Column("send_idempotency_key", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "uq_business_invitation_active_channel",
        "business_moment_invitations",
        ["moment_id", "local_id", "channel"],
        unique=True,
        postgresql_where=sa.text(
            "local_id IS NOT NULL AND channel IS NOT NULL "
            "AND invite_status::text = ANY (ARRAY['pending','sent']::text[])"
        ),
    )


def downgrade() -> None:
    op.drop_index("uq_business_invitation_active_channel", table_name="business_moment_invitations")
    op.drop_column("business_moment_invitations", "send_idempotency_key")
    op.drop_column("business_moment_invitations", "revoked_at")
    op.drop_column("business_moment_invitations", "channel")
    op.drop_column("business_moment_invitations", "local_id")

    op.drop_constraint("chk_member_role", "business_moment_members", type_="check")
    op.create_check_constraint(
        "chk_member_role",
        "business_moment_members",
        "role::text = ANY (ARRAY["
        "'Team Member','Team Lead','Budget Owner','Approver','Observer',"
        "'Runway Owner','Finance Lead','Operations Lead','Financial Contributor',"
        "'Viewer','Operations Owner','Budget Controller','Contributor'"
        "]::text[])",
    )
    op.drop_index("uq_business_members_moment_local", table_name="business_moment_members")
    op.drop_column("business_moment_members", "permission_version")
    op.drop_column("business_moment_members", "permission_profile")
    op.drop_column("business_moment_members", "local_id")

    op.drop_column("business_moment_structure", "structure_extras")
    op.drop_column("business_moment_structure", "approval_threshold_minor")

    op.alter_column("business_moment_setup", "visibility", existing_type=sa.String(length=50), nullable=False)
    op.alter_column("business_moment_setup", "work_style", existing_type=sa.String(length=50), nullable=False)
    op.drop_column("business_moment_setup", "setup_extras")
    op.drop_column("business_moment_setup", "monthly_budget_minor")
    op.drop_column("business_moment_setup", "review_cycle")
    op.drop_column("business_moment_setup", "timezone")
    op.drop_column("business_moment_setup", "locale")
    op.drop_column("business_moment_setup", "country_code")
    op.drop_column("business_moment_setup", "team_name")

    op.drop_index("uq_business_workspaces_owned_by_active", table_name="business_workspaces")
    op.drop_table("business_workspaces")
