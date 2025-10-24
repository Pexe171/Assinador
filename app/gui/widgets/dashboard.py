"""Dashboard com métricas em tempo real."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.core.container import Container


class DashboardWidget(QWidget):
    """Widget simplificado exibindo métricas sintéticas."""

    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._montar_layout()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("Visão Geral")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titulo)

        self._metricas = QLabel(
            "Contas conectadas: 0\n" "Listas mapeadas hoje: 0\n" "Erros nas últimas 24h: 0"
        )
        layout.addWidget(self._metricas)

    def atualizar_metricas(self, conectadas: int, mapeamentos: int, erros: int) -> None:
        self._metricas.setText(
            f"Contas conectadas: {conectadas}\n"
            f"Listas mapeadas hoje: {mapeamentos}\n"
            f"Erros nas últimas 24h: {erros}"
        )
