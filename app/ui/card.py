"""Widget de cartão para exibir informações de um cliente."""

from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QPushButton


class CustomerCard(QFrame):
    """Cartão com dados do cliente e ações rápidas."""

    def __init__(self, nome: str, status: str, parent=None) -> None:
        super().__init__(parent)
        self.nome = nome
        self.status = status
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(nome))
        layout.addWidget(QLabel(f"Status: {status}"))

        actions = QHBoxLayout()
        self.btn_first_contact = QPushButton("1º contato")
        self.btn_send_form = QPushButton("Enviar formulário")
        self.btn_validate = QPushButton("Validar agora")
        self.btn_resend = QPushButton("Reenviar")
        for btn in (
            self.btn_first_contact,
            self.btn_send_form,
            self.btn_validate,
            self.btn_resend,
        ):
            actions.addWidget(btn)
        layout.addLayout(actions)
