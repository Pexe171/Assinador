"""Widget de configurações gerais da plataforma."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
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

        layout.addWidget(self._criar_grupo_configuracoes_sistema())
        layout.addWidget(self._criar_grupo_configuracoes_automacao())
        layout.addStretch()
        layout.addWidget(QPushButton("Salvar alterações"))

    def _criar_grupo_configuracoes_sistema(self) -> QWidget:
        grupo = QGroupBox("⚙️ Configurações do sistema")
        form = QFormLayout(grupo)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setVerticalSpacing(12)

        combo_tema = QComboBox()
        combo_tema.addItems(["Automático", "Claro", "Escuro"])
        form.addRow("Tema", combo_tema)

        combo_idioma = QComboBox()
        combo_idioma.addItems([
            "Português (Brasil)",
            "Inglês (EN)",
            "Espanhol (ES)",
        ])
        form.addRow("Idioma", combo_idioma)

        botao_atalhos = QPushButton("Personalizar atalhos…")
        form.addRow("Atalhos de teclado", botao_atalhos)

        container_comportamento = QWidget()
        comportamento_layout = QVBoxLayout(container_comportamento)
        comportamento_layout.setContentsMargins(0, 0, 0, 0)
        comportamento_layout.setSpacing(6)

        check_iniciar_os = QCheckBox("Iniciar automaticamente com o sistema operacional")
        check_iniciar_os.setChecked(True)
        comportamento_layout.addWidget(check_iniciar_os)

        check_minimizar_tray = QCheckBox("Minimizar para a bandeja após autenticar")
        comportamento_layout.addWidget(check_minimizar_tray)

        form.addRow("Comportamento", container_comportamento)

        container_backup = QWidget()
        backup_layout = QHBoxLayout(container_backup)
        backup_layout.setContentsMargins(0, 0, 0, 0)
        backup_layout.setSpacing(8)

        check_backup = QCheckBox("Realizar backups automáticos das configurações")
        check_backup.setChecked(True)
        backup_layout.addWidget(check_backup)

        spinner_backup = QSpinBox()
        spinner_backup.setRange(1, 30)
        spinner_backup.setValue(7)
        spinner_backup.setSuffix(" dias")
        backup_layout.addWidget(spinner_backup)

        form.addRow("Backup", container_backup)

        return grupo

    def _criar_grupo_configuracoes_automacao(self) -> QWidget:
        grupo = QGroupBox("🤖 Configurações de automação")
        form = QFormLayout(grupo)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setVerticalSpacing(12)

        spinner_limite = QSpinBox()
        spinner_limite.setRange(10, 2000)
        spinner_limite.setValue(250)
        spinner_limite.setSuffix(" ações")
        form.addRow("Limites por conta", spinner_limite)

        spinner_delay = QSpinBox()
        spinner_delay.setRange(1, 120)
        spinner_delay.setValue(5)
        spinner_delay.setSuffix(" s")
        form.addRow("Delay entre ações", spinner_delay)

        container_retry = QWidget()
        retry_layout = QHBoxLayout(container_retry)
        retry_layout.setContentsMargins(0, 0, 0, 0)
        retry_layout.setSpacing(8)

        spinner_retry = QSpinBox()
        spinner_retry.setRange(0, 10)
        spinner_retry.setValue(3)
        spinner_retry.setPrefix("Tentativas: ")
        retry_layout.addWidget(spinner_retry)

        combo_retry = QComboBox()
        combo_retry.addItems(["Linear", "Exponencial", "Incremental"])
        retry_layout.addWidget(combo_retry)

        form.addRow("Retry policies", container_retry)

        botao_filtros = QPushButton("Configurar filtros avançados")
        form.addRow("Filtros de usuários", botao_filtros)

        combo_templates = QComboBox()
        combo_templates.addItems([
            "Padrão equilibrado",
            "Alta conversão",
            "Baixo risco",
        ])
        form.addRow("Templates de comportamento", combo_templates)

        return grupo
