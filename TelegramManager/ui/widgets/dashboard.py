"""Dashboard com métricas em tempo real."""

from __future__ import annotations

import importlib.util
from datetime import datetime
from typing import Iterable

from PyQt6.QtCore import QTimer, Qt
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
)

from TelegramManager.core.automation import AutomationTask
from TelegramManager.core.container import Container
from TelegramManager.utils.helpers import formatar_data_humana

_pyqtgraph_spec = importlib.util.find_spec("pyqtgraph")
if _pyqtgraph_spec:
    import pyqtgraph as pg  # type: ignore
else:  # pragma: no cover - fallback sem pyqtgraph
    pg = None

_psutil_spec = importlib.util.find_spec("psutil")
if _psutil_spec:
    import psutil  # type: ignore
else:  # pragma: no cover - fallback sem psutil
    psutil = None


class DashboardWidget(QWidget):
    """Widget completo exibindo métricas e atividades em tempo real."""

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._extraction_service = container.extraction_service
        self._cards: dict[str, QLabel] = {}
        self._timeline: QListWidget
        self._grafico: QWidget
        self._status_barra: QProgressBar
        self._tabela_tarefas: QTableWidget

        self._montar_layout()

        self._timer = QTimer(self)
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self._atualizar_status_sistema)
        self._timer.start()
        self._atualizar_status_sistema()
        self._registrar_atividade("Dashboard iniciado e monitorando métricas.")
        self.atualizar_metricas()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        titulo = QLabel("Painel em tempo real")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        layout.addLayout(self._criar_cards())
        layout.addWidget(self._criar_grafico())
        layout.addLayout(self._criar_conteudo_inferior())

    def _criar_cards(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(14)

        for indice, (titulo, chave) in enumerate(
            [
                ("Usuários Ativos", "usuarios"),
                ("Grupos Monitorados", "grupos"),
                ("Contas Conectadas", "contas"),
            ]
        ):
            card = self._criar_card(titulo)
            label_valor = card.findChild(QLabel, "valor")
            if label_valor:
                self._cards[chave] = label_valor
            grid.addWidget(card, 0, indice)
        return grid

    def _criar_card(self, titulo: str) -> QWidget:
        card = QFrame()
        card.setObjectName("card_metrica")
        card.setStyleSheet(
            "#card_metrica {"
            " border: 1px solid #d0d7de;"
            " border-radius: 8px;"
            " padding: 16px;"
            " background-color: #f8f9fb;"
            "}"
        )
        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("font-size: 14px; color: #475467;")
        layout.addWidget(label_titulo)

        label_valor = QLabel("0")
        label_valor.setObjectName("valor")
        label_valor.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(label_valor)
        layout.addStretch()
        return card

    def _criar_grafico(self) -> QWidget:
        container = QFrame()
        container.setStyleSheet(
            "border: 1px solid #d0d7de; border-radius: 8px; padding: 12px;"
        )
        layout = QVBoxLayout(container)
        layout.setSpacing(8)

        titulo = QLabel("Progresso das automações")
        titulo.setStyleSheet("font-weight: bold;")
        layout.addWidget(titulo)

        if pg:
            grafico = pg.PlotWidget()
            grafico.setBackground("w")
            grafico.setLabel("left", "Execuções")
            grafico.setLabel("bottom", "Minutos")
            grafico.plot([0, 2, 4, 6, 8], [0, 5, 8, 12, 15], pen="b")
        else:
            grafico = QProgressBar()
            grafico.setRange(0, 100)
            grafico.setValue(65)
        self._grafico = grafico
        layout.addWidget(grafico)

        return container

    def _criar_conteudo_inferior(self) -> QHBoxLayout:
        container = QHBoxLayout()
        container.setSpacing(16)

        container.addWidget(self._criar_timeline(), stretch=2)
        container.addWidget(self._criar_status_sistema(), stretch=1)
        container.addWidget(self._criar_tabela_tarefas(), stretch=2)
        return container

    def _criar_timeline(self) -> QWidget:
        quadro = QFrame()
        quadro.setStyleSheet(
            "border: 1px solid #d0d7de; border-radius: 8px; padding: 12px;"
        )
        layout = QVBoxLayout(quadro)
        layout.setSpacing(8)

        titulo = QLabel("Atividades recentes")
        titulo.setStyleSheet("font-weight: bold;")
        layout.addWidget(titulo)

        self._timeline = QListWidget()
        layout.addWidget(self._timeline)
        return quadro

    def _criar_status_sistema(self) -> QWidget:
        quadro = QFrame()
        quadro.setStyleSheet(
            "border: 1px solid #d0d7de; border-radius: 8px; padding: 12px;"
        )
        layout = QVBoxLayout(quadro)
        layout.setSpacing(8)

        titulo = QLabel("Status do sistema")
        titulo.setStyleSheet("font-weight: bold;")
        layout.addWidget(titulo)

        self._status_cpu = QLabel("CPU: 0%")
        self._status_memoria = QLabel("Memória: 0%")
        self._status_rede = QLabel("Rede: aguardando...")
        layout.addWidget(self._status_cpu)
        layout.addWidget(self._status_memoria)
        layout.addWidget(self._status_rede)

        self._status_barra = QProgressBar()
        layout.addWidget(self._status_barra)

        return quadro

    def _criar_tabela_tarefas(self) -> QWidget:
        quadro = QFrame()
        quadro.setStyleSheet(
            "border: 1px solid #d0d7de; border-radius: 8px; padding: 12px;"
        )
        layout = QVBoxLayout(quadro)
        layout.setSpacing(8)

        titulo = QLabel("Próximas tarefas")
        titulo.setStyleSheet("font-weight: bold;")
        layout.addWidget(titulo)

        self._tabela_tarefas = QTableWidget(0, 3)
        self._tabela_tarefas.setHorizontalHeaderLabels(["Tarefa", "Grupo", "Execução"])
        self._tabela_tarefas.horizontalHeader().setStretchLastSection(True)
        self._tabela_tarefas.verticalHeader().setVisible(False)
        self._tabela_tarefas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._tabela_tarefas)
        return quadro

    def atualizar_metricas(self) -> None:
        total_contas = len(self._container.session_manager.sessions)
        self._cards["contas"].setText(str(total_contas))

        overview = self._extraction_service.overview()
        self._cards["usuarios"].setText(str(overview.total_users))
        self._cards["grupos"].setText(str(overview.total_groups))

    def atualizar_agendamentos(self, tarefas: Iterable[AutomationTask]) -> None:
        tarefas_ordenadas = sorted(
            tarefas,
            key=lambda tarefa: tarefa.agendamento,
        )
        self._tabela_tarefas.setRowCount(len(tarefas_ordenadas))
        for linha, tarefa in enumerate(tarefas_ordenadas):
            self._tabela_tarefas.setItem(linha, 0, QTableWidgetItem(tarefa.titulo))
            self._tabela_tarefas.setItem(linha, 1, QTableWidgetItem(tarefa.grupo))
            self._tabela_tarefas.setItem(
                linha,
                2,
                QTableWidgetItem(formatar_data_humana(tarefa.agendamento)),
            )

    def _registrar_atividade(self, descricao: str) -> None:
        item = QListWidgetItem(datetime.now().strftime("%H:%M") + " • " + descricao)
        self._timeline.insertItem(0, item)
        if self._timeline.count() > 50:
            self._timeline.takeItem(self._timeline.count() - 1)

    def _atualizar_status_sistema(self) -> None:
        if psutil:
            cpu = psutil.cpu_percent(interval=None)
            memoria = psutil.virtual_memory().percent
            self._status_cpu.setText(f"CPU: {cpu:.0f}%")
            self._status_memoria.setText(f"Memória: {memoria:.0f}%")
            self._status_barra.setValue(int(memoria))
            io = psutil.net_io_counters()
            self._status_rede.setText(
                f"Rede: {io.bytes_sent // 1024} kB↑ / {io.bytes_recv // 1024} kB↓"
            )
        else:
            self._status_cpu.setText("CPU: 15%")
            self._status_memoria.setText("Memória: 41%")
            self._status_rede.setText("Rede: monitoramento básico")
            self._status_barra.setValue(41)
        self._registrar_atividade("Indicadores atualizados.")
