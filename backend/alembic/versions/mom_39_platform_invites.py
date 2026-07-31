"""Platform opaque invite codes (hashed lookup).

Revision ID: mom_39_platform_invites
Revises: mom_38_auth_refresh_sessions
"""
from typing import Sequence, Union

from alembic import op

revision: str = "mom_39_platform_invites"
down_revision: Union[str, Sequence[str], None] = "mom_38_auth_refresh_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS platform_invites (
            id UUID PRIMARY KEY,
            code_hash VARCHAR(64) NOT NULL,
            code_suffix VARCHAR(8) NOT NULL,
            invite_type VARCHAR(32) NOT NULL,
            target_context VARCHAR(32),
            target_id UUID,
            workspace_id UUID,
            moment_id UUID,
            role_code VARCHAR(64),
            status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
            created_by_user_id UUID NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ,
            revoked_by_user_id UUID,
            max_uses INTEGER NOT NULL DEFAULT 1,
            use_count INTEGER NOT NULL DEFAULT 0,
            last_used_at TIMESTAMPTZ,
            metadata JSONB,
            CONSTRAINT uq_platform_invites_code_hash UNIQUE (code_hash),
            CONSTRAINT chk_platform_invites_type
                CHECK (invite_type IN ('GROUP', 'COMPANY')),
            CONSTRAINT chk_platform_invites_status
                CHECK (status IN ('ACTIVE', 'ACCEPTED', 'EXPIRED', 'REVOKED', 'EXHAUSTED')),
            CONSTRAINT chk_platform_invites_max_uses CHECK (max_uses >= 1),
            CONSTRAINT chk_platform_invites_use_count CHECK (use_count >= 0)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_platform_invites_workspace_status
        ON platform_invites (workspace_id, status)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_platform_invites_moment_status
        ON platform_invites (moment_id, status)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_platform_invites_type_status
        ON platform_invites (invite_type, status)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_platform_invites_expires_at
        ON platform_invites (expires_at)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_platform_invites_created_by
        ON platform_invites (created_by_user_id)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS platform_invites")
