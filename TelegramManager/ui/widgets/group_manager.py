# Caminho: TelegramManager/ui/widgets/group_manager.py
"""Widget para organização e extração de dados de grupos."""

from __future__ import annotations

from random import randint
from typing import Callable, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
# Correcção: Importar QtWidgets corretamente (PyQt6 em vez de PyQt6t)
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

from TelegramManager.core.extraction import ExtractionService
from TelegramManager.notifications.dispatcher import NotificationDispatcher


class GroupManagerWidget(QWidget):
    """Permite gerenciar grupos e executar extrações guiadas."""

    # Sinal emitido quando uma extração é concluída com sucesso
    extraction_finished = pyqtSignal()

    def __init__(
        self,
        extraction_service: ExtractionService,
        notifications: NotificationDispatcher,
    ) -> None:
        super().__init__()
        self._extraction_service = extraction_service
        self._notifications = notifications
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

        titulo = QLabel("Gerenciar Grupos (Extração)")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        painel_layout.addWidget(titulo)

        descricao = QLabel(
            "Selecione múltiplos grupos para executar extrações de usuários."
        )
        descricao.setWordWrap(True)
        painel_layout.addWidget(descricao)

        self._lista_grupos = QListWidget()
        self._lista_grupos.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        # Dados de exemplo
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

        botao_continuar = QPushButton("Salvar no Banco e Concluir")
        botao_continuar.clicked.connect(self._concluir_extracao)
        botoes.addWidget(botao_continuar)
        layout.addLayout(botoes)
        return passo

    def _criar_passo_conclusao(self) -> QWidget:
        passo = QGroupBox("Passo 3 • Finalização")
        layout = QVBoxLayout(passo)
        layout.setSpacing(12)

        mensagem = QLabel(
            "Extração concluída! Os usuários foram salvos no Banco de Usuários local."
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
            self._notifications.notify("Aviso", "Selecione pelo menos um grupo para extrair.")
            return
        self._executar_extracao(selecionados)
        self._wizard.setCurrentIndex(1)

    def _executar_extracao(self, grupos: List[str]) -> None:
        filtro = self._input_filtro.text()
        try:
            # Em uma aplicação real, isso deveria rodar em background (ex: no engine)
            # Por enquanto, executamos direto para simular.
            resumo = self._extraction_service.run_basic_extraction(grupos, filtro=filtro)
        except ValueError as e:
            self._notifications.notify("Erro", str(e))
            return

        self._dados_preview = [
            (registro.username, registro.role, registro.origin_group)
            for registro in resumo.users
        ]
        self._popular_tabela(self._dados_preview)
        self._progresso.setValue(resumo.progress or randint(45, 95))

        self._notifications.notify(
            titulo="Extração Pré-visualizada",
            mensagem=f"{len(self._dados_preview)} usuários encontrados.",
        )

    def _concluir_extracao(self) -> None:
        # A lógica em _executar_extracao já salva no banco (run_basic_extraction)
        # Esta etapa apenas confirma e move o wizard.
        self._notifications.notify(
            titulo="Extração Salva",
            mensagem=f"{len(self._dados_preview)} usuários salvos no banco local.",
        )
        self.extraction_finished.emit()
        self._wizard.setCurrentIndex(2)

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
            self._progresso.setValue(100 if self._dados_preview else 0)
            return
        filtrados = [
            item
            for item in self._dados_preview
            if termo_normalizado in " ".join(item).lower()
        ]
        self._popular_tabela(filtrados)
        self._progresso.setValue(min(100, 50 + len(filtrados)) if filtrados else 0)

