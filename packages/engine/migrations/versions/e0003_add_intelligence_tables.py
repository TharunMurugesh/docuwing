"""Add Phase 5-9 Engine-owned intelligence tables.

Revision ID: e0003
Revises: e0002
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "e0003"
down_revision = "e0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("engine_llm_call_log", sa.Column("id", sa.String(), primary_key=True), sa.Column("workspace", sa.String(), nullable=False), sa.Column("provider", sa.String(), nullable=False), sa.Column("model", sa.String(), nullable=False), sa.Column("operation", sa.String(), nullable=False), sa.Column("input_tokens", sa.Integer(), nullable=False), sa.Column("output_tokens", sa.Integer(), nullable=False), sa.Column("cost", sa.Float(), nullable=False), sa.Column("latency_ms", sa.Float(), nullable=False))
    op.create_table("engine_schema", sa.Column("id", sa.String(), primary_key=True), sa.Column("workspace", sa.String(), nullable=False), sa.Column("name", sa.String(), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("definition", sa.JSON(), nullable=False))
    op.create_table("engine_extraction_result", sa.Column("id", sa.String(), primary_key=True), sa.Column("workspace", sa.String(), nullable=False), sa.Column("document_id", sa.String(), nullable=False), sa.Column("schema_id", sa.String(), nullable=False), sa.Column("review_status", sa.String(), nullable=False))
    op.create_table("engine_extraction_field", sa.Column("id", sa.String(), primary_key=True), sa.Column("result_id", sa.String(), nullable=False), sa.Column("name", sa.String(), nullable=False), sa.Column("value", sa.JSON()), sa.Column("validation_status", sa.String(), nullable=False), sa.Column("human_confirmed", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table("engine_extraction_span", sa.Column("id", sa.String(), primary_key=True), sa.Column("field_id", sa.String(), nullable=False), sa.Column("block_id", sa.String(), nullable=False), sa.Column("start_offset", sa.Integer(), nullable=False), sa.Column("end_offset", sa.Integer(), nullable=False))
    op.create_table("engine_knowledge_graph", sa.Column("id", sa.String(), primary_key=True), sa.Column("workspace", sa.String(), nullable=False), sa.Column("document_id", sa.String(), nullable=False))
    op.create_table("engine_entity", sa.Column("id", sa.String(), primary_key=True), sa.Column("graph_id", sa.String(), nullable=False), sa.Column("type", sa.String(), nullable=False), sa.Column("name", sa.String(), nullable=False), sa.Column("attributes", sa.JSON(), nullable=False))
    op.create_table("engine_relationship", sa.Column("id", sa.String(), primary_key=True), sa.Column("graph_id", sa.String(), nullable=False), sa.Column("type", sa.String(), nullable=False), sa.Column("source_entity_id", sa.String(), nullable=False), sa.Column("target_entity_id", sa.String(), nullable=False))
    op.create_table("engine_semantic_table", sa.Column("id", sa.String(), primary_key=True), sa.Column("graph_id", sa.String(), nullable=False), sa.Column("name", sa.String(), nullable=False), sa.Column("rows", sa.JSON(), nullable=False))
    op.create_table("engine_document_chunk", sa.Column("id", sa.String(), primary_key=True), sa.Column("document_id", sa.String(), nullable=False), sa.Column("ordinal", sa.Integer(), nullable=False), sa.Column("text", sa.Text(), nullable=False))
    op.create_table("engine_embedding", sa.Column("id", sa.String(), primary_key=True), sa.Column("chunk_id", sa.String(), nullable=False), sa.Column("model", sa.String(), nullable=False), sa.Column("vector", Vector(), nullable=False))


def downgrade() -> None:
    for table in ("engine_embedding", "engine_document_chunk", "engine_semantic_table", "engine_relationship", "engine_entity", "engine_knowledge_graph", "engine_extraction_span", "engine_extraction_field", "engine_extraction_result", "engine_schema", "engine_llm_call_log"):
        op.drop_table(table)
