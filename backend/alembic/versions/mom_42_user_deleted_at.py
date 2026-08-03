"""Add users.deleted_at and user_device_tokens for account deletion / push.

Revision ID: mom_42_user_deleted_at
Revises: mom_41_ops_quick_add_fields
"""
from typing import Sequence, Union

from alembic import op

revision: str = "mom_42_user_deleted_at"
down_revision: Union[str, Sequence[str], None] = "mom_41_ops_quick_add_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users (deleted_at) "
        "WHERE deleted_at IS NOT NULL"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_device_tokens (
            token_id UUID PRIMARY KEY,
            user_id UUID NOT NULL,
            platform VARCHAR(20) NOT NULL,
            fcm_token TEXT NOT NULL,
            app_version VARCHAR(64),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_user_device_tokens_user_id "
        "ON user_device_tokens (user_id)"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_device_tokens_user_fcm "
        "ON user_device_tokens (user_id, fcm_token)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_user_device_tokens_user_fcm")
    op.execute("DROP INDEX IF EXISTS ix_user_device_tokens_user_id")
    op.execute("DROP TABLE IF EXISTS user_device_tokens")
    op.execute("DROP INDEX IF EXISTS idx_users_deleted_at")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS deleted_at")
