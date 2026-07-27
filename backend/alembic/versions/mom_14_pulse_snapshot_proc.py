"""Add missing sp_refresh_personal_pulse_snapshot procedure alias.

Revision ID: mom_14_pulse_snapshot_proc
Revises: mom_13_account_type_codes

sp_refresh_personal_orchestration (mom_08) calls sp_refresh_personal_pulse_snapshot,
but mom_08 only defines sp_refresh_personal_pulse. Quick-add inserts fire
fn_personal_auto_refresh → orchestration → missing procedure → 500.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "mom_14_pulse_snapshot_proc"
down_revision: Union[str, Sequence[str], None] = "mom_13_account_type_codes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE PROCEDURE sp_refresh_personal_pulse_snapshot(
            p_moment_id UUID
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            CALL sp_refresh_personal_pulse(p_moment_id);
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP PROCEDURE IF EXISTS sp_refresh_personal_pulse_snapshot(UUID);")
