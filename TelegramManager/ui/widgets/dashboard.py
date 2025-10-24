# Caminho: TelegramManager/ui/widgets/dashboard.py
"""Dashboard com métricas em tempo real."""

from __future__ import annotations

import importlib.util
import logging
from datetime import datetime
from typing import Iterable, List

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QHeaderView,
    QAbstractItemView,
)

from TelegramManager.core.automation import AutomationTask, TaskStatus
from TelegramManager.core.container import Container
from TelegramManager.utils.helpers import formatar_data_humana
from TelegramManager.storage import AdditionJob

_pyqtgraph_spec = importlib.util.find_spec("pyqtgraph")
if _pyqtgraph_spec:
    import pyqtgraph as pg  # type: ignore

    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
else:  # pragma: no cover - fallback sem pyqtgraph
    pg = None

_psutil_spec = importlib.util.find_spec("psutil")
if _psutil_spec:
    import psutil  # type: ignore
else:  # pragma: no cover - fallback sem psutil
    psutil = None

logger = logging.getLogger(__name__)


class DashboardWidget(QWidget):
    """Widget completo exibindo métricas e atividades em tempo real."""

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._extraction_service = container.extraction_service
        self._report_service = container.report_service
        self._addition_manager = container.addition_manager
        self._cards: dict[str, QLabel] = {}
        self._timeline: QListWidget
        self._plot_widget: pg.PlotWidget | None = None
        self._plot_item: pg.PlotDataItem | None = None
        self._status_barra: QProgressBar
        self._tabela_tarefas: QTableWidget
        self._tabela_adicoes: QTableWidget

        self._montar_layout()
        self._aplicar_estilos()

        self._timer = QTimer(self)
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self._atualizar_status_sistema)
        self._timer.start()
        self._atualizar_status_sistema()
        self._registrar_atividade("Dashboard iniciado e monitorando métricas.")

    def _montar_layout(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        titulo = QLabel("Painel em Tempo Real")
        titulo.setObjectName("dashboard_title")
        layout.addWidget(titulo, 0, 0, 1, 4)

        # Linha 1: Cards de Métricas
        card_contas, label_contas = self._criar_card("Contas Conectadas", "0")
        card_usuarios_banco, label_usuarios_banco = self._criar_card(
            "Usuários no Banco", "0"
        )
        card_grupos_monitorados, label_grupos_monitorados = self._criar_card(
            "Grupos Monitorados", "0"
        )
        card_usuarios_adicionados, label_usuarios_adicionados = self._criar_card(
            "Usuários Adicionados (Total)", "0"
        )

        self._cards["contas"] = label_contas
        self._cards["usuarios_banco"] = label_usuarios_banco
        self._cards["grupos_monitorados"] = label_grupos_monitorados
        self._cards["usuarios_adicionados"] = label_usuarios_adicionados

        layout.addWidget(card_contas, 1, 0)
        layout.addWidget(card_usuarios_banco, 1, 1)
        layout.addWidget(card_grupos_monitorados, 1, 2)
        layout.addWidget(card_usuarios_adicionados, 1, 3)

        # Linha 2: Gráfico e Status
        layout.addWidget(self._criar_grafico_automacao(), 2, 0, 1, 2)
        layout.addWidget(self._criar_status_sistema(), 2, 2, 1, 2)

        # Linha 3: Tarefas e Logs
        layout.addWidget(self._criar_tabela_tarefas("Próximas Automações"), 3, 0, 1, 2)
        layout.addWidget(self._criar_tabela_adicoes(), 3, 2, 1, 2)

        # Linha 4: Logs
        layout.addWidget(self._criar_timeline(), 4, 0, 1, 4)

        # Definindo stretch das colunas e linhas
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(2, 1)  # Gráfico
        layout.setRowStretch(3, 2)  # Tabelas
        layout.setRowStretch(4, 1)  # Logs

    def _aplicar_estilos(self) -> None:
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fb;
            }
            #dashboard_title {
                font-size: 24px;
                font-weight: bold;
                color: #222;
                padding-bottom: 10px;
            }
            #card_metrica {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 16px;
                background-color: white;
            }
            #card_titulo {
                font-size: 14px;
                color: #555;
            }
            #card_valor {
                font-size: 28px;
                font-weight: bold;
                color: #0078d4;
                padding-top: 5px;
            }
            QFrame[objectName="quadro_painel"] {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                background-color: white;
            }
            QLabel[objectName="titulo_painel"] {
                font-weight: bold;
                font-size: 16px;
                color: #333;
                padding-bottom: 8px;
            }
            QTableWidget {
                border: none;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f0f2f5;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QListWidget {
                border: none;
                font-family: "Consolas", "Courier New", monospace;
            }
        """)

    def _criar_card(self, titulo: str, valor_inicial: str) -> tuple[QWidget, QLabel]:
        card = QFrame()
        card.setObjectName("card_metrica")
        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        label_titulo = QLabel(titulo)
        label_titulo.setObjectName("card_titulo")
        layout.addWidget(label_titulo)

        label_valor = QLabel(valor_inicial)
        label_valor.setObjectName("card_valor")
        layout.addWidget(label_valor)
        layout.addStretch()
        return card, label_valor

    def _criar_grafico_automacao(self) -> QWidget:
        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(8)

        titulo = QLabel("Atividade Diária (Automações Concluídas)")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        if pg:
            self._plot_widget = pg.PlotWidget()
            self._plot_item = self._plot_widget.plot(
                pen=pg.mkPen(color="#0078d4", width=2),
                symbol="o",
                symbolBrush="#0078d4",
                symbolSize=8,
            )
            self._plot_widget.setLabel("left", "Execuções")
            self._plot_widget.setLabel("bottom", "Data")
            layout.addWidget(self._plot_widget)
        else:
            layout.addWidget(
                QLabel("Instale 'pyqtgraph' para visualizar o gráfico de atividade.")
            )
        return quadro

    def _criar_status_sistema(self) -> QWidget:
        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(8)

        titulo = QLabel("Status do Sistema")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        self._status_cpu = QLabel("CPU: ...")
        self._status_memoria = QLabel("Memória: ...")
        self._status_rede = QLabel("Rede: ...")
        layout.addWidget(self._status_cpu)
        layout.addWidget(self._status_memoria)
        layout.addWidget(self._status_rede)

        self._status_barra = QProgressBar()
        self._status_barra.setTextVisible(False)
        layout.addWidget(self._status_barra)
        layout.addStretch()
        return quadro

    def _criar_tabela_tarefas(self, titulo_str: str) -> QWidget:
        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(8)

        titulo = QLabel(titulo_str)
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        self._tabela_tarefas = QTableWidget(0, 3)
        self._tabela_tarefas.setHorizontalHeaderLabels(["Tarefa", "Grupo", "Execução"])
        self._tabela_tarefas.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._tabela_tarefas.horizontalHeader().setStretchLastSection(True)
        self._tabela_tarefas.verticalHeader().setVisible(False)
        self._tabela_tarefas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela_tarefas.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        layout.addWidget(self._tabela_tarefas)
        return quadro

    def _criar_tabela_adicoes(self) -> QWidget:
        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(8)

        titulo = QLabel("Operações de Adição Recentes")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        self._tabela_adicoes = QTableWidget(0, 4)
        self._tabela_adicoes.setHorizontalHeaderLabels(
            ["Grupo Alvo", "Status", "Progresso", "Sucesso/Falha"]
        )
        self._tabela_adicoes.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._tabela_adicoes.horizontalHeader().setStretchLastSection(True)
        self._tabela_adicoes.verticalHeader().setVisible(False)
        self._tabela_adicoes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._tabela_adicoes)
        return quadro

    def _criar_timeline(self) -> QWidget:
        quadro = QFrame()
        quadro.setObjectName("quadro_painel")
        layout = QVBoxLayout(quadro)
        layout.setSpacing(8)

        titulo = QLabel("Atividades Recentes (Logs)")
        titulo.setObjectName("titulo_painel")
        layout.addWidget(titulo)

        self._timeline = QListWidget()
        layout.addWidget(self._timeline)
        return quadro

    # --- Slots de Atualização ---

    def atualizar_metricas(self) -> None:
        """Atualiza os cards de métricas (Contas e Extração)."""
        logger.debug("Dashboard: Atualizando métricas (contas e extração)")
        total_contas = len(self._container.session_manager.sessions)
        self._cards["contas"].setText(str(total_contas))

        overview = self._extraction_service.overview()
        self._cards["usuarios_banco"].setText(str(overview.total_users))
        self._cards["grupos_monitorados"].setText(str(overview.total_groups))

        # Atualiza gráfico
        if self._plot_item:
            atividade = self._report_service.gerar_atividade_diaria()
            x = [d.dia.timestamp() for d in atividade]
            y = [d.concluidas for d in atividade]
            if x:
                self._plot_item.setData(x, y)
                # Configura eixo X para mostrar datas
                try:
                    axis = self._plot_widget.getAxis("bottom")
                    ticks = [list(zip(x, [d.dia.strftime("%d/%m") for d in atividade]))]
                    axis.setTicks(ticks)
                except Exception as e:
                    logger.warning("Erro ao atualizar eixo do gráfico: %s", e)
            else:
                 self._plot_item.setData([], [])


        self._registrar_atividade("Métricas de extração e automação atualizadas.")

    def atualizar_metricas_adicao(self) -> None:
        """Atualiza os cards e tabelas da função de Adição."""
        logger.debug("Dashboard: Atualizando métricas (adição)")
        resumo = self._report_service.gerar_resumo_adicoes()
        self._cards["usuarios_adicionados"].setText(str(resumo.total_adicionados))

        # Atualiza tabela de jobs de adição
        jobs = self._addition_manager.list_recent_jobs(limit=10)
        self._tabela_adicoes.setRowCount(len(jobs))
        for linha, job in enumerate(jobs):
            self._tabela_adicoes.setItem(linha, 0, QTableWidgetItem(job.target_group))
            
            status_item = QTableWidgetItem(job.status)
            if job.status == TaskStatus.FAILED.value:
                status_item.setForeground(Qt.GlobalColor.red)
            elif job.status == TaskStatus.COMPLETED.value:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            self._tabela_adicoes.setItem(linha, 1, status_item)

            # Barra de progresso na tabela
            progress_bar = QProgressBar()
            progress_bar.setValue(job.progress)
            progress_bar.setFormat("%p%")
            progress_bar.setTextVisible(True)
            if job.status == TaskStatus.RUNNING.value:
                 progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #0078d4; }")
            self._tabela_adicoes.setCellWidget(linha, 2, progress_bar)

            sucesso_falha = f"✅ {job.success_count} / ❌ {job.fail_count}"
            self._tabela_adicoes.setItem(linha, 3, QTableWidgetItem(sucesso_falha))

        self._registrar_atividade("Métricas de adição de usuários atualizadas.")

    def atualizar_agendamentos(self, tarefas: Iterable[AutomationTask]) -> None:
        """Atualiza a tabela de próximas tarefas de automação."""
        logger.debug("Dashboard: Atualizando agendamentos")
        tarefas_agendadas = sorted(
            [t for t in tarefas if t.status == TaskStatus.SCHEDULED],
            key=lambda tarefa: tarefa.agendamento,
        )
        self._tabela_tarefas.setRowCount(len(tarefas_agendadas))
        for linha, tarefa in enumerate(tarefas_agendadas):
            self._tabela_tarefas.setItem(linha, 0, QTableWidgetItem(tarefa.titulo))
            self._tabela_tarefas.setItem(linha, 1, QTableWidgetItem(tarefa.grupo))
            self._tabela_tarefas.setItem(
                linha,
                2,
                QTableWidgetItem(formatar_data_humana(tarefa.agendamento)),
            )

    def _registrar_atividade(self, descricao: str) -> None:
        item = QListWidgetItem(f"[{datetime.now().strftime('%H:%M:%S')}] {descricao}")
        self._timeline.insertItem(0, item)
        if self._timeline.count() > 100:
            self._timeline.takeItem(self._timeline.count() - 1)

    def _atualizar_status_sistema(self) -> None:
        if psutil:
            cpu = psutil.cpu_percent(interval=None)
            memoria = psutil.virtual_memory().percent
            self._status_cpu.setText(f"CPU: {cpu:.0f}%")
            self._status_memoria.setText(f"Memória: {memoria:.0f}%")
            self._status_barra.setValue(int(memoria))
            try:
                io = psutil.net_io_counters()
                rede_txt = f"Rede: {io.bytes_sent // 1024} kB↑ / {io.bytes_recv // 1024} kB↓"
            except Exception:
                rede_txt = "Rede: N/A"  # Pode falhar em algumas permissões
            self._status_rede.setText(rede_txt)
        else:
            self._status_cpu.setText("CPU: (psutil não instalado)")
            self._status_memoria.setText("Memória: (psutil não instalado)")
            self._status_rede.setText("Rede: (psutil não instalado)")
            self._status_barra.setValue(0)

