"""Janela principal com navegação lateral."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QStackedWidget,
)

from app.core.theming import apply_theme, load_theme
from .dashboard import Dashboard
from .config import ConfigDialog
from .accounts_dashboard import AccountsDashboard


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Assinador")
        self._theme_name = "dark"

        # Navegação lateral
        container = QWidget()
        layout = QHBoxLayout(container)

        self.menu = QListWidget()
        self.menu.addItems(["Contas WhatsApp", "Clientes"])
        layout.addWidget(self.menu)

        self.stack = QStackedWidget()
        self.accounts_view = AccountsDashboard()
        self.clients_view = Dashboard()
        self.stack.addWidget(self.accounts_view)
        self.stack.addWidget(self.clients_view)
        layout.addWidget(self.stack)
        self.setCentralWidget(container)

        self.menu.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.menu.setCurrentRow(0)

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
