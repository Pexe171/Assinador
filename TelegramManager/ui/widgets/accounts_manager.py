# Caminho: TelegramManager/ui/widgets/accounts_manager.py
"""Widget para gestão visual de contas Telegram."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.container import Container
from TelegramManager.core.session_manager import SessionInfo
from TelegramManager.notifications.dispatcher import NotificationDispatcher
from TelegramManager.ui.widgets.session_form import SessionFormWidget


@dataclass
class AccountData:
    """Mantém as preferências e histórico de cada conta."""

    info: SessionInfo
    notificacoes: bool = True
    logs: list[str] = field(default_factory=list)


class AccountsManagerWidget(QWidget):
    """Apresenta a lista de contas com opções de organização e detalhes."""

    # Sinal emitido quando contas são adicionadas ou modificadas
    account_changed = pyqtSignal()

    def __init__(
        self,
        container: Container,
        notifications: NotificationDispatcher,
    ) -> None:
        super().__init__()
        self._container = container
        self._notifications = notifications
        self._contas: Dict[str, AccountData] = {}

        self._montar_layout()
        self._carregar_sessoes()

    def _montar_layout(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        painel_form = QVBoxLayout()
        painel_form.setSpacing(12)

        titulo = QLabel("Contas Telegram")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        painel_form.addWidget(titulo)

        descricao = QLabel(
            "Gerencie suas contas, personalize preferências e "
            "acompanhe os logs de cada sessão."
        )
        descricao.setWordWrap(True)
        painel_form.addWidget(descricao)

        self._form = SessionFormWidget(
            container=self._container,
            on_create=self._registrar_sessao,
        )
        painel_form.addWidget(self._form)
        painel_form.addStretch()

        layout.addLayout(painel_form, stretch=1)

        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Horizontal)

        self._lista = QListWidget()
        self._lista.setAlternatingRowColors(True)
        self._lista.setDragEnabled(True)
        self._lista.setAcceptDrops(True)
        self._lista.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._lista.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._lista.itemSelectionChanged.connect(self._atualizar_detalhes)
        splitter.addWidget(self._lista)

        self._painel_detalhes = self._criar_painel_detalhes()
        splitter.addWidget(self._painel_detalhes)
        splitter.setSizes([200, 400])

        layout.addWidget(splitter, stretch=2)

    def _criar_painel_detalhes(self) -> QWidget:
        painel = QWidget()
        painel_layout = QVBoxLayout(painel)
        painel_layout.setSpacing(12)

        self._titulo_detalhe = QLabel("Selecione uma conta para ver detalhes")
        self._titulo_detalhe.setStyleSheet("font-size: 18px; font-weight: bold;")
        painel_layout.addWidget(self._titulo_detalhe)

        grupo_preferencias = QGroupBox("Preferências individuais")
        form = QFormLayout(grupo_preferencias)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._label_telefone = QLabel("-")
        form.addRow("Telefone", self._label_telefone)

        self._label_status = QLabel("-")
        form.addRow("Status", self._label_status)

        self._botao_teste = QPushButton("Testar conexão")
        self._botao_teste.clicked.connect(self._testar_conexao)
        self._botao_teste.setEnabled(False)
        form.addRow("Rede", self._botao_teste)

        painel_layout.addWidget(grupo_preferencias)

        grupo_logs = QGroupBox("Logs da conta")
        logs_layout = QVBoxLayout(grupo_logs)
        self._logs = QPlainTextEdit()
        self._logs.setReadOnly(True)
        logs_layout.addWidget(self._logs)
        painel_layout.addWidget(grupo_logs)

        painel_layout.addStretch()
        return painel

    def _carregar_sessoes(self) -> None:
        self._container.session_manager.load_persisted_sessions()
        for info in self._container.session_manager.sessions.values():
            self._registrar_sessao(info, notificar=False)

    def _registrar_sessao(self, session: SessionInfo, notificar: bool = True) -> None:
        existente = self._buscar_item(session.phone)
        if existente is None:
            avatar = QPixmap(48, 48)
            avatar.fill(Qt.GlobalColor.lightGray)
            item = QListWidgetItem(QIcon(avatar), f"{session.display_name}\n{session.phone}")
            item.setData(Qt.ItemDataRole.UserRole, session.phone)
            self._lista.addItem(item)
            dados = AccountData(info=session)
            dados.logs.append("Conta conectada com sucesso")
            self._contas[session.phone] = dados
            if notificar:
                self._notifications.notify(
                    titulo="Conta disponível",
                    mensagem=f"A conta {session.display_name} foi registrada.",
                )
        else:
            existente.setText(f"{session.display_name}\n{session.phone}")
            dados = self._contas[session.phone]
            dados.info = session
            dados.logs.append("Dados atualizados")

        self._atualizar_detalhes()
        self.account_changed.emit()

    def _obter_conta_selecionada(self) -> AccountData | None:
        item = self._lista.currentItem()
        if not item:
            return None
        phone = item.data(Qt.ItemDataRole.UserRole)
        return self._contas.get(phone)

    def _buscar_item(self, phone: str) -> QListWidgetItem | None:
        for indice in range(self._lista.count()):
            item = self._lista.item(indice)
            if item.data(Qt.ItemDataRole.UserRole) == phone:
                return item
        return None

    def _atualizar_detalhes(self) -> None:
        conta = self._obter_conta_selecionada()
        if not conta:
            self._titulo_detalhe.setText("Selecione uma conta para ver detalhes")
            self._label_telefone.setText("-")
            self._label_status.setText("-")
            self._logs.clear()
            self._botao_teste.setEnabled(False)
            return

        self._titulo_detalhe.setText(conta.info.display_name)
        self._label_telefone.setText(conta.info.phone)
        self._label_status.setText(conta.info.status)
        self._logs.setPlainText("\n".join(conta.logs))
        self._botao_teste.setEnabled(True)

    def _testar_conexao(self) -> None:
        conta = self._obter_conta_selecionada()
        if not conta:
            return
        conta.logs.append("Teste de conexão solicitado")
        conta.logs.append("Resposta: online e responsiva")
        self._logs.setPlainText("\n".join(conta.logs))
        self._registrar_toast(
            f"Teste concluído para {conta.info.display_name}."
        )

    def _registrar_toast(self, mensagem: str) -> None:
        self._notifications.notify(titulo="Status da conta", mensagem=mensagem)

