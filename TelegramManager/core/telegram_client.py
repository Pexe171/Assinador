"""Pool de clientes do Telethon gerenciando múltiplas contas."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict

from telethon import TelegramClient
from telethon.sessions import StringSession

from TelegramManager.core.session_manager import SessionManager
from TelegramManager.utils.async_worker import BackgroundWorker
from TelegramManager.utils.config import AppConfig

logger = logging.getLogger(__name__)


@dataclass
class ClientEntry:
    phone: str
    client: TelegramClient
    worker: BackgroundWorker


class TelegramClientPool:
    """Cria e reaproveita conexões com o Telegram."""

    def __init__(self, config: AppConfig, session_manager: SessionManager) -> None:
        self._config = config
        self._session_manager = session_manager
        self._clients: Dict[str, ClientEntry] = {}

    def get_or_create(self, phone: str) -> TelegramClient:
        if phone in self._clients:
            return self._clients[phone].client

        if not self._config.telethon_api_id or not self._config.telethon_api_hash:
            raise RuntimeError("Credenciais do Telegram não configuradas")

        client = TelegramClient(
            StringSession(),
            api_id=int(self._config.telethon_api_id),
            api_hash=self._config.telethon_api_hash,
        )
        worker = BackgroundWorker(nome=f"worker-{phone}")
        self._clients[phone] = ClientEntry(phone=phone, client=client, worker=worker)
        logger.info("Cliente do Telegram criado para %s", phone)
        return client

    async def disconnect_all(self) -> None:
        await asyncio.gather(*(entry.client.disconnect() for entry in self._clients.values()))
        for entry in self._clients.values():
            entry.worker.stop()
        self._clients.clear()
