"""Dashboard exibindo fila de clientes e filtros."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QListWidget,
    QListWidgetItem,
)

from app.core.db import SessionLocal
from app.core.models import Company, Customer, Document

from .card import CustomerCard


class Dashboard(QWidget):
    """Área principal com filtros e lista de clientes."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.session = SessionLocal()

        self.filtro_empresa = QComboBox()
        layout.addWidget(self.filtro_empresa)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "Pendente", "Assinado"])
        layout.addWidget(self.filtro_status)

        self.lista = QListWidget()
        layout.addWidget(self.lista)

        self.filtro_empresa.currentIndexChanged.connect(self.atualizar_lista)
        self.filtro_status.currentIndexChanged.connect(self.atualizar_lista)

        self.carregar_empresas()
        self.atualizar_lista()

    def carregar_empresas(self) -> None:
        """Preenche o filtro de empresas com dados do banco."""
        self.filtro_empresa.clear()
        self.filtro_empresa.addItem("Todas", None)
        for empresa in self.session.query(Company).all():
            self.filtro_empresa.addItem(empresa.name, empresa.id)

    def atualizar_lista(self) -> None:
        """Atualiza a lista de clientes conforme os filtros."""
        self.lista.clear()
        empresa_id = self.filtro_empresa.currentData()
        status = self.filtro_status.currentText()

        query = self.session.query(Customer)
        if empresa_id:
            query = query.filter(Customer.company_id == empresa_id)
        if status != "Todos":
            query = (
                query.join(Document, isouter=True)
                .filter(Document.status == status.lower())
            )
        for cliente in query.all():
            self.adicionar_cliente(cliente)

    def adicionar_cliente(self, cliente: Customer) -> None:
        """Adiciona um cartão de cliente à fila."""
        item = QListWidgetItem()
        card = CustomerCard(cliente, self.session)
        item.setSizeHint(card.sizeHint())
        self.lista.addItem(item)
        self.lista.setItemWidget(item, card)
