"""Serviço centralizado para fluxos de autenticação de contas Telegram."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from threading import Event
from typing import Callable

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession

from TelegramManager.core.session_manager import SessionInfo, SessionManager
from TelegramManager.utils.config import AppConfig

logger = logging.getLogger(__name__)


class AuthenticationError(RuntimeError):
    """Erro genérico durante a autenticação."""


class AuthenticationCancelledError(AuthenticationError):
    """Indica que o usuário cancelou o fluxo de autenticação."""


@dataclass
class _StateCallbacks:
    """Coordena mensagens de status e cancelamento opcional."""

    on_state: Callable[[str], None] | None
    cancel_event: Event | None

    def emit(self, mensagem: str) -> None:
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

    def request_login_code(
        self,
        *,
        phone: str,
        on_state: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> str:
        """Envia o código de autenticação via Telegram e retorna o *hash* associado."""

        if not self._config.telethon_api_id or not self._config.telethon_api_hash:
            raise AuthenticationError("Credenciais da API do Telegram não configuradas.")

        callbacks = _StateCallbacks(on_state=on_state, cancel_event=cancel_event)

        def _run() -> str:
            logger.info("Solicitando código de login para %s.", phone)
            return asyncio.run(self._request_login_code(phone=phone, callbacks=callbacks))

        return _run()

    def authenticate_with_code(
        self,
        *,
        phone: str,
        code: str,
        phone_code_hash: str,
        display_name: str | None = None,
        password: str | None = None,
        on_state: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> SessionInfo:
        """Conclui a autenticação utilizando o código recebido pelo usuário."""

        if not self._config.telethon_api_id or not self._config.telethon_api_hash:
            raise AuthenticationError("Credenciais da API do Telegram não configuradas.")

        callbacks = _StateCallbacks(on_state=on_state, cancel_event=cancel_event)

        def _run() -> SessionInfo:
            logger.info("Finalizando autenticação por código para %s.", phone)
            return asyncio.run(
                self._authenticate_with_code(
                    phone=phone,
                    code=code,
                    phone_code_hash=phone_code_hash,
                    display_name=display_name,
                    password=password,
                    callbacks=callbacks,
                )
            )

        return _run()

    async def _request_login_code(self, *, phone: str, callbacks: _StateCallbacks) -> str:
        client = TelegramClient(
            StringSession(),
            api_id=int(self._config.telethon_api_id),
            api_hash=self._config.telethon_api_hash,
        )

        await client.connect()
        logger.info("Cliente Telethon conectado para solicitar código.")
        callbacks.emit("Conectado. Solicitando envio do código...")

        try:
            if callbacks.cancelled:
                raise AuthenticationCancelledError("Fluxo cancelado pelo usuário.")

            resultado = await client.send_code_request(phone)
            callbacks.emit("Código enviado. Verifique o Telegram associado ao número informado.")
            return resultado.phone_code_hash
        except FloodWaitError as exc:
            segundos = getattr(exc, "seconds", None)
            detalhe = f" Aguarde {segundos} segundos." if segundos else ""
            raise AuthenticationError(
                "Muitas tentativas em sequência. Tente novamente mais tarde." + detalhe
            ) from exc
        except PhoneNumberInvalidError as exc:
            raise AuthenticationError("O número informado não é válido no Telegram.") from exc
        finally:
            callbacks.emit("Finalizando conexão...")
            await client.disconnect()
            callbacks.emit("Conexão encerrada.")
            logger.info("Cliente Telethon desconectado do envio de código.")

    async def _authenticate_with_code(
        self,
        *,
        phone: str,
        code: str,
        phone_code_hash: str,
        display_name: str | None,
        password: str | None,
        callbacks: _StateCallbacks,
    ) -> SessionInfo:
        client = TelegramClient(
            StringSession(),
            api_id=int(self._config.telethon_api_id),
            api_hash=self._config.telethon_api_hash,
        )

        await client.connect()
        logger.info("Cliente Telethon conectado para finalizar autenticação.")
        callbacks.emit("Conectado. Validando o código informado...")

        try:
            if callbacks.cancelled:
                raise AuthenticationCancelledError("Fluxo cancelado pelo usuário.")

            try:
                await client.sign_in(
                    phone=phone,
                    code=code,
                    phone_code_hash=phone_code_hash,
                )
            except PhoneCodeInvalidError as exc:
                raise AuthenticationError("O código informado é inválido.") from exc
            except PhoneCodeExpiredError as exc:
                raise AuthenticationError("O código informado expirou. Solicite um novo.") from exc
            except SessionPasswordNeededError:
                if not password:
                    raise AuthenticationError(
                        "A conta possui senha em duas etapas. Informe a senha para concluir."
                    )
                callbacks.emit("Conta com 2FA. Validando senha adicional...")
                await client.sign_in(password=password)

            me = await client.get_me()
            if me is None:
                raise AuthenticationError("Não foi possível obter os dados da conta autenticada.")

            session_string = client.session.save()
            if display_name:
                nome_exibicao = display_name
            else:
                partes_nome = [me.first_name or "", me.last_name or ""]
                nome_exibicao = " ".join(parte for parte in partes_nome if parte).strip()
                if not nome_exibicao:
                    nome_exibicao = me.username or str(me.id)

            phone_number = me.phone or phone

            info = self._session_manager.register_session(
                phone=phone_number,
                display_name=nome_exibicao,
                session_string=session_string,
            )
            callbacks.emit("Conta autenticada com sucesso.")
            logger.info("Conta %s autenticada via código.", phone_number)
            return info
        finally:
            callbacks.emit("Finalizando conexão...")
            await client.disconnect()
            callbacks.emit("Conexão encerrada.")
            logger.info("Cliente Telethon desconectado após autenticação.")
