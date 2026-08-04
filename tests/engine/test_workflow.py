"""Tests for workflow execution (DAG scheduling)."""

import pytest

from docuwing_engine.adapters.memory.repositories import InMemoryWorkflowRepository
from docuwing_engine.config import EngineSettings
from docuwing_engine.workflow.events import LoggingEventPublisher
from docuwing_engine.workflow.models import (
    RunStatus,
    StepType,
    WorkflowDefinition,
    WorkflowStepDefinition,
)
from docuwing_engine.workflow.orchestrator import ConcurrencyLimitExceeded, WorkflowOrchestrator


class MockLogger:
    def info(self, *args, **kwargs):
        pass


@pytest.fixture
def repo():
    return InMemoryWorkflowRepository()


@pytest.fixture
def orchestrator(repo):
    publisher = LoggingEventPublisher(MockLogger())
    settings = EngineSettings(max_concurrent_per_workspace=2)
    return WorkflowOrchestrator(repo, publisher, settings)


@pytest.mark.asyncio
async def test_workflow_dag_execution(orchestrator, repo):
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

    run = await orchestrator.submit(workflow_def, "ws-1", "doc-1")

    # Wait for execution (simulated in MVP with asyncio.sleep)
    import asyncio

    await asyncio.sleep(0.5)

    finished_run = await repo.get_run(run.id)
    assert finished_run.status == RunStatus.SUCCEEDED

    # All 4 steps should be succeeded
    step_runs = await repo.get_step_runs(run.id)
    assert len(step_runs) == 4
    for sr in step_runs:
        assert sr.status == RunStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_concurrency_limit_enforced(orchestrator):
    workflow_def = WorkflowDefinition(
        name="test-single",
        steps=[WorkflowStepDefinition(id="step-1", step_type=StepType.PARSE)],
    )

    # Submit 2 runs (limit is 2)
    await orchestrator.submit(workflow_def, "ws-1", "doc-1")
    await orchestrator.submit(workflow_def, "ws-1", "doc-2")

    # 3rd run should raise
    with pytest.raises(ConcurrencyLimitExceeded):
        await orchestrator.submit(workflow_def, "ws-1", "doc-3")
