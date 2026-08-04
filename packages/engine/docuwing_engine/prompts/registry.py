"""Prompt Registry implementation (EDS §8)."""

from __future__ import annotations

from pathlib import Path

import structlog
import yaml
from pydantic import BaseModel, Field

from docuwing_engine.config import PromptRegistrySettings
from docuwing_engine.interfaces.repositories import PromptRepository

logger = structlog.get_logger(__name__)


class ModelCompatibility(BaseModel):
    """Declares which models a prompt is compatible with."""

    supported_models: list[str] = Field(
        default_factory=list, description="List of specific model IDs (e.g., 'gpt-4o')"
    )
    supported_families: list[str] = Field(
        default_factory=list, description="List of model families (e.g., 'openai', 'anthropic')"
    )


class PromptTemplate(BaseModel):
    """The actual prompt content (Jinja2 template string)."""

    system: str = Field(default="", description="System prompt template")
    user: str = Field(default="", description="User prompt template")


class PromptArtifact(BaseModel):
    """A versioned prompt loaded from disk."""

    task_type: str = Field(description="e.g., 'classification.document_type'")
    version: str = Field(description="e.g., 'v1', 'v1.1'")
    description: str = Field(default="")
    compatibility: ModelCompatibility
    template: PromptTemplate


class PromptResolutionError(Exception):
    """Raised when no compatible prompt can be resolved."""

    pass


class PromptRegistry:
    """Registry for loading and resolving prompts (EDS §8.4).

    Follows a 4-branch resolution policy:
    1. active pointer for task + model
    2. active pointer for task + model family fallback
    3. latest version compatible with model
    4. latest version compatible with model family fallback
    """

    def __init__(
        self,
        repository: PromptRepository,
        settings: PromptRegistrySettings | None = None,
    ) -> None:
        self._repo = repository
        self._settings = settings or PromptRegistrySettings()
        self._artifacts: dict[
            str, dict[str, PromptArtifact]
        ] = {}  # task_type -> version -> artifact
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load all YAML prompt artifacts from the configured directory."""
        artifacts_dir = Path(self._settings.artifacts_dir)
        if not artifacts_dir.exists():
            logger.warning("prompt_artifacts_dir_not_found", path=str(artifacts_dir))
            return

        for filepath in artifacts_dir.glob("**/*.yaml"):
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                artifact = PromptArtifact(**data)
                task_type = artifact.task_type

                if task_type not in self._artifacts:
                    self._artifacts[task_type] = {}

                self._artifacts[task_type][artifact.version] = artifact
                logger.debug("loaded_prompt_artifact", task=task_type, version=artifact.version)
            except Exception as e:
                logger.error("failed_to_load_prompt_artifact", path=str(filepath), error=str(e))

    def get_artifact(self, task_type: str, version: str) -> PromptArtifact | None:
        """Get a specific version of a prompt."""
        return self._artifacts.get(task_type, {}).get(version)

    def _get_latest_compatible(
        self, task_type: str, model_id: str, family: str | None = None
    ) -> PromptArtifact | None:
        """Find the latest (string-sorted) compatible version."""
        task_artifacts = self._artifacts.get(task_type, {})
        if not task_artifacts:
            return None

        # Sort versions descending
        sorted_versions = sorted(task_artifacts.keys(), reverse=True)

        for version in sorted_versions:
            artifact = task_artifacts[version]
            if model_id in artifact.compatibility.supported_models:
                return artifact
            if family and family in artifact.compatibility.supported_families:
                return artifact

        return None

    async def resolve(
        self, task_type: str, model_id: str, family: str | None = None
    ) -> PromptArtifact:
        """Resolve the correct prompt version per EDS §8.4 policy."""

        # Branch 1: Active pointer for specific model
        active_version = await self._repo.get_active_pointer(task_type, model_id)
        if active_version:
            artifact = self.get_artifact(task_type, active_version)
            if artifact:
                logger.info("resolved_prompt", task=task_type, branch=1, version=active_version)
                return artifact

        # Branch 2: Active pointer for model family
        if family:
            active_version_family = await self._repo.get_active_pointer(
                task_type, f"family:{family}"
            )
            if active_version_family:
                artifact = self.get_artifact(task_type, active_version_family)
                if artifact:
                    logger.info(
                        "resolved_prompt", task=task_type, branch=2, version=active_version_family
                    )
                    return artifact

        # Branch 3 & 4: Latest compatible
        latest = self._get_latest_compatible(task_type, model_id, family)
        if latest:
            logger.info("resolved_prompt", task=task_type, branch="3/4", version=latest.version)
            return latest

        # Hard failure branch
        raise PromptResolutionError(
            f"No compatible prompt found for task={task_type}, model={model_id}, family={family}"
        )
