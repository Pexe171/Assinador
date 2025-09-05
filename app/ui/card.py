"""Widget de cartão para exibir informações de um cliente."""

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
)

from app.core.models import Customer, Document, AuditLog
from app.flows.send_form import send_form_pdf


class CustomerCard(QFrame):
    """Cartão com dados do cliente e ações rápidas."""

    def __init__(self, cliente: Customer, session, parent=None) -> None:
        super().__init__(parent)
        self.cliente = cliente
        self.session = session
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(cliente.name))
        status = (
            cliente.documents[0].status if cliente.documents else "pendente"
        )
        self.lbl_status = QLabel(f"Status: {status}")
        layout.addWidget(self.lbl_status)
        revisado = (
            "Sim" if cliente.documents and cliente.documents[0].reviewed else "Não"
        )
        self.lbl_reviewed = QLabel(f"Revisado: {revisado}")
        layout.addWidget(self.lbl_reviewed)

        actions = QHBoxLayout()
        self.btn_first_contact = QPushButton("1º contato")
        self.btn_send_form = QPushButton("Enviar PDF")
        self.btn_validate = QPushButton("Marcar assinado")
        self.btn_review = QPushButton("Marcar validado")
        self.btn_resend = QPushButton("Reenviar")
        for btn in (
            self.btn_first_contact,
            self.btn_send_form,
            self.btn_validate,
            self.btn_review,
            self.btn_resend,
        ):
            actions.addWidget(btn)
        layout.addLayout(actions)

        self.btn_send_form.clicked.connect(self.enviar_formulario)
        self.btn_validate.clicked.connect(self.marcar_assinado)
        self.btn_review.clicked.connect(self.marcar_validado)

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
            self.lbl_status.setText("Status: pendente")
            self.lbl_reviewed.setText("Revisado: Não")

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
            self.lbl_status.setText("Status: assinado")
            self.lbl_reviewed.setText("Revisado: Não")

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
            self.lbl_status.setText("Status: validado")
            self.lbl_reviewed.setText("Revisado: Sim")
