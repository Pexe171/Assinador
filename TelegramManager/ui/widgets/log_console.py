"""Console de logs embutido para acompanhamento das operações."""

from __future__ import annotations

import logging

from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class LogConsoleWidget(QWidget):
    """Renderiza logs da aplicação em um painel somente leitura."""

    def __init__(self) -> None:
        super().__init__()
        self._montar_layout()
        self._conectar_logging()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._texto = QTextEdit()
        self._texto.setReadOnly(True)
        self._texto.setStyleSheet("background: #101820; color: #E0E0E0; font-family: monospace;")
        layout.addWidget(self._texto)

    def _conectar_logging(self) -> None:
        handler = _LogHandler(self._texto)
        logging.getLogger().addHandler(handler)


class _LogHandler(logging.Handler):
    def __init__(self, destino: QTextEdit) -> None:  # type: ignore[name-defined]
        super().__init__()
        self._destino = destino

    def emit(self, record: logging.LogRecord) -> None:
        mensagem = self.format(record)
        self._destino.append(mensagem)
        self._destino.verticalScrollBar().setValue(self._destino.verticalScrollBar().maximum())
