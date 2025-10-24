"""Console de logs embutido para acompanhamento das operações."""

from __future__ import annotations

import logging
from datetime import datetime

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QTextOption
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LogConsoleWidget(QWidget):
    """Renderiza logs da aplicação em um painel estilizado, semelhante a um terminal."""

    def __init__(self) -> None:
        super().__init__()
        self._auto_scroll = True
        self._animacao_status: QPropertyAnimation | None = None

        self._montar_layout()
        self._configurar_estilos()
        self._iniciar_animacao_status()
        self._conectar_logging()

    def _montar_layout(self) -> None:
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(12, 12, 12, 12)
        layout_principal.setSpacing(0)

        container = QFrame()
        container.setObjectName("console_container")

        layout_container = QVBoxLayout(container)
        layout_container.setContentsMargins(20, 20, 20, 20)
        layout_container.setSpacing(16)

        cabecalho = self._criar_cabecalho()
        layout_container.addLayout(cabecalho)

        botoes = self._criar_acoes()
        layout_container.addLayout(botoes)

        self._texto = QTextEdit()
        self._texto.setObjectName("terminal_texto")
        self._texto.setReadOnly(True)
        self._texto.setMinimumSize(520, 320)
        self._texto.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        layout_container.addWidget(self._texto)

        layout_principal.addWidget(container)
        self.setMinimumSize(560, 420)

    def _criar_cabecalho(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        titulo = QLabel("🖥️ Terminal de Logs")
        titulo.setObjectName("titulo_console")

        self._status = QLabel("Ao vivo • {}".format(datetime.now().strftime("%H:%M:%S")))
        self._status.setObjectName("status_console")

        layout.addWidget(titulo)
        layout.addStretch()
        layout.addWidget(self._status)

        return layout

    def _criar_acoes(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        self._botao_limpar = QPushButton("Limpar terminal")
        self._botao_limpar.clicked.connect(self._texto.clear)

        self._botao_copiar = QPushButton("Copiar tudo")
        self._botao_copiar.clicked.connect(self._copiar_logs)

        self._botao_scroll = QPushButton("Auto-rolagem ativa")
        self._botao_scroll.setCheckable(True)
        self._botao_scroll.setChecked(True)
        self._botao_scroll.clicked.connect(self._alternar_scroll)

        layout.addWidget(self._botao_limpar)
        layout.addWidget(self._botao_copiar)
        layout.addWidget(self._botao_scroll)
        layout.addStretch()

        return layout

    def _configurar_estilos(self) -> None:
        self.setStyleSheet(
            """
            #console_container {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0f172a,
                    stop: 1 #172554
                );
                border: 1px solid #1f2a44;
                border-radius: 16px;
            }

            #titulo_console {
                font-size: 18px;
                font-weight: 600;
                color: #e2e8f0;
            }

            #status_console {
                color: #38bdf8;
                background-color: rgba(56, 189, 248, 0.12);
                padding: 4px 10px;
                border-radius: 10px;
                font-size: 13px;
            }

            QPushButton {
                background-color: rgba(15, 23, 42, 0.6);
                color: #e2e8f0;
                padding: 8px 14px;
                border-radius: 10px;
                border: 1px solid rgba(148, 163, 184, 0.2);
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: rgba(59, 130, 246, 0.4);
            }

            QPushButton:checked {
                background-color: #38bdf8;
                color: #0f172a;
                border-color: #38bdf8;
            }

            #terminal_texto {
                background-color: rgba(15, 23, 42, 0.82);
                color: #f8fafc;
                font-family: "Cascadia Code", "Fira Code", monospace;
                font-size: 13px;
                border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 12px;
                padding: 12px;
            }
            """
        )

    def _iniciar_animacao_status(self) -> None:
        efeito = QGraphicsOpacityEffect(self._status)
        self._status.setGraphicsEffect(efeito)

        animacao = QPropertyAnimation(efeito, b"opacity", self)
        animacao.setStartValue(0.45)
        animacao.setEndValue(1.0)
        animacao.setDuration(2200)
        animacao.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animacao.setLoopCount(-1)
        animacao.start()

        self._animacao_status = animacao

    def _copiar_logs(self) -> None:
        QApplication.clipboard().setText(self._texto.toPlainText())

    def _alternar_scroll(self) -> None:
        self._auto_scroll = self._botao_scroll.isChecked()
        if self._auto_scroll:
            self._botao_scroll.setText("Auto-rolagem ativa")
            self._ajustar_scroll()
        else:
            self._botao_scroll.setText("Auto-rolagem pausada")

    def _ajustar_scroll(self) -> None:
        if self._auto_scroll:
            barra = self._texto.verticalScrollBar()
            barra.setValue(barra.maximum())

    def _conectar_logging(self) -> None:
        handler = _LogHandler(self)
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S")
        )
        logging.getLogger().addHandler(handler)

    def _registrar_mensagem(self, mensagem: str) -> None:
        horario = datetime.now().strftime("%H:%M:%S")
        self._status.setText(f"Ao vivo • {horario}")
        self._texto.append(mensagem)
        self._ajustar_scroll()


class _LogHandler(logging.Handler):
    def __init__(self, widget: LogConsoleWidget) -> None:
        super().__init__()
        self._widget = widget

    def emit(self, record: logging.LogRecord) -> None:
        mensagem = self.format(record)
        self._widget._registrar_mensagem(mensagem)
