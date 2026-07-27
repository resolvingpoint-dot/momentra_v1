"""Fix sp_refresh_circle_participants to match real group schema.

The original procedure referenced non-existent
``group_moment_participants``, ``group_moment_id``, and ``created_by_user_id``.
Actual tables use ``group_moment_members``, ``moment_id``, and ``created_by``
(with ``display_name`` / ``contact_phone`` / ``contact_email``).

This made every ``POST /api/v1/circle/refresh`` return HTTP 500.

Revision ID: mom_34_fix_circle_refresh
Revises: mom_33_harden_personal_life_snap
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_34_fix_circle_refresh"
down_revision: Union[str, Sequence[str], None] = "mom_33_harden_personal_life_snap"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CIRCLE_PARTICIPANTS_PROC = r"""
CREATE OR REPLACE PROCEDURE sp_refresh_circle_participants(p_user_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN

    /* GROUP PARTICIPANTS — from group_moment_members */
    INSERT INTO circle_participants (
        user_id,
        participant_user_id,
        participant_name,
        participant_phone,
        participant_email,
        first_seen_date,
        last_seen_date,
        is_active,
        updated_at
    )
    SELECT
        gm.created_by AS user_id,
        gmm.user_id AS participant_user_id,
        COALESCE(NULLIF(TRIM(gmm.display_name), ''), 'Unknown Participant'),
        gmm.contact_phone,
        gmm.contact_email,
        MIN(gmm.created_at)::DATE,
        MAX(COALESCE(gmm.joined_at, gmm.created_at))::DATE,
        BOOL_OR(
            gm.status IN ('ACTIVE', 'IN_PROGRESS', 'LIVE')
            OR UPPER(gmm.status) IN ('ACTIVE', 'INVITED')
        ),
        CURRENT_TIMESTAMP
    FROM group_moment_members gmm
    JOIN group_moments gm
        ON gm.moment_id = gmm.moment_id
    WHERE gm.created_by = p_user_id
    GROUP BY
        gm.created_by,
        gmm.user_id,
        gmm.display_name,
        gmm.contact_phone,
        gmm.contact_email
    ON CONFLICT (
        user_id,
        participant_name,
        COALESCE(participant_phone, ''),
        COALESCE(participant_email, '')
    )
    DO UPDATE SET
        last_seen_date = GREATEST(circle_participants.last_seen_date, EXCLUDED.last_seen_date),
        is_active = circle_participants.is_active OR EXCLUDED.is_active,
        updated_at = CURRENT_TIMESTAMP;

    /* BUSINESS PARTICIPANTS / MEMBERS */
    INSERT INTO circle_participants (
        user_id,
        participant_user_id,
        participant_name,
        participant_phone,
        participant_email,
        first_seen_date,
        last_seen_date,
        is_active,
        updated_at
    )
    SELECT
        bm.created_by AS user_id,
        bmm.user_id AS participant_user_id,
        COALESCE(NULLIF(TRIM(bmm.name), ''), 'Unknown Participant') AS participant_name,
        bmm.mobile AS participant_phone,
        bmm.email AS participant_email,
        MIN(bmm.created_at)::DATE,
        MAX(COALESCE(bmm.updated_at, bmm.created_at))::DATE,
        BOOL_OR(
            UPPER(bm.status::text) IN ('ACTIVE', 'IN_PROGRESS', 'LIVE')
            OR UPPER(bmm.member_status::text) IN ('ACTIVE', 'INVITED', 'CONFIGURED')
        ),
        CURRENT_TIMESTAMP
    FROM business_moment_members bmm
    JOIN business_moments bm
        ON bm.moment_id = bmm.moment_id
    WHERE bm.created_by = p_user_id
    GROUP BY
        bm.created_by,
        bmm.user_id,
        bmm.name,
        bmm.mobile,
        bmm.email
    ON CONFLICT (
        user_id,
        participant_name,
        COALESCE(participant_phone, ''),
        COALESCE(participant_email, '')
    )
    DO UPDATE SET
        last_seen_date = GREATEST(circle_participants.last_seen_date, EXCLUDED.last_seen_date),
        is_active = circle_participants.is_active OR EXCLUDED.is_active,
        updated_at = CURRENT_TIMESTAMP;

    /* GROUP SOURCES */
    INSERT INTO circle_participant_sources (
        circle_participant_id,
        user_id,
        source_type,
        source_moment_id,
        source_moment_name,
        source_moment_type,
        participation_date,
        is_active_source
    )
    SELECT
        cp.circle_participant_id,
        gm.created_by,
        'GROUP',
        gm.moment_id,
        gm.moment_name,
        gm.moment_type,
        gmm.created_at::DATE,
        gm.status IN ('ACTIVE', 'IN_PROGRESS', 'LIVE')
            OR UPPER(gmm.status) IN ('ACTIVE', 'INVITED')
    FROM group_moment_members gmm
    JOIN group_moments gm
        ON gm.moment_id = gmm.moment_id
    JOIN circle_participants cp
        ON cp.user_id = gm.created_by
       AND cp.participant_name = COALESCE(NULLIF(TRIM(gmm.display_name), ''), 'Unknown Participant')
       AND COALESCE(cp.participant_phone, '') = COALESCE(gmm.contact_phone, '')
       AND COALESCE(cp.participant_email, '') = COALESCE(gmm.contact_email, '')
    WHERE gm.created_by = p_user_id
    ON CONFLICT (circle_participant_id, source_type, source_moment_id)
    DO NOTHING;

    /* BUSINESS SOURCES */
    INSERT INTO circle_participant_sources (
        circle_participant_id,
        user_id,
        source_type,
        source_moment_id,
        source_moment_name,
        source_moment_type,
        participation_date,
        is_active_source
    )
    SELECT
        cp.circle_participant_id,
        bm.created_by,
        'BUSINESS',
        bm.moment_id,
        bm.moment_name,
        bm.moment_type,
        bmm.created_at::DATE,
        (
            UPPER(bm.status::text) IN ('ACTIVE', 'IN_PROGRESS', 'LIVE')
            OR UPPER(bmm.member_status::text) IN ('ACTIVE', 'INVITED', 'CONFIGURED')
        )
    FROM business_moment_members bmm
    JOIN business_moments bm
        ON bm.moment_id = bmm.moment_id
    JOIN circle_participants cp
        ON cp.user_id = bm.created_by
       AND cp.participant_name = COALESCE(NULLIF(TRIM(bmm.name), ''), 'Unknown Participant')
       AND COALESCE(cp.participant_phone, '') = COALESCE(bmm.mobile, '')
       AND COALESCE(cp.participant_email, '') = COALESCE(bmm.email, '')
    WHERE bm.created_by = p_user_id
    ON CONFLICT (circle_participant_id, source_type, source_moment_id)
    DO NOTHING;

END;
$$;
"""


def upgrade() -> None:
    op.execute(sa.text(_CIRCLE_PARTICIPANTS_PROC))


def downgrade() -> None:
    pass
