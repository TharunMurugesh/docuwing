"""Tests for prompt registry and resolution policy."""

import pytest

from docuwing_engine.adapters.memory.repositories import InMemoryPromptRepository
from docuwing_engine.config import PromptRegistrySettings
from docuwing_engine.prompts.registry import (
    ModelCompatibility,
    PromptArtifact,
    PromptRegistry,
    PromptResolutionError,
    PromptTemplate,
)


@pytest.fixture
def repo():
    return InMemoryPromptRepository()


@pytest.fixture
def registry(repo):
    reg = PromptRegistry(repo, PromptRegistrySettings(artifacts_dir="/tmp/none"))

    # Inject test artifacts manually rather than loading from disk
    reg._artifacts = {
        "test_task": {
            "v1": PromptArtifact(
                task_type="test_task",
                version="v1",
                compatibility=ModelCompatibility(
                    supported_models=["gpt-3.5"], supported_families=["openai"]
                ),
                template=PromptTemplate(),
            ),
            "v2": PromptArtifact(
                task_type="test_task",
                version="v2",
                compatibility=ModelCompatibility(
                    supported_models=["gpt-4o"], supported_families=["openai"]
                ),
                template=PromptTemplate(),
            ),
        }
    }
    return reg


@pytest.mark.asyncio
async def test_resolve_branch_1_active_model_pointer(registry, repo):
    # Set active pointer for specific model
    await repo.set_active_pointer("test_task", "gpt-4o", "v1")

    artifact = await registry.resolve("test_task", "gpt-4o")
    assert artifact.version == "v1"


@pytest.mark.asyncio
async def test_resolve_branch_2_active_family_pointer(registry, repo):
    # Set active pointer for family
    await repo.set_active_pointer("test_task", "family:openai", "v1")

    artifact = await registry.resolve("test_task", "unknown-openai-model", family="openai")
    assert artifact.version == "v1"


@pytest.mark.asyncio
async def test_resolve_branch_3_latest_compatible_model(registry):
    artifact = await registry.resolve("test_task", "gpt-4o")
    assert artifact.version == "v2"


@pytest.mark.asyncio
async def test_resolve_branch_4_latest_compatible_family(registry):
    artifact = await registry.resolve("test_task", "unknown-model", family="openai")
    # v2 is technically the latest by string sort
    assert artifact.version == "v2"


@pytest.mark.asyncio
async def test_resolve_hard_failure(registry):
    with pytest.raises(PromptResolutionError):
        await registry.resolve("test_task", "claude-3", family="anthropic")
