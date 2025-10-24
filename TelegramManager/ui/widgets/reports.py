# Caminho: TelegramManager/ui/widgets/reports.py
"""Widget dedicado aos relatórios de performance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

from PyQt6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QDateTimeAxis,
    QLineSeries,
    QValueAxis,
)
from PyQt6.QtCore import Qt, QDateTime, QTimer
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.reports import (
    AdditionSummary,
    AutomationSummary,
    DailyAutomationActivity,
    ReportService,
)
from TelegramManager.utils.helpers import formatar_data_humana


# Dados fictícios mantidos para métricas financeiras (não no escopo atual)
@dataclass(frozen=True)
class PeriodMetrics:
    """Representa métricas consolidadas por período."""

    novos_leads: int
    taxa_conversao: float
    receita: float
    tempo_medio_resposta: float


@dataclass(frozen=True)
class AccountPerformance:
    """Desempenho agregado de uma conta monitorada."""

    nome: str
    envios: int
    entregues: int
    erros: int
    conversoes: int

    @property
    def taxa_sucesso(self) -> float:
        if self.envios == 0:
            return 0.0
        return self.entregues / self.envios

    @property
    def taxa_conversao(self) -> float:
        if self.entregues == 0:
            return 0.0
        return self.conversoes / self.entregues


class ReportsWidget(QWidget):
    """Exibe relatórios consolidados com gráficos, tabelas e exportações."""

    _PERIODOS: Dict[str, PeriodMetrics] = {
        "Últimos 7 dias": PeriodMetrics(
            novos_leads=312,
            taxa_conversao=0.17,
            receita=18450.0,
            tempo_medio_resposta=3.6,
        ),
        "Últimos 30 dias": PeriodMetrics(
            novos_leads=1194,
            taxa_conversao=0.21,
            receita=72680.0,
            tempo_medio_resposta=4.2,
        ),
    }

    _PERFORMANCE_CONTAS: Tuple[AccountPerformance, ...] = (
        AccountPerformance("Equipe Suporte", 1880, 1764, 82, 486),
        AccountPerformance("Equipe Growth", 1440, 1372, 54, 396),
    )

    def __init__(self, report_service: ReportService | None = None) -> None:
        super().__init__()
        self._periodo_atual = "Últimos 7 dias"
        self._report_service = report_service
        self._resumo_automacao_labels: Dict[str, QLabel] = {}
        self._resumo_adicao_labels: Dict[str, QLabel] = {}
        self._serie_crescimento: QLineSeries | None = None

        self._montar_layout()
        self.atualizar_relatorios()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        titulo = QLabel("Relatórios e Insights")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        descricao = QLabel(
            "Visualize métricas chave das suas automações e exporte relatórios completos."
        )
        descricao.setWordWrap(True)
        layout.addWidget(descricao)

        # Painéis de Resumo Lado a Lado
        resumos_layout = QHBoxLayout()
        resumos_layout.addWidget(self._criar_painel_resumo_automacao())
        resumos_layout.addWidget(self._criar_painel_resumo_adicao())
        layout.addLayout(resumos_layout)

        layout.addWidget(self._criar_painel_resumo_financeiro())

        abas = QTabWidget()
        abas.addTab(self._criar_aba_crescimento(), "📈 Crescimento (Automação)")
        abas.addTab(self._criar_aba_contas(), "👥 Contas (Financeiro)")
        abas.addTab(self._criar_aba_atividade(), "🔥 Atividade (Heatmap)")
        layout.addWidget(abas, stretch=1)

        layout.addWidget(self._criar_painel_exportacao())
        layout.addStretch()

    # ------------------------------------------------------------------
    # Painéis principais
    # ------------------------------------------------------------------
    def _criar_painel_resumo_automacao(self) -> QWidget:
        painel = QGroupBox("Resumo: Automação (Agendador)")
        layout = QGridLayout(painel)
        layout.setSpacing(12)

        indicadores = [
            ("Tarefas registradas", "total"),
            ("Agendadas", "agendadas"),
            ("Em andamento", "em_andamento"),
            ("Concluídas", "concluidas"),
            ("Falhas", "falhas"),
            ("Progresso médio", "progresso"),
            ("Próxima execução", "proxima_execucao"),
        ]

        for linha, (titulo, chave) in enumerate(indicadores):
            label_titulo = QLabel(titulo)
            label_titulo.setStyleSheet("color: #475467;")
            valor = QLabel("—")
            valor.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(label_titulo, linha, 0)
            layout.addWidget(valor, linha, 1)
            self._resumo_automacao_labels[chave] = valor

        return painel

    def _criar_painel_resumo_adicao(self) -> QWidget:
        painel = QGroupBox("Resumo: Adição de Usuários")
        layout = QGridLayout(painel)
        layout.setSpacing(12)

        indicadores = [
            ("Total de Operações", "total_jobs"),
            ("Usuários Adicionados", "total_adicionados"),
            ("Total de Falhas", "total_falhas"),
            ("Taxa de Sucesso Geral", "taxa_sucesso_geral"),
        ]

        for linha, (titulo, chave) in enumerate(indicadores):
            label_titulo = QLabel(titulo)
            label_titulo.setStyleSheet("color: #475467;")
            valor = QLabel("—")
            valor.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(label_titulo, linha, 0)
            layout.addWidget(valor, linha, 1)
            self._resumo_adicao_labels[chave] = valor

        # Preenche espaço para alinhar com o outro card
        for linha_extra in range(len(indicadores), 7):
            layout.addWidget(QLabel(""), linha_extra, 0)

        return painel

    def _criar_painel_resumo_financeiro(self) -> QWidget:
        painel = QGroupBox("Métricas consolidadas (Exemplo Financeiro)")
        layout = QVBoxLayout(painel)
        layout.setSpacing(12)

        seletor = QComboBox()
        seletor.addItems(self._PERIODOS.keys())
        seletor.currentTextChanged.connect(self._atualizar_metricas_periodo)
        layout.addWidget(seletor)

        self._metricas_container = QGridLayout()
        self._metricas_container.setSpacing(16)
        layout.addLayout(self._metricas_container)

        self._atualizar_metricas_periodo(self._periodo_atual)
        seletor.setCurrentText(self._periodo_atual)
        return painel

    # ... (O resto dos métodos _criar_aba_* e helpers permanecem os mesmos) ...
    # (Omitidos por brevidade, pois não mudam)
    def _criar_aba_crescimento(self) -> QWidget:
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(16)
        layout.addWidget(self._criar_grafico_crescimento(), stretch=1)
        return aba

    def _criar_aba_contas(self) -> QWidget:
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(16)
        tabela = QTableWidget(len(self._PERFORMANCE_CONTAS), 5)
        tabela.setHorizontalHeaderLabels(
            ["Conta", "Envios", "Entregues", "Erros", "Conversões"]
        )
        tabela.verticalHeader().setVisible(False)
        tabela.horizontalHeader().setStretchLastSection(True)
        for linha, conta in enumerate(self._PERFORMANCE_CONTAS):
            tabela.setItem(linha, 0, QTableWidgetItem(conta.nome))
            tabela.setItem(linha, 1, QTableWidgetItem(self._formatar_inteiro(conta.envios)))
            tabela.setItem(linha, 2, QTableWidgetItem(self._formatar_inteiro(conta.entregues)))
            tabela.setItem(linha, 3, QTableWidgetItem(self._formatar_inteiro(conta.erros)))
            tabela.setItem(linha, 4, QTableWidgetItem(self._formatar_inteiro(conta.conversoes)))
        layout.addWidget(tabela, stretch=1)
        return aba

    def _criar_aba_atividade(self) -> QWidget:
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(16)
        layout.addWidget(QLabel("Heatmap (Exemplo Fictício)"), stretch=1)
        return aba

    def _criar_painel_exportacao(self) -> QWidget:
        painel = QGroupBox("Exportações")
        layout = QHBoxLayout(painel)
        layout.setSpacing(12)
        layout.addWidget(QPushButton("Gerar relatório PDF"))
        layout.addWidget(QPushButton("Exportar dados CSV"))
        layout.addStretch()
        return painel

    # ------------------------------------------------------------------
    # Builders auxiliares (Gráficos, Cards)
    # ------------------------------------------------------------------
    def _criar_grafico_crescimento(self) -> QChartView:
        """Cria gráfico de linha com execuções concluídas por dia."""
        serie = QLineSeries()
        serie.setName("Execuções concluídas")
        self._serie_crescimento = serie

        chart = QChart()
        chart.addSeries(serie)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTitle("Volume diário de execuções (Automação)")
        chart.legend().setVisible(True)

        eixo_x = QDateTimeAxis()
        eixo_x.setFormat("dd/MM")
        eixo_x.setTitleText("Dia")
        chart.addAxis(eixo_x, Qt.AlignmentFlag.AlignBottom)
        serie.attachAxis(eixo_x)

        eixo_y = QValueAxis()
        eixo_y.setLabelFormat("%.0f")
        eixo_y.setTitleText("Execuções")
        chart.addAxis(eixo_y, Qt.AlignmentFlag.AlignLeft)
        serie.attachAxis(eixo_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view

    # ------------------------------------------------------------------
    # Helpers de dados
    # ------------------------------------------------------------------
    def atualizar_relatorios(self) -> None:
        """Atualiza todos os painéis de resumo com dados reais."""
        if not self._report_service:
            return
        self._atualizar_resumo_automacao()
        self._atualizar_resumo_adicao()
        self._atualizar_grafico_crescimento()

    def _atualizar_resumo_automacao(self) -> None:
        if not self._report_service:
            return
        resumo: AutomationSummary = self._report_service.gerar_resumo_automacao()
        self._definir_valor_resumo(
            self._resumo_automacao_labels, "total", self._formatar_inteiro(resumo.total)
        )
        self._definir_valor_resumo(
            self._resumo_automacao_labels,
            "agendadas",
            self._formatar_inteiro(resumo.agendadas),
        )
        self._definir_valor_resumo(
            self._resumo_automacao_labels,
            "em_andamento",
            self._formatar_inteiro(resumo.em_andamento),
        )
        self._definir_valor_resumo(
            self._resumo_automacao_labels,
            "concluidas",
            self._formatar_inteiro(resumo.concluidas),
        )
        self._definir_valor_resumo(
            self._resumo_automacao_labels,
            "falhas",
            self._formatar_inteiro(resumo.falhas),
        )
        self._definir_valor_resumo(
            self._resumo_automacao_labels, "progresso", f"{resumo.progresso_medio:.1f}%"
        )
        proxima = (
            formatar_data_humana(resumo.proxima_execucao)
            if resumo.proxima_execucao
            else "N/A"
        )
        self._definir_valor_resumo(
            self._resumo_automacao_labels, "proxima_execucao", proxima
        )

    def _atualizar_resumo_adicao(self) -> None:
        if not self._report_service:
            return
        resumo: AdditionSummary = self._report_service.gerar_resumo_adicoes()
        self._definir_valor_resumo(
            self._resumo_adicao_labels,
            "total_jobs",
            self._formatar_inteiro(resumo.total_jobs),
        )
        self._definir_valor_resumo(
            self._resumo_adicao_labels,
            "total_adicionados",
            self._formatar_inteiro(resumo.total_adicionados),
        )
        self._definir_valor_resumo(
            self._resumo_adicao_labels,
            "total_falhas",
            self._formatar_inteiro(resumo.total_falhas),
        )
        self._definir_valor_resumo(
            self._resumo_adicao_labels,
            "taxa_sucesso_geral",
            f"{resumo.taxa_sucesso_geral:.1f}%",
        )

    def _definir_valor_resumo(
        self, label_dict: Dict[str, QLabel], chave: str, texto: str
    ) -> None:
        label = label_dict.get(chave)
        if label:
            label.setText(texto)

    def _obter_atividade_diaria(self) -> List[DailyAutomationActivity]:
        if not self._report_service:
            return []
        return self._report_service.gerar_atividade_diaria()

    def _atualizar_grafico_crescimento(self) -> None:
        if not self._report_service or not self._serie_crescimento:
            return
        dados = self._obter_atividade_diaria()
        if not dados:
            # Adiciona dados zerados se não houver atividade
            hoje = datetime.now()
            dados = [
                DailyAutomationActivity(dia=hoje - timedelta(days=i), concluidas=0)
                for i in range(7)
            ]

        chart = self._serie_crescimento.chart()
        self._serie_crescimento.clear()
        for atividade in dados:
            qt_datetime = QDateTime(
                atividade.dia.year, atividade.dia.month, atividade.dia.day, 0, 0
            )
            self._serie_crescimento.append(
                qt_datetime.toMSecsSinceEpoch(), atividade.concluidas
            )
        if chart:
            eixo_x = chart.axes(Qt.AlignmentFlag.AlignBottom)
            eixo_y = chart.axes(Qt.AlignmentFlag.AlignLeft)
            if eixo_x and dados:
                inicio = min(d.dia for d in dados)
                fim = max(d.dia for d in dados)
                eixo_x[0].setRange(
                    QDateTime(inicio.year, inicio.month, inicio.day, 0, 0),
                    QDateTime(fim.year, fim.month, fim.day, 0, 0),
                )
            if eixo_y and dados:
                eixo_y[0].setRange(0, max(max(d.concluidas for d in dados), 5))
            elif eixo_y:
                eixo_y[0].setRange(0, 5) # Default range

    # ... (Restante dos métodos de formatação e métricas fictícias) ...
    def _atualizar_metricas_periodo(self, periodo: str) -> None:
        self._periodo_atual = periodo
        metricas = self._PERIODOS.get(periodo)
        if not metricas:
            return
        while self._metricas_container.count():
            item = self._metricas_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        pares = [
            ("Novos leads", self._formatar_inteiro(metricas.novos_leads)),
            ("Taxa de conversão", f"{metricas.taxa_conversao * 100:.1f}%"),
            ("Receita estimada", self._formatar_moeda(metricas.receita)),
            ("Tempo médio", f"{metricas.tempo_medio_resposta:.1f} min"),
        ]
        for indice, (titulo, valor) in enumerate(pares):
            card = self._criar_card_metricas(titulo, valor)
            self._metricas_container.addWidget(card, 0, indice)

    def _criar_card_metricas(self, titulo: str, valor: str) -> QWidget:
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(card)
        lbl_titulo = QLabel(titulo)
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        return card

    def _formatar_inteiro(self, valor: int) -> str:
        return f"{valor:,}".replace(",", ".")

    def _formatar_moeda(self, valor: float) -> str:
        texto = f"R$ {valor:,.2f}"
        return texto.replace(",", "X").replace(".", ",").replace("X", ".")

