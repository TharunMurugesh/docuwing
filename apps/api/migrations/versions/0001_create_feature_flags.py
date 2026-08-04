"""App-schema migration: create feature_flags table.

Revision ID: 0001
Create Date: 2026-08-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the app schema
    op.execute("CREATE SCHEMA IF NOT EXISTS app")

    op.create_table(
        "feature_flags",
        sa.Column("name", sa.String(255), primary_key=True),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="app",
    )


def downgrade() -> None:
    op.drop_table("feature_flags", schema="app")
