"""Fix sp_write_business_operations_audit to match business_audit_history columns.

Revision ID: mom_40_fix_ops_audit_columns
Revises: mom_39_platform_invites

The Ops AFTER INSERT/UPDATE triggers call sp_write_business_operations_audit,
which incorrectly inserted entity_type / entity_id / action_type / change_summary.
The live table uses source_table / source_record_id / field_name / new_value /
change_type / changed_by / changed_by_name (see mom_04). That mismatch caused
500s when logging operations issues (and other Ops activity writes).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "mom_40_fix_ops_audit_columns"
down_revision: Union[str, Sequence[str], None] = "mom_39_platform_invites"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sp_write_business_operations_audit(
            p_moment_id UUID,
            p_entity_type VARCHAR,
            p_record_id UUID,
            p_change_type VARCHAR,
            p_changed_by UUID,
            p_change_summary TEXT
        )
        RETURNS VOID
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_name VARCHAR(255);
            v_change VARCHAR(50);
        BEGIN
            SELECT COALESCE(NULLIF(TRIM(display_name), ''), NULLIF(TRIM(email), ''), 'User')
              INTO v_name
              FROM users
             WHERE id = p_changed_by
             LIMIT 1;

            v_name := COALESCE(v_name, 'User');
            v_change := LOWER(COALESCE(p_change_type, 'create'));
            -- Triggers pass created/updated or TG_OP (insert/update/delete).
            IF v_change IN ('created', 'insert') THEN
                v_change := 'create';
            ELSIF v_change IN ('updated', 'update') THEN
                v_change := 'edit';
            ELSIF v_change NOT IN (
                'create', 'edit', 'delete', 'restore', 'approve', 'reject', 'resolve'
            ) THEN
                v_change := 'edit';
            END IF;

            INSERT INTO business_audit_history (
                moment_id,
                source_table,
                source_record_id,
                field_name,
                old_value,
                new_value,
                change_type,
                changed_by,
                changed_by_name,
                change_reason,
                changed_at
            )
            VALUES (
                p_moment_id,
                COALESCE(NULLIF(TRIM(p_entity_type), ''), 'operations'),
                p_record_id,
                'status',
                NULL,
                COALESCE(NULLIF(TRIM(p_change_summary), ''), v_change),
                v_change,
                p_changed_by,
                v_name,
                p_change_summary,
                CURRENT_TIMESTAMP
            );
        END;
        $$;
        """
    )


def downgrade() -> None:
    # Restore the broken signature shape (for rollback only). Prefer re-running
    # mom_07 SQL if a true reverse is needed.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sp_write_business_operations_audit(
            p_moment_id UUID,
            p_entity_type VARCHAR,
            p_record_id UUID,
            p_change_type VARCHAR,
            p_changed_by UUID,
            p_change_summary TEXT
        )
        RETURNS VOID
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO business_audit_history (
                moment_id,
                entity_type,
                entity_id,
                action_type,
                changed_by,
                change_summary,
                changed_at
            )
            VALUES (
                p_moment_id,
                p_entity_type,
                p_record_id,
                p_change_type,
                p_changed_by,
                p_change_summary,
                CURRENT_TIMESTAMP
            );
        END;
        $$;
        """
    )
