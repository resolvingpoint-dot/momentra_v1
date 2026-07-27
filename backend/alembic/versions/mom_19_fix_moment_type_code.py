"""Fix personal moment highlight/turning-point procs.

Revision ID: mom_19_fix_moment_type_code
Revises: mom_18_master_expense

sp_refresh_personal_moment_highlights / turning_points referenced
personal_moments.moment_type_code, which does not exist (moments store
moment_type_id). Use personal_events.moment_type_code instead — same fix
pattern as mom_15 for vw_personal_moment_journey.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "mom_19_fix_moment_type_code"
down_revision: Union[str, Sequence[str], None] = "mom_18_master_expense"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE PROCEDURE sp_refresh_personal_moment_highlights(
            p_user_id UUID
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            DELETE FROM personal_moment_highlights
            WHERE user_id = p_user_id;

            INSERT INTO personal_moment_highlights
            (
                user_id,
                moment_id,
                moment_type_code,
                highlight_title,
                highlight_type,
                impact_label,
                impact_score,
                amount,
                occurred_at
            )
            SELECT
                e.user_id,
                e.moment_id,
                e.moment_type_code,
                e.event_title,
                'BEST_MOMENT',
                CASE
                    WHEN e.mood_delta >= 20 THEN 'Major Positive Shift'
                    WHEN e.mood_delta >= 10 THEN 'Positive Shift'
                    ELSE 'Meaningful Event'
                END,
                scored.impact_score,
                e.amount,
                e.event_date
            FROM personal_events e
            CROSS JOIN LATERAL (
                SELECT fn_personal_highlight_impact_score(
                    COALESCE(e.mood_delta,50),
                    COALESCE(e.outcome_score,50),
                    COALESCE(e.financial_weight_score,50),
                    fn_personal_recency_score(e.event_date)
                ) AS impact_score
            ) scored
            WHERE e.user_id = p_user_id
            ORDER BY scored.impact_score DESC
            LIMIT 50;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE PROCEDURE sp_refresh_personal_moment_turning_points(
            p_user_id UUID
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            DELETE FROM personal_moment_turning_points
            WHERE user_id = p_user_id;

            INSERT INTO personal_moment_turning_points
            (
                user_id,
                moment_id,
                moment_type_code,
                turning_point_title,
                turning_point_type,
                turning_point_description,
                impact_score,
                occurred_at
            )
            SELECT
                e.user_id,
                e.moment_id,
                e.moment_type_code,
                e.event_title,
                'BEHAVIOR_SHIFT',
                'Detected significant behavioral change',
                fn_personal_turning_point_impact_score(
                    COALESCE(e.behavior_shift_score,50),
                    COALESCE(e.duration_score,50),
                    COALESCE(e.outcome_score,50),
                    COALESCE(e.mood_delta,50)
                ),
                e.event_date
            FROM personal_events e
            WHERE e.user_id = p_user_id
              AND COALESCE(e.behavior_shift_score,0) >= 70;
        END;
        $$;
        """
    )


def downgrade() -> None:
    # Restore prior (broken) definitions that join personal_moments.moment_type_code.
    op.execute(
        """
        CREATE OR REPLACE PROCEDURE sp_refresh_personal_moment_highlights(
            p_user_id UUID
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            DELETE FROM personal_moment_highlights
            WHERE user_id = p_user_id;

            INSERT INTO personal_moment_highlights
            (
                user_id,
                moment_id,
                moment_type_code,
                highlight_title,
                highlight_type,
                impact_label,
                impact_score,
                amount,
                occurred_at
            )
            SELECT
                e.user_id,
                e.moment_id,
                m.moment_type_code,
                e.event_title,
                'BEST_MOMENT',
                CASE
                    WHEN e.mood_delta >= 20 THEN 'Major Positive Shift'
                    WHEN e.mood_delta >= 10 THEN 'Positive Shift'
                    ELSE 'Meaningful Event'
                END,
                fn_personal_highlight_impact_score(
                    COALESCE(e.mood_delta,50),
                    COALESCE(e.outcome_score,50),
                    COALESCE(e.financial_weight_score,50),
                    fn_personal_recency_score(e.event_date)
                ),
                e.amount,
                e.event_date
            FROM personal_events e
            JOIN personal_moments m
              ON m.moment_id = e.moment_id
            WHERE e.user_id = p_user_id
            ORDER BY impact_score DESC
            LIMIT 50;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE PROCEDURE sp_refresh_personal_moment_turning_points(
            p_user_id UUID
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            DELETE FROM personal_moment_turning_points
            WHERE user_id = p_user_id;

            INSERT INTO personal_moment_turning_points
            (
                user_id,
                moment_id,
                moment_type_code,
                turning_point_title,
                turning_point_type,
                turning_point_description,
                impact_score,
                occurred_at
            )
            SELECT
                e.user_id,
                e.moment_id,
                m.moment_type_code,
                e.event_title,
                'BEHAVIOR_SHIFT',
                'Detected significant behavioral change',
                fn_personal_turning_point_impact_score(
                    COALESCE(e.behavior_shift_score,50),
                    COALESCE(e.duration_score,50),
                    COALESCE(e.outcome_score,50),
                    COALESCE(e.mood_delta,50)
                ),
                e.event_date
            FROM personal_events e
            JOIN personal_moments m
              ON m.moment_id = e.moment_id
            WHERE e.user_id = p_user_id
              AND COALESCE(e.behavior_shift_score,0) >= 70;
        END;
        $$;
        """
    )
