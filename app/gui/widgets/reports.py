"""Widget dedicado aos relatórios de performance."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ReportsWidget(QWidget):
    """Exibe relatórios consolidados e atalhos de exportação."""

    def __init__(self) -> None:
        super().__init__()
        self._montar_layout()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        titulo = QLabel("Relatórios")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        descricao = QLabel(
            "Gere insights das automações com indicadores prontos para apresentação."
        )
        descricao.setWordWrap(True)
        layout.addWidget(descricao)

        layout.addWidget(self._criar_tabela_resumo(), stretch=1)
        layout.addWidget(self._criar_painel_exportacao())
        layout.addStretch()

    def _criar_tabela_resumo(self) -> QWidget:
        tabela = QTableWidget(0, 4)
        tabela.setHorizontalHeaderLabels(
            ["Campanha", "Envios", "Conversões", "Taxa"]
        )
        tabela.horizontalHeader().setStretchLastSection(True)
        tabela.verticalHeader().setVisible(False)

        dados = [
            ("Onboarding parceiros", "1.250", "230", "18%"),
            ("Reengajamento MQL", "980", "121", "12%"),
            ("Lançamento beta", "640", "96", "15%"),
        ]
        tabela.setRowCount(len(dados))
        for linha, (campanha, envios, conversoes, taxa) in enumerate(dados):
            tabela.setItem(linha, 0, QTableWidgetItem(campanha))
            tabela.setItem(linha, 1, QTableWidgetItem(envios))
            tabela.setItem(linha, 2, QTableWidgetItem(conversoes))
            tabela.setItem(linha, 3, QTableWidgetItem(taxa))
        return tabela

    def _criar_painel_exportacao(self) -> QWidget:
        painel = QGroupBox("Exportação e compartilhamento")
        layout = QHBoxLayout(painel)
        layout.setSpacing(12)

        layout.addWidget(QPushButton("Exportar PDF"))
        layout.addWidget(QPushButton("Enviar por e-mail"))
        layout.addWidget(QPushButton("Compartilhar no Slack"))
        layout.addStretch()
        return painel
