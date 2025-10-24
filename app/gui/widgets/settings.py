"""Widget de configurações gerais da plataforma."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsWidget(QWidget):
    """Reúne parâmetros essenciais para personalizar a operação."""

    def __init__(self) -> None:
        super().__init__()
        self._montar_layout()

    def _montar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(18)

        titulo = QLabel("Configurações")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        layout.addWidget(self._criar_grupo_aplicacao())
        layout.addWidget(self._criar_grupo_notificacoes())
        layout.addStretch()
        layout.addWidget(QPushButton("Salvar alterações"))

    def _criar_grupo_aplicacao(self) -> QWidget:
        grupo = QGroupBox("Preferências do aplicativo")
        form = QFormLayout(grupo)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        input_nome = QLineEdit("Assinador One")
        form.addRow("Nome da workspace", input_nome)

        combo_tema = QComboBox()
        combo_tema.addItems(["Automático", "Claro", "Escuro"])
        form.addRow("Tema visual", combo_tema)

        spinner_intervalo = QSpinBox()
        spinner_intervalo.setRange(1, 60)
        spinner_intervalo.setValue(5)
        spinner_intervalo.setSuffix(" min")
        form.addRow("Intervalo de sincronização", spinner_intervalo)

        return grupo

    def _criar_grupo_notificacoes(self) -> QWidget:
        grupo = QGroupBox("Alertas e automações")
        form = QFormLayout(grupo)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        check_sons = QCheckBox("Habilitar sons do sistema")
        check_sons.setChecked(True)
        form.addRow("Áudio", check_sons)

        check_resumo = QCheckBox("Receber resumo diário por e-mail")
        form.addRow("Relatórios", check_resumo)

        return grupo
