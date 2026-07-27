"""create user_preferences, module_states, moments, moment_media

Revision ID: a1b2c3d4e5f6
Revises: 277f4d287e5d
Create Date: 2026-07-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '277f4d287e5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_preferences
    op.create_table('user_preferences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('selected_context', sa.String(32), nullable=False, server_default='MY_MONEY'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=True)

    # module_states
    op.create_table('module_states',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('module_key', sa.String(32), nullable=False),
        sa.Column('state', sa.String(32), nullable=False, server_default='EMPTY'),
        sa.Column('reason', sa.String(256), nullable=True),
        sa.Column('payload', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'module_key', name='uq_user_module')
    )
    op.create_index('ix_module_states_user_id_module_key', 'module_states', ['user_id', 'module_key'])

    # moments
    op.create_table('moments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('context_type', sa.String(32), nullable=False),
        sa.Column('moment_type', sa.String(64), nullable=True),
        sa.Column('title', sa.String(256), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='DRAFT'),
        sa.Column('setup_state', sa.String(32), nullable=False, server_default='EMPTY'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_moments_user_id_context_type', 'moments', ['user_id', 'context_type'])
    op.create_index('ix_moments_user_id_status', 'moments', ['user_id', 'status'])
    op.create_index('ix_moments_user_id_created_at', 'moments', ['user_id', 'created_at'])

    # moment_media
    op.create_table('moment_media',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('moment_id', sa.UUID(), nullable=True),
        sa.Column('storage_bucket', sa.String(256), nullable=True),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('media_type', sa.String(32), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['moment_id'], ['moments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('moment_media')
    op.drop_index('ix_moments_user_id_created_at')
    op.drop_index('ix_moments_user_id_status')
    op.drop_index('ix_moments_user_id_context_type')
    op.drop_table('moments')
    op.drop_index('ix_module_states_user_id_module_key')
    op.drop_table('module_states')
    op.drop_index('ix_user_preferences_user_id')
    op.drop_table('user_preferences')
