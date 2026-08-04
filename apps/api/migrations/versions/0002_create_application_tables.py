"""Application-owned tenancy tables; no FKs cross into engine schema."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("organization", sa.Column("id", sa.String(), primary_key=True), sa.Column("name", sa.String(), nullable=False))
    op.create_table("user", sa.Column("id", sa.String(), primary_key=True), sa.Column("organization_id", sa.String(), nullable=False), sa.Column("email", sa.String(), nullable=False, unique=True), sa.Column("role", sa.String(), nullable=False))
    op.create_table("project", sa.Column("id", sa.String(), primary_key=True), sa.Column("organization_id", sa.String(), nullable=False), sa.Column("name", sa.String(), nullable=False))
    op.create_table("collection", sa.Column("id", sa.String(), primary_key=True), sa.Column("project_id", sa.String(), nullable=False), sa.Column("name", sa.String(), nullable=False))

def downgrade() -> None:
    for table in ("collection", "project", "user", "organization"): op.drop_table(table)
