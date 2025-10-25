"""Formulário para autenticação de novas contas."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.authentication import AuthenticationError
from TelegramManager.core.container import Container
from TelegramManager.core.session_manager import SessionInfo


class SessionFormWidget(QWidget):
    """Widget que centraliza o fluxo de criação de contas."""

    def __init__(self, container: Container, on_create: Callable[[SessionInfo], None]) -> None:
        super().__init__()
        self._container = container
        self._on_create = on_create
        self._phone_code_hash: str | None = None
        self._montar_layout()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()
        self._input_phone = QLineEdit()
        self._input_phone.setPlaceholderText("Ex.: +5511999999999")
        self._input_display = QLineEdit()
        self._input_display.setPlaceholderText("Como a conta será exibida na lista")
        self._input_code = QLineEdit()
        self._input_code.setPlaceholderText("Código enviado pelo Telegram")
        self._input_code.setMaxLength(10)
        self._input_code.setEnabled(False)
        self._input_password = QLineEdit()
        self._input_password.setPlaceholderText("Senha 2FA (se houver)")
        self._input_password.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Telefone", self._input_phone)
        form.addRow("Nome de exibição", self._input_display)
        form.addRow("Código", self._input_code)
        form.addRow("Senha 2FA", self._input_password)

        layout.addLayout(form)

        self._status_label = QLabel("Informe o número e solicite o código de login.")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setWordWrap(True)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._status_label)

        self._botao_enviar_codigo = QPushButton("Enviar código")
        self._botao_enviar_codigo.clicked.connect(self._enviar_codigo)
        layout.addWidget(self._botao_enviar_codigo)

        self._botao_concluir = QPushButton("Concluir login")
        self._botao_concluir.setEnabled(False)
        self._botao_concluir.clicked.connect(self._concluir_login)
        layout.addWidget(self._botao_concluir)
        layout.addStretch()

    def _enviar_codigo(self) -> None:
        phone = self._input_phone.text().strip()
        if not phone:
            self._atualizar_status("Informe um número de telefone válido, incluindo o código do país.")
            return

        # Reinicia o estado para evitar reutilizar hashes antigos.
        self._phone_code_hash = None
        self._input_code.clear()
        self._input_code.setEnabled(False)
        self._botao_concluir.setEnabled(False)

        servico = self._container.authentication_service
        self._definir_interacoes_habilitadas(False)
        try:
            self._phone_code_hash = servico.request_login_code(
                phone=phone,
                on_state=self._atualizar_status,
            )
        except AuthenticationError as exc:
            self._phone_code_hash = None
            self._atualizar_status(str(exc))
        finally:
            self._definir_interacoes_habilitadas(True)

        if self._phone_code_hash:
            self._input_code.setEnabled(True)
            self._botao_concluir.setEnabled(True)
            self._input_code.setFocus()

    def _concluir_login(self) -> None:
        phone = self._input_phone.text().strip()
        code = self._input_code.text().strip()
        display = self._input_display.text().strip()
        password = self._input_password.text().strip() or None

        if not phone:
            self._atualizar_status("Informe o número de telefone utilizado na solicitação do código.")
            return
        if not self._phone_code_hash:
            self._atualizar_status("Envie o código primeiro para gerar um hash válido.")
            return
        if not code:
            self._atualizar_status("Digite o código recebido pelo Telegram.")
            return

        servico = self._container.authentication_service
        self._definir_interacoes_habilitadas(False)
        try:
            session = servico.authenticate_with_code(
                phone=phone,
                code=code,
                phone_code_hash=self._phone_code_hash,
                display_name=display or None,
                password=password,
                on_state=self._atualizar_status,
            )
        except AuthenticationError as exc:
            self._atualizar_status(str(exc))
            self._definir_interacoes_habilitadas(True)
            return

        self._on_create(session)
        self._atualizar_status("Conta autenticada e registrada com sucesso.")
        self._limpar_campos()
        self._definir_interacoes_habilitadas(True)

    def _definir_interacoes_habilitadas(self, habilitado: bool) -> None:
        self._input_phone.setEnabled(habilitado)
        self._input_display.setEnabled(habilitado)
        self._input_password.setEnabled(habilitado)
        self._botao_enviar_codigo.setEnabled(habilitado)
        possui_hash = self._phone_code_hash is not None
        self._input_code.setEnabled(habilitado and possui_hash)
        self._botao_concluir.setEnabled(habilitado and possui_hash)

    def _limpar_campos(self) -> None:
        self._input_phone.clear()
        self._input_display.clear()
        self._input_code.clear()
        self._input_password.clear()
        self._input_code.setEnabled(False)
        self._botao_concluir.setEnabled(False)
        self._phone_code_hash = None

    def _atualizar_status(self, mensagem: str) -> None:
        self._status_label.setText(mensagem)
