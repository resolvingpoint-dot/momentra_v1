"""Fix ops memory patterns spend category column.

``sp_refresh_business_operations_memory_patterns`` grouped by
``se.budget_category_name``, which does not exist on
``operations_spend_entries``. Use the budget category join (or
``spend_category`` fallback) instead.

Revision ID: mom_29_fix_ops_memory_patterns
Revises: mom_28_fix_ops_snapshot_cols

Revision id must stay <= 32 chars (alembic_version.version_num).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_29_fix_ops_memory_patterns"
down_revision: Union[str, Sequence[str], None] = "mom_28_fix_ops_snapshot_cols"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    defn = conn.execute(
        sa.text(
            """
            SELECT pg_get_functiondef(p.oid)
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = 'public'
              AND p.proname = 'sp_refresh_business_operations_memory_patterns'
              AND p.prokind = 'f'
            """
        )
    ).scalar()
    if not defn:
        return
    if "se.budget_category_name" not in defn:
        return

    patched = defn.replace(
        "se.budget_category_name",
        "COALESCE(bc.category_name, se.spend_category, 'Uncategorized')",
    )
    # Insert join before the spend WHERE clause (only occurrence in this proc).
    marker = "FROM operations_spend_entries se"
    join_sql = (
        "FROM operations_spend_entries se\n"
        "    LEFT JOIN business_operations_budget_categories bc\n"
        "      ON bc.budget_category_id = se.budget_category_id"
    )
    if marker not in patched:
        raise RuntimeError(
            "Could not locate operations_spend_entries join point in "
            "sp_refresh_business_operations_memory_patterns"
        )
    patched = patched.replace(marker, join_sql, 1)
    if "se.budget_category_name" in patched:
        raise RuntimeError(
            "Failed to remove se.budget_category_name from "
            "sp_refresh_business_operations_memory_patterns"
        )
    conn.execute(sa.text(patched))


def downgrade() -> None:
    # No-op: restoring the broken column reference would re-break activate.
    pass
