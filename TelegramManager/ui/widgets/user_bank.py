"""Widget para acompanhar o banco de usuários qualificados."""

from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.extraction import ExtractionService, ExtractedUserRecord


class UserBankWidget(QWidget):
    """Permite classificar e filtrar rapidamente usuários capturados."""

    def __init__(self, extraction_service: ExtractionService) -> None:
        super().__init__()
        self._service = extraction_service
        self._dataset: List[ExtractedUserRecord] = []
        self._montar_layout()
        self._carregar_dados()

    def _montar_layout(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        layout.addWidget(self._criar_segmentos(), stretch=1)
        layout.addWidget(self._criar_painel_principal(), stretch=3)

    def _criar_segmentos(self) -> QWidget:
        painel = QWidget()
        painel_layout = QVBoxLayout(painel)
        painel_layout.setSpacing(12)

        titulo = QLabel("Segmentos e campanhas")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold;")
        painel_layout.addWidget(titulo)

        self._lista_segmentos = QListWidget()
        self._lista_segmentos.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        for etiqueta in sorted({"Lançamento", "Clientes VIP", "Nutrição", "Reengajamento"}):
            self._lista_segmentos.addItem(QListWidgetItem(etiqueta))
        self._lista_segmentos.currentItemChanged.connect(lambda *_: self._filtrar())
        painel_layout.addWidget(self._lista_segmentos)

        painel_layout.addStretch()
        return painel

    def _criar_painel_principal(self) -> QWidget:
        painel = QWidget()
        layout = QVBoxLayout(painel)
        layout.setSpacing(14)

        cabecalho = QLabel("Banco de usuários")
        cabecalho.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(cabecalho)

        filtros = QGroupBox("Filtros inteligentes")
        form = QFormLayout(filtros)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._input_busca = QLineEdit()
        self._input_busca.setPlaceholderText("Busque por @usuário ou palavra-chave")
        self._input_busca.textChanged.connect(lambda *_: self._filtrar())
        form.addRow("Pesquisa", self._input_busca)

        layout.addWidget(filtros)

        self._tabela = QTableWidget(0, 3)
        self._tabela.setHorizontalHeaderLabels(["Usuário", "Segmento", "Status"])
        self._tabela.horizontalHeader().setStretchLastSection(True)
        self._tabela.verticalHeader().setVisible(False)
        layout.addWidget(self._tabela, stretch=1)

        botoes = QHBoxLayout()
        botoes.addStretch()
        botoes.addWidget(QPushButton("Exportar CSV"))
        botoes.addWidget(QPushButton("Enviar Broadcast"))
        layout.addLayout(botoes)

        return painel

    def _carregar_dados(self) -> None:
        self._dataset = self._service.list_recent_users()
        if not self._dataset:
            self._lista_segmentos.clear()
            self._tabela.setRowCount(0)
            return
        segmentos = sorted({item.segment for item in self._dataset})
        self._lista_segmentos.clear()
        for segmento in segmentos:
            self._lista_segmentos.addItem(QListWidgetItem(segmento))
        if self._lista_segmentos.count() > 0:
            self._lista_segmentos.setCurrentRow(0)
        self._preencher_tabela(self._dataset)
        self._filtrar()

    def _preencher_tabela(self, dados: List[ExtractedUserRecord]) -> None:
        self._tabela.setRowCount(len(dados))
        for linha, item in enumerate(dados):
            self._tabela.setItem(linha, 0, QTableWidgetItem(item.username))
            self._tabela.setItem(linha, 1, QTableWidgetItem(item.segment))
            self._tabela.setItem(linha, 2, QTableWidgetItem(item.status))

    def _filtrar(self) -> None:
        termo = self._input_busca.text().lower().strip()
        item_segmento = self._lista_segmentos.currentItem()
        segmento = item_segmento.text() if item_segmento else None
        dados = [
            item
            for item in self._dataset
            if (not segmento or item.segment == segmento)
            and (not termo or termo in " ".join(
                [item.username.lower(), item.role.lower(), item.origin_group.lower(), item.segment.lower(), item.status.lower()]
            ))
        ]
        self._preencher_tabela(dados)

    def recarregar(self) -> None:
        """Reprocessa os dados de forma idempotente para refletir novas extrações."""

        self._carregar_dados()
