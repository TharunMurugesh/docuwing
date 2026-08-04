"""Workflow Orchestrator (EDS §9.2)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import structlog

from docuwing_engine.config import EngineSettings
from docuwing_engine.interfaces.repositories import WorkflowRepository
from docuwing_engine.workflow.events import EngineEvent, EventPublisher, EventType
from docuwing_engine.workflow.models import (
    RunStatus,
    WorkflowDefinition,
    WorkflowRun,
    WorkflowStepDefinition,
    WorkflowStepRun,
)

logger = structlog.get_logger(__name__)


class ConcurrencyLimitExceeded(Exception):
    """Raised when a workspace exceeds its active workflow limit."""

    pass


class WorkflowOrchestrator:
    """Topological DAG orchestrator.

    Phase 1 MVP implementation: schedules steps based on dependencies,
    enforces a per-workspace concurrency cap, and emits events.
    Execution is simulated in Phase 1 (no real steps run yet).
    """

    def __init__(
        self,
        repository: WorkflowRepository,
        event_publisher: EventPublisher,
        settings: EngineSettings | None = None,
    ) -> None:
        self._repo = repository
        self._events = event_publisher
        self._settings = settings or EngineSettings()

    async def submit(
        self,
        workflow_def: WorkflowDefinition,
        workspace: str,
        document_id: str,
        inputs: dict[str, Any] | None = None,
    ) -> WorkflowRun:
        """Submit a workflow for execution."""
        # Enforce concurrency cap
        active_runs = await self._repo.count_active_runs(workspace)
        if active_runs >= self._settings.max_concurrent_per_workspace:
            logger.warning(
                "concurrency_limit_exceeded",
                workspace=workspace,
                active=active_runs,
                limit=self._settings.max_concurrent_per_workspace,
            )
            raise ConcurrencyLimitExceeded(
                f"Workspace {workspace} has {active_runs} active runs "
                f"(limit {self._settings.max_concurrent_per_workspace})"
            )

        # Create the run
        run = WorkflowRun(
            workflow_id=workflow_def.id,
            workspace=workspace,
            document_id=document_id,
            status=RunStatus.PENDING,
            inputs=inputs or {},
        )
        await self._repo.save_run(run)

        # In a real implementation (Phase 12), this dispatches to Arq.
        # For Phase 1, we simulate immediate execution to prove the DAG logic.
        asyncio.create_task(self._execute_run(run, workflow_def))

        return run

    async def _execute_run(self, run: WorkflowRun, workflow_def: WorkflowDefinition) -> None:
        """Execute the workflow DAG (simulated for Phase 1)."""
        run.status = RunStatus.RUNNING
        run.started_at = datetime.now(UTC)
        await self._repo.update_run(run)

        await self._events.publish(
            EngineEvent(
                event_type=EventType.WORKFLOW_STARTED,
                workspace=run.workspace,
                payload={"run_id": run.id, "document_id": run.document_id},
            )
        )

        try:
            # Build dependency graph
            step_runs: dict[str, WorkflowStepRun] = {}
            for step_def in workflow_def.steps:
                step_run = WorkflowStepRun(run_id=run.id, step_id=step_def.id)
                await self._repo.save_step_run(step_run)
                step_runs[step_def.id] = step_run

            # Topological execution
            completed_steps: set[str] = set()
            in_progress: set[asyncio.Task[None]] = set()

            while len(completed_steps) < len(workflow_def.steps):
                # Find ready steps
                for step_def in workflow_def.steps:
                    if step_def.id in completed_steps or step_def.id in [
                        t.get_name() for t in in_progress
                    ]:
                        continue

                    # Are dependencies met?
                    if all(dep in completed_steps for dep in step_def.depends_on):
                        task = asyncio.create_task(
                            self._execute_step(run, step_def, step_runs[step_def.id]),
                            name=step_def.id,
                        )
                        in_progress.add(task)

                if not in_progress and len(completed_steps) < len(workflow_def.steps):
                    raise RuntimeError("Deadlock in workflow DAG")

                # Wait for at least one step to complete
                done, in_progress = await asyncio.wait(
                    in_progress, return_when=asyncio.FIRST_COMPLETED
                )

                for task in done:
                    completed_step_id = task.get_name()
                    completed_steps.add(completed_step_id)
                    # task exception handling omitted in this MVP

            run.status = RunStatus.SUCCEEDED
            run.completed_at = datetime.now(UTC)
            await self._repo.update_run(run)

            await self._events.publish(
                EngineEvent(
                    event_type=EventType.WORKFLOW_COMPLETED,
                    workspace=run.workspace,
                    payload={"run_id": run.id},
                )
            )

        except Exception as e:
            logger.exception("workflow_failed", run_id=run.id)
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            run.completed_at = datetime.now(UTC)
            await self._repo.update_run(run)

            await self._events.publish(
                EngineEvent(
                    event_type=EventType.WORKFLOW_FAILED,
                    workspace=run.workspace,
                    payload={"run_id": run.id, "error": str(e)},
                )
            )

    async def _execute_step(
        self, run: WorkflowRun, step_def: WorkflowStepDefinition, step_run: WorkflowStepRun
    ) -> None:
        """Execute a single step."""
        step_run.status = RunStatus.RUNNING
        step_run.started_at = datetime.now(UTC)
        await self._repo.update_step_run(step_run)

        await self._events.publish(
            EngineEvent(
                event_type=EventType.STEP_STARTED,
                workspace=run.workspace,
                payload={
                    "run_id": run.id,
                    "step_id": step_def.id,
                    "step_type": step_def.step_type.value,
                },
            )
        )

        # Simulate work
        await asyncio.sleep(0.1)

        step_run.status = RunStatus.SUCCEEDED
        step_run.completed_at = datetime.now(UTC)
        await self._repo.update_step_run(step_run)

        await self._events.publish(
            EngineEvent(
                event_type=EventType.STEP_COMPLETED,
                workspace=run.workspace,
                payload={"run_id": run.id, "step_id": step_def.id},
            )
        )
