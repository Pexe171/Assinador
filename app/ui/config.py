"""Janela de configurações de contas e temas."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
)


class ConfigDialog(QDialog):
    """Permite editar contas do WhatsApp, temas e modelos de mensagem."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.token_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        form.addRow("Token WhatsApp:", self.token_edit)
        form.addRow("Phone Number ID:", self.phone_edit)
        layout.addLayout(form)

        self.save_btn = QPushButton("Salvar")
        layout.addWidget(self.save_btn)
