"""Janela de configurações de contas e temas."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
)

from app.core.theming import available_themes


class ConfigDialog(QDialog):
    """Permite editar contas do WhatsApp, temas e modelos de mensagem."""

    def __init__(self, parent=None, tema_atual: str | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self._parent = parent

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.token_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(sorted(available_themes()))
        if tema_atual:
            index = self.theme_combo.findText(tema_atual)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

        form.addRow("Token WhatsApp:", self.token_edit)
        form.addRow("Phone Number ID:", self.phone_edit)
        form.addRow("Tema:", self.theme_combo)
        layout.addLayout(form)

        self.save_btn = QPushButton("Salvar")
        self.save_btn.clicked.connect(self._salvar)
        layout.addWidget(self.save_btn)

    def _salvar(self) -> None:
        """Aplica o tema selecionado."""
        if self._parent is not None:
            tema = self.theme_combo.currentText()
            if hasattr(self._parent, "set_theme"):
                self._parent.set_theme(tema)
        self.accept()
