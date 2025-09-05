"""Widget de cartão para exibir informações de um cliente."""

# Autor: Pexe – Instagram: @David.devloli

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QStyle,
)

from app.core.models import Customer, Document, AuditLog
from app.core.theming import load_theme
from app.flows.send_form import send_form_pdf


class CustomerCard(QFrame):
    """Cartão com dados do cliente e ações rápidas."""

    def __init__(self, cliente: Customer, session, parent=None) -> None:
        super().__init__(parent)
        self.cliente = cliente
        self.session = session
        self.setFrameShape(QFrame.StyledPanel)

        theme_name = cliente.company.name.lower()
        self.theme = load_theme(theme_name)
        self.primary_color = self.theme.get("cor_primaria", "#000000")

        layout = QVBoxLayout(self)

        # Cabeçalho com nome e logo
        header = QHBoxLayout()
        name_lbl = QLabel(cliente.name)
        font = name_lbl.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        name_lbl.setFont(font)
        header.addWidget(name_lbl)
        header.addStretch()
        logo_lbl = QLabel()
        pixmap = QPixmap(self.theme.get("logo", ""))
        if not pixmap.isNull():
            logo_lbl.setPixmap(
                pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        header.addWidget(logo_lbl)
        layout.addLayout(header)

        # Corpo com informações secundárias
        layout.addWidget(QLabel(f"Telefone: {cliente.phone}"))

        # Rodapé com status e ações
        footer = QHBoxLayout()

        self.status_badge = QFrame()
        status_layout = QHBoxLayout(self.status_badge)
        status_layout.setContentsMargins(6, 2, 6, 2)
        self.status_icon = QLabel()
        self.status_text = QLabel()
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_text)
        footer.addWidget(self.status_badge)

        footer.addStretch()

        actions = QHBoxLayout()
        style = self.style()
        self.btn_first_contact = QPushButton("1º Contato")
        self.btn_first_contact.setIcon(style.standardIcon(QStyle.SP_MessageBoxInformation))
        self.btn_send_form = QPushButton("Enviar PDF")
        self.btn_send_form.setIcon(style.standardIcon(QStyle.SP_FileIcon))
        self.btn_validate = QPushButton("Marcar assinado")
        self.btn_validate.setIcon(style.standardIcon(QStyle.SP_DialogApplyButton))
        self.btn_review = QPushButton("Marcar validado")
        self.btn_review.setIcon(style.standardIcon(QStyle.SP_DialogYesButton))
        self.btn_resend = QPushButton("Reenviar")
        self.btn_resend.setIcon(style.standardIcon(QStyle.SP_BrowserReload))
        for btn in (
            self.btn_first_contact,
            self.btn_send_form,
            self.btn_validate,
            self.btn_review,
            self.btn_resend,
        ):
            actions.addWidget(btn)
        footer.addLayout(actions)
        layout.addLayout(footer)

        self.btn_send_form.clicked.connect(self.enviar_formulario)
        self.btn_validate.clicked.connect(self.marcar_assinado)
        self.btn_review.clicked.connect(self.marcar_validado)

        status = (
            cliente.documents[0].status if cliente.documents else "pendente"
        )
        self.update_status_badge(status)
        self.update_highlight(status)

    # --- Atualizações de interface -------------------------------------------------
    def update_status_badge(self, status: str) -> None:
        """Atualiza a *badge* de status no rodapé."""

        if status in {"assinado", "validado"}:
            color = "#28a745"
            text = "Assinado" if status == "assinado" else "Validado"
            icon = self.style().standardIcon(QStyle.SP_DialogApplyButton)
        else:
            color = "#FFC107"
            text = "Pendente"
            icon = QIcon()

        self.status_badge.setStyleSheet(
            f"QFrame {{background-color: {color}; border-radius: 4px;}}"
        )
        if icon.isNull():
            self.status_icon.clear()
        else:
            self.status_icon.setPixmap(icon.pixmap(16, 16))
        self.status_text.setText(text)

    def update_highlight(self, status: str) -> None:
        """Destaca o botão com a próxima ação."""

        for btn in (
            self.btn_first_contact,
            self.btn_send_form,
            self.btn_validate,
            self.btn_review,
            self.btn_resend,
        ):
            btn.setStyleSheet("")

        target: QPushButton | None = None
        if status == "pendente":
            target = self.btn_resend if self.cliente.documents else self.btn_send_form
        elif status == "assinado":
            target = self.btn_review

        if target is not None:
            target.setStyleSheet(
                f"background-color: {self.primary_color}; color: white;"
            )

    # --- Ações ---------------------------------------------------------------------
    def enviar_formulario(self) -> None:
        """Seleciona um PDF e envia ao cliente."""

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar PDF", filter="PDF (*.pdf)"
        )
        if file_path:
            send_form_pdf(self.cliente.phone, file_path, "Formulário")
            documento = Document(
                customer=self.cliente, file_path=file_path, status="pendente"
            )
            self.session.add(documento)
            self.session.add(
                AuditLog(
                    actor="dashboard",
                    action="enviar_pdf",
                    payload=str(self.cliente.id),
                )
            )
            self.session.commit()
            self.update_status_badge("pendente")
            self.update_highlight("pendente")

    def marcar_assinado(self) -> None:
        """Atualiza o status do documento para assinado."""

        if self.cliente.documents:
            doc = self.cliente.documents[0]
            doc.status = "assinado"
            doc.reviewed = False
            self.session.add(
                AuditLog(
                    actor="dashboard", action="marcar_assinado", payload=str(doc.id)
                )
            )
            self.session.commit()
            self.update_status_badge("assinado")
            self.update_highlight("assinado")

    def marcar_validado(self) -> None:
        """Atualiza o status do documento para validado."""

        if self.cliente.documents:
            doc = self.cliente.documents[0]
            doc.status = "validado"
            doc.reviewed = True
            self.session.add(
                AuditLog(
                    actor="dashboard", action="marcar_validado", payload=str(doc.id)
                )
            )
            self.session.commit()
            self.update_status_badge("validado")
            self.update_highlight("validado")

