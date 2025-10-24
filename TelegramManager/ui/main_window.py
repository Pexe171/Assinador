# Caminho: TelegramManager/ui/main_window.py
"""Definição da janela principal usando PyQt6."""

from __future__ import annotations

import logging # Adicionado para logging
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

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Janela principal com navegação lateral e conteúdo dinâmico."""

    def __init__(self, container: Container, notifications: NotificationDispatcher) -> None:
        super().__init__()
        self._container = container
        self._notifications = notifications

        self.setWindowTitle(container.config.app_name)
        self.resize(1366, 800) # Aumentado tamanho padrão
        self.setStyleSheet("QMainWindow { background-color: #f8f9fb; }") # Fundo geral

        self._views: Dict[str, QWidget] = {}

        self._montar_interface()
        self._configurar_status_bar()
        # Conexões movidas para _configurar_conexoes para organização
        self._configurar_conexoes() # Chamada após inicializar views

        # Carregamento inicial após tudo montado
        self._carregar_dados_iniciais()

        # Seleciona o Dashboard ao iniciar
        if self._navegacao.count() > 0:
            self._navegacao.setCurrentRow(0)
        else:
             logger.warning("Nenhum item de navegação encontrado.")

    def _montar_interface(self) -> None:
        """Monta a estrutura visual da janela (Navegação + Conteúdo)."""
        raiz = QWidget()
        layout = QHBoxLayout(raiz)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) # Remove espaço entre navegação e conteúdo

        # --- Barra de Navegação Lateral ---
        self._navegacao = QListWidget()
        self._navegacao.setObjectName("sidebarNavigation") # ID para estilo
        self._navegacao.setFixedWidth(250) # Ligeiramente mais larga
        self._navegacao.setSpacing(5) # Espaço entre itens
        self._navegacao.currentRowChanged.connect(self._alterar_secao)
        # Aplica estilo moderno (será definido em _aplicar_estilos)
        self._aplicar_estilos_navegacao()

        # --- Área de Conteúdo Principal ---
        self._conteudo = QStackedWidget()
        self._conteudo.setObjectName("mainContentArea") # ID para estilo
        self._conteudo.setStyleSheet("#mainContentArea { background-color: #ffffff; }") # Fundo branco

        layout.addWidget(self._navegacao)
        layout.addWidget(self._conteudo, stretch=1) # Conteúdo ocupa o resto

        self.setCentralWidget(raiz)

        # Inicializa as diferentes "telas" (widgets)
        self._inicializar_views()

    def _aplicar_estilos_navegacao(self) -> None:
         """Aplica CSS-like styles à barra de navegação."""
         self._navegacao.setStyleSheet("""
            QListWidget#sidebarNavigation {
                background-color: #ffffff; /* Fundo branco */
                border-right: 1px solid #e2e8f0; /* Borda direita suave */
                padding-top: 15px; /* Espaço no topo */
                outline: 0px; /* Remove foco visual padrão */
            }
            QListWidget#sidebarNavigation::item {
                padding: 14px 25px; /* Mais padding interno */
                border-radius: 8px; /* Cantos arredondados */
                margin: 4px 15px; /* Espaço vertical e horizontal */
                color: #4a5568; /* Cor do texto padrão */
                font-size: 14px; /* Tamanho da fonte */
                font-weight: 500; /* Peso médio */
            }
            QListWidget#sidebarNavigation::item:hover {
                background-color: #f0f4f8; /* Fundo suave ao passar o mouse */
                color: #2d3748; /* Texto escuro no hover */
            }
            QListWidget#sidebarNavigation::item:selected {
                background-color: #4299e1; /* Azul vibrante para seleção */
                color: white; /* Texto branco */
                font-weight: 600; /* Negrito */
            }
            /* Remove a borda pontilhada ao focar um item */
            QListWidget#sidebarNavigation:focus {
                outline: none;
            }
             QListWidget#sidebarNavigation::item:focus {
                outline: none;
                border: none; /* Garante que não haja borda de foco */
            }

        """)


    def _configurar_status_bar(self) -> None:
        """Configura a barra de status inferior."""
        barra = QStatusBar()
        barra.setStyleSheet("""
            QStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e2e8f0;
                color: #718096; /* Cinza médio */
                font-size: 12px;
                padding-left: 10px;
            }
        """)
        barra.showMessage("Pronto.")
        self.setStatusBar(barra)

    def _inicializar_views(self) -> None:
        """Cria as instâncias dos widgets de cada seção."""
        logger.debug("Inicializando widgets das views...")
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
        self._addition = AdditionManagerWidget(
            container=self._container,
            notifications=self._notifications,
        )
        self._reports = ReportsWidget(report_service=self._container.report_service)
        self._settings = SettingsWidget()

        # Mapeamento Título -> Chave -> Instância do Widget
        # Usar ícones (placeholders) melhora a identificação
        self._nav_items = [
            ("📊 Dashboard", "dashboard", self._dashboard),
            ("👥 Contas Telegram", "accounts", self._accounts),
            ("🔍 Gerenciar Grupos (Extração)", "groups", self._groups),
            ("뱅 Banco de Usuários", "user_bank", self._user_bank), # Emoji Banco
            ("➕ Adicionar Usuários", "addition", self._addition),
            ("⚙️ Automação (Agendador)", "automation", self._automation), # Emoji engrenagem
            ("📈 Relatórios", "reports", self._reports),
            ("🔧 Configurações", "settings", self._settings), # Emoji chave inglesa
        ]

        # Adiciona itens à navegação e widgets ao StackedWidget
        for titulo, chave, widget in self._nav_items:
            item = QListWidgetItem(titulo)
            # Adiciona um tooltip para acessibilidade ou nomes longos
            item.setToolTip(f"Acessar a seção {titulo.split('(')[0].strip()}")
            item.setData(Qt.ItemDataRole.UserRole, chave) # Armazena a chave para referência
            self._navegacao.addItem(item)
            self._conteudo.addWidget(widget)
            self._views[chave] = widget
        logger.debug("Widgets das views inicializados e adicionados.")


    def _configurar_conexoes(self) -> None:
        """Centraliza as conexões (sinais/slots) entre os widgets."""
        logger.debug("Configurando conexões (sinais e slots)...")

        # Verifica se os widgets existem antes de conectar para evitar erros
        if hasattr(self, '_accounts') and hasattr(self, '_dashboard'):
            self._accounts.account_changed.connect(self._dashboard.atualizar_metricas)
            logger.debug("Conectado: _accounts.account_changed -> _dashboard.atualizar_metricas")

        if hasattr(self, '_groups') and hasattr(self, '_user_bank') and hasattr(self, '_dashboard') and hasattr(self, '_reports'):
            self._groups.extraction_finished.connect(self._user_bank.recarregar)
            self._groups.extraction_finished.connect(self._dashboard.atualizar_metricas)
            self._groups.extraction_finished.connect(self._reports.atualizar_relatorios)
            logger.debug("Conectado: _groups.extraction_finished -> _user_bank.recarregar, _dashboard.atualizar_metricas, _reports.atualizar_relatorios")

        if hasattr(self, '_automation') and hasattr(self, '_dashboard'):
            self._automation.tasks_changed.connect(self._dashboard.atualizar_agendamentos)
            logger.debug("Conectado: _automation.tasks_changed -> _dashboard.atualizar_agendamentos")

        if hasattr(self, '_addition') and hasattr(self, '_dashboard') and hasattr(self, '_reports'):
            self._addition.job_changed.connect(self._dashboard.atualizar_metricas_adicao)
            self._addition.job_changed.connect(self._reports.atualizar_relatorios)
            logger.debug("Conectado: _addition.job_changed -> _dashboard.atualizar_metricas_adicao, _reports.atualizar_relatorios")

    def _carregar_dados_iniciais(self) -> None:
        """Força a primeira atualização dos dados no Dashboard."""
        logger.debug("Carregando dados iniciais do Dashboard...")
        if hasattr(self, '_dashboard'):
            try:
                self._dashboard.atualizar_metricas()
                self._dashboard.atualizar_metricas_adicao()
                # Garante que automation_engine existe antes de chamar listar()
                if hasattr(self._container, 'automation_engine'):
                    self._dashboard.atualizar_agendamentos(self._container.automation_engine.listar())
                else:
                    logger.warning("AutomationEngine não encontrado no container.")
            except Exception as e:
                logger.exception("Erro durante o carregamento inicial de dados do Dashboard")
                self.statusBar().showMessage(f"Erro ao carregar dados: {e}")
        else:
            logger.error("Dashboard não foi inicializado corretamente.")


    def _alterar_secao(self, indice_atual: int) -> None:
        """Chamado quando o item selecionado na navegação muda."""
        if not (0 <= indice_atual < len(self._nav_items)):
            logger.warning("Índice de navegação inválido: %d", indice_atual)
            return

        titulo, chave, _ = self._nav_items[indice_atual]
        logger.info("Navegando para a seção: %s (chave: %s)", titulo, chave)
        self._conteudo.setCurrentIndex(indice_atual)
        self.statusBar().showMessage(f"Visualizando: {titulo.split('(')[0].strip()}")

        # Lógica para recarregar dados específicos ao entrar na seção
        try:
            if chave == "dashboard":
                 self._carregar_dados_iniciais() # Força recarga completa do dashboard
            elif chave == "user_bank" and hasattr(self, '_user_bank'):
                self._user_bank.recarregar()
            elif chave == "reports" and hasattr(self, '_reports'):
                self._reports.atualizar_relatorios()
            elif chave == "addition" and hasattr(self, '_addition'):
                # Recarrega contas e usuários na tela de adição
                self._addition._carregar_dados_iniciais()
            # Adicionar outras recargas se necessário
        except Exception as e:
            logger.exception("Erro ao recarregar dados da seção %s", chave)
            self.statusBar().showMessage(f"Erro ao carregar seção {chave}: {e}")

