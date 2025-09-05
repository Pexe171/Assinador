"""Ícone de bandeja e status do túnel."""

from PySide6.QtWidgets import QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    """Gerencia o ícone de bandeja da aplicação."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
