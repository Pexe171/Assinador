"""Formulário para autenticação de novas contas."""

from __future__ import annotations

import json
import re
from typing import Callable

from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from TelegramManager.core.container import Container
from TelegramManager.core.session_manager import SessionInfo
from TelegramManager.utils.qr import decode_qr_image


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

        botoes_layout = QHBoxLayout()
        botoes_layout.setContentsMargins(0, 16, 0, 0)
        botoes_layout.setSpacing(12)

        self._botao_autenticar = QPushButton("Iniciar autenticação")
        self._botao_autenticar.clicked.connect(self._iniciar_autenticacao)
        botoes_layout.addWidget(self._botao_autenticar)

        self._botao_autenticar_qr = QPushButton("Autenticar com QR Code")
        self._botao_autenticar_qr.clicked.connect(self._iniciar_autenticacao_qr)
        botoes_layout.addWidget(self._botao_autenticar_qr)

        layout.addLayout(botoes_layout)
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

    def _iniciar_autenticacao_qr(self) -> None:
        """Permite registrar uma conta lendo um QR Code existente."""

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar QR Code",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.webp);;Todos os arquivos (*)",
        )
        if not arquivo:
            return

        try:
            payload = decode_qr_image(arquivo)
            telefone, display, status = self._interpretar_payload(payload)
        except ValueError as exc:
            QMessageBox.critical(self, "QR Code inválido", str(exc))
            return

        session = self._container.session_manager.register_session(phone=telefone, display_name=display)
        if status and status.lower() != session.status.lower():
            self._container.session_manager.update_status(telefone, status)
            session = self._container.session_manager.get_session(telefone) or session

        self._on_create(session)
        self._limpar_campos()

    def _interpretar_payload(self, payload: str) -> tuple[str, str, str]:
        """Extrai telefone, nome e status de diferentes formatos suportados."""

        dados: dict[str, str]
        try:
            estrutura = json.loads(payload)
        except json.JSONDecodeError:
            dados = {}
            for parte in re.split(r"[;\n]", payload):
                if "=" not in parte:
                    continue
                chave, valor = parte.split("=", 1)
                dados[chave.strip().lower()] = valor.strip()
        else:
            if not isinstance(estrutura, dict):
                raise ValueError("O QR Code precisa conter um objeto JSON ou pares chave=valor.")
            dados = {str(k).lower(): str(v) for k, v in estrutura.items()}

        telefone = dados.get("phone") or dados.get("telefone") or dados.get("numero")
        display = dados.get("display_name") or dados.get("nome") or dados.get("nome_exibicao")
        status = dados.get("status", "online")

        if not telefone or not display:
            raise ValueError(
                "O QR Code não contém os dados mínimos necessários (telefone e nome de exibição)."
            )

        return telefone, display, status
