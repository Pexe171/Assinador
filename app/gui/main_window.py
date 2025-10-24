"""Definição da janela principal usando PyQt6."""

from __future__ import annotations

from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QStatusBar,
    QWidget,
)

from app.core.container import Container
from app.notifications.dispatcher import NotificationDispatcher
from app.gui.widgets import (
    AccountsManagerWidget,
    DashboardWidget,
    GroupAutomationWidget,
    GroupManagerWidget,
    ReportsWidget,
    SettingsWidget,
    UserBankWidget,
)


class MainWindow(QMainWindow):
    """Janela principal com navegação lateral e conteúdo dinâmico."""

    def __init__(self, container: Container, notifications: NotificationDispatcher) -> None:
        super().__init__()
        self._container = container
        self._notifications = notifications

        self.setWindowTitle(container.config.app_name)
        self.resize(1280, 760)

        self._views: Dict[str, QWidget] = {}

        self._montar_interface()
        self._configurar_status_bar()

    def _montar_interface(self) -> None:
        raiz = QWidget()
        layout = QHBoxLayout(raiz)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._navegacao = QListWidget()
        self._navegacao.setFixedWidth(240)
        self._navegacao.setSpacing(4)
        self._navegacao.currentRowChanged.connect(self._alterar_secao)

        self._conteudo = QStackedWidget()

        layout.addWidget(self._navegacao)
        layout.addWidget(self._conteudo, stretch=1)

        self.setCentralWidget(raiz)

        self._inicializar_views()
        self._navegacao.setCurrentRow(0)

    def _configurar_status_bar(self) -> None:
        barra = QStatusBar()
        barra.showMessage("Bem-vindo! Selecione uma área para começar.")
        self.setStatusBar(barra)

    def _inicializar_views(self) -> None:
        self._dashboard = DashboardWidget(container=self._container)
        self._automation = GroupAutomationWidget()
        self._automation.tasks_changed.connect(self._sincronizar_agendamentos)

        self._accounts = AccountsManagerWidget(
            container=self._container,
            notifications=self._notifications,
            on_change=self._dashboard.atualizar_metricas,
        )

        self._groups = GroupManagerWidget()
        self._user_bank = UserBankWidget()
        self._reports = ReportsWidget()
        self._settings = SettingsWidget()

        self._dashboard.atualizar_metricas()
        self._sincronizar_agendamentos()

        self._nav_items = [
            ("📊 Dashboard", "dashboard", self._dashboard),
            ("👥 Contas Telegram", "accounts", self._accounts),
            ("🗂️ Gerenciar Grupos", "groups", self._groups),
            ("👤 Banco de Usuários", "user_bank", self._user_bank),
            ("⚡ Automação", "automation", self._automation),
            ("📈 Relatórios", "reports", self._reports),
            ("⚙️ Configurações", "settings", self._settings),
        ]

        for indice, (titulo, chave, widget) in enumerate(self._nav_items):
            item = QListWidgetItem(titulo)
            item.setData(Qt.ItemDataRole.UserRole, chave)
            self._navegacao.addItem(item)
            self._conteudo.addWidget(widget)
            self._views[chave] = widget

    def _alterar_secao(self, indice: int) -> None:
        if indice < 0 or indice >= len(self._nav_items):
            return
        self._conteudo.setCurrentIndex(indice)
        titulo, chave, _ = self._nav_items[indice]
        self.statusBar().showMessage(f"Visualizando {titulo}.")
        if chave == "automation":
            self._sincronizar_agendamentos()
        elif chave == "dashboard":
            self._dashboard.atualizar_metricas()

    def _sincronizar_agendamentos(self) -> None:
        self._dashboard.atualizar_agendamentos(self._automation.obter_tarefas())
