"""Postgres-backed workflow repository."""

from __future__ import annotations

import json
from typing import Any

from docuwing_engine.interfaces.repositories import WorkflowRepository
from docuwing_engine.workflow.models import (
    WorkflowRun,
    WorkflowStepRun,
)


class PostgresWorkflowRepository(WorkflowRepository):
    """Postgres implementation of WorkflowRepository.

    Uses Engine schema tables directly via SQLAlchemy core.
    """

    def __init__(self, session_factory: Any) -> None:
        self._session_factory = session_factory

    async def save_definition(self, definition: Any) -> Any:
        # Phase 1: MVP stub, real definition persistence added later
        return definition

    async def get_definition(self, definition_id: str) -> Any | None:
        return None

    async def save_run(self, run: WorkflowRun) -> WorkflowRun:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text(
                """
                INSERT INTO engine.workflow_run (
                    id, workflow_id, workspace, document_id, status, inputs
                )
                VALUES (:id, :workflow_id, :workspace, :document_id, :status, :inputs)
                """
            )
            await session.execute(
                stmt,
                {
                    "id": run.id,
                    "workflow_id": run.workflow_id,
                    "workspace": run.workspace,
                    "document_id": run.document_id,
                    "status": run.status.value,
                    "inputs": json.dumps(run.inputs),
                },
            )
            await session.commit()
        return run

    async def get_run(self, run_id: str) -> WorkflowRun | None:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text("SELECT * FROM engine.workflow_run WHERE id = :id")
            result = await session.execute(stmt, {"id": run_id})
            row = result.mappings().one_or_none()

            if not row:
                return None

            return WorkflowRun(
                id=row["id"],
                workflow_id=row["workflow_id"],
                workspace=row["workspace"],
                document_id=row["document_id"],
                status=row["status"],
                inputs=row["inputs"],
                started_at=row["started_at"],
                completed_at=row["completed_at"],
                error_message=row["error_message"],
            )

    async def update_run(self, run: WorkflowRun) -> WorkflowRun:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text(
                """
                UPDATE engine.workflow_run
                SET status = :status,
                    started_at = :started_at,
                    completed_at = :completed_at,
                    error_message = :error_message
                WHERE id = :id
                """
            )
            await session.execute(
                stmt,
                {
                    "id": run.id,
                    "status": run.status.value,
                    "started_at": run.started_at,
                    "completed_at": run.completed_at,
                    "error_message": run.error_message,
                },
            )
            await session.commit()
        return run

    async def save_step_run(self, step_run: WorkflowStepRun) -> WorkflowStepRun:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text(
                """
                INSERT INTO engine.workflow_step_run (id, run_id, step_id, status)
                VALUES (:id, :run_id, :step_id, :status)
                """
            )
            await session.execute(
                stmt,
                {
                    "id": step_run.id,
                    "run_id": step_run.run_id,
                    "step_id": step_run.step_id,
                    "status": step_run.status.value,
                },
            )
            await session.commit()
        return step_run

    async def get_step_runs(self, run_id: str) -> list[WorkflowStepRun]:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text("SELECT * FROM engine.workflow_step_run WHERE run_id = :run_id")
            result = await session.execute(stmt, {"run_id": run_id})
            rows = result.mappings().all()

            return [
                WorkflowStepRun(
                    id=row["id"],
                    run_id=row["run_id"],
                    step_id=row["step_id"],
                    status=row["status"],
                    started_at=row["started_at"],
                    completed_at=row["completed_at"],
                    error_message=row["error_message"],
                    outputs=row["outputs"],
                )
                for row in rows
            ]

    async def update_step_run(self, step_run: WorkflowStepRun) -> WorkflowStepRun:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text(
                """
                UPDATE engine.workflow_step_run
                SET status = :status,
                    started_at = :started_at,
                    completed_at = :completed_at,
                    error_message = :error_message,
                    outputs = :outputs
                WHERE id = :id
                """
            )
            await session.execute(
                stmt,
                {
                    "id": step_run.id,
                    "status": step_run.status.value,
                    "started_at": step_run.started_at,
                    "completed_at": step_run.completed_at,
                    "error_message": step_run.error_message,
                    "outputs": json.dumps(step_run.outputs),
                },
            )
            await session.commit()
        return step_run

    async def save_event(self, event: Any) -> Any:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text(
                """
                INSERT INTO engine.engine_event (id, event_type, workspace, timestamp, payload)
                VALUES (:id, :event_type, :workspace, :timestamp, :payload)
                """
            )
            await session.execute(
                stmt,
                {
                    "id": event.id,
                    "event_type": event.event_type.value,
                    "workspace": event.workspace,
                    "timestamp": event.timestamp,
                    "payload": json.dumps(event.payload),
                },
            )
            await session.commit()
        return event

    async def get_events(self, run_id: str | None = None, limit: int = 100) -> list[Any]:
        return []  # Basic stub

    async def count_active_runs(self, workspace: str) -> int:
        from sqlalchemy import text

        async with self._session_factory() as session:
            stmt = text(
                """
                SELECT COUNT(*) FROM engine.workflow_run
                WHERE workspace = :workspace AND status IN ('pending', 'running')
                """
            )
            result = await session.execute(stmt, {"workspace": workspace})
            return int(result.scalar_one())
