"""Definições de configuração da aplicação."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel


class LoggingConfig(BaseModel):
    """Configurações de logging."""

    level: str = "INFO"


class PathsConfig(BaseModel):
    """Diretórios utilizados pela aplicação."""

    base_dir: Path = Path.home() / ".assinador"
    logs_dir: Path = base_dir / "logs"
    database_path: Path = base_dir / "data" / "app.sqlite3"
    sessions_dir: Path = base_dir / "sessions"


@dataclass
class AppConfig:
    """Objeto de configuração carregado a partir de variáveis de ambiente."""

    app_name: str = "Assinador Desktop"
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    telethon_api_id: str | None = None
    telethon_api_hash: str | None = None

    @classmethod
    def from_env(cls, env: Dict[str, Any] | None = None) -> "AppConfig":
        """Cria uma configuração baseada em um *mapping* de ambiente."""

        env = env or {}

        logging_config = LoggingConfig(level=env.get("APP_LOG_LEVEL", "INFO"))

        default_paths = PathsConfig()
        base_dir = Path(env.get("APP_BASE_DIR", default_paths.base_dir))
        paths_config = PathsConfig(
            base_dir=base_dir,
            logs_dir=Path(env.get("APP_LOG_DIR", base_dir / "logs")),
            database_path=Path(
                env.get("APP_DB_PATH", base_dir / "data" / "app.sqlite3")
            ),
            sessions_dir=Path(env.get("APP_SESSIONS_DIR", base_dir / "sessions")),
        )

        return cls(
            app_name=env.get("APP_NAME", "Assinador Desktop"),
            logging=logging_config,
            paths=paths_config,
            telethon_api_id=env.get("TELEGRAM_API_ID"),
            telethon_api_hash=env.get("TELEGRAM_API_HASH"),
        )
