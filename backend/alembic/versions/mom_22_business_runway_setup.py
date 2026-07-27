"""Business Runway setup bridge: minor money, goal months, CHECK expansion.

Revision ID: mom_22_business_runway_setup
Revises: mom_21_team_ops_setup
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "mom_22_business_runway_setup"
down_revision: Union[str, Sequence[str], None] = "mom_21_team_ops_setup"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "business_runway_setup",
        sa.Column("current_cash_minor", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "business_runway_setup",
        sa.Column("monthly_burn_minor", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "business_runway_setup",
        sa.Column("estimated_monthly_revenue_minor", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "business_runway_setup",
        sa.Column("runway_goal_months", sa.Integer(), nullable=True),
    )
    op.add_column(
        "business_runway_setup",
        sa.Column("revenue_status", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "business_runway_setup",
        sa.Column("country_code", sa.String(length=8), nullable=True),
    )
    op.add_column(
        "business_runway_setup",
        sa.Column("locale", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "business_runway_setup",
        sa.Column("timezone", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "business_runway_setup",
        sa.Column("setup_extras", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.alter_column("business_runway_setup", "runway_goal", existing_type=sa.String(length=100), nullable=True)

    op.drop_constraint("chk_runway_business_stage", "business_runway_setup", type_="check")
    op.create_check_constraint(
        "chk_runway_business_stage",
        "business_runway_setup",
        "business_stage::text = ANY (ARRAY["
        "'IDEA','PRE_REVENUE','EARLY_REVENUE','GROWTH','MATURE','TURNAROUND','CUSTOM',"
        "'idea','mvp','growth','smb','custom'"
        "]::text[])",
    )
    op.drop_constraint("chk_runway_goal", "business_runway_setup", type_="check")

    op.add_column(
        "business_runway_structure",
        sa.Column("runway_alert_threshold_months", sa.Integer(), nullable=True),
    )
    op.add_column(
        "business_runway_structure",
        sa.Column("collection_rate_percent", sa.Integer(), nullable=True),
    )
    op.add_column(
        "business_runway_structure",
        sa.Column("funding_sources", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "business_runway_structure",
        sa.Column("revenue_model_canonical", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "business_runway_structure",
        sa.Column("structure_extras", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.alter_column(
        "business_runway_structure",
        "revenue_model",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "business_runway_structure",
        "funding_structure",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "business_runway_structure",
        "runway_philosophy",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.drop_constraint("chk_runway_revenue_model", "business_runway_structure", type_="check")
    op.drop_constraint("chk_runway_funding_structure", "business_runway_structure", type_="check")
    op.drop_constraint("chk_runway_philosophy", "business_runway_structure", type_="check")

    op.add_column(
        "business_runway_governance_rules",
        sa.Column("large_expense_threshold_minor", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "business_runway_governance_rules",
        sa.Column("visibility", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "business_runway_governance_rules",
        sa.Column("governance_extras", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.drop_constraint("chk_member_role", "business_moment_members", type_="check")
    op.create_check_constraint(
        "chk_member_role",
        "business_moment_members",
        "role::text = ANY (ARRAY["
        "'OWNER','ADMIN','TEAM_LEAD','OPERATIONS_LEAD','FINANCE_LEAD','BUDGET_OWNER',"
        "'APPROVER','CONTRIBUTOR','MEMBER','OBSERVER',"
        "'FOUNDER','ADVISOR',"
        "'Team Member','Team Lead','Budget Owner','Approver','Observer',"
        "'Runway Owner','Finance Lead','Operations Lead','Financial Contributor',"
        "'Viewer','Operations Owner','Budget Controller','Contributor','Founder','Advisor'"
        "]::text[])",
    )


def downgrade() -> None:
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

    op.drop_column("business_runway_governance_rules", "governance_extras")
    op.drop_column("business_runway_governance_rules", "visibility")
    op.drop_column("business_runway_governance_rules", "large_expense_threshold_minor")

    op.drop_column("business_runway_structure", "structure_extras")
    op.drop_column("business_runway_structure", "revenue_model_canonical")
    op.drop_column("business_runway_structure", "funding_sources")
    op.drop_column("business_runway_structure", "collection_rate_percent")
    op.drop_column("business_runway_structure", "runway_alert_threshold_months")
    op.create_check_constraint(
        "chk_runway_revenue_model",
        "business_runway_structure",
        "revenue_model::text = ANY (ARRAY["
        "'product_sales','service_revenue','subscription_revenue','project_revenue',"
        "'commission_revenue','mixed','custom']::text[])",
    )
    op.create_check_constraint(
        "chk_runway_funding_structure",
        "business_runway_structure",
        "funding_structure::text = ANY (ARRAY["
        "'owner_funded','revenue_funded','bank_loan','credit_line',"
        "'investor_funded','government_grant','mixed','custom']::text[])",
    )
    op.create_check_constraint(
        "chk_runway_philosophy",
        "business_runway_structure",
        "runway_philosophy::text = ANY (ARRAY["
        "'conservative','balanced','growth_focused','aggressive_expansion']::text[])",
    )
    op.alter_column(
        "business_runway_structure",
        "runway_philosophy",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "business_runway_structure",
        "funding_structure",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "business_runway_structure",
        "revenue_model",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.drop_constraint("chk_runway_business_stage", "business_runway_setup", type_="check")
    op.create_check_constraint(
        "chk_runway_business_stage",
        "business_runway_setup",
        "business_stage::text = ANY (ARRAY['idea','mvp','growth','smb','custom']::text[])",
    )
    op.create_check_constraint(
        "chk_runway_goal",
        "business_runway_setup",
        "runway_goal::text = ANY (ARRAY["
        "'extend_runway','control_burn','plan_hiring','track_funding',"
        "'reach_profitability','custom']::text[])",
    )
    op.alter_column("business_runway_setup", "runway_goal", existing_type=sa.String(length=100), nullable=False)
    op.drop_column("business_runway_setup", "setup_extras")
    op.drop_column("business_runway_setup", "timezone")
    op.drop_column("business_runway_setup", "locale")
    op.drop_column("business_runway_setup", "country_code")
    op.drop_column("business_runway_setup", "revenue_status")
    op.drop_column("business_runway_setup", "runway_goal_months")
    op.drop_column("business_runway_setup", "estimated_monthly_revenue_minor")
    op.drop_column("business_runway_setup", "monthly_burn_minor")
    op.drop_column("business_runway_setup", "current_cash_minor")
