"""Create personal_events view and harden auto-refresh trigger.

Revision ID: mom_15_personal_events_view
Revises: mom_14_pulse_snapshot_proc

Procedures sp_refresh_personal_moment_highlights / turning_points query
personal_events, which was never created (mom_10 logged vw_personal_moment_journey
as unfixable). Back the name with a view over personal_activity_timeline.

Also wrap fn_personal_auto_refresh in EXCEPTION so a broken refresh procedure
cannot roll back quick-add inserts.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "mom_15_personal_events_view"
down_revision: Union[str, Sequence[str], None] = "mom_14_pulse_snapshot_proc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE VIEW personal_events AS
        SELECT
            t.user_id,
            t.moment_id,
            t.moment_type_code,
            t.event_type,
            t.display_title AS event_title,
            t.display_amount AS amount,
            t.event_occurred_at AS event_date,
            NULL::DECIMAL(5,2) AS mood_delta,
            NULL::DECIMAL(5,2) AS outcome_score,
            NULL::DECIMAL(5,2) AS financial_weight_score,
            NULL::DECIMAL(5,2) AS behavior_shift_score,
            NULL::DECIMAL(5,2) AS duration_score
        FROM personal_activity_timeline t
        WHERE t.is_voided = FALSE;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW vw_personal_moment_journey AS
        SELECT
            e.user_id,
            e.moment_id,
            e.moment_type_code,
            e.event_date,
            e.event_title,
            e.amount,
            e.mood_delta,
            e.outcome_score
        FROM personal_events e
        JOIN personal_moments m ON m.moment_id = e.moment_id;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_personal_auto_refresh()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        BEGIN
            BEGIN
                CALL sp_refresh_personal_orchestration(NEW.moment_id);
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING
                        'fn_personal_auto_refresh skipped for moment %: %',
                        NEW.moment_id,
                        SQLERRM;
            END;
            RETURN NEW;
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_personal_auto_refresh()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        BEGIN
            CALL sp_refresh_personal_orchestration(NEW.moment_id);
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute("DROP VIEW IF EXISTS vw_personal_moment_journey CASCADE;")
    op.execute("DROP VIEW IF EXISTS personal_events CASCADE;")
