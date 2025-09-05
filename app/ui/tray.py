"""Ícone de bandeja com ações rápidas e status do túnel."""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication


class TrayIcon(QSystemTrayIcon):
    """Gerencia o ícone de bandeja da aplicação."""

    def __init__(self, url: str | None = None, parent=None) -> None:
        super().__init__(QIcon(), parent)
        self.url: str | None = url
        menu = QMenu()
        self.action_copy = menu.addAction("Copiar URL")
        self.action_copy.triggered.connect(self.copy_url)
        menu.addSeparator()
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
        self.webhook_status.setText(texto)
