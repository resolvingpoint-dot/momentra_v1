"""Business Operations setup bridge: minor money, extras, CHECK expansion.

Revision ID: mom_23_business_operations_setup
Revises: mom_22_business_runway_setup

Idempotent: ``business_operations_structure.approval_model`` / ``issue_sensitivity``
already exist from mom_04_business SQL; this revision must not re-ADD them.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_23_business_operations_setup"
down_revision: Union[str, Sequence[str], None] = "mom_22_business_runway_setup"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_column_if_missing(table: str, column: str, coltype_sql: str) -> None:
    op.execute(
        sa.text(
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {coltype_sql}"
        )
    )


def _drop_constraint_if_exists(name: str, table: str) -> None:
    op.execute(sa.text(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name}"))


def upgrade() -> None:
    # --- business_operations_setup ---
    _add_column_if_missing("business_operations_setup", "operations_name", "VARCHAR(255)")
    _add_column_if_missing("business_operations_setup", "operations_scope", "VARCHAR(64)")
    _add_column_if_missing(
        "business_operations_setup", "operating_model_canonical", "VARCHAR(64)"
    )
    _add_column_if_missing("business_operations_setup", "monthly_budget_minor", "BIGINT")
    _add_column_if_missing("business_operations_setup", "review_cycle", "VARCHAR(32)")
    _add_column_if_missing(
        "business_operations_setup", "financial_year_start", "VARCHAR(32)"
    )
    _add_column_if_missing("business_operations_setup", "country_code", "VARCHAR(8)")
    _add_column_if_missing("business_operations_setup", "locale", "VARCHAR(32)")
    _add_column_if_missing("business_operations_setup", "timezone", "VARCHAR(64)")
    _add_column_if_missing("business_operations_setup", "setup_extras", "JSONB")

    op.alter_column(
        "business_operations_setup",
        "operations_type",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "business_operations_setup",
        "operating_model",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "business_operations_setup",
        "operational_owner_role",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    _drop_constraint_if_exists("chk_business_operations_type", "business_operations_setup")
    _drop_constraint_if_exists("chk_business_operations_model", "business_operations_setup")
    _drop_constraint_if_exists(
        "chk_business_operations_owner_role", "business_operations_setup"
    )

    # --- business_operations_structure ---
    # approval_model / issue_sensitivity already exist from mom_04 — do not ADD again.
    _add_column_if_missing(
        "business_operations_structure", "vendor_dependency_level", "VARCHAR(32)"
    )
    _add_column_if_missing(
        "business_operations_structure", "monitoring_level_canonical", "VARCHAR(32)"
    )
    _add_column_if_missing(
        "business_operations_structure", "allocation_mode", "VARCHAR(32)"
    )
    _add_column_if_missing(
        "business_operations_structure", "budget_allocations", "JSONB"
    )
    _add_column_if_missing(
        "business_operations_structure", "budget_categories", "JSONB"
    )
    _add_column_if_missing(
        "business_operations_structure", "alert_conditions", "JSONB"
    )
    _add_column_if_missing(
        "business_operations_structure", "structure_extras", "JSONB"
    )

    op.alter_column(
        "business_operations_structure",
        "vendor_dependency",
        existing_type=sa.String(length=50),
        nullable=True,
    )
    op.alter_column(
        "business_operations_structure",
        "approval_model",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "business_operations_structure",
        "issue_sensitivity",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "business_operations_structure",
        "performance_review_cycle",
        existing_type=sa.String(length=50),
        nullable=True,
    )
    _drop_constraint_if_exists(
        "chk_operations_approval_model", "business_operations_structure"
    )
    _drop_constraint_if_exists(
        "chk_operations_issue_sensitivity", "business_operations_structure"
    )
    _drop_constraint_if_exists(
        "chk_operations_review_cycle", "business_operations_structure"
    )
    _drop_constraint_if_exists(
        "chk_operations_vendor_dependency", "business_operations_structure"
    )
    _drop_constraint_if_exists(
        "chk_operations_monitoring_level", "business_operations_governance_rules"
    )

    # --- business_operations_governance_rules ---
    _add_column_if_missing(
        "business_operations_governance_rules", "approval_threshold_minor", "BIGINT"
    )
    _add_column_if_missing(
        "business_operations_governance_rules", "secondary_approver_ids", "JSONB"
    )
    _add_column_if_missing(
        "business_operations_governance_rules", "alert_recipient_ids", "JSONB"
    )
    _add_column_if_missing(
        "business_operations_governance_rules", "visibility", "VARCHAR(32)"
    )
    _add_column_if_missing(
        "business_operations_governance_rules", "governance_extras", "JSONB"
    )

    # --- business_operations_budget_categories ---
    _add_column_if_missing(
        "business_operations_budget_categories", "allocation_id", "VARCHAR(64)"
    )
    _add_column_if_missing(
        "business_operations_budget_categories", "allocated_budget_minor", "BIGINT"
    )
    _add_column_if_missing(
        "business_operations_budget_categories", "percentage", "INTEGER"
    )
    _add_column_if_missing(
        "business_operations_budget_categories", "category_code", "VARCHAR(64)"
    )
    op.alter_column(
        "business_operations_budget_categories",
        "category_name",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    _drop_constraint_if_exists(
        "chk_operations_budget_category_name", "business_operations_budget_categories"
    )

    _drop_constraint_if_exists("chk_member_role", "business_moment_members")
    op.create_check_constraint(
        "chk_member_role",
        "business_moment_members",
        "role::text = ANY (ARRAY["
        "'OWNER','ADMIN','TEAM_LEAD','OPERATIONS_LEAD','FINANCE_LEAD','BUDGET_OWNER',"
        "'BUDGET_CONTROLLER','APPROVER','CONTRIBUTOR','MEMBER','OBSERVER',"
        "'FOUNDER','ADVISOR','VENDOR_MANAGER',"
        "'Team Member','Team Lead','Budget Owner','Approver','Observer',"
        "'Runway Owner','Finance Lead','Operations Lead','Financial Contributor',"
        "'Viewer','Operations Owner','Budget Controller','Contributor','Founder','Advisor',"
        "'Vendor Manager'"
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
        "'FOUNDER','ADVISOR',"
        "'Team Member','Team Lead','Budget Owner','Approver','Observer',"
        "'Runway Owner','Finance Lead','Operations Lead','Financial Contributor',"
        "'Viewer','Operations Owner','Budget Controller','Contributor','Founder','Advisor'"
        "]::text[])",
    )

    for col in (
        "category_code",
        "percentage",
        "allocated_budget_minor",
        "allocation_id",
    ):
        op.execute(
            sa.text(
                f"ALTER TABLE business_operations_budget_categories "
                f"DROP COLUMN IF EXISTS {col}"
            )
        )
    op.create_check_constraint(
        "chk_operations_budget_category_name",
        "business_operations_budget_categories",
        "category_name::text = ANY (ARRAY["
        "'inventory','payroll','marketing','operations','utilities','maintenance',"
        "'vendor_services','travel','technology','custom']::text[])",
    )
    op.alter_column(
        "business_operations_budget_categories",
        "category_name",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    for col in (
        "governance_extras",
        "visibility",
        "alert_recipient_ids",
        "secondary_approver_ids",
        "approval_threshold_minor",
    ):
        op.execute(
            sa.text(
                f"ALTER TABLE business_operations_governance_rules "
                f"DROP COLUMN IF EXISTS {col}"
            )
        )

    # Only drop columns this revision introduced (not legacy approval_model /
    # issue_sensitivity from mom_04).
    for col in (
        "structure_extras",
        "alert_conditions",
        "budget_categories",
        "budget_allocations",
        "allocation_mode",
        "monitoring_level_canonical",
        "vendor_dependency_level",
    ):
        op.execute(
            sa.text(
                f"ALTER TABLE business_operations_structure DROP COLUMN IF EXISTS {col}"
            )
        )

    for col in (
        "setup_extras",
        "timezone",
        "locale",
        "country_code",
        "financial_year_start",
        "review_cycle",
        "monthly_budget_minor",
        "operating_model_canonical",
        "operations_scope",
        "operations_name",
    ):
        op.execute(
            sa.text(
                f"ALTER TABLE business_operations_setup DROP COLUMN IF EXISTS {col}"
            )
        )

    op.create_check_constraint(
        "chk_business_operations_owner_role",
        "business_operations_setup",
        "operational_owner_role::text = ANY (ARRAY["
        "'Business Owner','Operations Manager','Department Head',"
        "'Branch Manager','Store Manager','Custom']::text[])",
    )
    op.create_check_constraint(
        "chk_business_operations_model",
        "business_operations_setup",
        "operating_model::text = ANY (ARRAY["
        "'budget_driven','vendor_driven','performance_driven',"
        "'compliance_driven','balanced_operations']::text[])",
    )
    op.create_check_constraint(
        "chk_business_operations_type",
        "business_operations_setup",
        "operations_type::text = ANY (ARRAY["
        "'store','branch','department','warehouse','restaurant',"
        "'clinic','factory','custom']::text[])",
    )
    op.alter_column(
        "business_operations_setup",
        "operational_owner_role",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "business_operations_setup",
        "operating_model",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "business_operations_setup",
        "operations_type",
        existing_type=sa.String(length=100),
        nullable=False,
    )
