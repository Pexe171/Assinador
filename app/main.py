"""Ponto de entrada da aplicação desktop."""

from PySide6.QtWidgets import QApplication

from app.ui.window import MainWindow


def main() -> None:
    """Inicializa a aplicação gráfica."""
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
