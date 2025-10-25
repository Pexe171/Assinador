"""Sistema de notificações integrado ao SO."""

from __future__ import annotations

from dataclasses import dataclass

from TelegramManager.utils.config import AppConfig

try:
    from plyer import notification
except ImportError:  # pragma: no cover - fallback amigável
    notification = None


@dataclass
class NotificationMessage:
    titulo: str
    mensagem: str


class NotificationDispatcher:
    """Envia notificações usando a biblioteca nativa quando disponível."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def notify(self, titulo: str, mensagem: str) -> None:
        titulo = self._limitar_texto(titulo)
        mensagem = self._limitar_texto(mensagem)
        dados = NotificationMessage(titulo=titulo, mensagem=mensagem)
        if notification is None:
            print(f"[NOTIFICAÇÃO] {dados.titulo}: {dados.mensagem}")
            return

        notification.notify(
            title=dados.titulo,
            message=dados.mensagem,
            app_name=self._config.app_name,
        )

    @staticmethod
    def _limitar_texto(texto: str, limite: int = 250) -> str:
        """Evita exceder o limite de caracteres das notificações nativas."""

        if len(texto) <= limite:
            return texto
        return f"{texto[: limite - 1]}…"
