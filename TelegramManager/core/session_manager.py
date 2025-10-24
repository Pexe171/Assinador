"""Gerenciamento de sessões autenticadas do Telegram."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from TelegramManager.core.database import Database
from TelegramManager.utils.config import AppConfig


logger = logging.getLogger(__name__)


@dataclass
class SessionInfo:
    """Metadados mínimos sobre uma sessão ativa."""

    phone: str
    display_name: str
    status: str


class SessionManager:
    """Centraliza persistência e ciclo de vida das sessões."""

    def __init__(self, config: AppConfig, database: Database) -> None:
        self._config = config
        self._database = database
        self._sessions: Dict[str, SessionInfo] = {}
        Path(self._config.paths.sessions_dir).mkdir(parents=True, exist_ok=True)

    @property
    def sessions(self) -> Dict[str, SessionInfo]:
        return dict(self._sessions)

    def load_persisted_sessions(self) -> None:
        """Carrega sessões do banco ou disco (implementação futura)."""
        logger.info("Carregando sessões persistidas (não implementado)")

    def register_session(self, phone: str, display_name: str) -> SessionInfo:
        info = SessionInfo(phone=phone, display_name=display_name, status="online")
        self._sessions[phone] = info
        logger.info("Sessão %s registrada", phone)
        return info

    def update_status(self, phone: str, status: str) -> None:
        if phone in self._sessions:
            self._sessions[phone].status = status
            logger.debug("Status da sessão %s atualizado para %s", phone, status)

    def get_session(self, phone: str) -> Optional[SessionInfo]:
        return self._sessions.get(phone)
