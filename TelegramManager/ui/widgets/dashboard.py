# Caminho: TelegramManager/ui/widgets/dashboard.py
"""Dashboard com métricas em tempo real e visual aprimorado."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional

from PyQt6.QtCore import QSize, QTimer, Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.addition_manager import AdditionOverview
from TelegramManager.core.automation import TaskStatus
from TelegramManager.core.container import Container
from TelegramManager.core.extraction import SyncedGroup
from TelegramManager.storage import AdditionJob
from TelegramManager.utils.helpers import formatar_data_humana

# Tentativa de carregar psutil
_psutil_spec = importlib.util.find_spec("psutil")
if _psutil_spec:
    try:
        import psutil # type: ignore
    except ImportError:
        psutil = None
else:
    psutil = None

logger = logging.getLogger(__name__)


class DashboardWidget(QWidget):
    """Widget completo exibindo métricas e atividades com visual moderno."""

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._extraction_service = container.extraction_service
        self._addition_manager = container.addition_manager
        self._cards: Dict[str, QLabel] = {}
        self._timeline: QListWidget
        self._status_barra: QProgressBar
        self._tabela_grupos: QTableWidget
        self._tabela_adicoes: QTableWidget
        self._lista_resumo_grupos: QListWidget

        self._montar_layout()
        self._aplicar_estilos() # Centraliza estilos

        # Timer para atualizar dados dinâmicos
        self._timer_dados = QTimer(self)
        self._timer_dados.setInterval(15000) # Atualiza a cada 15 segundos
        self._timer_dados.timeout.connect(self._atualizar_dados_dinamicos)
        self._timer_dados.start()

        # Timer para status do sistema (mais frequente)
        self._timer_sistema = QTimer(self)
        self._timer_sistema.setInterval(3000) # Atualiza a cada 3 segundos
        self._timer_sistema.timeout.connect(self._atualizar_status_sistema)
        self._timer_sistema.start()

        # Atualização inicial
        self._atualizar_dados_dinamicos()
        self._atualizar_status_sistema()
        self._registrar_atividade("Dashboard iniciado e monitorando métricas.")

    def _montar_layout(self) -> None:
        """Define a estrutura principal do layout em grade."""
        layout = QGridLayout(self)
        layout.setContentsMargins(25, 25, 25, 25) # Mais margem externa
        layout.setSpacing(25) # Mais espaçamento entre elementos

        titulo = QLabel("Painel Principal")
        titulo.setObjectName("dashboard_title")
        layout.addWidget(titulo, 0, 0, 1, 4) # Ocupa toda a largura

        # --- Linha 1: Cards ---
        card_contas, self._cards["contas"] = self._criar_card(
            "Contas Ativas", "0", ":/icons/users.svg" # Exemplo de ícone
        )
        card_usuarios_banco, self._cards["usuarios_banco"] = self._criar_card(
            "Usuários no Banco", "0", ":/icons/database.svg"
        )
        card_grupos, self._cards["grupos_monitorados"] = self._criar_card(
            "Grupos Monitorados", "0", ":/icons/folder.svg"
        )
        card_adicionados, self._cards["usuarios_adicionados"] = self._criar_card(
            "Adições Totais", "0", ":/icons/user-plus.svg"
        )

        layout.addWidget(card_contas, 1, 0)
        layout.addWidget(card_usuarios_banco, 1, 1)
        layout.addWidget(card_grupos, 1, 2)
        layout.addWidget(card_adicionados, 1, 3)

        # --- Linha 2: Resumo e Status ---
        layout.addWidget(self._criar_resumo_grupos(), 2, 0, 1, 2) # Ocupa 2 colunas
        layout.addWidget(self._criar_status_sistema(), 2, 2, 1, 2) # Ocupa 2 colunas

        # --- Linha 3: Tabelas ---
        layout.addWidget(self._criar_tabela_grupos(), 3, 0, 1, 2)
        layout.addWidget(self._criar_tabela_adicoes(), 3, 2, 1, 2)

        # --- Linha 4: Logs ---
        layout.addWidget(self._criar_timeline(), 4, 0, 1, 4) # Ocupa toda a largura

        # --- Configuração de Stretch ---
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(1, 0) # Cards altura fixa
        layout.setRowStretch(2, 1) # Gráfico e Status flexíveis
        layout.setRowStretch(3, 2) # Tabelas com mais espaço
        layout.setRowStretch(4, 1) # Logs flexíveis

    def _aplicar_estilos(self) -> None:
        """Aplica a folha de estilos (Stylesheet) para a aparência."""
        self.setStyleSheet("""
            /* Estilo Geral */
            DashboardWidget {
                background-color: #f8f9fb; /* Fundo principal mais claro */
            }

            /* Título Principal */
            #dashboard_title {
                font-size: 26px; /* Maior */
                font-weight: 600; /* Levemente mais forte */
                color: #1a202c; /* Cor escura */
                padding-bottom: 15px;
                margin-left: 5px; /* Pequeno ajuste */
            }

            /* Cards de Métricas */
            QFrame#card_metrica {
                border: 1px solid #e2e8f0; /* Borda suave */
                border-radius: 12px; /* Mais arredondado */
                padding: 20px;
                background-color: white;
                min-height: 110px; /* Altura mínima */
            }
            QLabel#card_icon {
                /* Para o QLabel que vai conter o ícone */
                min-width: 32px;
                min-height: 32px;
                max-width: 32px;
                max-height: 32px;
                /* Adicionar cor de fundo ou borda se quiser destacar */
            }
            QLabel#card_titulo {
                font-size: 15px; /* Ligeiramente maior */
                font-weight: 500;
                color: #4a5568; /* Cinza escuro */
                margin-left: 10px; /* Espaço após ícone */
            }
            QLabel#card_valor {
                font-size: 30px; /* Maior */
                font-weight: 600; /* Mais forte */
                color: #2d3748; /* Cor escura principal */
                padding-top: 8px;
                margin-left: 10px;
            }

            /* Quadros dos Painéis (Gráfico, Status, Tabelas, Logs) */
            QFrame#quadro_painel {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 18px;
                background-color: white;
            }
            QLabel#titulo_painel {
                font-weight: 600; /* Mais forte */
                font-size: 17px; /* Maior */
                color: #2d3748;
                padding-bottom: 12px; /* Mais espaço abaixo */
            }

            /* Tabelas */
            QTableWidget {
                border: none;
                gridline-color: #e2e8f0; /* Linhas suaves */
                alternate-background-color: #f7fafc; /* Zebrado sutil */
            }
            QHeaderView::section {
                background-color: #f7fafc; /* Fundo do header */
                padding: 8px 10px; /* Mais padding */
                border: none;
                border-bottom: 1px solid #e2e8f0; /* Linha divisória */
                font-weight: 600; /* Header em negrito */
                color: #4a5568;
                text-align: left; /* Alinhamento */
            }
            QTableWidget::item {
                padding: 8px 10px; /* Padding nas células */
                border-bottom: 1px solid #e2e8f0;
            }

            /* Lista de Logs */
            QListWidget#timeline_list {
                border: none;
                font-family: "Segoe UI", "Consolas", monospace; /* Fontes mais comuns */
                font-size: 13px;
                color: #4a5568;
            }
            QListWidget#timeline_list::item {
                padding: 6px 0px; /* Espaçamento vertical */
                border-bottom: 1px dashed #e2e8f0; /* Linha pontilhada sutil */
            }
            QListWidget#timeline_list::item:last-child {
                border-bottom: none; /* Remove a última linha */
            }

            /* Barra de Progresso */
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                text-align: center;
                height: 16px; /* Altura fixa */
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #4299e1; /* Azul mais vibrante */
                border-radius: 7px;
            }
            QProgressBar#status_barra::chunk {
                 background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #86efac, stop:1 #16a34a); /* Gradiente verde */
            }

        """)

    def _criar_card(self, titulo: str, valor_inicial: str, icon_path: Optional[str] = None) -> tuple[QWidget, QLabel]:
        """Cria um card de métrica com título, valor e ícone opcional."""
        card = QFrame()
        card.setObjectName("card_metrica")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5) # Reduz espaçamento interno

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # Ícone (se fornecido)
        # Nota: Ícones precisam estar acessíveis (ex: via Qt Resource System ou path direto)
        # Usando placeholders simples por enquanto
        icon_label = QLabel()
        icon_label.setObjectName("card_icon")
        icon_label.setText("📊") # Placeholder Emoji
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # icon_label.setStyleSheet("background-color: #e6f7ff; border-radius: 16px;") # Exemplo de fundo
        header_layout.addWidget(icon_label)


        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("card_titulo")
        header_layout.addWidget(label_titulo)
        header_layout.addStretch() # Empurra título e ícone para esquerda

        card_layout.addLayout(header_layout)

        label_valor = QLabel(valor_inicial)
        label_valor.setObjectName("card_valor")
        card_layout.addWidget(label_valor)

        # Adiciona um spacer para garantir altura mínima mesmo sem valor
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_layout.addWidget(spacer)


        return card, label_valor

    def _criar_resumo_grupos(self) -> QWidget:
        """Cria o painel de resumo dos grupos sincronizados por conta."""

        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(10)

        titulo = QLabel("Grupos sincronizados por conta")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        descricao = QLabel(
            "Veja rapidamente quantos grupos cada conta disponibilizou e o volume de usuários já no banco."
        )
        descricao.setWordWrap(True)
        descricao.setStyleSheet("color: #64748b;")
        layout.addWidget(descricao)

        self._lista_resumo_grupos = QListWidget()
        self._lista_resumo_grupos.setObjectName("lista_resumo_grupos")
        self._lista_resumo_grupos.setAlternatingRowColors(True)
        self._lista_resumo_grupos.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        layout.addWidget(self._lista_resumo_grupos, stretch=1)

        return quadro

    def _criar_status_sistema(self) -> QWidget:
        """Cria o painel de status do sistema."""
        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(10) # Aumenta espaçamento

        titulo = QLabel("Status do Sistema")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        # Usando GridLayout para alinhar melhor
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)

        grid_layout.addWidget(QLabel("CPU:"), 0, 0)
        self._status_cpu = QLabel("...")
        self._status_cpu.setStyleSheet("font-weight: 500;")
        grid_layout.addWidget(self._status_cpu, 0, 1)

        grid_layout.addWidget(QLabel("Memória:"), 1, 0)
        self._status_memoria = QLabel("...")
        self._status_memoria.setStyleSheet("font-weight: 500;")
        grid_layout.addWidget(self._status_memoria, 1, 1)

        self._status_barra = QProgressBar()
        self._status_barra.setObjectName("status_barra") # Para estilização específica
        self._status_barra.setTextVisible(True)
        self._status_barra.setFormat("%p%")
        grid_layout.addWidget(self._status_barra, 2, 0, 1, 2) # Ocupa 2 colunas

        grid_layout.addWidget(QLabel("Rede:"), 3, 0)
        self._status_rede = QLabel("...")
        self._status_rede.setStyleSheet("font-size: 12px; color: #718096;") # Menor e cinza
        grid_layout.addWidget(self._status_rede, 3, 1)

        layout.addLayout(grid_layout)
        layout.addStretch() # Empurra para cima
        return quadro

    def _criar_tabela_base(self, colunas: List[str]) -> QTableWidget:
        """Cria uma QTableWidget com estilo base."""
        tabela = QTableWidget(0, len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabela.verticalHeader().setVisible(False)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabela.setAlternatingRowColors(True) # Habilita zebrado
        tabela.setShowGrid(False) # Remove gridlines internas, usa borda inferior
        return tabela

    def _criar_tabela_grupos(self) -> QWidget:
        """Cria o painel com a tabela de grupos sincronizados."""

        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(10)

        titulo = QLabel("Grupos disponíveis no banco")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        self._tabela_grupos = self._criar_tabela_base(
            ["Grupo", "Conta", "Última sincronização", "Usuários"]
        )
        self._tabela_grupos.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._tabela_grupos.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._tabela_grupos.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self._tabela_grupos.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        layout.addWidget(self._tabela_grupos)
        return quadro

    def _criar_tabela_adicoes(self) -> QWidget:
        """Cria o painel com a tabela de operações de adição."""
        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(10)

        titulo = QLabel("Operações de Adição Recentes")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        self._tabela_adicoes = self._criar_tabela_base(
             ["Grupo Alvo", "Status", "Progresso", "Sucesso/Falha"]
        )
        # Ajuste fino das colunas
        self._tabela_adicoes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._tabela_adicoes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._tabela_adicoes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive) # Permite ajustar
        self._tabela_adicoes.setColumnWidth(2, 120) # Largura inicial para progresso
        self._tabela_adicoes.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self._tabela_adicoes)
        return quadro

    def _criar_timeline(self) -> QWidget:
        """Cria o painel com a lista de logs/atividades."""
        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(10)

        titulo = QLabel("Atividades Recentes")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        self._timeline = QListWidget()
        self._timeline.setObjectName("timeline_list") # Para estilização
        layout.addWidget(self._timeline)
        return quadro

    # --- Slots de Atualização ---

    def _atualizar_dados_dinamicos(self) -> None:
        """Atualiza todas as métricas e tabelas que dependem do backend."""
        logger.debug("Dashboard: Atualizando dados dinâmicos...")
        try:
            self.atualizar_metricas()
            self.atualizar_metricas_adicao()

        except Exception as e:
            logger.exception("Erro ao atualizar dados dinâmicos do dashboard")
            self._registrar_atividade(f"Erro ao atualizar dados: {e}")

    def atualizar_metricas(self) -> None:
        """Atualiza os cards de métricas (Contas e Extração)."""
        total_contas = len(self._container.session_manager.sessions)
        self._cards["contas"].setText(str(total_contas))

        try:
            overview = self._extraction_service.overview()
            self._cards["usuarios_banco"].setText(f"{overview.total_users:,}".replace(",", "."))
            self._cards["grupos_monitorados"].setText(str(overview.total_groups))
        except Exception as e:
            logger.error("Falha ao obter overview da extração: %s", e)
            self._cards["usuarios_banco"].setText("Erro")
            self._cards["grupos_monitorados"].setText("Erro")
        try:
            grupos = self._extraction_service.list_synced_groups()
        except Exception as e_grupos:
            logger.error("Falha ao listar grupos sincronizados: %s", e_grupos)
            grupos = []

        self._preencher_resumo_grupos(grupos)
        self._popular_tabela_grupos(grupos)

        self._registrar_atividade("Métricas de contas e grupos atualizadas.")

    def _preencher_resumo_grupos(self, grupos: List[SyncedGroup]) -> None:
        """Atualiza a lista resumida com contagem de grupos por conta."""

        self._lista_resumo_grupos.clear()
        if not grupos:
            self._lista_resumo_grupos.addItem(
                "Nenhum grupo sincronizado até o momento."
            )
            return

        agregados: Dict[str, Dict[str, int | str]] = {}
        for grupo in grupos:
            chave = grupo.account_phone or grupo.account_display_name or "—"
            entrada = agregados.setdefault(
                chave,
                {
                    "nome": grupo.account_display_name
                    or grupo.account_phone
                    or "Conta não identificada",
                    "grupos": 0,
                    "membros": 0,
                },
            )
            entrada["grupos"] += 1
            entrada["membros"] += grupo.total_members

        for dados in sorted(agregados.values(), key=lambda item: str(item["nome"]).lower()):
            texto = (
                f"{dados['nome']} • {dados['grupos']} grupos • "
                f"{dados['membros']} usuários"
            )
            self._lista_resumo_grupos.addItem(texto)

    def _popular_tabela_grupos(self, grupos: List[SyncedGroup]) -> None:
        """Preenche a tabela detalhada de grupos sincronizados."""

        self._tabela_grupos.setRowCount(len(grupos))
        for linha, grupo in enumerate(grupos):
            conta = "—"
            if grupo.account_display_name:
                conta = grupo.account_display_name
                if grupo.account_phone:
                    conta = f"{conta} ({grupo.account_phone})"
            elif grupo.account_phone:
                conta = grupo.account_phone

            ultima = (
                formatar_data_humana(grupo.last_sync) if grupo.last_sync else "—"
            )
            membros = f"{grupo.total_members:,}".replace(",", ".")

            self._tabela_grupos.setItem(linha, 0, QTableWidgetItem(grupo.name))
            self._tabela_grupos.setItem(linha, 1, QTableWidgetItem(conta))
            self._tabela_grupos.setItem(linha, 2, QTableWidgetItem(ultima))
            self._tabela_grupos.setItem(linha, 3, QTableWidgetItem(membros))

    def atualizar_metricas_adicao(self) -> None:
        """Atualiza os cards e tabelas da função de Adição."""
        try:
            resumo: AdditionOverview = self._addition_manager.overview()
            self._cards["usuarios_adicionados"].setText(
                f"{resumo.total_success:,}".replace(",", ".")
            )
        except Exception as e:
            logger.error("Falha ao gerar resumo de adições: %s", e)
            self._cards["usuarios_adicionados"].setText("Erro")
            return # Sai se não conseguir o resumo

        # Atualiza tabela de jobs de adição
        try:
            jobs = self._addition_manager.list_recent_jobs(limit=10)
            self._tabela_adicoes.setRowCount(len(jobs))
            for linha, job in enumerate(jobs):
                self._tabela_adicoes.setItem(linha, 0, QTableWidgetItem(job.target_group))

                status_val = job.status # Pega o valor string do Enum (se for Enum)
                status_item = QTableWidgetItem(status_val)
                # Define cor baseada no status
                if status_val == TaskStatus.FAILED.value:
                    status_item.setForeground(Qt.GlobalColor.red)
                elif status_val == TaskStatus.COMPLETED.value:
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif status_val == TaskStatus.RUNNING.value:
                    status_item.setForeground(Qt.GlobalColor.blue)
                self._tabela_adicoes.setItem(linha, 1, status_item)

                # Barra de progresso na tabela
                progress_widget = self._tabela_adicoes.cellWidget(linha, 2)
                if not isinstance(progress_widget, QProgressBar):
                    progress_widget = QProgressBar()
                    progress_widget.setFormat("%p%")
                    progress_widget.setTextVisible(True)
                    progress_widget.setFixedHeight(20) # Altura menor
                    progress_widget.setStyleSheet("QProgressBar { margin: 2px; }") # Pequena margem
                    self._tabela_adicoes.setCellWidget(linha, 2, progress_widget)

                progress_widget.setValue(job.progress)
                if job.status == TaskStatus.RUNNING.value:
                     progress_widget.setStyleSheet(
                         "QProgressBar::chunk { background-color: #3182ce; border-radius: 5px; margin: 1px;}"
                         "QProgressBar { margin: 2px; border-radius: 6px; text-align: center;}"
                         )
                else:
                    progress_widget.setStyleSheet(
                        "QProgressBar::chunk { background-color: #a0aec0; border-radius: 5px; margin: 1px;}"
                         "QProgressBar { margin: 2px; border-radius: 6px; text-align: center;}"
                        )


                sucesso_falha = f"✅{job.success_count} / ❌{job.fail_count}"
                sf_item = QTableWidgetItem(sucesso_falha)
                sf_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._tabela_adicoes.setItem(linha, 3, sf_item)

            self._registrar_atividade("Métricas de adição de usuários atualizadas.")
        except Exception as e_table:
            logger.exception("Erro ao atualizar tabela de adições")
            self._registrar_atividade(f"Erro ao carregar operações de adição: {e_table}")

    def _registrar_atividade(self, descricao: str) -> None:
        """Adiciona uma entrada à lista de logs/timeline."""
        if hasattr(self, '_timeline'): # Garante que _timeline foi inicializada
            timestamp = datetime.now().strftime('%H:%M:%S')
            item = QListWidgetItem(f"[{timestamp}] {descricao}")
            # Define cor sutil baseada no tipo de mensagem
            if "Erro" in descricao:
                item.setForeground(Qt.GlobalColor.red)
            elif "atualizad" in descricao.lower():
                 item.setForeground(Qt.GlobalColor.darkGray)

            self._timeline.insertItem(0, item)
            # Limita o número de itens para performance
            if self._timeline.count() > 150:
                self._timeline.takeItem(self._timeline.count() - 1)

    def _atualizar_status_sistema(self) -> None:
        """Atualiza os indicadores de uso de CPU, memória e rede."""
        if psutil:
            try:
                cpu = psutil.cpu_percent(interval=None)
                memoria = psutil.virtual_memory()
                mem_percent = memoria.percent
                mem_used = memoria.used / (1024**3) # GB
                mem_total = memoria.total / (1024**3) # GB

                self._status_cpu.setText(f"{cpu:.0f}%")
                self._status_memoria.setText(f"{mem_percent:.0f}% ({mem_used:.1f}/{mem_total:.1f} GB)")
                self._status_barra.setValue(int(mem_percent))

                io = psutil.net_io_counters()
                rede_txt = f"{io.bytes_sent // 1024} kB↑ / {io.bytes_recv // 1024} kB↓"
                self._status_rede.setText(rede_txt)

            except Exception as e:
                logger.warning("Falha ao ler status do sistema: %s", e)
                self._status_cpu.setText("Erro")
                self._status_memoria.setText("Erro")
                self._status_rede.setText("Erro")
                self._status_barra.setValue(0)
        else:
            self._status_cpu.setText("N/A")
            self._status_memoria.setText("N/A (psutil ausente)")
            self._status_rede.setText("N/A")
            self._status_barra.setValue(0)
            self._status_barra.setFormat("psutil não instalado")
            self._timer_sistema.stop() # Para de tentar atualizar se não tem psutil

