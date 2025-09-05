"""Ícone de bandeja com ações rápidas e status do túnel."""

# Autor: Pexe – Instagram: @David.devloli

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication


class TrayIcon(QSystemTrayIcon):
    """Gerencia o ícone de bandeja da aplicação."""

    instance: "TrayIcon | None" = None

    def __init__(self, url: str | None = None, parent=None) -> None:
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "tray_icon.png"
        super().__init__(QIcon(str(icon_path)), parent)
        TrayIcon.instance = self

        self.url: str | None = url
        menu = QMenu()
        self.action_copy = menu.addAction("Copiar URL")
        self.action_copy.triggered.connect(self.copy_url)
        menu.addSeparator()
        self.icon_ok = self._status_icon("#28a745")
        self.icon_error = self._status_icon("#dc3545")
        self.webhook_status = menu.addAction("Webhooks: desconhecido")
        self.setContextMenu(menu)
        self.update_url(url)

    def update_url(self, url: str | None) -> None:
        """Atualiza o tooltip exibindo a URL pública do túnel."""
        self.url = url
        texto = url or "Túnel não disponível"
        self.setToolTip(texto)
        self.action_copy.setEnabled(bool(url))

    def copy_url(self) -> None:
        """Copia a URL pública do túnel para a área de transferência."""
        if not self.url:
            return
        QApplication.clipboard().setText(self.url)

    def update_webhooks_status(self, ok: bool) -> None:
        """Exibe no menu o status dos webhooks."""
        texto = "Webhooks OK" if ok else "Webhooks com erro"
        icon = self.icon_ok if ok else self.icon_error
        self.webhook_status.setIcon(icon)
        self.webhook_status.setText(texto)

    def notify(self, message: str, title: str = "Assinador") -> None:
        """Exibe uma notificação nativa do sistema."""
        self.showMessage(title, message, self.icon())

    @classmethod
    def notify_global(cls, message: str, title: str = "Assinador") -> None:
        """Atalho para exibir notificação usando a instância ativa."""
        if cls.instance is not None:
            cls.instance.notify(message, title)

    @staticmethod
    def _status_icon(color: str) -> QIcon:
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 16, 16)
        painter.end()
        return QIcon(pixmap)
