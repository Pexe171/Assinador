"""Conexão com o banco de dados usando SQLAlchemy."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, inspect, text
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
        self._apply_migrations()

    def session(self) -> Session:
        return self._session_factory()

    def _apply_migrations(self) -> None:
        """Aplica pequenas migrações automáticas para bancos já existentes."""

        inspector = inspect(self._engine)
        if "accounts" not in inspector.get_table_names():
            return

        colunas = {coluna["name"] for coluna in inspector.get_columns("accounts")}
        if "session_string" in colunas:
            return

        with self._engine.connect() as conexao:
            conexao.execute(text("ALTER TABLE accounts ADD COLUMN session_string TEXT"))
            conexao.commit()
