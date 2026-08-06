from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DOCUWING_")
    storage_root: Path = Path.home() / ".docuwing"
    database_url: str | None = None
    ollama_url: str = "http://localhost:11434"
    primary_model: str = "qwen2.5:7b-instruct"
    router_model: str = "qwen2.5:3b-instruct"
    embedding_model: str = "nomic-embed-text"
    cors_origin: str = "http://localhost:3000"
    max_upload_mb: int = 50
    worker_poll_seconds: float = 0.5

    @property
    def db_url(self) -> str:
        path = (self.storage_root / "db" / "docuwing.sqlite3").resolve().as_posix()
        return self.database_url or f"sqlite+aiosqlite:///{path}"

    def ensure_layout(self) -> None:
        for item in (self.storage_root / "db", self.storage_root / "projects", self.storage_root / "tmp"):
            item.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_layout()
    return settings
