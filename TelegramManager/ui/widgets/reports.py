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
    AutomationSummary,
    DailyAutomationActivity,
    ReportService,
)
from TelegramManager.utils.helpers import formatar_data_humana


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
        """Calcula a taxa de mensagens entregues com sucesso."""

        if self.envios == 0:
            return 0.0
        return self.entregues / self.envios

    @property
    def taxa_conversao(self) -> float:
        """Percentual de conversões sobre o total entregue."""

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
        "Trimestre": PeriodMetrics(
            novos_leads=3278,
            taxa_conversao=0.19,
            receita=211430.0,
            tempo_medio_resposta=4.5,
        ),
    }

    _PERFORMANCE_CONTAS: Tuple[AccountPerformance, ...] = (
        AccountPerformance("Equipe Suporte", 1880, 1764, 82, 486),
        AccountPerformance("Equipe Growth", 1440, 1372, 54, 396),
        AccountPerformance("Onboarding Beta", 860, 792, 41, 218),
        AccountPerformance("Parcerias", 620, 584, 22, 156),
    )

    def __init__(self, report_service: ReportService | None = None) -> None:
        super().__init__()
        self._periodo_atual = "Últimos 7 dias"
        self._report_service = report_service
        self._resumo_labels: Dict[str, QLabel] = {}
        self._resumo_timer: QTimer | None = None
        self._serie_crescimento: QLineSeries | None = None
        self._montar_layout()
        self._iniciar_timer_resumo()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        titulo = QLabel("Relatórios e Insights")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        descricao = QLabel(
            "Visualize métricas chave das suas automações e exporte relatórios completos com poucos cliques."
        )
        descricao.setWordWrap(True)
        layout.addWidget(descricao)

        layout.addWidget(self._criar_painel_resumo_automacao())
        layout.addWidget(self._criar_painel_resumo())

        abas = QTabWidget()
        abas.addTab(self._criar_aba_crescimento(), "📈 Crescimento")
        abas.addTab(self._criar_aba_contas(), "👥 Contas")
        abas.addTab(self._criar_aba_atividade(), "🔥 Atividade")
        layout.addWidget(abas, stretch=1)

        layout.addWidget(self._criar_painel_exportacao())
        layout.addStretch()

    # ------------------------------------------------------------------
    # Painéis principais
    # ------------------------------------------------------------------
    def _criar_painel_resumo_automacao(self) -> QWidget:
        painel = QGroupBox("Sistema de automação")
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
            self._resumo_labels[chave] = valor

        self._atualizar_resumo_automacao()
        return painel

    def _criar_painel_resumo(self) -> QWidget:
        painel = QGroupBox("Métricas consolidadas por período")
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

    def _criar_aba_crescimento(self) -> QWidget:
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(16)

        layout.addWidget(self._criar_grafico_crescimento(), stretch=2)
        layout.addWidget(self._criar_grafico_taxas_sucesso(), stretch=1)
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
        tabela.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        for linha, conta in enumerate(self._PERFORMANCE_CONTAS):
            tabela.setItem(linha, 0, QTableWidgetItem(conta.nome))
            tabela.setItem(linha, 1, QTableWidgetItem(self._formatar_inteiro(conta.envios)))
            tabela.setItem(
                linha,
                2,
                QTableWidgetItem(self._formatar_inteiro(conta.entregues)),
            )
            tabela.setItem(linha, 3, QTableWidgetItem(self._formatar_inteiro(conta.erros)))
            tabela.setItem(
                linha,
                4,
                QTableWidgetItem(self._formatar_inteiro(conta.conversoes)),
            )

        layout.addWidget(tabela, stretch=2)
        layout.addWidget(self._criar_cards_taxa_sucesso())
        return aba

    def _criar_aba_atividade(self) -> QWidget:
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setSpacing(16)

        explicacao = QLabel(
            "O mapa de calor destaca os períodos com maior volume de ações automatizadas."
        )
        explicacao.setWordWrap(True)
        layout.addWidget(explicacao)

        layout.addWidget(self._criar_heatmap_atividade(), stretch=1)
        return aba

    def _criar_painel_exportacao(self) -> QWidget:
        painel = QGroupBox("Exportações e compartilhamento")
        layout = QGridLayout(painel)
        layout.setSpacing(12)

        botoes = [
            ("Gerar relatório PDF", "Ideal para apresentações executivas."),
            ("Exportar dashboard (PNG)", "Compartilhe rapidamente a visão geral."),
            ("Exportar dados CSV", "Importe em planilhas e CRMs."),
            ("Exportar dados JSON", "Integrações com pipelines personalizados."),
            ("Exportar dados Excel", "Modelos avançados de análise."),
            ("Salvar como template", "Reutilize configurações em novos projetos."),
        ]

        for indice, (titulo, dica) in enumerate(botoes):
            botao = QPushButton(titulo)
            botao.setToolTip(dica)
            botao.setCursor(Qt.CursorShape.PointingHandCursor)
            botao.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout.addWidget(botao, indice // 3, indice % 3)

        return painel

    # ------------------------------------------------------------------
    # Builders auxiliares
    # ------------------------------------------------------------------
    def _criar_grafico_crescimento(self) -> QChartView:
        """Cria gráfico de linha com execuções concluídas por dia."""

        serie = QLineSeries()
        serie.setName("Execuções concluídas")
        self._serie_crescimento = serie

        dados = self._obter_atividade_diaria()
        if not dados:
            hoje = date.today()
            dados = [
                DailyAutomationActivity(
                    dia=datetime.combine(hoje - timedelta(days=i), datetime.min.time()),
                    concluidas=0,
                )
                for i in reversed(range(6, -1, -1))
            ]

        for atividade in dados:
            qt_datetime = QDateTime(
                atividade.dia.year, atividade.dia.month, atividade.dia.day, 0, 0
            )
            serie.append(qt_datetime.toMSecsSinceEpoch(), atividade.concluidas)

        chart = QChart()
        chart.addSeries(serie)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setTitle("Volume diário de execuções")
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
        chart_view.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
        chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return chart_view

    def _criar_grafico_taxas_sucesso(self) -> QChartView:
        """Gráfico de barras com taxas de sucesso/erro por conta."""

        series = QBarSeries()
        series.setLabelsVisible(True)

        categorias: List[str] = []
        sucessos = QBarSet("Sucesso")
        falhas = QBarSet("Falhas")

        for conta in self._PERFORMANCE_CONTAS:
            categorias.append(conta.nome)
            sucessos.append(round(conta.taxa_sucesso * 100, 1))
            falhas.append(round(100 - (conta.taxa_sucesso * 100), 1))

        series.append(sucessos)
        series.append(falhas)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Taxa de sucesso vs. falhas por conta")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        eixo_x = QBarCategoryAxis()
        eixo_x.append(categorias)
        chart.addAxis(eixo_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(eixo_x)

        eixo_y = QValueAxis()
        eixo_y.setRange(0, 100)
        eixo_y.setLabelFormat("%.0f%%")
        eixo_y.setTitleText("Taxa")
        chart.addAxis(eixo_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(eixo_y)

        chart_view = QChartView(chart)
        chart_view.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
        chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return chart_view

    def _criar_cards_taxa_sucesso(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(12)

        for conta in self._PERFORMANCE_CONTAS:
            card = self._criar_card_performance(conta)
            layout.addWidget(card)

        layout.addStretch()
        return container

    def _criar_card_performance(self, conta: AccountPerformance) -> QWidget:
        card = QGroupBox(conta.nome)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        progresso = QProgressBar()
        progresso.setRange(0, 100)
        progresso.setValue(int(conta.taxa_sucesso * 100))
        progresso.setFormat("%v%")
        progresso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progresso.setToolTip(
            f"{conta.taxa_sucesso * 100:.1f}% de entregas bem-sucedidas"
        )

        conversao = QLabel(
            f"Conversão: {conta.taxa_conversao * 100:.1f}% ({conta.conversoes} vendas)"
        )
        conversao.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(progresso)
        card_layout.addWidget(conversao)
        return card

    def _criar_heatmap_atividade(self) -> QWidget:
        dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        horarios = ["08h", "10h", "12h", "14h", "16h", "18h", "20h"]

        tabela = QTableWidget(len(horarios), len(dias_semana))
        tabela.setHorizontalHeaderLabels(dias_semana)
        tabela.setVerticalHeaderLabels(horarios)
        tabela.verticalHeader().setVisible(True)
        tabela.horizontalHeader().setStretchLastSection(True)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabela.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        atividade = self._gerar_matriz_atividade(len(horarios), len(dias_semana))
        maior_valor = max(max(linha) for linha in atividade)

        for linha, valores in enumerate(atividade):
            for coluna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                cor = self._calcular_cor_heatmap(valor, maior_valor)
                item.setBackground(cor)
                tabela.setItem(linha, coluna, item)

        return tabela

    # ------------------------------------------------------------------
    # Helpers de dados
    # ------------------------------------------------------------------
    def _iniciar_timer_resumo(self) -> None:
        if not self._report_service:
            return
        self._resumo_timer = QTimer(self)
        self._resumo_timer.setInterval(10_000)
        self._resumo_timer.timeout.connect(self._atualizar_resumo_automacao)
        self._resumo_timer.start()

    def _atualizar_resumo_automacao(self) -> None:
        if not self._report_service:
            return
        resumo: AutomationSummary = self._report_service.gerar_resumo_automacao()
        self._definir_valor_resumo("total", self._formatar_inteiro(resumo.total))
        self._definir_valor_resumo(
            "agendadas", self._formatar_inteiro(resumo.agendadas)
        )
        self._definir_valor_resumo(
            "em_andamento", self._formatar_inteiro(resumo.em_andamento)
        )
        self._definir_valor_resumo(
            "concluidas", self._formatar_inteiro(resumo.concluidas)
        )
        self._definir_valor_resumo("falhas", self._formatar_inteiro(resumo.falhas))
        self._definir_valor_resumo(
            "progresso", f"{resumo.progresso_medio:.1f}%"
        )
        proxima = (
            formatar_data_humana(resumo.proxima_execucao)
            if resumo.proxima_execucao
            else "Sem agendamentos"
        )
        self._definir_valor_resumo("proxima_execucao", proxima)
        self._atualizar_grafico_crescimento()

    def _definir_valor_resumo(self, chave: str, texto: str) -> None:
        label = self._resumo_labels.get(chave)
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
            return
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
            if eixo_x:
                inicio = min(d.dia for d in dados)
                fim = max(d.dia for d in dados)
                eixo_x[0].setRange(
                    QDateTime(inicio.year, inicio.month, inicio.day, 0, 0),
                    QDateTime(fim.year, fim.month, fim.day, 0, 0),
                )
            if eixo_y:
                eixo_y[0].setRange(0, max(max(d.concluidas for d in dados), 1))

    def _atualizar_metricas_periodo(self, periodo: str) -> None:
        self._periodo_atual = periodo
        metricas = self._PERIODOS.get(periodo)
        if not metricas:
            return

        # Limpa widgets anteriores
        while self._metricas_container.count():
            item = self._metricas_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        pares = [
            ("Novos leads", self._formatar_inteiro(metricas.novos_leads)),
            ("Taxa de conversão", f"{metricas.taxa_conversao * 100:.1f}%"),
            ("Receita estimada", self._formatar_moeda(metricas.receita)),
            (
                "Tempo médio de resposta",
                f"{metricas.tempo_medio_resposta:.1f} min",
            ),
        ]

        for indice, (titulo, valor) in enumerate(pares):
            card = self._criar_card_metricas(titulo, valor)
            self._metricas_container.addWidget(card, indice // 2, indice % 2)

    def _criar_card_metricas(self, titulo: str, valor: str) -> QWidget:
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet("border-radius: 8px; background-color: palette(Base);")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-weight: 600; color: palette(Mid);")
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("font-size: 20px; font-weight: bold;")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        return card

    def _gerar_matriz_atividade(self, linhas: int, colunas: int) -> List[List[int]]:
        """Gera matriz de atividade fictícia com padrão de pico no meio do dia."""

        matriz: List[List[int]] = []
        for linha in range(linhas):
            base = 20 + linha * 8
            linha_valores = []
            for coluna in range(colunas):
                fator = 1 + 0.3 * (3 - abs(3 - coluna))
                linha_valores.append(int(base * fator))
            matriz.append(linha_valores)
        return matriz

    def _calcular_cor_heatmap(self, valor: int, maior_valor: int) -> QColor:
        if maior_valor <= 0:
            return QColor("#e0e0e0")

        intensidade = valor / maior_valor
        start_color = QColor(255, 244, 229)
        end_color = QColor(255, 87, 34)

        r = int(start_color.red() + (end_color.red() - start_color.red()) * intensidade)
        g = int(start_color.green() + (end_color.green() - start_color.green()) * intensidade)
        b = int(start_color.blue() + (end_color.blue() - start_color.blue()) * intensidade)

        return QColor(r, g, b)

    def _formatar_inteiro(self, valor: int) -> str:
        return f"{valor:,}".replace(",", ".")

    def _formatar_moeda(self, valor: float) -> str:
        texto = f"R$ {valor:,.2f}"
        return texto.replace(",", "X").replace(".", ",").replace("X", ".")
