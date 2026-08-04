"""Engine-schema migration: create engine schema + enable pgvector.

Revision ID: e0001
Create Date: 2026-08-03
"""

from alembic import op

revision = "e0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS engine")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    # Don't drop the extension or schema on downgrade — too destructive
    pass
