"""Conexão com o banco de dados usando SQLAlchemy."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from TelegramManager.storage import models
from TelegramManager.utils.config import AppConfig


class Database:
    """Cria e mantém a *engine* SQLAlchemy."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        Path(self._config.paths.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(f"sqlite:///{self._config.paths.database_path}", future=True)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False, class_=Session)
        models.Base.metadata.create_all(self._engine)

    def session(self) -> Session:
        return self._session_factory()
