"""Fix ORDER BY in sp_refresh_personal_moment_highlights.

Revision ID: mom_35_fix_highlight_order_by
Revises: mom_34_fix_circle_refresh

INSERT INTO personal_moment_highlights … SELECT … ORDER BY impact_score
fails with UndefinedColumnError: the name binds to the INSERT target
column, which is not visible in that part of the query. Alias the
computed score and order by the alias.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "mom_35_fix_highlight_order_by"
down_revision: Union[str, Sequence[str], None] = "mom_34_fix_circle_refresh"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_PROC = """
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
            COALESCE(e.mood_delta, 50),
            COALESCE(e.outcome_score, 50),
            COALESCE(e.financial_weight_score, 50),
            fn_personal_recency_score(e.event_date)
        ) AS impact_score
    ) scored
    WHERE e.user_id = p_user_id
    ORDER BY scored.impact_score DESC
    LIMIT 50;
END;
$$;
"""


def upgrade() -> None:
    op.execute(_PROC)


def downgrade() -> None:
    # Prior broken ORDER BY impact_score (target-column ambiguity).
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
                fn_personal_highlight_impact_score(
                    COALESCE(e.mood_delta,50),
                    COALESCE(e.outcome_score,50),
                    COALESCE(e.financial_weight_score,50),
                    fn_personal_recency_score(e.event_date)
                ),
                e.amount,
                e.event_date
            FROM personal_events e
            WHERE e.user_id = p_user_id
            ORDER BY impact_score DESC
            LIMIT 50;
        END;
        $$;
        """
    )
