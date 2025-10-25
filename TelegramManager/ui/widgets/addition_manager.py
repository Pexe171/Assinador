# Caminho: TelegramManager/ui/widgets/addition_manager.py
"""Widget da "Função de Adição".

Implementa o wizard de 3 passos (Seleção, Configuração, Monitoramento)
para adicionar usuários do banco local a grupos de destino.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List

# Correcção: Importar pyqtSlot
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, pyqtSlot
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.addition_manager import (
    AdditionJobConfig,
    AdditionManager,
    AdditionJobMonitor,
)
from TelegramManager.core.automation import TaskStatus
from TelegramManager.core.container import Container
from TelegramManager.core.extraction import ExtractedUserRecord, SyncedGroup
from TelegramManager.notifications.dispatcher import NotificationDispatcher

if TYPE_CHECKING:
    from TelegramManager.core.session_manager import SessionInfo

logger = logging.getLogger(__name__)


class AdditionManagerWidget(QWidget):
    """Wizard de 3 passos para adição de usuários."""

    # Sinal emitido quando um job de adição é criado ou atualizado
    job_changed = pyqtSignal()

    def __init__(
        self,
        container: Container,
        notifications: NotificationDispatcher,
    ) -> None:
        super().__init__()
        self._container = container
        self._notifications = notifications
        self._addition_manager = container.addition_manager
        self._extraction_service = container.extraction_service

        self._all_users: List[ExtractedUserRecord] = []
        self._selected_users: List[ExtractedUserRecord] = []
        self._grupos_disponiveis: List[SyncedGroup] = []

        self._current_job_monitor: AdditionJobMonitor | None = None
        self._monitor_timer = QTimer(self)
        self._monitor_timer.setInterval(1000)
        self._monitor_timer.timeout.connect(self._update_monitor_ui)

        self._montar_layout()
        self._carregar_dados_iniciais()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        titulo = QLabel("Adicionar Usuários a Grupos")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        self._wizard = QStackedWidget()
        self._wizard.addWidget(self._criar_passo_1_selecao())
        self._wizard.addWidget(self._criar_passo_2_configuracao())
        self._wizard.addWidget(self._criar_passo_3_monitoramento())

        layout.addWidget(self._wizard)
        self.setLayout(layout)

    def _carregar_dados_iniciais(self) -> None:
        """Carrega dados necessários para os formulários."""
        logger.debug("Carregando dados iniciais para AdditionManagerWidget")
        # Carrega contas ativas
        sessions = self._container.session_manager.sessions
        self._combo_contas.clear()
        if not sessions:
            self._combo_contas.addItem("Nenhuma conta conectada", None)
            self._combo_contas.setEnabled(False)
        else:
            self._combo_contas.setEnabled(True) # Garante que está ativo se houver contas
            for session in sessions.values():
                self._combo_contas.addItem(
                    f"{session.display_name} ({session.phone})", session
                )
        logger.debug("%d contas carregadas no ComboBox", self._combo_contas.count())

        self._atualizar_grupos_disponiveis()

        # Carrega usuários do banco
        try:
            self._all_users = self._extraction_service.list_recent_users(limite=5000)
            self._popular_tabela_usuarios(self._all_users)
            logger.debug("%d usuários carregados do banco", len(self._all_users))
        except Exception as e:
            logger.exception("Erro ao carregar usuários do banco para AdditionManager")
            self._notifications.notify("Erro", f"Não foi possível carregar usuários: {e}")


    def _atualizar_grupos_disponiveis(self) -> None:
        """Atualiza a lista de grupos sincronizados para a conta selecionada."""

        session: SessionInfo | None = self._combo_contas.currentData()
        phone = session.phone if session else None

        try:
            self._grupos_disponiveis = self._extraction_service.list_synced_groups(
                account_phone=phone
            )
        except Exception as exc:
            logger.exception("Erro ao listar grupos sincronizados")
            self._combo_grupo_destino.blockSignals(True)
            self._combo_grupo_destino.clear()
            self._combo_grupo_destino.addItem(
                "Não foi possível carregar os grupos", None
            )
            self._combo_grupo_destino.setEnabled(False)
            self._combo_grupo_destino.blockSignals(False)
            self._notifications.notify(
                "Erro",
                "Não foi possível carregar os grupos sincronizados: %s" % exc,
            )
            return

        self._combo_grupo_destino.blockSignals(True)
        self._combo_grupo_destino.clear()

        if not self._grupos_disponiveis:
            self._combo_grupo_destino.addItem(
                "Nenhum grupo sincronizado disponível", None
            )
            self._combo_grupo_destino.setEnabled(False)
        else:
            self._combo_grupo_destino.addItem("Selecione um grupo", None)
            for grupo in self._grupos_disponiveis:
                conta_label = grupo.account_display_name or "Conta não informada"
                membros_txt = (
                    f"{grupo.total_members} usuários"
                    if grupo.total_members
                    else "Sem usuários no banco"
                )
                if session is None:
                    texto = f"{grupo.name} • {conta_label} ({membros_txt})"
                else:
                    texto = f"{grupo.name} ({membros_txt})"
                self._combo_grupo_destino.addItem(texto, grupo.name)
            self._combo_grupo_destino.setEnabled(True)

        self._combo_grupo_destino.blockSignals(False)
        self._atualizar_contador_selecao()


    def _filtrar_usuarios(self) -> None:
        """Filtra a tabela de usuários com base nos filtros da UI."""
        termo = self._filtro_nome.text().lower().strip()
        grupo_origem = self._filtro_grupo_origem.text().lower().strip()

        filtrados = [
            user
            for user in self._all_users
            if (not termo or termo in user.username.lower())
            and (not grupo_origem or grupo_origem in user.origin_group.lower())
        ]
        self._popular_tabela_usuarios(filtrados)

    def _popular_tabela_usuarios(self, usuarios: List[ExtractedUserRecord]) -> None:
        """Preenche a QTableWidget com os usuários."""
        self._tabela_usuarios.setRowCount(0)  # Limpa antes de adicionar
        self._tabela_usuarios.setRowCount(len(usuarios))
        for row, user in enumerate(usuarios):
            # Checkbox na Coluna 0
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_item.setCheckState(Qt.CheckState.Unchecked)
            check_item.setData(Qt.ItemDataRole.UserRole, user)  # Armazena o objeto ExtractedUser
            self._tabela_usuarios.setItem(row, 0, check_item)

            # Dados
            self._tabela_usuarios.setItem(row, 1, QTableWidgetItem(user.username))
            self._tabela_usuarios.setItem(row, 2, QTableWidgetItem(user.origin_group))
            self._tabela_usuarios.setItem(row, 3, QTableWidgetItem(user.status))

        self._atualizar_contador_selecao()

    def _atualizar_contador_selecao(self) -> None:
        """Conta quantos usuários estão marcados na tabela."""
        count = 0
        for i in range(self._tabela_usuarios.rowCount()):
            if self._tabela_usuarios.item(i, 0).checkState() == Qt.CheckState.Checked:
                count += 1
        self._label_contador.setText(f"{count} usuários selecionados")
        grupo_selecionado = bool(self._combo_grupo_destino.currentData())
        self._botao_ir_passo_2.setEnabled(count > 0 and grupo_selecionado)

    def _selecionar_todos(self, state: int) -> None:
        """Marca ou desmarca todos os checkboxes visíveis."""
        check_state = Qt.CheckState(state)
        for i in range(self._tabela_usuarios.rowCount()):
            self._tabela_usuarios.item(i, 0).setCheckState(check_state)
        self._atualizar_contador_selecao()

    # --- PASSO 1: SELEÇÃO ---

    def _criar_passo_1_selecao(self) -> QWidget:
        """Cria a UI para o Passo 1: Seleção de Conta, Grupo e Usuários."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # 1. Seleção de Destino (Conta e Grupo)
        grupo_destino = QGroupBox("1. Seleção de Destino")
        form_destino = QFormLayout(grupo_destino)
        form_destino.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._combo_contas = QComboBox()
        self._combo_contas.currentIndexChanged.connect(
            lambda *_: self._atualizar_grupos_disponiveis()
        )
        form_destino.addRow("Usar a conta:", self._combo_contas)

        self._combo_grupo_destino = QComboBox()
        self._combo_grupo_destino.setEnabled(False)
        self._combo_grupo_destino.setPlaceholderText(
            "Sincronize uma conta para listar os grupos disponíveis"
        )
        self._combo_grupo_destino.currentIndexChanged.connect(
            lambda *_: self._atualizar_contador_selecao()
        )
        form_destino.addRow("Grupo de Destino:", self._combo_grupo_destino)
        layout.addWidget(grupo_destino)

        # 2. Seleção de Usuários (Filtros e Tabela)
        grupo_usuarios = QGroupBox("2. Seleção de Usuários (do Banco de Dados)")
        layout_usuarios = QVBoxLayout(grupo_usuarios)

        # Filtros
        filtros_layout = QHBoxLayout()
        self._filtro_nome = QLineEdit()
        self._filtro_nome.setPlaceholderText("Filtrar por nome...")
        self._filtro_nome.textChanged.connect(self._filtrar_usuarios)
        filtros_layout.addWidget(self._filtro_nome)

        self._filtro_grupo_origem = QLineEdit()
        self._filtro_grupo_origem.setPlaceholderText("Filtrar por grupo de origem...")
        self._filtro_grupo_origem.textChanged.connect(self._filtrar_usuarios)
        filtros_layout.addWidget(self._filtro_grupo_origem)
        layout_usuarios.addLayout(filtros_layout)

        # Tabela
        self._tabela_usuarios = QTableWidget(0, 4)
        self._tabela_usuarios.setHorizontalHeaderLabels(
            ["", "Usuário", "Grupo de Origem", "Status"]
        )
        self._tabela_usuarios.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self._tabela_usuarios.verticalHeader().setVisible(False)
        self._tabela_usuarios.horizontalHeader().setStretchLastSection(True)
        self._tabela_usuarios.setColumnWidth(0, 30)  # Checkbox
        # Conectar itemChanged APENAS se precisar reagir a CADA mudança de checkbox
        # self._tabela_usuarios.itemChanged.connect(self._atualizar_contador_selecao)
        # É mais eficiente conectar ao clique, mas pode ser menos preciso se houver outras interações
        self._tabela_usuarios.itemClicked.connect(self._atualizar_contador_selecao) # Atualiza ao clicar
        layout_usuarios.addWidget(self._tabela_usuarios)

        # Rodapé Tabela (Contador e Seleção em Lote)
        rodape_tabela = QHBoxLayout()
        self._check_selecionar_todos = QCheckBox("Selecionar Todos")
        self._check_selecionar_todos.stateChanged.connect(self._selecionar_todos)
        rodape_tabela.addWidget(self._check_selecionar_todos)
        rodape_tabela.addStretch()
        self._label_contador = QLabel("0 usuários selecionados")
        rodape_tabela.addWidget(self._label_contador)
        layout_usuarios.addLayout(rodape_tabela)

        layout.addWidget(grupo_usuarios)

        # 3. Navegação
        botoes_layout = QHBoxLayout()
        botoes_layout.addStretch()
        self._botao_ir_passo_2 = QPushButton("Ir para Configuração ➔")
        self._botao_ir_passo_2.setEnabled(False)
        self._botao_ir_passo_2.clicked.connect(self._validar_e_ir_passo_2)
        botoes_layout.addWidget(self._botao_ir_passo_2)
        layout.addLayout(botoes_layout)

        return widget

    def _validar_e_ir_passo_2(self) -> None:
        """Valida a seleção e coleta os usuários para o próximo passo."""
        logger.debug("Validando e indo para o passo 2...")
        # Valida conta e grupo
        self._current_session: SessionInfo | None = self._combo_contas.currentData()
        grupo_selecionado = self._combo_grupo_destino.currentData()
        self._target_group_str = (grupo_selecionado or "").strip()

        if not self._current_session:
            self._notifications.notify("Erro", "Nenhuma conta do Telegram selecionada.")
            logger.warning("Nenhuma conta selecionada.")
            return
        if not self._target_group_str:
            self._notifications.notify(
                "Erro", "Selecione um grupo sincronizado para continuar."
            )
            logger.warning("Nenhum grupo de destino selecionado.")
            return

        # Coleta usuários selecionados
        self._selected_users = []
        for i in range(self._tabela_usuarios.rowCount()):
            item = self._tabela_usuarios.item(i, 0)
            if item.checkState() == Qt.CheckState.Checked:
                # Recupera o objeto ExtractedUserRecord armazenado
                user_data: ExtractedUserRecord | None = item.data(Qt.ItemDataRole.UserRole)
                if user_data:
                    # Precisamos do ID do usuário no banco de dados, não do objeto Record
                    # Assumindo que ExtractedUserRecord deveria ter um campo ID
                    # Se não tiver, precisamos buscar no banco.
                    # Vamos assumir que list_recent_users agora retorna objetos com ID
                    # Se não, esta parte precisará de ajuste na ExtractionService
                    if hasattr(user_data, 'id'):
                        self._selected_users.append(user_data)
                    else:
                        logger.error("Objeto ExtractedUserRecord não possui ID.")
                        # Tentar buscar pelo username (menos ideal)
                        # usuario_db = self._buscar_usuario_db(user_data.username) # Implementar busca
                        # if usuario_db: self._selected_users_ids.append(usuario_db.id)
                        pass # Ignorar por enquanto se não tiver ID


        if not self._selected_users:
            self._notifications.notify("Erro", "Nenhum usuário foi selecionado.")
            logger.warning("Nenhum usuário selecionado na tabela.")
            return

        logger.info("%d usuários selecionados para adição.", len(self._selected_users))

        # Atualiza a UI do Passo 2 com os dados
        self._label_resumo_conta.setText(
            f"{self._current_session.display_name} ({self._current_session.phone})"
        )
        self._label_resumo_grupo.setText(self._target_group_str)
        self._label_resumo_usuarios.setText(f"{len(self._selected_users)} usuários")

        self._wizard.setCurrentIndex(1)

    # --- PASSO 2: CONFIGURAÇÃO ---

    def _criar_passo_2_configuracao(self) -> QWidget:
        """Cria a UI para o Passo 2: Configuração de Delays e Limites."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # 1. Resumo da Seleção
        grupo_resumo = QGroupBox("Resumo da Operação")
        form_resumo = QFormLayout(grupo_resumo)
        self._label_resumo_conta = QLabel("-")
        self._label_resumo_grupo = QLabel("-")
        self._label_resumo_usuarios = QLabel("-")
        form_resumo.addRow("Conta:", self._label_resumo_conta)
        form_resumo.addRow("Grupo Alvo:", self._label_resumo_grupo)
        form_resumo.addRow("Usuários:", self._label_resumo_usuarios)
        layout.addWidget(grupo_resumo)

        # 2. Configurações de Segurança
        grupo_config = QGroupBox("Configurações de Segurança e Delays")
        form_config = QFormLayout(grupo_config)
        form_config.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Delays
        self._input_delay_min = QSpinBox()
        self._input_delay_min.setRange(5, 300)
        self._input_delay_min.setValue(30)
        self._input_delay_min.setSuffix(" seg")
        form_config.addRow("Delay MÍNIMO entre adições:", self._input_delay_min)

        self._input_delay_max = QSpinBox()
        self._input_delay_max.setRange(10, 600)
        self._input_delay_max.setValue(120)
        self._input_delay_max.setSuffix(" seg")
        form_config.addRow("Delay MÁXIMO entre adições:", self._input_delay_max)

        # Limites
        self._input_max_dia = QSpinBox()
        self._input_max_dia.setRange(10, 500)
        self._input_max_dia.setValue(200)
        form_config.addRow("Limite MÁXIMO por dia:", self._input_max_dia)

        self._input_erros_consec = QSpinBox()
        self._input_erros_consec.setRange(3, 20)
        self._input_erros_consec.setValue(5)
        form_config.addRow("Parar após N erros consecutivos:", self._input_erros_consec)
        layout.addWidget(grupo_config)

        layout.addStretch()

        # 3. Navegação
        botoes_layout = QHBoxLayout()
        self._botao_voltar_passo_1 = QPushButton("❮ Voltar para Seleção")
        self._botao_voltar_passo_1.clicked.connect(lambda: self._wizard.setCurrentIndex(0))
        botoes_layout.addWidget(self._botao_voltar_passo_1)

        botoes_layout.addStretch()
        self._botao_iniciar_operacao = QPushButton("INICIAR OPERAÇÃO 🚀")
        self._botao_iniciar_operacao.setStyleSheet(
            "font-weight: bold; background-color: #28a745; color: white; padding: 8px;"
        )
        self._botao_iniciar_operacao.clicked.connect(self._iniciar_operacao)
        botoes_layout.addWidget(self._botao_iniciar_operacao)
        layout.addLayout(botoes_layout)

        return widget

    def _iniciar_operacao(self) -> None:
        """Cria o Job no AdditionManager e muda para a tela de monitoramento."""
        try:
            if not self._current_session or not self._selected_users:
                self._notifications.notify("Erro", "Sessão ou usuários perdidos. Tente novamente.")
                logger.error("Tentativa de iniciar operação sem sessão ou usuários selecionados.")
                self._wizard.setCurrentIndex(0)
                return

            # Extrai os IDs dos objetos ExtractedUserRecord
            selected_user_ids = []
            for user in self._selected_users:
                 if hasattr(user, 'id'):
                     selected_user_ids.append(user.id)
                 else:
                     logger.warning("Usuário %s sem ID encontrado, será ignorado.", user.username)

            if not selected_user_ids:
                 self._notifications.notify("Erro", "Nenhum usuário válido (com ID) foi encontrado para adição.")
                 logger.error("Nenhum ID de usuário válido coletado.")
                 return

            config = AdditionJobConfig(
                account_phone=self._current_session.phone,
                target_group=self._target_group_str,
                user_ids=selected_user_ids, # Passa a lista de IDs
                delay_min=self._input_delay_min.value(),
                delay_max=self._input_delay_max.value(),
                max_add_per_day=self._input_max_dia.value(),
                stop_on_consecutive_errors=self._input_erros_consec.value(),
            )

            job_db = self._addition_manager.create_job(config)
            logger.info("Job de adição %d criado no banco.", job_db.id)

            # Prepara o monitor usando o _prepare_monitor interno do manager
            self._current_job_monitor = self._addition_manager._prepare_monitor(job_db.id)
            if not self._current_job_monitor:
                logger.error("Falha ao preparar monitor para job %d.", job_db.id)
                self._notifications.notify("Erro", "Não foi possível iniciar o monitoramento.")
                return

            # Preenche a UI de monitoramento
            self._label_monitor_status.setText(self._current_job_monitor.status.value)
            self._label_monitor_conta.setText(
                f"{self._current_session.display_name} -> {self._target_group_str}"
            )
            self._progress_bar_geral.setValue(0)
            self._label_contador_sucesso.setText("0")
            self._label_contador_falha.setText("0")
            self._logs_list.clear()
            self._logs_list.addItem("Iniciando operação...") # Log inicial

            # Inicia o job
            self._addition_manager.start_job(
                job_id=job_db.id, on_update=self._handle_monitor_update
            )

            # Inicia o timer da UI
            self._monitor_timer.start()
            self._wizard.setCurrentIndex(2)
            self.job_changed.emit() # Notifica outras partes da UI

        except Exception as e:
            logger.exception("Erro ao iniciar operação de adição")
            self._notifications.notify("Erro ao Iniciar", f"Não foi possível criar o job: {e}")

    # --- PASSO 3: MONITORAMENTO ---

    def _criar_passo_3_monitoramento(self) -> QWidget:
        """Cria a UI para o Passo 3: Monitoramento em Tempo Real."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # 1. Status Geral
        grupo_status = QGroupBox("Status da Operação")
        layout_status = QGridLayout(grupo_status)

        self._label_monitor_conta = QLabel("Conta -> Grupo")
        self._label_monitor_conta.setStyleSheet("font-weight: bold;")
        layout_status.addWidget(self._label_monitor_conta, 0, 0, 1, 2)

        self._label_monitor_status = QLabel("Aguardando...")
        self._label_monitor_status.setStyleSheet("font-size: 16px; color: #00529B;")
        layout_status.addWidget(self._label_monitor_status, 0, 2, 1, 1, Qt.AlignmentFlag.AlignRight)

        self._progress_bar_geral = QProgressBar()
        self._progress_bar_geral.setValue(0)
        self._progress_bar_geral.setFormat("%p%")
        layout_status.addWidget(self._progress_bar_geral, 1, 0, 1, 3)

        # Contadores
        self._label_contador_sucesso = QLabel("0")
        self._label_contador_sucesso.setStyleSheet("font-size: 20px; color: green;")
        self._label_contador_falha = QLabel("0")
        self._label_contador_falha.setStyleSheet("font-size: 20px; color: red;")
        self._label_timer_proxima = QLabel("0s")
        self._label_timer_proxima.setStyleSheet("font-size: 20px; color: #333;")

        layout_status.addWidget(QLabel("✅ Sucesso:"), 2, 0)
        layout_status.addWidget(self._label_contador_sucesso, 2, 1)
        layout_status.addWidget(QLabel("❌ Falha:"), 3, 0)
        layout_status.addWidget(self._label_contador_falha, 3, 1)
        layout_status.addWidget(QLabel("⏳ Próxima em:"), 4, 0)
        layout_status.addWidget(self._label_timer_proxima, 4, 1)
        layout.addWidget(grupo_status)

        # 2. Controles
        grupo_controles = QGroupBox("Controles")
        layout_controles = QHBoxLayout(grupo_controles)
        self._botao_pausar = QPushButton("Pausar")
        self._botao_parar = QPushButton("Parar Operação")
        self._botao_pausar.setEnabled(False)  # TODO: Implementar lógica
        self._botao_parar.setEnabled(False)  # TODO: Implementar lógica
        layout_controles.addWidget(self._botao_pausar)
        layout_controles.addWidget(self._botao_parar)
        layout.addWidget(grupo_controles)

        # 3. Logs
        grupo_logs = QGroupBox("Logs em Tempo Real")
        layout_logs = QVBoxLayout(grupo_logs)
        self._logs_list = QListWidget()
        layout_logs.addWidget(self._logs_list)
        layout.addWidget(grupo_logs, stretch=1)

        # 4. Navegação
        self._botao_nova_operacao = QPushButton("Concluído (Nova Operação)")
        self._botao_nova_operacao.clicked.connect(self._finalizar_e_resetar)
        self._botao_nova_operacao.setEnabled(False)
        layout.addWidget(self._botao_nova_operacao)

        return widget

    @pyqtSlot(AdditionJobMonitor)
    def _handle_monitor_update(self, monitor: AdditionJobMonitor) -> None:
        """Slot para receber atualizações do worker."""
        # Esta função é chamada de um thread diferente (via on_update).
        # Armazenamos o estado mais recente. O QTimer cuidará da UI.
        self._current_job_monitor = monitor

    def _update_monitor_ui(self) -> None:
        """Atualiza a UI de monitoramento com base no estado mais recente."""
        if not self._current_job_monitor:
            return

        monitor = self._current_job_monitor

        # Atualiza Status e Progresso
        self._label_monitor_status.setText(monitor.status.value)
        self._progress_bar_geral.setValue(monitor.progress)

        # Atualiza Contadores
        self._label_contador_sucesso.setText(str(monitor.success_count))
        self._label_contador_falha.setText(str(monitor.fail_count))
        self._label_timer_proxima.setText(f"{monitor.next_add_in_seconds}s")

        # Atualiza Logs (apenas os novos)
        current_log_count = self._logs_list.count()
        new_logs = monitor.logs[0 : (len(monitor.logs) - current_log_count)]
        for log_msg in reversed(new_logs): # Adiciona do mais antigo para o mais novo
            self._logs_list.insertItem(0, log_msg)


        # Verifica se o job terminou
        if monitor.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            logger.info("Job %d finalizado com status %s. Parando timer da UI.", monitor.job_id, monitor.status)
            self._monitor_timer.stop()
            self._botao_nova_operacao.setEnabled(True)
            self._botao_pausar.setEnabled(False)
            self._botao_parar.setEnabled(False)
            self._notifications.notify(
                "Operação Concluída",
                f"Job {monitor.job_id} finalizado com status: {monitor.status.value}",
            )
            self.job_changed.emit() # Notifica outras partes da UI

    def _finalizar_e_resetar(self) -> None:
        """Limpa a UI e volta ao Passo 1."""
        logger.info("Resetando UI do Addition Manager para nova operação.")
        self._current_job_monitor = None
        self._selected_users = []
        self._monitor_timer.stop()

        # Recarrega dados
        self._carregar_dados_iniciais()
        self._check_selecionar_todos.setCheckState(Qt.CheckState.Unchecked)

        # Reseta botões e campos
        self._botao_nova_operacao.setEnabled(False)
        self._botao_pausar.setEnabled(False) # Começa desativado
        self._botao_parar.setEnabled(False) # Começa desativado
        if self._combo_grupo_destino.count() > 0:
            self._combo_grupo_destino.setCurrentIndex(0)
        self._filtro_nome.clear()
        self._filtro_grupo_origem.clear()


        self._wizard.setCurrentIndex(0)

