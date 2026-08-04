"""Public API shell for the Engine (EDS §2.3)."""

from __future__ import annotations

from typing import Any

from docuwing_engine.config import EngineSettings
from docuwing_engine.interfaces.repositories import RepositoryBundle
from docuwing_engine.plugins.registry import PluginRegistry
from docuwing_engine.workflow.events import EventPublisher
from docuwing_engine.workflow.models import WorkflowDefinition, WorkflowRun
from docuwing_engine.workflow.orchestrator import WorkflowOrchestrator


class DocuwingEngine:
    """The central Engine facade.

    Constructed with a RepositoryBundle (ports/adapters). All App-layer
    interactions with the engine flow through this class.
    """

    def __init__(
        self,
        repositories: RepositoryBundle,
        event_publisher: EventPublisher,
        settings: EngineSettings | None = None,
    ) -> None:
        self.repositories = repositories
        self.settings = settings or EngineSettings()

        # Initialize subsystems
        self.plugins = PluginRegistry()
        self.plugins.discover()

        self.orchestrator = WorkflowOrchestrator(
            repository=self.repositories.workflows,
            event_publisher=event_publisher,
            settings=self.settings,
        )

    async def run_workflow(
        self,
        workflow_def: WorkflowDefinition,
        workspace: str,
        document_id: str,
        inputs: dict[str, Any] | None = None,
    ) -> WorkflowRun:
        """Submit a workflow for execution."""
        return await self.orchestrator.submit(
            workflow_def=workflow_def,
            workspace=workspace,
            document_id=document_id,
            inputs=inputs,
        )

    async def get_run(self, run_id: str) -> WorkflowRun | None:
        """Get the status of a workflow run."""
        return await self.repositories.workflows.get_run(run_id)

    # Phase 2+ placeholders — signatures will be formalised in later phases
    async def process_document(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Implemented in Phase 2")

    async def extract(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Implemented in Phase 6")

    async def query(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Implemented in Phase 11")

    async def generate_output(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Implemented in Phase 10")
