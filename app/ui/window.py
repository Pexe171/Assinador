"""Janela principal com dashboard e configurações."""

from PySide6.QtWidgets import QMainWindow

from app.core.theming import apply_theme, load_theme
from .dashboard import Dashboard
from .config import ConfigDialog


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Assinador")
        self.dashboard = Dashboard()
        self.setCentralWidget(self.dashboard)
        self._theme_name = "dark"
        self.set_theme(self._theme_name)

        config_action = self.menuBar().addAction("Configurações")
        config_action.triggered.connect(self.abrir_config)

    def abrir_config(self) -> None:
        """Abre a janela de configurações."""
        dialog = ConfigDialog(self, self._theme_name)
        dialog.exec()

    def set_theme(self, name: str) -> None:
        """Aplica um tema pelo nome."""
        theme = load_theme(name)
        apply_theme(self, theme)
        self._theme_name = name
