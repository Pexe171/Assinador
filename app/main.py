"""Ponto de entrada da aplicação desktop."""

from PySide6.QtWidgets import QApplication

from app.ui.window import MainWindow
from app.ui.tray import TrayIcon
from app.server.http import run_server
from app.services.tunnel import start_tunnel, stop_tunnel, get_public_url


def main() -> None:
    """Inicializa a aplicação gráfica e serviços auxiliares."""
    app = QApplication([])

    # Inicia servidor HTTP para webhooks e callbacks
    run_server()

    # Abre túnel seguro e obtém URL pública
    tunnel_proc = start_tunnel(8000)
    public_url = get_public_url()

    # Ícone de bandeja exibindo a URL
    tray = TrayIcon(public_url)
    tray.show()

    window = MainWindow()
    window.show()

    app.aboutToQuit.connect(lambda: stop_tunnel(tunnel_proc))
    app.exec()


if __name__ == "__main__":
    main()
