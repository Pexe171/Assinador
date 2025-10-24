"""Gerenciamento de sessões autenticadas do Telegram."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, Optional

from sqlalchemy import select

from TelegramManager.core.database import Database
from TelegramManager.storage import Account
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

    @contextmanager
    def _db_session(self) -> Iterator:
        sessao = self._database.session()
        try:
            yield sessao
        finally:
            sessao.close()

    @property
    def sessions(self) -> Dict[str, SessionInfo]:
        return dict(self._sessions)

    def load_persisted_sessions(self) -> None:
        """Carrega as contas persistidas no banco local."""

        with self._db_session() as sessao:
            stmt = select(Account)
            contas = sessao.scalars(stmt).all()

        self._sessions.clear()
        for conta in contas:
            self._sessions[conta.phone] = SessionInfo(
                phone=conta.phone,
                display_name=conta.display_name,
                status=conta.status or "offline",
            )
        logger.info("%s contas carregadas do banco local", len(self._sessions))

    def register_session(self, phone: str, display_name: str) -> SessionInfo:
        info = SessionInfo(phone=phone, display_name=display_name, status="online")
        self._sessions[phone] = info

        with self._db_session() as sessao:
            conta = sessao.scalar(select(Account).where(Account.phone == phone))
            if conta is None:
                conta = Account(
                    phone=phone,
                    display_name=display_name,
                    status="online",
                )
                sessao.add(conta)
            else:
                conta.display_name = display_name
                conta.status = "online"
            sessao.commit()

        logger.info("Sessão %s registrada", phone)
        return info

    def update_status(self, phone: str, status: str) -> None:
        if phone in self._sessions:
            self._sessions[phone].status = status
            logger.debug("Status da sessão %s atualizado para %s", phone, status)

        with self._db_session() as sessao:
            conta = sessao.scalar(select(Account).where(Account.phone == phone))
            if conta:
                conta.status = status
                sessao.commit()

    def get_session(self, phone: str) -> Optional[SessionInfo]:
        return self._sessions.get(phone)
