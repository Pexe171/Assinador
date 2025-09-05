"""Utilitários para lidar com temas da interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget


THEMES_PATH = Path("assets/themes")


def available_themes() -> Iterable[str]:
    """Lista os temas disponíveis."""
    for file in THEMES_PATH.glob("*.json"):
        yield file.stem


def load_theme(name: str) -> dict[str, Any]:
    """Carrega um tema pelo nome."""
    theme_path = THEMES_PATH / f"{name}.json"
    if theme_path.exists():
        return json.loads(theme_path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Tema {name} não encontrado")


def apply_theme(widget: QWidget, theme: dict[str, Any]) -> None:
    """Aplica as propriedades do tema ao *widget* raiz."""
    style = f"""
        QWidget {{
            background-color: {theme.get('fundo', '#FFFFFF')};
            font-family: '{theme.get('fonte', 'Inter')}', sans-serif;
        }}

        QPushButton, QLineEdit {{
            border-radius: {theme.get('raio_borda', 0)}px;
        }}

        QFrame {{
            background-color: {theme.get('card', '#FFFFFF')};
            border-radius: {theme.get('raio_borda', 0)}px;
        }}
    """

    widget.setStyleSheet(style)

    logo = theme.get("logo")
    if logo:
        widget.setWindowIcon(QIcon(logo))
