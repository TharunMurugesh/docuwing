#!/usr/bin/env python3
"""Engine Harness for standalone execution (Phase 1).

Constructs the Engine with Filesystem/Memory adapters and runs a trivial DAG
to demonstrate topological execution, event emission, and the plugin registry.
"""

from __future__ import annotations

import asyncio
import sys

import structlog

from docuwing_engine.adapters.filesystem.repositories import FilesystemRepositoryBundle
from docuwing_engine.adapters.filesystem.storage import FilesystemStorageProvider
from docuwing_engine.engine import DocuwingEngine
from docuwing_engine.workflow.events import LoggingEventPublisher
from docuwing_engine.workflow.models import (
    StepType,
    WorkflowDefinition,
    WorkflowStepDefinition,
)

# Initialize basic logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger(__name__)


async def main() -> int:
    storage = FilesystemStorageProvider()
    bundle = FilesystemRepositoryBundle(storage)
    event_publisher = LoggingEventPublisher(logger)

    # Initialize Engine
    engine = DocuwingEngine(
        repositories=bundle,
        event_publisher=event_publisher,
    )

    print("\n--- Registered Plugins ---")
    for plugin in engine.plugins.list(include_disabled=True):
        status = "ENABLED" if plugin.enabled else f"DISABLED ({plugin.disable_reason})"
        print(f"{plugin.manifest.name} ({plugin.manifest.category.value}): {status}")

    print("\n--- Submitting Workflow ---")

    # Create a simple DAG: Step A -> (Step B1, Step B2) -> Step C
    workflow_def = WorkflowDefinition(
        name="test-dag",
        steps=[
            WorkflowStepDefinition(id="step-a", step_type=StepType.PARSE),
            WorkflowStepDefinition(id="step-b1", step_type=StepType.LAYOUT, depends_on=["step-a"]),
            WorkflowStepDefinition(
                id="step-b2", step_type=StepType.CLASSIFY, depends_on=["step-a"]
            ),
            WorkflowStepDefinition(
                id="step-c", step_type=StepType.EXTRACT, depends_on=["step-b1", "step-b2"]
            ),
        ],
    )

    run = await engine.run_workflow(
        workflow_def=workflow_def,
        workspace="ws-123",
        document_id="doc-abc",
    )

    print(f"Submitted run: {run.id}")

    # Wait for simulated execution to finish
    await asyncio.sleep(1)

    finished_run = await engine.get_run(run.id)
    if finished_run:
        print(f"\nFinal run status: {finished_run.status.value}")
    else:
        print(f"\nFailed to retrieve run: {run.id}")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
