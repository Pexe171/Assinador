"""Janela principal com dashboard e configurações."""

from PySide6.QtWidgets import QMainWindow

from .dashboard import Dashboard
from .config import ConfigDialog


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Assinador")
        self.dashboard = Dashboard()
        self.setCentralWidget(self.dashboard)

        config_action = self.menuBar().addAction("Configurações")
        config_action.triggered.connect(self.abrir_config)

    def abrir_config(self) -> None:
        """Abre a janela de configurações."""
        dialog = ConfigDialog(self)
        dialog.exec()
