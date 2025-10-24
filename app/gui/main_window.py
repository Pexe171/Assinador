"""Definição da janela principal usando PyQt6."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.container import Container
from app.core.session_manager import SessionInfo
from app.notifications.dispatcher import NotificationDispatcher
from app.gui.widgets.dashboard import DashboardWidget
from app.gui.widgets.log_console import LogConsoleWidget
from app.gui.widgets.session_form import SessionFormWidget


@dataclass
class AccountItem:
    phone: str
    display_name: str
    status: str


class MainWindow(QMainWindow):
    """Janela principal com abas e painel lateral de contas."""

    def __init__(self, container: Container, notifications: NotificationDispatcher) -> None:
        super().__init__()
        self._container = container
        self._notifications = notifications

        self.setWindowTitle(container.config.app_name)
        self.resize(1200, 720)

        self._accounts: Dict[str, AccountItem] = {}

        self._criar_componentes()
        self._popular_sessoes()

    def _criar_componentes(self) -> None:
        raiz = QWidget()
        layout = QHBoxLayout(raiz)
        layout.setContentsMargins(0, 0, 0, 0)

        self._lista_contas = QListWidget()
        self._lista_contas.setMaximumWidth(280)
        self._lista_contas.itemClicked.connect(self._selecionar_conta)

        painel_central = QTabWidget()
        painel_central.addTab(DashboardWidget(container=self._container), "Dashboard")
        painel_central.addTab(SessionFormWidget(container=self._container, on_create=self._adicionar_sessao), "Contas")
        painel_central.addTab(LogConsoleWidget(), "Logs")

        self._detalhes_stack = QStackedWidget()
        self._detalhes_stack.addWidget(self._criar_placeholder("Selecione uma conta"))

        layout.addWidget(self._lista_contas)
        layout.addWidget(painel_central, stretch=3)
        layout.addWidget(self._detalhes_stack, stretch=2)

        self.setCentralWidget(raiz)
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

    def _criar_placeholder(self, texto: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addStretch()
        label = QLabel(texto)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
        return widget

    def _popular_sessoes(self) -> None:
        self._container.session_manager.load_persisted_sessions()
        for info in self._container.session_manager.sessions.values():
            self._adicionar_item_lista(info)

    def _adicionar_item_lista(self, info: SessionInfo) -> None:
        item = QListWidgetItem(f"{info.display_name} ({info.status})")
        item.setData(Qt.ItemDataRole.UserRole, info.phone)
        self._lista_contas.addItem(item)
        self._accounts[info.phone] = AccountItem(
            phone=info.phone,
            display_name=info.display_name,
            status=info.status,
        )

    def _selecionar_conta(self, item: QListWidgetItem) -> None:
        phone = item.data(Qt.ItemDataRole.UserRole)
        dados = self._accounts.get(phone)
        if not dados:
            QMessageBox.warning(self, "Conta não encontrada", "Os dados da conta não foram carregados.")
            return
        self.statusBar().showMessage(f"Conta selecionada: {dados.display_name}")

    def _adicionar_sessao(self, session: SessionInfo) -> None:
        self._adicionar_item_lista(session)
        self._notifications.notify(
            titulo="Conta conectada",
            mensagem=f"A conta {session.display_name} foi autenticada com sucesso.",
        )
