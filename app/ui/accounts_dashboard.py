"""Dashboard para gerenciar contas do WhatsApp.

Autor: Pexe – Instagram: @David.devloli
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QInputDialog,
)


class AccountCard(QFrame):
    """Cartão simples representando uma conta do WhatsApp."""

    def __init__(self, name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._name = name
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)

        # Cabeçalho com nome e status
        header = QHBoxLayout()
        self.name_lbl = QLabel(name)
        header.addWidget(self.name_lbl)
        header.addStretch()
        self.status_lbl = QLabel("Desconectado")
        header.addWidget(self.status_lbl)
        layout.addLayout(header)

        # Área do QR Code (placeholder)
        self.qr_lbl = QLabel("Aguardando QR Code")
        self.qr_lbl.setAlignment(Qt.AlignCenter)
        self.qr_lbl.setMinimumSize(200, 200)
        layout.addWidget(self.qr_lbl)

        # Botões de ação
        buttons = QHBoxLayout()
        self.connect_btn = QPushButton("Conectar")
        self.disconnect_btn = QPushButton("Desconectar")
        self.rename_btn = QPushButton("Renomear")
        self.remove_btn = QPushButton("Remover")
        for btn in (self.connect_btn, self.disconnect_btn, self.rename_btn, self.remove_btn):
            buttons.addWidget(btn)
        layout.addLayout(buttons)

        # Conexões básicas de sinais
        self.connect_btn.clicked.connect(self._on_connect)
        self.disconnect_btn.clicked.connect(self._on_disconnect)
        self.rename_btn.clicked.connect(self._on_rename)

    # --- Slots -------------------------------------------------------------
    def _on_connect(self) -> None:
        """Simula a conexão da conta."""
        self.status_lbl.setText("Conectado")
        self.qr_lbl.setText("Conta ativa")

    def _on_disconnect(self) -> None:
        """Simula a desconexão da conta."""
        self.status_lbl.setText("Desconectado")
        self.qr_lbl.setText("Aguardando QR Code")

    def _on_rename(self) -> None:
        """Permite renomear a conta."""
        novo_nome, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=self._name)
        if ok and novo_nome:
            self._name = novo_nome
            self.name_lbl.setText(novo_nome)


class AccountsDashboard(QWidget):
    """Dashboard com listagem de contas do WhatsApp."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Cabeçalho com título e botão de adicionar
        header = QHBoxLayout()
        header.addWidget(QLabel("Gerir Contas de WhatsApp"))
        header.addStretch()
        self.add_btn = QPushButton("+ Adicionar Conta")
        header.addWidget(self.add_btn)
        layout.addLayout(header)

        # Área rolável para cartões
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        scroll.setWidget(self._cards_container)
        layout.addWidget(scroll)

        # Sinal do botão de adicionar
        self.add_btn.clicked.connect(self._add_account_dialog)

        # Exemplo inicial
        self.add_account("pexe")

    def add_account(self, name: str) -> None:
        """Adiciona um novo cartão de conta."""
        card = AccountCard(name)
        self._cards_layout.addWidget(card)

    def _add_account_dialog(self) -> None:
        """Solicita um nome e cria uma conta."""
        nome, ok = QInputDialog.getText(self, "Nova Conta", "Nome da conta:")
        if ok and nome:
            self.add_account(nome)
