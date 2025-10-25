"""Painel de grupos sincronizados para escolha rápida de destinos."""

from __future__ import annotations

from typing import List

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.extraction import ExtractionService, SyncedGroup
from TelegramManager.core.session_manager import SessionManager
from TelegramManager.notifications.dispatcher import NotificationDispatcher
from TelegramManager.utils.helpers import formatar_data_humana


class GroupAutomationWidget(QWidget):
    """Lista os grupos disponíveis por conta após a sincronização."""

    def __init__(
        self,
        *,
        session_manager: SessionManager,
        extraction_service: ExtractionService,
        notifications: NotificationDispatcher | None = None,
    ) -> None:
        super().__init__()
        self._session_manager = session_manager
        self._extraction_service = extraction_service
        self._notifications = notifications
        self._grupos: List[SyncedGroup] = []

        self._combo_contas: QComboBox
        self._filtro_nome: QLineEdit
        self._tabela: QTableWidget
        self._label_status: QLabel

        self._montar_interface()
        self.recarregar()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Grupos sincronizados")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()
        botao_recarregar = QPushButton("Recarregar")
        botao_recarregar.clicked.connect(self.recarregar)
        cabecalho.addWidget(botao_recarregar)
        layout.addLayout(cabecalho)

        descricao = QLabel(
            "Visualize todos os grupos importados do Telegram após a sincronização das contas."
            " Escolha o destino ideal sem depender de agendamentos artificiais."
        )
        descricao.setWordWrap(True)
        layout.addWidget(descricao)

        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Conta sincronizada:"))
        self._combo_contas = QComboBox()
        self._combo_contas.currentIndexChanged.connect(lambda *_: self._atualizar_tabela())
        filtros.addWidget(self._combo_contas, stretch=1)
        filtros.addWidget(QLabel("Filtro por nome:"))
        self._filtro_nome = QLineEdit()
        self._filtro_nome.setPlaceholderText("Digite para filtrar os grupos")
        self._filtro_nome.textChanged.connect(self._filtrar)
        filtros.addWidget(self._filtro_nome, stretch=1)
        layout.addLayout(filtros)

        self._tabela = QTableWidget(0, 4)
        self._tabela.setHorizontalHeaderLabels(
            ["Grupo", "Conta", "Última sincronização", "Usuários no banco"]
        )
        self._tabela.verticalHeader().setVisible(False)
        self._tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabela.setAlternatingRowColors(True)
        header = self._tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self._tabela, stretch=1)

        self._label_status = QLabel()
        self._label_status.setStyleSheet("color: #64748b;")
        layout.addWidget(self._label_status)

    def recarregar(self) -> None:
        """Força a atualização da lista de contas e dos grupos carregados."""

        self._preencher_contas()
        self._atualizar_tabela()

    def _preencher_contas(self) -> None:
        sessions = self._session_manager.sessions
        self._combo_contas.blockSignals(True)
        self._combo_contas.clear()
        self._combo_contas.addItem("Todas as contas sincronizadas", None)
        for session in sorted(sessions.values(), key=lambda item: item.display_name.lower()):
            rotulo = f"{session.display_name} ({session.phone})"
            self._combo_contas.addItem(rotulo, session.phone)
        habilitar = bool(sessions)
        self._combo_contas.setEnabled(habilitar)
        self._combo_contas.blockSignals(False)

    def _atualizar_tabela(self) -> None:
        phone = self._combo_contas.currentData()
        try:
            self._grupos = self._extraction_service.list_synced_groups(
                account_phone=phone
            )
        except Exception as exc:  # pragma: no cover - proteção extra
            self._grupos = []
            self._notificar(
                "Erro",
                f"Não foi possível carregar os grupos sincronizados: {exc}",
            )
        self._filtrar()

    def _filtrar(self) -> None:
        termo = self._filtro_nome.text().lower().strip()
        if not termo:
            filtrados = list(self._grupos)
        else:
            filtrados = [
                grupo
                for grupo in self._grupos
                if termo in grupo.name.lower()
                or (grupo.account_display_name and termo in grupo.account_display_name.lower())
            ]
        self._popular_tabela(filtrados)
        self._atualizar_status(len(filtrados))

    def _popular_tabela(self, grupos: List[SyncedGroup]) -> None:
        self._tabela.setRowCount(len(grupos))
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

            self._tabela.setItem(linha, 0, QTableWidgetItem(grupo.name))
            self._tabela.setItem(linha, 1, QTableWidgetItem(conta))
            self._tabela.setItem(linha, 2, QTableWidgetItem(ultima))
            self._tabela.setItem(linha, 3, QTableWidgetItem(membros))

    def _atualizar_status(self, quantidade_filtrada: int) -> None:
        total = len(self._grupos)
        conta = self._combo_contas.currentText()
        if not total:
            mensagem = "Nenhum grupo sincronizado encontrado." if total == 0 else ""
        else:
            mensagem = (
                f"Mostrando {quantidade_filtrada} de {total} grupos sincronizados"
                f" • {conta}"
            )
        self._label_status.setText(mensagem)

    def _notificar(self, titulo: str, mensagem: str) -> None:
        if self._notifications:
            self._notifications.notify(titulo, mensagem)
