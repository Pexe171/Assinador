"""Dashboard exibindo fila de clientes e filtros."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QListWidget,
    QListWidgetItem,
)

from .card import CustomerCard


class Dashboard(QWidget):
    """Área principal com filtros e lista de clientes."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.filtro_empresa = QComboBox()
        self.filtro_empresa.addItems(["Todas", "MRV", "Direcional"])
        layout.addWidget(self.filtro_empresa)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(
            ["Todos", "Novo", "Engajado", "Form enviado", "Assinado", "Validado"]
        )
        layout.addWidget(self.filtro_status)

        self.lista = QListWidget()
        layout.addWidget(self.lista)

    def adicionar_cliente(self, nome: str, status: str) -> None:
        """Adiciona um cartão de cliente à fila."""
        item = QListWidgetItem()
        card = CustomerCard(nome, status)
        item.setSizeHint(card.sizeHint())
        self.lista.addItem(item)
        self.lista.setItemWidget(item, card)
