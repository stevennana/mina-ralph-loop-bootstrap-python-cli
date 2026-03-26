from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="{{ENV_PREFIX}}_",
        extra="ignore",
    )

    app_name: str = "{{PROJECT_NAME}}"
    log_level: str = "INFO"
    state_dir: Path = Path("var/{{PYTHON_PACKAGE_NAME}}")
    logs_dir: Path = Path("logs")
    worker_poll_seconds: float = 2.0

    def ensure_runtime_dirs(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    return Settings()
