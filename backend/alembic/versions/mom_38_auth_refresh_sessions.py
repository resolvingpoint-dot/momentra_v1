"""Auth refresh session store for revocation and rotation.

Revision ID: mom_38_auth_refresh_sessions
Revises: mom_36_money_event_title

Note: GitHub/Dokploy history is at mom_36 (mom_37 exists only in some local
trees). Chain mom_38 directly after mom_36 for deployable upgrades.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "mom_38_auth_refresh_sessions"
down_revision: Union[str, Sequence[str], None] = "mom_36_money_event_title"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_refresh_sessions (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            firebase_uid VARCHAR(128) NOT NULL,
            token_hash VARCHAR(64) NOT NULL,
            family_id UUID NOT NULL,
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            last_used_at TIMESTAMPTZ,
            user_agent TEXT,
            ip VARCHAR(64),
            CONSTRAINT uq_auth_refresh_sessions_token_hash UNIQUE (token_hash)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_auth_refresh_sessions_user_id
        ON auth_refresh_sessions (user_id)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_auth_refresh_sessions_firebase_uid
        ON auth_refresh_sessions (firebase_uid)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_auth_refresh_sessions_family_id
        ON auth_refresh_sessions (family_id)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_auth_refresh_sessions_token_hash
        ON auth_refresh_sessions (token_hash)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS auth_refresh_sessions")
