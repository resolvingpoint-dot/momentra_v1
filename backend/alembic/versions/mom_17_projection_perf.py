"""Phase 6.9 projection query indexes.

Revision ID: mom_17_projection_perf
Revises: mom_16_b7a_hardening
"""
from typing import Sequence, Union

from alembic import op

revision: str = "mom_17_projection_perf"
down_revision: Union[str, Sequence[str], None] = "mom_16_b7a_hardening"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_personal_recommendations_user_scope_status
        ON personal_recommendations (user_id, recommendation_scope, status);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_personal_memory_emotional_dna_user_current
        ON personal_memory_emotional_dna (user_id, is_current);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_personal_life_aggregate_snapshots_user_current
        ON personal_life_aggregate_snapshots (user_id, is_current);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_personal_life_health_snapshots_user_current
        ON personal_life_health_snapshots (user_id, is_current);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_moments_user_context_status
        ON moments (user_id, context_type, status);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_personal_recommendations_user_scope_status;")
    op.execute("DROP INDEX IF EXISTS ix_personal_memory_emotional_dna_user_current;")
    op.execute("DROP INDEX IF EXISTS ix_personal_life_aggregate_snapshots_user_current;")
    op.execute("DROP INDEX IF EXISTS ix_personal_life_health_snapshots_user_current;")
    op.execute("DROP INDEX IF EXISTS ix_moments_user_context_status;")
