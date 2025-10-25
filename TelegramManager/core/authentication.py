"""Serviço centralizado para fluxos de autenticação de contas Telegram."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from threading import Event
from typing import Callable

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

from TelegramManager.core.session_manager import SessionInfo, SessionManager
from TelegramManager.utils.config import AppConfig

logger = logging.getLogger(__name__)


class AuthenticationError(RuntimeError):
    """Erro genérico durante a autenticação."""


class AuthenticationCancelledError(AuthenticationError):
    """Indica que o usuário cancelou o fluxo de autenticação."""


@dataclass
class _Callbacks:
    on_code: Callable[[str], None]
    on_state: Callable[[str], None] | None
    cancel_event: Event | None

    def emit_code(self, url: str) -> None:
        if self.cancelled:
            return
        self.on_code(url)

    def emit_state(self, mensagem: str) -> None:
        if self.cancelled:
            return
        if self.on_state:
            self.on_state(mensagem)

    @property
    def cancelled(self) -> bool:
        return bool(self.cancel_event and self.cancel_event.is_set())


class AuthenticationService:
    """Fornece fluxos de autenticação com Telethon de forma sincrônica."""

    def __init__(self, config: AppConfig, session_manager: SessionManager) -> None:
        self._config = config
        self._session_manager = session_manager

    def authenticate_with_qr(
        self,
        on_code: Callable[[str], None],
        *,
        on_state: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> SessionInfo:
        """Executa o fluxo de autenticação via QR Code de forma bloqueante."""

        if not self._config.telethon_api_id or not self._config.telethon_api_hash:
            raise AuthenticationError("Credenciais da API do Telegram não configuradas.")

        callbacks = _Callbacks(on_code=on_code, on_state=on_state, cancel_event=cancel_event)

        def _run() -> SessionInfo:
            logger.info("Iniciando fluxo de autenticação via QR Code.")
            return asyncio.run(self._authenticate_with_qr(callbacks))

        return _run()

    async def _authenticate_with_qr(self, callbacks: _Callbacks) -> SessionInfo:
        client = TelegramClient(
            StringSession(),
            api_id=int(self._config.telethon_api_id),
            api_hash=self._config.telethon_api_hash,
        )

        await client.connect()
        logger.info("Cliente Telethon conectado para autenticação via QR.")
        callbacks.emit_state("Conectado. Gerando QR Code...")

        try:
            qr_login = await client.qr_login()
            callbacks.emit_code(qr_login.url)
            callbacks.emit_state("Escaneie o QR Code usando o Telegram no celular.")

            while True:
                if callbacks.cancelled:
                    raise AuthenticationCancelledError("Fluxo cancelado pelo usuário.")
                try:
                    await asyncio.wait_for(qr_login.wait(), timeout=25)
                    break
                except asyncio.TimeoutError:
                    callbacks.emit_state("QR Code expirou, gerando um novo...")
                    logger.debug("QR Code expirou, solicitando um novo token.")
                    qr_login = await qr_login.recreate()
                    callbacks.emit_code(qr_login.url)
                except SessionPasswordNeededError as exc:
                    raise AuthenticationError(
                        "A conta possui senha em duas etapas. Use o login tradicional."
                    ) from exc

            callbacks.emit_state("Autenticando conta...")
            me = await client.get_me()
            if me is None:
                raise AuthenticationError("Não foi possível obter os dados da conta.")

            session_string = client.session.save()
            display_name_parts = [me.first_name or "", me.last_name or ""]
            display_name = " ".join(parte for parte in display_name_parts if parte).strip()
            if not display_name:
                display_name = me.username or str(me.id)

            phone = me.phone or str(me.id)

            info = self._session_manager.register_session(
                phone=phone,
                display_name=display_name,
                session_string=session_string,
            )
            logger.info("Conta %s autenticada via QR Code.", phone)
            callbacks.emit_state("Conta autenticada com sucesso.")
            return info

        finally:
            callbacks.emit_state("Finalizando conexão...")
            await client.disconnect()
            logger.info("Cliente Telethon desconectado do fluxo de autenticação.")
            callbacks.emit_state("Conexão encerrada.")
