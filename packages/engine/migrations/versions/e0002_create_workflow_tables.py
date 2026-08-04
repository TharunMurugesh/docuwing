"""Engine-schema migration: create workflow and event tables.

Revision ID: e0002
Revises: e0001
Create Date: 2026-08-03
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "e0002"
down_revision = "e0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # workflow_run
    op.create_table(
        "workflow_run",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workflow_id", sa.String(255), nullable=False),
        sa.Column("workspace", sa.String(255), nullable=False),
        sa.Column("document_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("inputs", JSONB, nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        schema="engine",
    )
    op.create_index(
        "ix_engine_workflow_run_workspace", "workflow_run", ["workspace"], schema="engine"
    )

    # workflow_step_run
    op.create_table(
        "workflow_step_run",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "run_id",
            sa.String(36),
            sa.ForeignKey("engine.workflow_run.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_id", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("outputs", JSONB, nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        schema="engine",
    )
    op.create_index(
        "ix_engine_workflow_step_run_run_id", "workflow_step_run", ["run_id"], schema="engine"
    )

    # engine_event
    op.create_table(
        "engine_event",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("workspace", sa.String(255), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", JSONB, nullable=False, server_default="{}"),
        schema="engine",
    )
    op.create_index("ix_engine_event_workspace", "engine_event", ["workspace"], schema="engine")
    op.create_index("ix_engine_event_timestamp", "engine_event", ["timestamp"], schema="engine")

    # prompt_active_pointer
    op.create_table(
        "prompt_active_pointer",
        sa.Column("task_type", sa.String(255), nullable=False),
        sa.Column("model_id", sa.String(255), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("task_type", "model_id", name="pk_prompt_active_pointer"),
        schema="engine",
    )


def downgrade() -> None:
    op.drop_table("prompt_active_pointer", schema="engine")
    op.drop_table("engine_event", schema="engine")
    op.drop_table("workflow_step_run", schema="engine")
    op.drop_table("workflow_run", schema="engine")
