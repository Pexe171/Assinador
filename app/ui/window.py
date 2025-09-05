"""Janela principal com a lista de clientes e ações."""

from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Assinador")
