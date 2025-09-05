"""Ícone de bandeja e status do túnel."""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QMenu


class TrayIcon(QSystemTrayIcon):
    """Gerencia o ícone de bandeja da aplicação."""

    def __init__(self, url: str | None = None, parent=None) -> None:
        super().__init__(QIcon(), parent)
        menu = QMenu()
        self.setContextMenu(menu)
        self.update_url(url)

    def update_url(self, url: str | None) -> None:
        """Atualiza o tooltip exibindo a URL pública do túnel."""
        texto = url or "Túnel não disponível"
        self.setToolTip(texto)
