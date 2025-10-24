"""Funções auxiliares reutilizadas em diferentes camadas."""

from __future__ import annotations

from datetime import datetime
import uuid


def gerar_identificador(prefixo: str) -> str:
    """Gera um identificador curto legível para entidades temporárias."""

    sufixo = uuid.uuid4().hex[:8]
    return f"{prefixo}-{sufixo}"


def formatar_data_humana(valor: datetime) -> str:
    """Formata datas em um padrão amigável para a interface."""

    return valor.strftime("%d/%m/%Y %H:%M")
