"""Widget de automação de grupos com agendamento e monitoramento."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from PyQt6.QtCore import QDateTime, QTimer, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass
class AutomationTask:
    """Representa uma tarefa de automação agendada."""

    titulo: str
    grupo: str
    agendamento: datetime
    delay_min: int
    delay_max: int
    status: str = "Agendado"
    progresso: int = 0
    logs: List[str] = field(default_factory=list)


class GroupAutomationWidget(QWidget):
    """Centraliza o fluxo de automação de grupos com monitoramento em tempo real."""

    tasks_changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._tasks: List[AutomationTask] = []
        self._paused = False

        self._scheduler_timer = QTimer(self)
        self._scheduler_timer.setInterval(1000)
        self._scheduler_timer.timeout.connect(self._verificar_tarefas)
        self._scheduler_timer.start()

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        layout.addWidget(self._criar_cabecalho())
        layout.addWidget(self._criar_painel_agendamento())
        layout.addWidget(self._criar_tabela_tarefas())
        layout.addWidget(self._criar_monitor())
        layout.addStretch()

    def _criar_cabecalho(self) -> QWidget:
        cabecalho = QWidget()
        cabecalho_layout = QHBoxLayout(cabecalho)
        cabecalho_layout.setContentsMargins(0, 0, 0, 0)

        titulo = QLabel("Automação de Grupos")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")

        self._botao_pausar = QPushButton("Pausar operações")
        self._botao_pausar.setCheckable(True)
        self._botao_pausar.toggled.connect(self._alternar_pausa)

        cabecalho_layout.addWidget(titulo)
        cabecalho_layout.addStretch()
        cabecalho_layout.addWidget(self._botao_pausar)

        return cabecalho

    def _criar_painel_agendamento(self) -> QWidget:
        painel = QGroupBox("Agendador de tarefas")
        painel_layout = QHBoxLayout(painel)
        painel_layout.setSpacing(16)

        formulario = QFormLayout()
        formulario.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._input_titulo = QLineEdit()
        self._input_titulo.setPlaceholderText("Ex: Monitorar novos membros")
        formulario.addRow("Nome da tarefa", self._input_titulo)

        self._input_grupo = QComboBox()
        self._input_grupo.setEditable(True)
        self._input_grupo.setPlaceholderText("Informe ou selecione o grupo")
        formulario.addRow("Grupo alvo", self._input_grupo)

        self._input_data = QDateTimeEdit()
        self._input_data.setDisplayFormat("dd/MM/yyyy HH:mm")
        self._input_data.setDateTime(QDateTime.currentDateTime().addSecs(600))
        formulario.addRow("Execução", self._input_data)

        self._input_delay_min = QSpinBox()
        self._input_delay_min.setRange(0, 3600)
        self._input_delay_min.setSuffix(" s")
        self._input_delay_min.setValue(10)
        self._input_delay_min.valueChanged.connect(self._ajustar_delay_minimo)
        formulario.addRow("Delay mínimo", self._input_delay_min)

        self._input_delay_max = QSpinBox()
        self._input_delay_max.setRange(0, 3600)
        self._input_delay_max.setSuffix(" s")
        self._input_delay_max.setValue(30)
        self._input_delay_max.valueChanged.connect(self._ajustar_delay_maximo)
        formulario.addRow("Delay máximo", self._input_delay_max)

        painel_layout.addLayout(formulario, stretch=2)

        controles = QVBoxLayout()
        controles.setSpacing(12)

        self._slider_delay = QSlider(Qt.Orientation.Horizontal)
        self._slider_delay.setRange(0, 120)
        self._slider_delay.setValue(15)
        self._slider_delay.valueChanged.connect(self._sincronizar_slider)

        controles.addWidget(QLabel("Ajuste visual do intervalo"))
        controles.addWidget(self._slider_delay)

        self._botao_agendar = QPushButton("Agendar tarefa")
        self._botao_agendar.clicked.connect(self._agendar_tarefa)
        controles.addWidget(self._botao_agendar)
        controles.addStretch()

        painel_layout.addLayout(controles, stretch=1)
        return painel

    def _criar_tabela_tarefas(self) -> QWidget:
        self._tabela = QTableWidget(0, 5)
        self._tabela.setHorizontalHeaderLabels(
            ["Tarefa", "Grupo", "Execução", "Status", "Delay"]
        )
        self._tabela.horizontalHeader().setStretchLastSection(True)
        self._tabela.verticalHeader().setVisible(False)
        self._tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return self._tabela

    def _criar_monitor(self) -> QWidget:
        monitor = QGroupBox("Monitor em tempo real")
        layout = QVBoxLayout(monitor)
        layout.setSpacing(12)

        self._lista_eventos = QListWidget()
        layout.addWidget(self._lista_eventos)

        rodape = QHBoxLayout()
        rodape.addWidget(QLabel("Alertas sonoros"))

        self._check_alerta = QCheckBox("Notificar quando concluir")
        self._check_alerta.setChecked(True)
        rodape.addWidget(self._check_alerta)
        rodape.addStretch()

        botao_limpar = QPushButton("Limpar histórico")
        botao_limpar.clicked.connect(self._lista_eventos.clear)
        rodape.addWidget(botao_limpar)

        layout.addLayout(rodape)
        return monitor

    def _sincronizar_slider(self, valor: int) -> None:
        self._input_delay_max.setValue(self._input_delay_min.value() + valor)

    def _ajustar_delay_minimo(self, valor: int) -> None:
        if self._input_delay_max.value() < valor:
            self._input_delay_max.setValue(valor)
        self._slider_delay.setValue(self._input_delay_max.value() - valor)

    def _ajustar_delay_maximo(self, valor: int) -> None:
        if valor < self._input_delay_min.value():
            self._input_delay_min.setValue(valor)
        self._slider_delay.setValue(valor - self._input_delay_min.value())

    def _agendar_tarefa(self) -> None:
        titulo = self._input_titulo.text().strip()
        grupo = self._input_grupo.currentText().strip()
        if not titulo or not grupo:
            self._registrar_evento("Preencha o nome da tarefa e o grupo alvo para agendar.")
            return

        agendamento = self._input_data.dateTime().toPyDateTime()
        delay_min = min(self._input_delay_min.value(), self._input_delay_max.value())
        delay_max = max(self._input_delay_min.value(), self._input_delay_max.value())

        tarefa = AutomationTask(
            titulo=titulo,
            grupo=grupo,
            agendamento=agendamento,
            delay_min=delay_min,
            delay_max=delay_max,
        )
        tarefa.logs.append(
            f"Tarefa cadastrada para {agendamento.strftime('%d/%m/%Y %H:%M')}"
        )
        self._tasks.append(tarefa)
        self._input_titulo.clear()
        self._registrar_evento(
            f"Tarefa '{titulo}' agendada para o grupo {grupo} às "
            f"{agendamento.strftime('%H:%M')}"
        )
        if grupo and grupo not in [self._input_grupo.itemText(i) for i in range(self._input_grupo.count())]:
            self._input_grupo.addItem(grupo)
        self._atualizar_tabela()
        self.tasks_changed.emit()

    def _atualizar_tabela(self) -> None:
        self._tabela.setRowCount(len(self._tasks))
        for linha, tarefa in enumerate(self._tasks):
            self._tabela.setItem(linha, 0, QTableWidgetItem(tarefa.titulo))
            self._tabela.setItem(linha, 1, QTableWidgetItem(tarefa.grupo))
            self._tabela.setItem(
                linha,
                2,
                QTableWidgetItem(tarefa.agendamento.strftime("%d/%m/%Y %H:%M")),
            )
            self._tabela.setItem(linha, 3, QTableWidgetItem(tarefa.status))
            self._tabela.setItem(
                linha,
                4,
                QTableWidgetItem(f"{tarefa.delay_min}-{tarefa.delay_max}s"),
            )

    def _verificar_tarefas(self) -> None:
        if self._paused:
            return

        agora = datetime.now()
        houve_alteracao = False
        for tarefa in self._tasks:
            if tarefa.status == "Agendado" and tarefa.agendamento <= agora:
                tarefa.status = "Em andamento"
                tarefa.logs.append("Execução iniciada")
                self._registrar_evento(
                    f"Iniciando '{tarefa.titulo}' no grupo {tarefa.grupo}."
                )
                houve_alteracao = True
            elif tarefa.status == "Em andamento":
                tarefa.progresso += max(5, int((tarefa.delay_max or 1) / 2))
                if tarefa.progresso >= 100:
                    tarefa.status = "Concluído"
                    tarefa.logs.append("Fluxo concluído com sucesso")
                    self._registrar_evento(
                        f"Tarefa '{tarefa.titulo}' concluída no grupo {tarefa.grupo}."
                    )
                    if self._check_alerta.isChecked():
                        QApplication.beep()
                    houve_alteracao = True
                else:
                    restante = max(0, 100 - tarefa.progresso)
                    tarefa.logs.append(
                        f"Progresso atualizado: {tarefa.progresso}% (restante {restante}%)"
                    )
        self._atualizar_tabela()
        if houve_alteracao:
            self.tasks_changed.emit()

    def _registrar_evento(self, mensagem: str) -> None:
        item = QListWidgetItem(datetime.now().strftime("%H:%M:%S") + " • " + mensagem)
        self._lista_eventos.insertItem(0, item)

    def _alternar_pausa(self, ativo: bool) -> None:
        self._paused = ativo
        if ativo:
            self._botao_pausar.setText("Retomar operações")
            self._registrar_evento("Fila de automação pausada.")
        else:
            self._botao_pausar.setText("Pausar operações")
            self._registrar_evento("Fila retomada e monitorando novamente.")

    def obter_tarefas(self) -> List[AutomationTask]:
        """Retorna uma cópia das tarefas agendadas para uso externo."""

        return list(self._tasks)
