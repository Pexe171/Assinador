"""Carregamento de temas para a interface."""

import json
from pathlib import Path
from typing import Any


def load_theme(name: str) -> dict[str, Any]:
    """Carrega um tema pelo nome."""
    theme_path = Path("assets/themes") / f"{name}.json"
    if theme_path.exists():
        return json.loads(theme_path.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Tema {name} não encontrado")
