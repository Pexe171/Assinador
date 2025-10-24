# Caminho: TelegramManager/ui/main_window.py
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

from TelegramManager.core.container import Container
from TelegramManager.notifications.dispatcher import NotificationDispatcher
from TelegramManager.ui.widgets import (
    AccountsManagerWidget,
    AdditionManagerWidget,
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
        # Aplicando um estilo mais moderno à navegação
        self._navegacao.setStyleSheet("""
            QListWidget {
                background-color: #f0f2f5;
                border-right: 1px solid #dcdcdc;
                padding-top: 10px;
                outline: 0px;
            }
            QListWidget::item {
                padding: 12px 20px;
                border-radius: 6px;
                margin: 2px 10px;
            }
            QListWidget::item:hover {
                background-color: #e6e9ed;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
            }
        """)

        self._conteudo = QStackedWidget()

        layout.addWidget(self._navegacao)
        layout.addWidget(self._conteudo, stretch=1)

        self.setCentralWidget(raiz)

        self._inicializar_views()
        self._configurar_conexoes()
        self._navegacao.setCurrentRow(0)

    def _configurar_status_bar(self) -> None:
        barra = QStatusBar()
        barra.showMessage("Bem-vindo! Selecione uma área para começar.")
        self.setStatusBar(barra)

    def _inicializar_views(self) -> None:
        self._dashboard = DashboardWidget(container=self._container)
        self._automation = GroupAutomationWidget(
            automation_engine=self._container.automation_engine
        )
        self._accounts = AccountsManagerWidget(
            container=self._container,
            notifications=self._notifications,
        )
        self._groups = GroupManagerWidget(
            extraction_service=self._container.extraction_service,
            notifications=self._notifications,
        )
        self._user_bank = UserBankWidget(
            extraction_service=self._container.extraction_service,
        )
        # --- Nova Tela de Adição ---
        self._addition = AdditionManagerWidget(
            container=self._container,
            notifications=self._notifications,
        )
        # --- Fim Nova Tela ---
        self._reports = ReportsWidget(report_service=self._container.report_service)
        self._settings = SettingsWidget()

        self._nav_items = [
            ("📊 Dashboard", "dashboard", self._dashboard),
            ("👥 Contas Telegram", "accounts", self._accounts),
            ("🗂️ Gerenciar Grupos (Extração)", "groups", self._groups),
            ("👤 Banco de Usuários", "user_bank", self._user_bank),
            ("➕ Adicionar Usuários (Novo)", "addition", self._addition),
            ("⚡ Automação (Agendador)", "automation", self._automation),
            ("📈 Relatórios", "reports", self._reports),
            ("⚙️ Configurações", "settings", self._settings),
        ]

        for indice, (titulo, chave, widget) in enumerate(self._nav_items):
            item = QListWidgetItem(titulo)
            item.setData(Qt.ItemDataRole.UserRole, chave)
            self._navegacao.addItem(item)
            self._conteudo.addWidget(widget)
            self._views[chave] = widget

    def _configurar_conexoes(self) -> None:
        """Centraliza as conexões (sinais/slots) entre os widgets."""

        # Quando uma conta nova é adicionada, atualiza o dashboard
        self._accounts.account_changed.connect(self._dashboard.atualizar_metricas)

        # Quando uma extração termina, atualiza o banco e o dashboard
        self._groups.extraction_finished.connect(self._user_bank.recarregar)
        self._groups.extraction_finished.connect(self._dashboard.atualizar_metricas)
        self._groups.extraction_finished.connect(self._reports.atualizar_relatorios)

        # Quando uma automação é agendada, atualiza o dashboard
        self._automation.tasks_changed.connect(self._dashboard.atualizar_agendamentos)

        # Quando um job de adição muda, atualiza o dashboard e relatórios
        self._addition.job_changed.connect(self._dashboard.atualizar_metricas_adicao)
        self._addition.job_changed.connect(self._reports.atualizar_relatorios)

        # Inicia o carregamento inicial
        self._dashboard.atualizar_metricas()
        self._dashboard.atualizar_agendamentos(self._automation.obter_tarefas())
        self._dashboard.atualizar_metricas_adicao()

    def _alterar_secao(self, indice: int) -> None:
        if indice < 0 or indice >= len(self._nav_items):
            return
        self._conteudo.setCurrentIndex(indice)
        titulo, chave, _ = self._nav_items[indice]
        self.statusBar().showMessage(f"Visualizando {titulo}.")

        # Recarrega dados ao visitar certas telas
        if chave == "dashboard":
            self._dashboard.atualizar_metricas()
            self._dashboard.atualizar_metricas_adicao()
            self._dashboard.atualizar_agendamentos(self._automation.obter_tarefas())
        elif chave == "automation":
            self._dashboard.atualizar_agendamentos(self._automation.obter_tarefas())
        elif chave == "user_bank":
            self._user_bank.recarregar()
        elif chave == "reports":
            self._reports.atualizar_relatorios()
        elif chave == "addition":
            # Recarrega os dados da tela de adição (contas e usuários)
            self._addition._carregar_dados_iniciais()

