"""Contêiner de dependências simples para orquestrar serviços."""

from __future__ import annotations

from functools import cached_property

from app.config import AppConfig
from app.core.session_manager import SessionManager
from app.services.telegram_client import TelegramClientPool
from app.storage.database import Database


class Container:
    """Mantém instâncias compartilhadas entre a interface e o backend."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    @property
    def config(self) -> AppConfig:
        return self._config

    @cached_property
    def database(self) -> Database:
        return Database(self._config)

    @cached_property
    def session_manager(self) -> SessionManager:
        return SessionManager(config=self._config, database=self.database)

    @cached_property
    def telegram_pool(self) -> TelegramClientPool:
        return TelegramClientPool(config=self._config, session_manager=self.session_manager)
