"""Layered Pydantic BaseSettings for the API application.

Each settings class reads from environment variables with its own prefix.
Settings classes for modules not yet built (Auth, LLM) are defined here
so the pattern is established from Phase 0.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Application database connection settings."""

    model_config = SettingsConfigDict(env_prefix="APP_DB_")

    url: str = "postgresql+asyncpg://docuwing:docuwing@localhost:5432/docuwing_app"
    pool_size: int = 20
    pool_overflow: int = 10
    echo: bool = False


class RedisSettings(BaseSettings):
    """Redis connection settings for caching and task queue."""

    model_config = SettingsConfigDict(env_prefix="APP_REDIS_")

    url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300


class StorageSettings(BaseSettings):
    """Object storage settings (MinIO / S3-compatible)."""

    model_config = SettingsConfigDict(env_prefix="APP_STORAGE_")

    endpoint: str = "localhost:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket: str = "docuwing-uploads"
    use_ssl: bool = False


class AuthSettings(BaseSettings):
    """Authentication settings — stub until Auth is implemented (Phase 13)."""

    model_config = SettingsConfigDict(env_prefix="APP_AUTH_")

    secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


class LLMSettings(BaseSettings):
    """LLM provider settings — stub until LLM Router (Phase 5)."""

    model_config = SettingsConfigDict(env_prefix="APP_LLM_")

    default_provider: str = "openai"
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"


class ObservabilitySettings(BaseSettings):
    """Observability / telemetry settings."""

    model_config = SettingsConfigDict(env_prefix="APP_OTEL_")

    service_name: str = "docuwing-api"
    exporter: str = "console"  # console | otlp
    otlp_endpoint: str = "http://localhost:4317"
    log_level: str = "INFO"
    log_format: str = "json"  # json | console


class AppSettings(BaseSettings):
    """Top-level application settings aggregating all sub-settings."""

    model_config = SettingsConfigDict(env_prefix="APP_")

    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Sub-settings (instantiated separately for independent env prefix handling)
    @staticmethod
    def database() -> DatabaseSettings:
        return DatabaseSettings()

    @staticmethod
    def redis() -> RedisSettings:
        return RedisSettings()

    @staticmethod
    def storage() -> StorageSettings:
        return StorageSettings()

    @staticmethod
    def auth() -> AuthSettings:
        return AuthSettings()

    @staticmethod
    def llm() -> LLMSettings:
        return LLMSettings()

    @staticmethod
    def observability() -> ObservabilitySettings:
        return ObservabilitySettings()


def get_settings() -> AppSettings:
    """Return the application settings singleton."""
    return AppSettings()
