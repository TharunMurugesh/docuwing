"""Engine-specific configuration via Pydantic BaseSettings.

Each settings class reads from environment variables with the stated prefix.
These are independent of the App-layer settings in apps/api/core/settings.py.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class EngineSettings(BaseSettings):
    """Top-level engine runtime settings."""

    model_config = SettingsConfigDict(env_prefix="ENGINE_")

    # Workflow concurrency
    max_concurrent_per_workspace: int = 2
    workflow_timeout_seconds: int = 600

    # Database
    database_url: str = "postgresql+asyncpg://docuwing:docuwing@localhost:5432/docuwing_engine"

    # Redis (Arq task queue)
    redis_url: str = "redis://localhost:6379/0"


class EngineStorageSettings(BaseSettings):
    """Object storage settings for engine artifacts."""

    model_config = SettingsConfigDict(env_prefix="ENGINE_STORAGE_")

    backend: str = "minio"  # minio | filesystem
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "docuwing-engine"
    filesystem_root: str = "/tmp/docuwing-engine-storage"


class PromptRegistrySettings(BaseSettings):
    """Prompt registry settings."""

    model_config = SettingsConfigDict(env_prefix="ENGINE_PROMPTS_")

    artifacts_dir: str = "docuwing_engine/prompts/artifacts"
    default_model: str = "gpt-4o"


class CacheSettings(BaseSettings):
    """Cache layer settings."""

    model_config = SettingsConfigDict(env_prefix="ENGINE_CACHE_")

    enabled: bool = True
    redis_url: str = "redis://localhost:6379/1"
    ttl_seconds: int = 86400  # 24 hours
