"""Workflow execution models."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StepType(str, Enum):
    """Types of steps in a workflow."""

    PARSE = "parse"
    LAYOUT = "layout"
    CLASSIFY = "classify"
    EXTRACT = "extract"
    VALIDATE = "validate"
    BUILD_KNOWLEDGE = "build_knowledge"
    EMBED = "embed"
    GENERATE_OUTPUT = "generate_output"
    AGENT_TASK = "agent_task"


class RunStatus(str, Enum):
    """Status of a workflow run or step run."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepDefinition(BaseModel, frozen=True):
    """Definition of a single step within a workflow."""

    id: str = Field(description="Unique ID for this step within the workflow")
    step_type: StepType
    depends_on: list[str] = Field(
        default_factory=list, description="IDs of steps that must complete before this one"
    )
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel, frozen=True):
    """A DAG of steps defining a processing pipeline."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    version: int = Field(default=1, ge=1)
    steps: list[WorkflowStepDefinition]
    description: str = Field(default="")


class WorkflowStepRun(BaseModel):
    """Execution state of a single step."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = Field(description="ID of the parent WorkflowRun")
    step_id: str = Field(description="ID of the WorkflowStepDefinition")
    status: RunStatus = Field(default=RunStatus.PENDING)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    outputs: dict[str, Any] = Field(default_factory=dict)


class WorkflowRun(BaseModel):
    """Execution state of a full workflow."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = Field(description="ID of the WorkflowDefinition")
    workspace: str = Field(description="Tenant isolation key")
    document_id: str = Field(description="ID of the document being processed")
    status: RunStatus = Field(default=RunStatus.PENDING)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
