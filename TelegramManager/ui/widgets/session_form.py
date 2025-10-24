"""Formulário para autenticação de novas contas."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtWidgets import (
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.container import Container
from TelegramManager.core.session_manager import SessionInfo


class SessionFormWidget(QWidget):
    """Widget que centraliza o fluxo de criação de contas."""

    def __init__(self, container: Container, on_create: Callable[[SessionInfo], None]) -> None:
        super().__init__()
        self._container = container
        self._on_create = on_create
        self._montar_layout()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()
        self._input_phone = QLineEdit()
        self._input_display = QLineEdit()
        form.addRow("Telefone", self._input_phone)
        form.addRow("Nome de exibição", self._input_display)

        layout.addLayout(form)

        self._botao_autenticar = QPushButton("Iniciar autenticação")
        self._botao_autenticar.clicked.connect(self._iniciar_autenticacao)
        layout.addWidget(self._botao_autenticar)
        layout.addStretch()

    def _iniciar_autenticacao(self) -> None:
        phone = self._input_phone.text().strip()
        display = self._input_display.text().strip()
        if not phone or not display:
            return

        session = self._container.session_manager.register_session(phone=phone, display_name=display)
        self._on_create(session)
        self._limpar_campos()

    def _limpar_campos(self) -> None:
        self._input_phone.clear()
        self._input_display.clear()
