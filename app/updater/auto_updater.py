"""Módulo responsável por verificar e aplicar atualizações."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

from app.config import AppConfig

logger = logging.getLogger(__name__)


@dataclass
class UpdateInfo:
    version: str
    url: str
    checksum: str


class AutoUpdater:
    """Consulta um endpoint remoto e aplica updates de forma segura."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def check_for_updates(self, endpoint: str) -> Optional[UpdateInfo]:
        logger.info("Verificando atualizações em %s", endpoint)
        resposta = requests.get(endpoint, timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()
        if dados.get("version"):
            info = UpdateInfo(version=dados["version"], url=dados["url"], checksum=dados["checksum"])
            logger.info("Atualização %s disponível", info.version)
            return info
        logger.info("Nenhuma atualização encontrada")
        return None

    def download_update(self, info: UpdateInfo, destino: Path) -> Path:
        destino.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Baixando atualização %s", info.version)
        resposta = requests.get(info.url, timeout=30)
        resposta.raise_for_status()
        destino.write_bytes(resposta.content)
        self._validate_checksum(destino, info.checksum)
        return destino

    def _validate_checksum(self, arquivo: Path, esperado: str) -> None:
        checksum = hashlib.sha256(arquivo.read_bytes()).hexdigest()
        if checksum != esperado:
            raise ValueError("Checksum inválido para o pacote baixado")

    def apply_update(self, pacote: Path) -> None:
        logger.info("Aplicando atualização a partir de %s", pacote)
        # Implementação dependente do empacotamento final (AppImage, MSI, etc.)
        # Manter backups e rollback em caso de erro.
