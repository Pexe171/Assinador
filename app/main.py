"""Ponto de entrada da aplicação desktop.

Este módulo inicializa a aplicação Qt, configura serviços centrais e exibe a
janela principal. Foi escrito de forma a manter responsabilidades separadas
entre interface, backend e infraestrutura, garantindo testabilidade.
"""

from __future__ import annotations

import logging
import signal
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from app.config import AppConfig
from app.core.container import Container
from app.gui.main_window import MainWindow
from app.notifications.dispatcher import NotificationDispatcher


def configurar_logging(config: AppConfig) -> None:
    """Configura o logging básico da aplicação.

    Utilizamos rotação de logs em disco para facilitar suporte e auditoria,
    além de também imprimir no *stderr* durante o modo desenvolvimento.
    """

    log_path = Path(config.paths.logs_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=config.logging.level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_path / "app.log", encoding="utf-8"),
        ],
    )


def main() -> int:
    """Executa a aplicação seguindo boas práticas de inicialização."""

    config = AppConfig.from_env()
    configurar_logging(config)
    logging.getLogger(__name__).info("Iniciando aplicação de mapeamento")

    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)

    container = Container(config)
    notificacoes = NotificationDispatcher(config=config)

    janela = MainWindow(container=container, notifications=notificacoes)
    janela.show()

    # Permite encerramento limpo ao receber CTRL+C no terminal
    signal.signal(signal.SIGINT, lambda *_: app.quit())

    codigo_saida = app.exec()
    logging.getLogger(__name__).info("Aplicação finalizada com código %s", codigo_saida)
    return codigo_saida


if __name__ == "__main__":
    sys.exit(main())
