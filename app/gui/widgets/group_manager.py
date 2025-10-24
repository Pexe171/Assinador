"""Widget para organização e extração de dados de grupos."""

from __future__ import annotations

from random import randint
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
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class GroupManagerWidget(QWidget):
    """Permite gerenciar grupos e executar extrações guiadas."""

    def __init__(self) -> None:
        super().__init__()
        self._dados_preview: List[tuple[str, str, str]] = []
        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        layout.addWidget(self._criar_sidebar(), stretch=1)
        layout.addWidget(self._criar_area_principal(), stretch=3)

    def _criar_sidebar(self) -> QWidget:
        painel = QWidget()
        painel_layout = QVBoxLayout(painel)
        painel_layout.setSpacing(12)

        titulo = QLabel("Gerenciar Grupos")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        painel_layout.addWidget(titulo)

        descricao = QLabel(
            "Selecione múltiplos grupos para estruturar listas de extração."
        )
        descricao.setWordWrap(True)
        painel_layout.addWidget(descricao)

        self._lista_grupos = QListWidget()
        self._lista_grupos.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for indice in range(1, 11):
            item = QListWidgetItem(f"Grupo estratégico {indice}")
            self._lista_grupos.addItem(item)
        painel_layout.addWidget(self._lista_grupos, stretch=1)

        self._botao_iniciar = QPushButton("Iniciar extração assistida")
        self._botao_iniciar.clicked.connect(self._iniciar_wizard)
        painel_layout.addWidget(self._botao_iniciar)

        painel_layout.addStretch()
        return painel

    def _criar_area_principal(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        self._wizard = QStackedWidget()
        self._wizard.addWidget(self._criar_passo_validacao())
        self._wizard.addWidget(self._criar_passo_preview())
        self._wizard.addWidget(self._criar_passo_conclusao())
        layout.addWidget(self._wizard, stretch=1)

        return container

    def _criar_passo_validacao(self) -> QWidget:
        passo = QGroupBox("Passo 1 • Seleção e filtros")
        layout = QFormLayout(passo)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._input_filtro = QLineEdit()
        self._input_filtro.setPlaceholderText("Filtrar por palavra-chave em tempo real")
        self._input_filtro.textChanged.connect(self._filtrar_preview)
        layout.addRow("Filtro", self._input_filtro)

        info = QLabel(
            "Escolha os grupos na barra lateral e ajuste o filtro para refinar a extração."
        )
        info.setWordWrap(True)
        layout.addRow("Orientações", info)
        return passo

    def _criar_passo_preview(self) -> QWidget:
        passo = QGroupBox("Passo 2 • Pré-visualização")
        layout = QVBoxLayout(passo)
        layout.setSpacing(12)

        self._tabela = QTableWidget(0, 3)
        self._tabela.setHorizontalHeaderLabels(["Usuário", "Cargo", "Origem"])
        self._tabela.horizontalHeader().setStretchLastSection(True)
        self._tabela.verticalHeader().setVisible(False)
        layout.addWidget(self._tabela)

        self._progresso = QProgressBar()
        self._progresso.setValue(0)
        layout.addWidget(self._progresso)

        botoes = QHBoxLayout()
        botoes.addStretch()
        botao_anterior = QPushButton("Voltar")
        botao_anterior.clicked.connect(lambda: self._wizard.setCurrentIndex(0))
        botoes.addWidget(botao_anterior)

        botao_continuar = QPushButton("Exportar e concluir")
        botao_continuar.clicked.connect(lambda: self._wizard.setCurrentIndex(2))
        botoes.addWidget(botao_continuar)
        layout.addLayout(botoes)
        return passo

    def _criar_passo_conclusao(self) -> QWidget:
        passo = QGroupBox("Passo 3 • Finalização")
        layout = QVBoxLayout(passo)
        layout.setSpacing(12)

        mensagem = QLabel(
            "Tudo pronto! Baixe o resultado ou dispare ações de onboarding nos grupos."
        )
        mensagem.setWordWrap(True)
        layout.addWidget(mensagem)

        botao_reiniciar = QPushButton("Configurar nova extração")
        botao_reiniciar.clicked.connect(lambda: self._wizard.setCurrentIndex(0))
        layout.addWidget(botao_reiniciar)

        layout.addStretch()
        return passo

    def _iniciar_wizard(self) -> None:
        selecionados = [item.text() for item in self._lista_grupos.selectedItems()]
        if not selecionados:
            return
        self._gerar_preview(selecionados)
        self._wizard.setCurrentIndex(1)

    def _gerar_preview(self, grupos: List[str]) -> None:
        self._dados_preview = [
            (f"@lead{indice}", "Decisor", grupos[indice % len(grupos)])
            for indice in range(1, 31)
        ]
        self._popular_tabela(self._dados_preview)
        self._progresso.setValue(randint(45, 95))

    def _popular_tabela(self, dados: List[tuple[str, str, str]]) -> None:
        self._tabela.setRowCount(len(dados))
        for linha, (usuario, cargo, origem) in enumerate(dados):
            self._tabela.setItem(linha, 0, QTableWidgetItem(usuario))
            self._tabela.setItem(linha, 1, QTableWidgetItem(cargo))
            self._tabela.setItem(linha, 2, QTableWidgetItem(origem))

    def _filtrar_preview(self, termo: str) -> None:
        termo_normalizado = termo.lower().strip()
        if not termo_normalizado:
            self._popular_tabela(self._dados_preview)
            return
        filtrados = [
            item
            for item in self._dados_preview
            if termo_normalizado in " ".join(item).lower()
        ]
        self._popular_tabela(filtrados)
        self._progresso.setValue(min(100, 50 + len(filtrados)))
