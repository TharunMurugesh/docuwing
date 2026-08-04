"""Engine event bus (EDS §9)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of engine events."""

    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    STEP_STARTED = "workflow.step.started"
    STEP_COMPLETED = "workflow.step.completed"
    STEP_FAILED = "workflow.step.failed"
    KNOWLEDGE_GRAPH_UPDATED = "knowledge.graph.updated"


class EngineEvent(BaseModel):
    """An event emitted by the engine."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    workspace: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, Any] = Field(default_factory=dict)


class EventPublisher(Protocol):
    """Protocol for publishing engine events."""

    async def publish(self, event: EngineEvent) -> None:
        """Publish an event to the bus."""
        ...


class LoggingEventPublisher:
    """A minimal event publisher that just logs (used in early phases)."""

    def __init__(self, logger: Any) -> None:
        self.logger = logger

    async def publish(self, event: EngineEvent) -> None:
        self.logger.info(
            "engine_event_published",
            event_type=event.event_type.value,
            workspace=event.workspace,
            event_id=event.id,
        )
